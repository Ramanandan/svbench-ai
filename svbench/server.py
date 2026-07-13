"""Local review web app -- `svbench serve OUTDIR`.

Zero external dependencies (stdlib http.server). It upgrades the static
dashboard.html where static hits its limits:

  * images are streamed from disk, not base64-embedded, so it scales to
    thousands of loci (the static file would balloon to hundreds of MB);
  * triage decisions are persisted to OUTDIR/decisions.json, so they survive a
    restart and can feed back into the pipeline;
  * a single locus can be re-reviewed live (POST /api/review/<id>).

The static dashboard.html remains as the zero-setup offline fallback; this is
the live-demo surface. Runs entirely on localhost -- nothing is uploaded.

Routes
  GET  /                       the review UI (cards rendered server-side)
  GET  /images/<name>          stream a samplot PNG from disk
  GET  /api/loci               reviewed loci as JSON
  GET  /api/decisions          persisted decisions (JSON array)
  POST /api/decisions          upsert one decision {locus_id, decision, final, note, ...}
  POST /api/review/<locus_id>  re-run Claude on one locus; returns the new verdict
  GET  /api/export.csv         decisions as CSV
"""
from __future__ import annotations

import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from . import report
from .schema import ReviewedLocus

# The static template carries the full stylesheet; reuse it verbatim so the
# live app and the offline dashboard look identical.
_CSS = report._DASH_TEMPLATE.split("<style>", 1)[1].split("</style>", 1)[0]


def _load_reviewed(out_dir: Path) -> list[ReviewedLocus]:
    raw = json.loads((out_dir / "reviews.json").read_text())
    return [ReviewedLocus.model_validate(r) for r in raw]


def _load_summary(out_dir: Path) -> dict:
    p = out_dir / "summary.json"
    return json.loads(p.read_text()) if p.exists() else {}


def _decisions_file(out_dir: Path) -> Path:
    return out_dir / "decisions.json"


def _load_decisions(out_dir: Path) -> dict:
    p = _decisions_file(out_dir)
    return json.loads(p.read_text()) if p.exists() else {}


def _save_decisions(out_dir: Path, decisions: dict) -> None:
    _decisions_file(out_dir).write_text(json.dumps(decisions, indent=2))


def _find_image(out_dir: Path, name: str) -> Path | None:
    """Resolve a samplot filename to a real file, guarding against traversal."""
    if "/" in name or "\\" in name or ".." in name:
        return None
    for sub in ("images", "images_clean", "."):
        cand = (out_dir / sub / name).resolve()
        # Stay inside out_dir.
        if out_dir.resolve() in cand.parents and cand.exists():
            return cand
    return None


def _img_url(out_dir: Path, image_path: str | None) -> str:
    if not image_path:
        return ""
    name = Path(image_path).name
    return f"/images/{name}" if _find_image(out_dir, name) else ""


def render_page(out_dir: Path, caller: str) -> str:
    reviewed = _load_reviewed(out_dir)
    summary = _load_summary(out_dir)
    ordered = sorted(reviewed, key=lambda x: x.verdict.confidence, reverse=True)
    cards = "".join(
        report._card_html(r, img_src=_img_url(out_dir, r.packet.image_path), rereview=True)
        for r in ordered
    )
    banner = report.banner_html(reviewed, summary)
    return (_PAGE
            .replace("__CSS__", _CSS)
            .replace("__CARDS__", cards)
            .replace("__BANNER__", banner)
            .replace("__NREVIEWED__", str(len(reviewed)))
            .replace("__CALLER__", caller))


class _Handler(BaseHTTPRequestHandler):
    out_dir: Path
    caller: str
    lock = threading.Lock()

    def log_message(self, *a):  # quiet the default per-request stderr spam
        pass

    # -- helpers -------------------------------------------------------------
    def _send(self, code, body: bytes, ctype: str):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, json.dumps(obj).encode(), "application/json")

    def _read_body(self) -> dict:
        n = int(self.headers.get("Content-Length", 0) or 0)
        if not n:
            return {}
        try:
            return json.loads(self.rfile.read(n).decode() or "{}")
        except json.JSONDecodeError:
            return {}

    # -- routing -------------------------------------------------------------
    def do_GET(self):
        path = unquote(urlparse(self.path).path)
        try:
            if path == "/":
                self._send(200, render_page(self.out_dir, self.caller).encode(), "text/html; charset=utf-8")
            elif path.startswith("/images/"):
                self._serve_image(path[len("/images/"):])
            elif path == "/api/loci":
                self._json(json.loads((self.out_dir / "reviews.json").read_text()))
            elif path == "/api/decisions":
                self._json(list(_load_decisions(self.out_dir).values()))
            elif path == "/api/export.csv":
                self._export_csv()
            else:
                self._send(404, b"not found", "text/plain")
        except Exception as e:  # never crash the server on one bad request
            self._json({"error": str(e)}, 500)

    def do_HEAD(self):
        self.do_GET()

    def do_POST(self):
        path = unquote(urlparse(self.path).path)
        try:
            if path == "/api/decisions":
                self._post_decision()
            elif path.startswith("/api/review/"):
                self._rereview(path[len("/api/review/"):])
            else:
                self._send(404, b"not found", "text/plain")
        except Exception as e:
            self._json({"error": str(e)}, 500)

    # -- endpoints -----------------------------------------------------------
    def _serve_image(self, name: str):
        f = _find_image(self.out_dir, name)
        if not f:
            self._send(404, b"no such image", "text/plain")
            return
        self._send(200, f.read_bytes(), "image/png")

    def _post_decision(self):
        d = self._read_body()
        locus = d.get("locus_id")
        if not locus:
            self._json({"error": "locus_id required"}, 400)
            return
        with self.lock:
            decisions = _load_decisions(self.out_dir)
            decisions[locus] = d
            _save_decisions(self.out_dir, decisions)
        self._json({"ok": True, "saved": locus, "count": len(decisions)})

    def _rereview(self, locus_id: str):
        from . import review
        with self.lock:
            reviewed = _load_reviewed(self.out_dir)
            match = next((r for r in reviewed if r.packet.locus_id == locus_id), None)
            if not match:
                self._json({"error": f"unknown locus {locus_id}"}, 404)
                return
            try:
                is_trio = bool(match.packet.image_path and "trio" in Path(match.packet.image_path).name)
                mode = "qc" if match.packet.truvari_label == "QC" else "benchmark"
                fresh = review.review_locus(match.packet, mode=mode, trio=is_trio)
            except Exception as e:
                self._json({"error": f"re-review failed: {e}. Is ANTHROPIC_API_KEY set?"}, 503)
                return
            updated = [fresh if r.packet.locus_id == locus_id else r for r in reviewed]
            review.save_reviews(updated, self.out_dir / "reviews.json")
        v = fresh.verdict
        self._json({
            "locus_id": locus_id,
            "classification": v.classification,
            "confidence": v.confidence,
            "primary_reason": v.primary_reason,
            "explanation": v.explanation,
            "evidence_used": list(v.evidence_used),
        })

    def _export_csv(self):
        decisions = _load_decisions(self.out_dir)
        rows = [["locus_id", "truvari", "claude", "final", "decision", "confidence", "svtype", "note"]]
        for d in decisions.values():
            note = str(d.get("note", "")).replace('"', '""')
            rows.append([str(d.get(k, "")) for k in
                         ("locus_id", "truvari", "claude", "final", "decision", "confidence", "svtype")]
                        + [f'"{note}"'])
        csv = "\n".join(",".join(r) for r in rows)
        self.send_response(200)
        self.send_header("Content-Type", "text/csv")
        self.send_header("Content-Disposition", f"attachment; filename=svbench_decisions_{self.caller}.csv")
        self.send_header("Content-Length", str(len(csv.encode())))
        self.end_headers()
        self.wfile.write(csv.encode())


def serve(out_dir: Path, caller: str, port: int = 8000, open_browser: bool = True) -> None:
    out_dir = Path(out_dir)
    if not (out_dir / "reviews.json").exists():
        raise SystemExit(f"[serve] no reviews.json in {out_dir} — run `svbench review` first.")
    handler = type("Handler", (_Handler,), {"out_dir": out_dir, "caller": caller})
    httpd = ThreadingHTTPServer(("127.0.0.1", port), handler)
    url = f"http://127.0.0.1:{port}"
    n = len(_load_reviewed(out_dir))
    print(f"[serve] SVBench AI — {caller}: {n} loci at {url}  (Ctrl-C to stop)")
    if open_browser:
        threading.Thread(target=lambda: webbrowser.open(url), daemon=True).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[serve] stopped.")
        httpd.server_close()


# -- the dynamic page: same CSS/cards as the static dashboard, fetch-based JS --
_PAGE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SVBench AI (live) — __CALLER__</title>
<style>__CSS__
  .rerev{background:#1b2436 !important;color:#8fb6e8 !important}
  .rerev.busy{opacity:.5;pointer-events:none}
  .live{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;
    background:#123a2a;color:#7fe0a8;margin-left:8px}
</style></head><body>
<header>
  <h1>SVBench AI <span class="live">● live</span> — __CALLER__</h1>
  <div class="sub">__NREVIEWED__ discordant loci · decisions persist to <code>decisions.json</code> on disk · <kbd>j</kbd>/<kbd>k</kbd> move · <kbd>a</kbd> accept · <kbd>o</kbd> override</div>
  <div class="banner">__BANNER__</div>
  <div class="bar">
    <button class="filt active" data-f="all" onclick="filt(this,'all')">all</button>
    <button class="filt" data-f="benchmark_artifact" onclick="filt(this,'benchmark_artifact')">artifacts</button>
    <button class="filt" data-f="false_positive" onclick="filt(this,'false_positive')">false positives</button>
    <button class="filt" data-f="false_negative" onclick="filt(this,'false_negative')">false negatives</button>
    <button class="filt" data-f="true_positive" onclick="filt(this,'true_positive')">true positives</button>
    <button class="filt" data-f="uncertain" onclick="filt(this,'uncertain')">uncertain</button>
    <input id="q" placeholder="search locus…" oninput="search(this.value)"/>
    <span class="spacer"></span>
    <span class="progress" id="prog"></span>
    <button onclick="location='/api/decisions'">⤓ JSON</button>
    <button onclick="location='/api/export.csv'">⤓ CSV</button>
  </div>
</header>
__CARDS__
<script>
  const CALLER = "__CALLER__";
  let decisions = {};
  const cards = () => [...document.querySelectorAll('.card')];
  let focusIdx = 0;

  async function boot(){
    try{
      const arr = await (await fetch('/api/decisions')).json();
      arr.forEach(d=> decisions[d.locus_id]=d);
    }catch(e){}
    render();
  }
  function cardData(c){ return {
    locus_id:c.dataset.id, truvari:c.dataset.label, claude:c.dataset.cls,
    confidence:+c.dataset.conf, svtype:c.dataset.svtype }; }

  async function save(rec){
    decisions[rec.locus_id]=rec; render();
    try{ await fetch('/api/decisions',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify(rec)}); }catch(e){ alert('save failed: '+e); }
  }
  function decide(btn,kind){
    const d=cardData(btn.closest('.card'));
    save({...d, decision:'accept', final:d.claude, note:(decisions[d.locus_id]||{}).note||''});
  }
  function override(sel){
    if(!sel.value) return;
    const d=cardData(sel.closest('.card'));
    save({...d, decision:'override', final:sel.value, note:(decisions[d.locus_id]||{}).note||''});
  }
  function setNote(inp){
    const id=inp.closest('.card').dataset.id;
    if(decisions[id]){ decisions[id].note=inp.value; save(decisions[id]); }
  }

  async function reReview(btn){
    const c=btn.closest('.card'); const id=c.dataset.id;
    btn.classList.add('busy'); const t=btn.textContent; btn.textContent='↻ reviewing…';
    try{
      const r=await fetch('/api/review/'+encodeURIComponent(id),{method:'POST'});
      const v=await r.json();
      if(v.error){ alert(v.error); }
      else{
        c.dataset.cls=v.classification; c.dataset.conf=v.confidence.toFixed(3);
        c.querySelector('.cls').textContent='Claude: '+v.classification;
        c.querySelector('.cls').className='pill cls '+v.classification;
        c.querySelector('.conf').textContent='conf '+v.confidence.toFixed(2);
        c.querySelector('.reason').innerHTML='<b>'+v.primary_reason+'</b>';
        c.querySelector('.expl').textContent=v.explanation;
      }
    }catch(e){ alert('re-review failed: '+e); }
    btn.classList.remove('busy'); btn.textContent=t;
  }

  function render(){
    let acc=0, ovr=0;
    cards().forEach(c=>{
      const d=decisions[c.dataset.id]; const span=c.querySelector('.decision');
      c.classList.toggle('done', !!d);
      if(!d){ span.textContent=''; span.className='decision'; return; }
      if(d.decision==='accept'){ acc++; span.textContent='accepted ✓'; span.className='decision accepted'; }
      else { ovr++; span.textContent='→ '+d.final+' ✗'; span.className='decision overridden'; }
      const inp=c.querySelector('.note'); if(inp && d.note!==undefined && inp.value!==d.note) inp.value=d.note;
    });
    document.getElementById('prog').textContent =
      `reviewed ${acc+ovr}/${cards().length} · ${acc} accepted · ${ovr} overridden`;
  }
  function filt(btn,cls){
    document.querySelectorAll('.filt').forEach(b=>b.classList.toggle('active', b===btn));
    cards().forEach(c=> c.style.display=(cls==='all'||c.dataset.cls===cls)?'flex':'none');
  }
  function search(q){ q=q.toLowerCase();
    cards().forEach(c=> c.style.display=c.dataset.id.toLowerCase().includes(q)?'flex':'none'); }
  function setFocus(i){
    const vis=cards().filter(c=>c.style.display!=='none'); if(!vis.length) return;
    focusIdx=Math.max(0,Math.min(i,vis.length-1));
    cards().forEach(c=>c.classList.remove('focus'));
    const c=vis[focusIdx]; c.classList.add('focus'); c.scrollIntoView({block:'center',behavior:'smooth'});
  }
  document.addEventListener('keydown', e=>{
    if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName)) return;
    if(e.key==='j') setFocus(focusIdx+1);
    else if(e.key==='k') setFocus(focusIdx-1);
    else if(e.key==='a'){ const c=cards().filter(x=>x.style.display!=='none')[focusIdx]; if(c) c.querySelector('.accept').click(); }
    else if(e.key==='o'){ const c=cards().filter(x=>x.style.display!=='none')[focusIdx]; if(c) c.querySelector('.ovr').focus(); }
  });
  window.decide=decide; window.override=override; window.setNote=setNote;
  window.reReview=reReview; window.filt=filt; window.search=search;
  boot();
</script>
</body></html>"""
