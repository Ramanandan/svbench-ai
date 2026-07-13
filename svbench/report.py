"""Report agent -- turns reviewed loci into a scientific report + review dashboard.

Three artifacts:
  * headline.json  -- the machine-readable "impact" numbers: how many of the
                      caller's flagged false positives are actually benchmark
                      artifacts, and the resulting *adjusted* precision.
  * report.md      -- Truvari metrics table, verdict breakdown, the headline, and
                      per-locus explanations.
  * dashboard.html -- self-contained (base64 images) triage UI: each discordant
                      locus shows the samplot image beside Claude's verdict,
                      confidence-sorted, with accept / override-to-class controls,
                      a live progress counter, localStorage resume, and JSON+CSV
                      export. Human-in-the-loop, no server, no dependencies.

This is the layer a metrics-only benchmark cannot produce: a *reason* for every
discordance and a curated, exportable decision set the caller developer keeps.
"""
from __future__ import annotations

import base64
import html
import json
from collections import Counter
from pathlib import Path

from .schema import ReviewedLocus

_ARTIFACT = "benchmark_artifact"
# Truvari label -> the classification that means "the discordance was real"
_GENUINE = {"FP": "false_positive", "FN": "false_negative"}


def _metrics_row(summary: dict) -> dict:
    return {
        "precision": summary.get("precision"),
        "recall": summary.get("recall"),
        "f1": summary.get("f1"),
        "TP": summary.get("TP-comp", summary.get("TP-call")),
        "FP": summary.get("FP"),
        "FN": summary.get("FN"),
    }


def headline_stats(reviewed: list[ReviewedLocus], summary: dict | None = None) -> dict:
    """The impact numbers, computed honestly.

    Among the *reviewed* discordant loci, what fraction of each Truvari error
    class does Claude judge to be a benchmark artifact (a representation /
    repeat-region difference) rather than a genuine caller error?  From the FP
    artifact-rate we derive an *adjusted precision*: precision recomputed after
    removing the FPs that are not really errors.

    We separate what is OBSERVED on the reviewed sample from what is PROJECTED to
    the full callset, and label the projection as an estimate -- so the headline
    never overclaims beyond what was actually inspected.
    """
    summary = summary or {}
    by_label: dict[str, dict] = {}
    for label in ("FP", "FN"):
        loci = [r for r in reviewed if r.packet.truvari_label == label]
        if not loci:
            continue
        artifact = sum(1 for r in loci if r.verdict.classification == _ARTIFACT)
        genuine = sum(1 for r in loci if r.verdict.classification == _GENUINE[label])
        uncertain = len(loci) - artifact - genuine
        by_label[label] = {
            "reviewed": len(loci),
            "artifact": artifact,
            "genuine": genuine,
            "uncertain": uncertain,
            "artifact_rate": round(artifact / len(loci), 3),
        }

    out: dict = {"by_label": by_label, "reviewed_total": len(reviewed)}

    fp = by_label.get("FP")
    tp = summary.get("TP-comp", summary.get("TP-call"))
    total_fp = summary.get("FP")
    if fp and fp["reviewed"]:
        out["fp_artifact_rate"] = fp["artifact_rate"]
        out["reported_precision"] = summary.get("precision")
        # Observed adjusted precision: drop the artifacts we actually inspected.
        if isinstance(tp, (int, float)) and isinstance(total_fp, (int, float)):
            adj_fp_observed = total_fp - fp["artifact"]
            if tp + adj_fp_observed > 0:
                out["adjusted_precision_observed"] = round(tp / (tp + adj_fp_observed), 3)
            # Projected: assume the sampled artifact-rate holds across all FPs.
            projected_genuine_fp = total_fp * (1 - fp["artifact_rate"])
            if tp + projected_genuine_fp > 0:
                out["adjusted_precision_projected"] = round(tp / (tp + projected_genuine_fp), 3)
            out["fp_sampled"] = fp["reviewed"]
            out["fp_total"] = int(total_fp)
            out["fully_reviewed"] = fp["reviewed"] >= total_fp
    return out


def _headline_sentence(h: dict) -> str:
    fp = h.get("by_label", {}).get("FP")
    if not fp:
        return ("Claude attached an evidence-grounded reason to every reviewed "
                "discordance — the judgment a metrics-only benchmark cannot make.")
    scope = "" if h.get("fully_reviewed") else "reviewed "
    s = (f"**{fp['artifact']} of {fp['reviewed']} {scope}false positives "
         f"({100*fp['artifact_rate']:.0f}%) are benchmark artifacts** — "
         f"representation / repeat-region differences, not genuine caller errors.")
    if "adjusted_precision_observed" in h and h.get("reported_precision") is not None:
        s += (f" Removing them raises precision from "
              f"**{h['reported_precision']:.3f} → {h['adjusted_precision_observed']:.3f}**")
        if not h.get("fully_reviewed") and "adjusted_precision_projected" in h:
            s += (f" (≈{h['adjusted_precision_projected']:.3f} if the sampled rate "
                  f"holds across all {h['fp_total']} FPs)")
        s += "."
    return s


def write_report_md(reviewed: list[ReviewedLocus], summary: dict, caller: str, out: Path) -> Path:
    m = _metrics_row(summary)
    classes = Counter(r.verdict.classification for r in reviewed)
    n = len(reviewed) or 1
    h = headline_stats(reviewed, summary)

    lines = [
        f"# SVBench AI review — {caller}",
        "",
        "## Truvari benchmark (commodity metrics)",
        "",
        "| precision | recall | F1 | TP | FP | FN |",
        "|---|---|---|---|---|---|",
        f"| {m['precision']} | {m['recall']} | {m['f1']} | {m['TP']} | {m['FP']} | {m['FN']} |",
        "",
        "## The added layer — Claude's review of the discordances",
        "",
        f"> {_headline_sentence(h)}",
        "",
        f"- Discordant loci reviewed: **{len(reviewed)}**",
    ]
    for cls, cnt in classes.most_common():
        lines.append(f"- {cls}: {cnt} ({100*cnt/n:.0f}%)")

    if h.get("by_label"):
        lines += ["", "### Error-class breakdown", "",
                  "| Truvari class | reviewed | benchmark artifact | genuine error | uncertain |",
                  "|---|---|---|---|---|"]
        for label, d in h["by_label"].items():
            lines.append(f"| {label} | {d['reviewed']} | {d['artifact']} "
                         f"| {d['genuine']} | {d['uncertain']} |")

    lines += ["", "## Per-locus explanations", ""]
    for r in sorted(reviewed, key=lambda x: x.verdict.confidence, reverse=True):
        p, v = r.packet, r.verdict
        lines += [
            f"### {p.locus_id}",
            f"- Truvari: **{p.truvari_label}** → Claude: **{v.classification}** "
            f"(confidence {v.confidence:.2f})",
            f"- Region: segdup={p.in_segdup}, low_mappability={p.in_low_mappability}, "
            f"tandem_repeat={p.in_tandem_repeat}; nearest truth {p.nearest_truth_dist} bp",
            f"- Reason: {v.primary_reason}",
            f"- Evidence: {', '.join(v.evidence_used) or 'n/a'}",
            f"- {v.explanation}",
            "",
        ]
    path = Path(out) / "report.md"
    path.write_text("\n".join(lines))

    (Path(out) / "headline.json").write_text(json.dumps(h, indent=2))
    return path


_STRATS = ["tandem_repeat", "segdup", "low_mappability", "homopolymer"]
_STRAT_FLAG = {"tandem_repeat": "in_tandem_repeat", "segdup": "in_segdup",
               "low_mappability": "in_low_mappability", "homopolymer": "in_homopolymer"}


def _run_count(cmd) -> int:
    import subprocess
    try:
        r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    except FileNotFoundError:
        return -1
    if r.returncode != 0:
        return -1
    return sum(1 for ln in r.stdout.splitlines() if ln and not ln.startswith("#"))


def region_breakdown(bench_dir, reviewed=None, data_dir=None) -> dict | None:
    """Where a caller's errors concentrate. For each GIAB stratification, count
    TP/FP calls falling inside it (bedtools) -> reported precision + FP share.
    With reviewed loci, add the artifact rate among reviewed FPs in that region
    and the resulting artifact-adjusted precision. Returns None if the bench
    output VCFs or bedtools/bcftools aren't available."""
    from pathlib import Path as _P
    from . import config
    bench_dir = _P(bench_dir)
    data_dir = _P(data_dir or config.DATA_DIR)
    tp_vcf, fp_vcf = bench_dir / "tp-comp.vcf.gz", bench_dir / "fp.vcf.gz"
    if not (tp_vcf.exists() and fp_vcf.exists()):
        return None
    tp_tot = _run_count(["bcftools", "view", "-H", tp_vcf])
    fp_tot = _run_count(["bcftools", "view", "-H", fp_vcf])
    if tp_tot < 0 or fp_tot < 0:
        return None
    rows = []
    for key in _STRATS:
        bed = data_dir / f"strat_{key}.bed.gz"
        if not bed.exists():
            continue
        tp = _run_count(["bedtools", "intersect", "-u", "-a", tp_vcf, "-b", bed])
        fp = _run_count(["bedtools", "intersect", "-u", "-a", fp_vcf, "-b", bed])
        if tp < 0 or fp < 0 or tp + fp == 0:
            continue
        row = {"region": key, "tp": tp, "fp": fp,
               "precision": round(tp / (tp + fp), 3),
               "fp_share": round(fp / fp_tot, 3) if fp_tot else 0.0}
        if reviewed:
            flag = _STRAT_FLAG[key]
            revs = [r for r in reviewed
                    if r.packet.truvari_label == "FP" and getattr(r.packet, flag)]
            if revs:
                arts = sum(1 for r in revs if r.verdict.classification == _ARTIFACT)
                rate = arts / len(revs)
                row["reviewed"] = len(revs)
                row["artifact_rate"] = round(rate, 3)
                row["adjusted_precision"] = round(tp / (tp + fp * (1 - rate)), 3)
        rows.append(row)
    return {
        "tp_total": tp_tot, "fp_total": fp_tot,
        "precision": round(tp_tot / (tp_tot + fp_tot), 3) if tp_tot + fp_tot else None,
        "regions": rows,
    }


def _img_data_uri(image_path: str | None) -> str:
    if not image_path or not Path(image_path).exists():
        return ""
    b64 = base64.standard_b64encode(Path(image_path).read_bytes()).decode()
    return f"data:image/png;base64,{b64}"


def _chip(text: str, kind: str = "") -> str:
    return f'<span class="chip {kind}">{html.escape(text)}</span>'


def _card_html(r: ReviewedLocus, img_src: str | None = None, rereview: bool = False) -> str:
    """Render one review card.

    * img_src=None  -> embed the samplot as a base64 data URI (static dashboard).
    * img_src="..." -> use that URL (the server serves images from disk); "" = no image.
    * rereview=True -> add a live "Re-review" button (server only).
    """
    p, v = r.packet, r.verdict
    region_chips = "".join(
        _chip(k, "warn") for k, val in {
            "segdup": p.in_segdup, "low_mappability": p.in_low_mappability,
            "tandem_repeat": p.in_tandem_repeat, "homopolymer": p.in_homopolymer,
        }.items() if val
    ) or _chip("no repeat flags", "ok")
    evidence_chips = "".join(_chip(e, "ev") for e in v.evidence_used) or _chip("n/a")
    if p.pop_catalog_hits:
        pop_txt = "known SV: " + ", ".join(p.pop_catalog_hits)
        if p.pop_max_af is not None:
            pop_txt += f" · AF {p.pop_max_af:.2f}"
        pop_chip = _chip(pop_txt, "pop")
    else:
        pop_chip = ""
    is_trio = bool(p.image_path and "trio" in Path(p.image_path).name)
    trio_badge = _chip("trio / Mendelian", "trio") if is_trio else ""
    if img_src is None:
        src = _img_data_uri(p.image_path)
    else:
        src = img_src
    img = (f'<img loading="lazy" src="{src}"/>' if src
           else '<div class="noimg">no image</div>')
    rerev_btn = ('<button class="rerev" onclick="reReview(this)">↻ Re-review</button>'
                 if rereview else "")
    cls = v.classification
    return f"""
    <div class="card" data-cls="{cls}" data-label="{p.truvari_label}"
         data-id="{html.escape(p.locus_id)}" data-conf="{v.confidence:.3f}"
         data-svtype="{html.escape(p.svtype)}">
      <div class="img">{img}</div>
      <div class="meta">
        <div class="ids"><code>{html.escape(p.locus_id)}</code> {trio_badge}</div>
        <div class="verdict">
          <span class="pill truvari">Truvari: {p.truvari_label}</span>
          <span class="pill cls {cls}">Claude: {cls}</span>
          <span class="pill conf">conf {v.confidence:.2f}</span>
        </div>
        <div class="chips">{region_chips} · nearest truth {p.nearest_truth_dist} bp · qual {p.caller_qual} {pop_chip}</div>
        <div class="reason"><b>{html.escape(v.primary_reason)}</b></div>
        <div class="expl">{html.escape(v.explanation)}</div>
        <div class="chips">evidence: {evidence_chips}</div>
        <div class="actions">
          <button class="accept" onclick="decide(this,'accept')">✓ Accept Claude</button>
          <select class="ovr" onchange="override(this)">
            <option value="">✗ Override to…</option>
            <option>true_positive</option>
            <option>false_positive</option>
            <option>false_negative</option>
            <option>benchmark_artifact</option>
            <option>uncertain</option>
          </select>
          <input class="note" placeholder="note (optional)" oninput="setNote(this)"/>
          {rerev_btn}
          <span class="decision"></span>
        </div>
      </div>
    </div>"""


def banner_html(reviewed: list[ReviewedLocus], summary: dict | None = None) -> str:
    """The headline banner shared by the static dashboard and the live server."""
    h = headline_stats(reviewed, summary or {})
    fp = h.get("by_label", {}).get("FP")
    if not fp:
        return ("Every discordance carries an evidence-grounded reason — accept or "
                "override to build a curated set.")
    banner = (f"<b>{fp['artifact']} of {fp['reviewed']}</b> reviewed false positives "
              f"(<b>{100*fp['artifact_rate']:.0f}%</b>) are benchmark artifacts, not genuine "
              f"caller errors.")
    if "adjusted_precision_observed" in h and h.get("reported_precision") is not None:
        banner += (f" Precision <b>{h['reported_precision']:.3f} → "
                   f"{h['adjusted_precision_observed']:.3f}</b> after removing them.")
    return banner


# Template kept separate so CSS/JS literal braces need no f-string escaping.
_DASH_TEMPLATE = """<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SVBench AI — __CALLER__</title>
<style>
  :root{color-scheme:dark}
  body{font:14px/1.5 -apple-system,system-ui,sans-serif;margin:0;background:#0f1115;color:#e6e6e6}
  header{padding:14px 24px;background:#161a22;position:sticky;top:0;z-index:5;border-bottom:1px solid #262b36}
  header h1{margin:0;font-size:18px}
  .sub{color:#9aa4b2;font-size:13px;margin-top:2px}
  .banner{margin-top:10px;padding:10px 12px;background:#10241b;border:1px solid #1c4b36;border-radius:8px;color:#bdead0}
  .banner b{color:#7fe0a8}
  .bar{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin-top:10px}
  .bar button,.bar input{background:#222a36;color:#e6e6e6;border:1px solid #333;border-radius:6px;padding:6px 10px;cursor:pointer}
  .bar input{cursor:text}
  .bar button.active{background:#2d3a4d;border-color:#456}
  .spacer{flex:1}
  .progress{color:#9aa4b2;font-size:13px}
  .card{display:flex;gap:16px;padding:16px 24px;border-bottom:1px solid #1e232c;scroll-margin-top:150px}
  .card.focus{background:#141a24;outline:2px solid #2d3a4d}
  .card.done{opacity:.55}
  .img img{max-width:520px;width:100%;border-radius:6px;background:#fff}
  .noimg{width:520px;height:180px;display:grid;place-items:center;color:#666;border:1px dashed #333;border-radius:6px}
  .meta{flex:1;min-width:280px}
  .pill{display:inline-block;padding:2px 8px;border-radius:12px;font-size:12px;margin-right:6px}
  .truvari{background:#3a2a10;color:#f0c674} .conf{background:#22303a;color:#8fd4e8}
  .cls.benchmark_artifact{background:#123a2a;color:#7fe0a8}
  .cls.false_positive,.cls.false_negative{background:#3a1220;color:#f08fa8}
  .cls.true_positive{background:#123a2a;color:#7fe0a8} .cls.uncertain{background:#2a2a2a;color:#bbb}
  .chip{display:inline-block;padding:1px 7px;border-radius:10px;font-size:11px;margin:2px 4px 2px 0;background:#222a36;color:#9aa4b2}
  .chip.warn{background:#332012;color:#f0b06c} .chip.ok{background:#16281f;color:#7fbf9a}
  .chip.ev{background:#1b2436;color:#8fb6e8} .chip.trio{background:#2a1836;color:#c79ae8}
  .chip.pop{background:#122a2a;color:#6fd0c8;font-weight:600}
  .chips{margin:5px 0;font-size:12px;color:#9aa4b2}
  .reason{margin:6px 0} .expl{color:#cdd6e0}
  .actions{margin-top:10px;display:flex;flex-wrap:wrap;gap:8px;align-items:center}
  .actions button,.actions select,.actions .note{background:#222a36;color:#e6e6e6;border:1px solid #333;border-radius:6px;padding:6px 10px}
  .actions button{cursor:pointer}
  .note{min-width:180px}
  .decision{font-weight:600}
  .decision.accepted{color:#7fe0a8} .decision.overridden{color:#f0b06c}
  code{color:#9aa4b2}
  kbd{background:#222a36;border:1px solid #333;border-radius:4px;padding:0 5px;font-size:11px}
</style></head><body>
<header>
  <h1>SVBench AI — __CALLER__</h1>
  <div class="sub">__NREVIEWED__ discordant loci · Claude-reviewed · sorted by confidence · triage with <kbd>j</kbd>/<kbd>k</kbd> to move, <kbd>a</kbd> accept, <kbd>o</kbd> override</div>
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
    <button onclick="exportJSON()">⤓ JSON</button>
    <button onclick="exportCSV()">⤓ CSV</button>
    <button onclick="resetAll()">reset</button>
  </div>
</header>
__CARDS__
<script>
  const CALLER = "__CALLER__";
  const KEY = "svbench_decisions:" + CALLER;
  const decisions = JSON.parse(localStorage.getItem(KEY) || "{}");
  const cards = () => [...document.querySelectorAll('.card')];
  let focusIdx = 0;

  function persist(){ localStorage.setItem(KEY, JSON.stringify(decisions)); render(); }
  function cardData(c){ return {
    locus_id:c.dataset.id, truvari:c.dataset.label, claude:c.dataset.cls,
    confidence:+c.dataset.conf, svtype:c.dataset.svtype }; }

  function decide(btn,kind){
    const c = btn.closest('.card'); const d = cardData(c);
    decisions[d.locus_id] = {...d, decision:'accept', final:d.claude,
      note:(decisions[d.locus_id]||{}).note||''};
    persist();
  }
  function override(sel){
    const c = sel.closest('.card'); const d = cardData(c); const val = sel.value;
    if(!val){ return; }
    decisions[d.locus_id] = {...d, decision:'override', final:val,
      note:(decisions[d.locus_id]||{}).note||''};
    persist();
  }
  function setNote(inp){
    const c = inp.closest('.card'); const id = c.dataset.id;
    if(decisions[id]){ decisions[id].note = inp.value; persist(); }
  }

  function render(){
    let acc=0, ovr=0;
    cards().forEach(c=>{
      const d = decisions[c.dataset.id]; const span = c.querySelector('.decision');
      c.classList.toggle('done', !!d);
      if(!d){ span.textContent=''; span.className='decision'; return; }
      if(d.decision==='accept'){ acc++; span.textContent='accepted ✓'; span.className='decision accepted'; }
      else { ovr++; span.textContent='→ '+d.final+' ✗'; span.className='decision overridden'; }
      const inp = c.querySelector('.note'); if(inp && d.note!==undefined && inp.value!==d.note) inp.value=d.note;
    });
    const total = cards().length;
    document.getElementById('prog').textContent =
      `reviewed ${acc+ovr}/${total} · ${acc} accepted · ${ovr} overridden`;
  }

  function filt(btn,cls){
    document.querySelectorAll('.filt').forEach(b=>b.classList.toggle('active', b===btn));
    cards().forEach(c=> c.style.display = (cls==='all'||c.dataset.cls===cls)?'flex':'none');
  }
  function search(q){
    q = q.toLowerCase();
    cards().forEach(c=> c.style.display = c.dataset.id.toLowerCase().includes(q)?'flex':'none');
  }
  function resetAll(){
    if(!confirm('Clear all decisions for '+CALLER+'?')) return;
    for(const k in decisions) delete decisions[k]; persist();
  }

  function setFocus(i){
    const vis = cards().filter(c=>c.style.display!=='none');
    if(!vis.length) return;
    focusIdx = Math.max(0, Math.min(i, vis.length-1));
    cards().forEach(c=>c.classList.remove('focus'));
    const c = vis[focusIdx]; c.classList.add('focus');
    c.scrollIntoView({block:'center', behavior:'smooth'});
  }
  document.addEventListener('keydown', e=>{
    if(['INPUT','SELECT','TEXTAREA'].includes(e.target.tagName)) return;
    if(e.key==='j'){ setFocus(focusIdx+1); }
    else if(e.key==='k'){ setFocus(focusIdx-1); }
    else if(e.key==='a'){ const c=cards().filter(x=>x.style.display!=='none')[focusIdx]; if(c) c.querySelector('.accept').click(); }
    else if(e.key==='o'){ const c=cards().filter(x=>x.style.display!=='none')[focusIdx]; if(c) c.querySelector('.ovr').focus(); }
  });

  function download(name,text,type){
    const a=document.createElement('a');
    a.href=URL.createObjectURL(new Blob([text],{type})); a.download=name; a.click();
  }
  function exportJSON(){ download('svbench_decisions_'+CALLER+'.json',
    JSON.stringify(Object.values(decisions),null,2),'application/json'); }
  function exportCSV(){
    const rows=[['locus_id','truvari','claude','final','decision','confidence','svtype','note']];
    Object.values(decisions).forEach(d=>rows.push(
      [d.locus_id,d.truvari,d.claude,d.final,d.decision,d.confidence,d.svtype,
       '"'+(d.note||'').replace(/"/g,'""')+'"']));
    download('svbench_decisions_'+CALLER+'.csv', rows.map(r=>r.join(',')).join('\\n'),'text/csv');
  }
  render();
</script>
</body></html>"""


def write_dashboard_html(reviewed: list[ReviewedLocus], caller: str, out: Path,
                         summary: dict | None = None) -> Path:
    ordered = sorted(reviewed, key=lambda x: x.verdict.confidence, reverse=True)
    cards = "".join(_card_html(r) for r in ordered)
    banner = banner_html(reviewed, summary)

    doc = (_DASH_TEMPLATE
           .replace("__CARDS__", cards)
           .replace("__BANNER__", banner)
           .replace("__NREVIEWED__", str(len(reviewed)))
           .replace("__CALLER__", html.escape(caller)))
    path = Path(out) / "dashboard.html"
    path.write_text(doc)
    return path
