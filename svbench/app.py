"""SVBench AI — Streamlit run console.

`streamlit run svbench/app.py`  (or `svbench app`)

The "front door" for a scientist: upload an HG002 GRCh38 caller VCF (or hit
"Run demo"), watch the pipeline run — Truvari → annotate → samplot → Claude
Opus review — with live progress, then hand off to the full review dashboard
(`svbench serve`) for deep accept/override triage.

Design notes
  * Run console + handoff: this app *runs* and *first-looks*; the dashboard does
    deep triage (it is better at per-locus state than Streamlit's re-run model).
  * Bundled demo is the reliable default (data pre-cached, small slice). A live
    run is attempted when the full stack + ANTHROPIC_API_KEY are present, and
    degrades gracefully to cached results if any stage can't run here.
  * localhost only; nothing is uploaded off the machine. GRCh38 HG002 callsets
    only (that is the truth set / reads the benchmark is built from).
"""
from __future__ import annotations

import base64
import gzip
import html
import io
import os
import subprocess
import sys
import time
from pathlib import Path

import streamlit as st

from svbench import config, popfreq, report
from svbench.server import _load_reviewed, _load_summary


def _natural_chroms(chroms) -> list[str]:
    def key(c):
        b = c[3:] if c.startswith("chr") else c
        return (0, int(b)) if b.isdigit() else (1, b)
    return sorted(set(chroms), key=key)


def _scan_vcf(raw: bytes, name: str, max_lines: int = 200_000) -> dict:
    """Peek a VCF's chromosomes and SV content without a full parse.

    Returns {chroms, has_svtype, n_records, chr_prefixed} for populating the
    chromosome selector and validating an upload up front.
    """
    # gzip errors surface lazily at read time, so decompress up front and fall
    # back to treating the bytes as plain text if it isn't really gzipped.
    if name.endswith(".gz"):
        try:
            text = gzip.decompress(raw).decode("utf-8", "replace")
        except (OSError, EOFError):
            text = raw.decode("utf-8", "replace")
    else:
        text = raw.decode("utf-8", "replace")
    chroms, seen, has_sv, n = [], set(), False, 0
    for i, line in enumerate(text.splitlines()):
        if i > max_lines:
            break
        if not line or line[0] == "#":
            continue
        f = line.split("\t", 8)
        if len(f) < 8:
            continue
        n += 1
        if f[0] not in seen:
            seen.add(f[0]); chroms.append(f[0])
        if not has_sv and ("SVTYPE=" in f[7] or "<" in f[4]):
            has_sv = True
    return {
        "chroms": _natural_chroms(chroms),
        "has_svtype": has_sv,
        "n_records": n,
        "chr_prefixed": bool(chroms) and all(c.startswith("chr") for c in chroms),
    }


def _validate_vcf(scan: dict) -> list[tuple[str, str]]:
    """(level, message) list — surfaced before a scientist starts a run."""
    msgs = []
    if scan["n_records"] == 0:
        return [("error", "No variant records found — is this a VCF with calls?")]
    if not scan["has_svtype"]:
        msgs.append(("warning", "No SVTYPE / symbolic alleles detected — this may not be a "
                                "structural-variant callset."))
    if not scan["chr_prefixed"]:
        msgs.append(("warning", "Chromosomes are not 'chr'-prefixed — this looks like GRCh37/hg19. "
                                "SVBench AI expects a GRCh38 (chr-prefixed) HG002 callset."))
    return msgs


_DEMO_CALLERS = [
    ("sniffles_ont_chr21.vcf.gz", "sniffles_ont"),
    ("svim_chr21.vcf.gz", "svim"),
    ("sniffles_chr21.vcf.gz", "sniffles"),
]
# Human-facing labels for the demo picker. Keys stay the internal caller ids
# (used for bench dirs / filenames); only the displayed text changes. Verified
# from VCF headers + read stats: sniffles_ont=ONT, sniffles=HiFi, svim=HiFi.
_CALLER_LABELS = {
    "sniffles_ont": "Sniffles_ONT",
    "svim": "SVIM",
    "sniffles": "Sniffles_HiFi",
}


def _demos():
    """All bundled demo callers whose VCF is present, as (vcf, caller, bench_dir)."""
    out = config.OUTPUT_DIR
    return [(out / vcf, caller, out / f"bench_{caller}")
            for vcf, caller in _DEMO_CALLERS if (out / vcf).exists()]


@st.cache_data(show_spinner=False)
def _catalog_counts(keys: tuple) -> dict:
    """SV record count per available catalog (cached; keyed on the catalog set).
    Self-contained so it survives Streamlit hot-reloads that leave popfreq stale."""
    out = {}
    for k in keys:
        p = config.DATA_DIR / f"pop_{k}.bed.gz"
        try:
            with gzip.open(p, "rt") as fh:
                out[k] = sum(1 for _ in fh)
        except OSError:
            out[k] = 0
    return out


def _demo():
    """First available demo caller (back-compat)."""
    ds = _demos()
    return ds[0] if ds else (None, None, None)


# --- styled review card (mirrors the `svbench serve` dashboard look) --------
# (bg, fg) palette shared with report.py's dashboard so the two UIs match.
_CLS_PILL = {
    "benchmark_artifact": ("#16281f", "#7fbf9a"), "true_positive": ("#16281f", "#7fbf9a"),
    "false_positive": ("#3a1616", "#f0a0a0"), "false_negative": ("#3a2a12", "#f0c88a"),
    "uncertain": ("#26262c", "#b8b8c0"),
}
# Final recommendation: (icon, headline, accent, bg, fg) per classification.
_REC = {
    "benchmark_artifact": ("✓", "Benchmark artifact — a real variant Truvari mislabeled, "
                           "not a caller error.", "#2f9e5c", "#12351f", "#8fe6ac"),
    "true_positive": ("✓", "Real variant — correctly called by the caller.",
                      "#2f9e5c", "#12351f", "#8fe6ac"),
    "false_positive": ("✗", "Genuine false positive — the alignment evidence does not "
                       "support this call.", "#d05656", "#351414", "#f2a6a6"),
    "false_negative": ("!", "Real variant the caller missed (false negative).",
                       "#d0a24e", "#352712", "#f2ce8f"),
    "uncertain": ("?", "Uncertain — the evidence is insufficient to decide.",
                  "#8a8a94", "#26262c", "#c4c4cc"),
}


# Full-word Truvari labels for display (packet stores the short code).
_TRUVARI_LABELS = {
    "FP": "False Positive", "FN": "False Negative",
    "TP": "True Positive", "QC": "QC",
}

# One-glance plain-English verdict label (complements the technical class name).
_VERDICT_SHORT = {
    "benchmark_artifact": "Real variant — mislabeled by the benchmark",
    "true_positive": "Real variant — correctly called",
    "false_positive": "Not supported — genuine false positive",
    "false_negative": "Real variant — missed by the caller",
    "uncertain": "Inconclusive",
}


def _pill(label: str, value: str, bg: str, fg: str) -> str:
    return (f'<span style="display:inline-flex;align-items:center;gap:6px;padding:3px 11px;'
            f'border-radius:20px;font-size:12.5px;font-weight:600;background:{bg};color:{fg}">'
            f'<span style="opacity:.6;font-weight:500">{html.escape(label)}</span>'
            f'{html.escape(value)}</span>')


def _chip(text: str, bg: str, fg: str) -> str:
    return (f'<span style="display:inline-block;padding:1px 9px;border-radius:10px;font-size:11px;'
            f'margin:2px 5px 2px 0;background:{bg};color:{fg}">{html.escape(text)}</span>')


def _conf_meter(conf: float) -> str:
    pct = int(round(conf * 100))
    color = "#7fbf9a" if conf >= 0.8 else ("#f0c88a" if conf >= 0.6 else "#f0a0a0")
    return (f'<div style="display:flex;align-items:center;gap:8px;margin:2px 0 12px">'
            f'<div style="flex:0 0 150px;height:7px;border-radius:4px;background:#20252e;overflow:hidden">'
            f'<div style="height:100%;width:{pct}%;background:{color}"></div></div>'
            f'<span style="font-size:11px;color:#9aa4b2">confidence {conf:.2f}</span></div>')


def _card_html(r) -> str:
    p, v = r.packet, r.verdict
    cls = v.classification
    cbg, cfg = _CLS_PILL.get(cls, ("#26262c", "#b8b8c0"))
    is_trio = bool(p.image_path and "trio" in Path(p.image_path).name)

    pills = (
        _pill("Truvari", _TRUVARI_LABELS.get(p.truvari_label, p.truvari_label), "#332012", "#f0b06c")
        + _pill("Claude", cls, cbg, cfg)
        + _pill("Confidence", f"{v.confidence:.2f}", "#1b2436", "#8fb6e8")
        + (_pill("", "trio / Mendelian", "#2a1836", "#c79ae8") if is_trio else "")
    )
    region = [k for k, val in {
        "segdup": p.in_segdup, "low_mappability": p.in_low_mappability,
        "tandem_repeat": p.in_tandem_repeat, "homopolymer": p.in_homopolymer,
    }.items() if val]
    region_chips = "".join(_chip(k, "#332012", "#f0b06c") for k in region) \
        or _chip("no repeat flags", "#16281f", "#7fbf9a")
    pop_chip = ""
    if p.pop_catalog_hits:
        src = ", ".join(p.pop_catalog_hits)
        af_txt = f" · AF {p.pop_max_af:.2f}" if p.pop_max_af is not None else ""
        af_help = (f" at allele frequency {p.pop_max_af:.2f} "
                   f"(~{round(p.pop_max_af * 100)}% of people carry it)"
                   if p.pop_max_af is not None else "")
        tip = (f"A structurally matching SV is already catalogued in {src}{af_help}. "
               "Independent evidence that a real SV recurs at this locus — it supports "
               "reading this as a real variant, not a caller error. Absence would be neutral.")
        pop_chip = (
            f'<span title="{html.escape(tip)}" style="display:inline-block;padding:2px 10px;'
            f'border-radius:10px;font-size:11px;margin:2px 5px 2px 0;background:#122a2a;'
            f'color:#6fd0c8">🧬 Population evidence · {html.escape(src)}{html.escape(af_txt)} '
            f'<span style="opacity:.75">· corroborates a real variant</span></span>'
        )
    ev_chips = "".join(_chip(e, "#1b2436", "#8fb6e8") for e in v.evidence_used) or _chip("n/a", "#26262c", "#b8b8c0")

    icon, headline, accent, rbg, rfg = _REC.get(cls, _REC["uncertain"])
    rec = (
        f'<div style="display:flex;gap:12px;align-items:center;margin-top:14px;padding:12px 14px;'
        f'border-radius:10px;background:{rbg};border-left:4px solid {accent}">'
        f'<div style="flex:0 0 30px;height:30px;border-radius:50%;background:{accent};color:#0b0e12;'
        f'font-weight:800;font-size:17px;display:flex;align-items:center;justify-content:center">{icon}</div>'
        f'<div><div style="font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;opacity:.7;'
        f'color:{rfg}">Claude&#39;s final recommendation</div>'
        f'<div style="color:{rfg};font-weight:600;font-size:14px;line-height:1.35">{html.escape(headline)}</div>'
        f'</div></div>'
    )
    return (
        f'<div style="font-family:-apple-system,Segoe UI,Roboto,sans-serif;color:#c9d2de">'
        f'<div style="font-family:ui-monospace,SFMono-Regular,Menlo,monospace;font-size:12.5px;'
        f'color:#7fbf9a;margin-bottom:8px">{html.escape(p.locus_id)}</div>'
        f'<div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:2px">{pills}</div>'
        f'<div style="font-size:12.5px;font-weight:600;color:{cfg};margin:6px 0 2px">'
        f'{html.escape(_VERDICT_SHORT.get(cls, cls))}</div>'
        f'{_conf_meter(v.confidence)}'
        f'<div style="font-size:12px;color:#9aa4b2;margin-bottom:12px">'
        f'<span style="opacity:.7">Region</span> {region_chips}'
        f'<span style="opacity:.6"> · nearest truth {p.nearest_truth_dist} bp · qual {p.caller_qual}</span>'
        f' {pop_chip}</div>'
        f'<div style="font-size:10.5px;letter-spacing:.09em;text-transform:uppercase;color:#6f7986;'
        f'margin-bottom:3px">Claude&#39;s assessment</div>'
        f'<div style="font-weight:700;font-size:15px;color:#eef2f7;margin-bottom:6px">'
        f'{html.escape(v.primary_reason)}</div>'
        f'<div style="font-size:13.5px;line-height:1.5;color:#c2ccd8;margin-bottom:12px">'
        f'{html.escape(v.explanation)}</div>'
        f'<div style="font-size:12px;color:#9aa4b2"><span style="opacity:.7">Evidence</span> {ev_chips}</div>'
        f'{rec}</div>'
    )


def _render_card(r, container) -> None:
    p = r.packet
    with container:
        card = st.container(border=True)
        with card:
            # Samplot on top, centered, at a readable-but-contained width.
            if p.image_path and Path(p.image_path).exists():
                _b = base64.b64encode(Path(p.image_path).read_bytes()).decode()
                st.markdown(
                    f'<div style="text-align:center;margin:2px 0 8px">'
                    f'<img src="data:image/png;base64,{_b}" '
                    f'style="width:900px;max-width:100%;height:auto;border-radius:8px"/>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.info("no samplot image")
            st.markdown(_card_html(r), unsafe_allow_html=True)


def _apply_support(reviewed, pop_sources) -> None:
    """Recompute population-catalog support on cached loci from the current UI
    selection (pure tabix, no API), and report the coverage. This is what lets a
    cached demo reflect the databases the user picked in the sidebar."""
    n_fp = sum(1 for r in reviewed if r.packet.truvari_label == "FP")
    n_hit = popfreq.reannotate_population(reviewed, pop_sources)
    if not pop_sources:
        st.caption("Population evidence: no databases selected.")
    else:
        labels = ", ".join(config.POP_CATALOG_LABELS.get(k, k) for k in pop_sources)
        n_fp_hit = sum(1 for r in reviewed
                       if r.packet.truvari_label == "FP" and r.packet.pop_catalog_hits)
        st.caption(f"Population evidence from **{labels}**: "
                   f"{n_fp_hit}/{n_fp} false positives corroborated by a known population SV.")


def _show_headline(reviewed, summary) -> None:
    h = report.headline_stats(reviewed, summary or {})
    fp = h.get("by_label", {}).get("FP")
    if not fp:
        return
    rep = h.get("reported_precision")
    obs = h.get("adjusted_precision_observed")
    proj = h.get("adjusted_precision_projected")
    a, b, c = st.columns(3)
    a.metric("FPs that are artifacts", f"{fp['artifact']} / {fp['reviewed']}",
             f"{100*fp['artifact_rate']:.0f}%")
    if rep is not None:
        b.metric("Precision (reported)", f"{rep:.3f}")
    if obs is not None:
        c.metric("Precision (artifact-adjusted)", f"{obs:.3f}", f"+{obs-(rep or 0):.3f}")

    # The exciting, honest reveal: the caller's *true* precision once repeat-region
    # representation artifacts are removed, projected across all FPs.
    if proj is not None and rep is not None:
        if h.get("fully_reviewed"):
            st.success(f"### 📈 True precision: **{rep:.3f} → {obs:.3f}**\n"
                       f"All {fp['reviewed']} false positives reviewed — "
                       f"{fp['artifact']} were benchmark artifacts, not caller errors.")
        else:
            st.success(f"### 📈 Projected true precision: **{rep:.3f} → ~{proj:.3f}**\n"
                       f"If the **{100*fp['artifact_rate']:.0f}%** artifact rate from "
                       f"{fp['reviewed']} reviewed FPs holds across all "
                       f"**{h.get('fp_total')}** false positives. "
                       f"Raise *Max loci* to review more and firm up the estimate.")
    st.info("These false positives aren't caller errors — they're representation "
            "differences in repeat regions, the hardest and most disease-relevant "
            "part of the genome to both call and benchmark.")


def _show_region_breakdown(bench_dir, reviewed) -> None:
    """Where the caller's errors concentrate — reported vs artifact-adjusted
    precision within each hard-to-call region. Needs the bench output VCFs +
    bedtools/bcftools; silently skips if unavailable."""
    try:
        b = report.region_breakdown(bench_dir, reviewed=reviewed)
    except Exception:
        b = None
    if not b or not b.get("regions"):
        return
    with st.expander("🧬 Where the errors are — region breakdown", expanded=True):
        st.caption("For each hard-to-call region: reported precision, the share of ALL "
                   "false positives it holds, and the artifact-adjusted precision from Claude.")
        rows = [{
            "region": r["region"],
            "reported precision": f"{r['precision']:.3f}",
            "share of all FPs": f"{100*r['fp_share']:.0f}%",
            "reviewed FPs": r.get("reviewed", "—"),
            "artifact rate": (f"{100*r['artifact_rate']:.0f}%" if "artifact_rate" in r else "—"),
            "adjusted precision": (f"{r['adjusted_precision']:.3f}" if "adjusted_precision" in r else "—"),
        } for r in b["regions"]]
        st.dataframe(rows, hide_index=True, width="stretch")
        top = max(b["regions"], key=lambda r: r["fp_share"])
        if "adjusted_precision" in top:
            st.success(f"**{100*top['fp_share']:.0f}% of all false positives fall in "
                       f"`{top['region']}` regions** — where reported precision is "
                       f"**{top['precision']:.3f}** but the AI-adjusted precision is "
                       f"**{top['adjusted_precision']:.3f}**. The caller isn't wrong there; "
                       f"the benchmark just represents these variants differently.")


def _filtered(reviewed, svtypes, limit, chrom=None):
    """Apply the sidebar chromosome / SV-type / max-loci filters to a reviewed
    set, confidence-sorted. Keeps those controls responsive in cached mode."""
    ordered = sorted(reviewed, key=lambda x: x.verdict.confidence, reverse=True)
    if chrom:
        ordered = [r for r in ordered if r.packet.chrom == chrom]
    if svtypes:
        ordered = [r for r in ordered if r.packet.svtype in svtypes]
    if limit:
        ordered = ordered[:limit]
    return ordered


def _stream(reviewed, summary, svtypes=None, limit=None, chrom=None, animate: bool = True) -> None:
    # Headline reflects the full benchmark result; the queue respects the filters.
    _show_headline(reviewed, summary)
    shown = _filtered(reviewed, svtypes, limit, chrom)
    total = len(reviewed)
    if not shown:
        st.warning("No loci match the current filters (chromosome / SV type). "
                   "Adjust them in the sidebar.")
        return
    suffix = f" (of {total})" if len(shown) < total else ""
    st.subheader(f"{len(shown)}{suffix} reviewed discordances — confidence-sorted")
    bar = st.progress(0.0, text="streaming verdicts…")
    holder = st.container()
    for i, r in enumerate(shown, 1):
        _render_card(r, holder)
        bar.progress(i / len(shown), text=f"verdict {i}/{len(shown)}")
        if animate:
            time.sleep(0.12)
    bar.empty()


def _run_live(vcf: Path, caller: str, chrom, limit, svtypes, trio, status, refine=False,
              pop_sources=None):
    """Attempt a genuine run using the real pipeline. Raises on any missing
    dependency / data / key so the caller can fall back to cached results."""
    from svbench import annotate, benchmark, data, review, visualize
    out_dir = config.OUTPUT_DIR / f"bench_{caller}"
    # refine only actually runs if a reference FASTA is present; say so honestly.
    will_refine = refine and config.REFERENCE_FASTA.exists()
    label1 = "① Benchmarking with Truvari (bench%s)…" % (" + refine — this can take minutes"
                                                         if will_refine else "")
    if refine and not will_refine:
        label1 += "  [refine requested but no reference FASTA → skipping]"
    t0 = time.perf_counter()
    status.update(label=label1)
    benchmark.run_bench(Path(vcf), out_dir, chrom=chrom, refine=refine)
    summary = benchmark.read_summary(out_dir)
    t1 = time.perf_counter()

    status.update(label=f"② Annotating discordant loci…   (bench {t1-t0:.0f}s ✓)")
    packets = annotate.load_discordant_loci(out_dir, caller, svtypes=svtypes, limit=limit,
                                            pop_sources=pop_sources)
    if not packets:
        raise RuntimeError("no discordant loci found (check svtype filter / chromosome).")
    t2 = time.perf_counter()

    status.update(label=f"③ Rendering {len(packets)} alignments with samplot…   "
                        f"(annotate {t2-t1:.0f}s ✓)")
    child_bam = data.slice_bam_for_loci(packets)
    packets = visualize.render_all(packets, out_dir / "images", bam=child_bam)
    t3 = time.perf_counter()

    status.update(label=f"④ Reviewing {len(packets)} loci with Claude Opus 4.8…   "
                        f"(samplot {t3-t2:.0f}s ✓)")
    reviewed = []
    live = st.container()
    bar = st.progress(0.0)
    for i, p in enumerate(packets, 1):
        reviewed.append(review.review_locus(p, mode="benchmark", trio=trio))
        _render_card(reviewed[-1], live)
        bar.progress(i / len(packets), text=f"Claude verdict {i}/{len(packets)}")
    bar.empty()
    t4 = time.perf_counter()
    review.save_reviews(reviewed, out_dir / "reviews.json")
    report.write_report_md(reviewed, summary, caller, out_dir)
    report.write_dashboard_html(reviewed, caller, out_dir, summary)
    st.caption(f"⏱ bench {t1-t0:.0f}s · annotate {t2-t1:.0f}s · samplot {t3-t2:.0f}s · "
               f"review {t4-t3:.0f}s · **total {t4-t0:.0f}s**")
    _show_headline(reviewed, summary)
    return out_dir, reviewed, summary


def _handoff(bench_dir: Path, caller: str) -> None:
    st.divider()
    st.subheader("Deep triage → full review app")
    st.write("Hand off to the dashboard to accept/override every call, add notes, "
             "and export a curated decision set (it persists to disk).")
    st.code(f"svbench serve {bench_dir} --caller {caller}", language="bash")
    if st.button("▶ Launch review app (localhost:8000)"):
        try:
            subprocess.Popen([sys.executable, "-m", "svbench.cli", "serve",
                              str(bench_dir), "--caller", caller, "--no-browser"])
            st.success("Launched. Open http://localhost:8000")
        except Exception as e:  # pragma: no cover
            st.error(f"Could not launch: {e}")


def main() -> None:
    st.set_page_config(page_title="SVBench AI", page_icon="🧬", layout="wide")
    # Trim the default empty padding above the sidebar + main content.
    st.markdown(
        "<style>"
        "section[data-testid='stSidebar'] [data-testid='stSidebarUserContent']"
        "{padding-top:1.2rem !important}"
        "[data-testid='stMainBlockContainer']{padding-top:2rem !important}"
        "</style>",
        unsafe_allow_html=True,
    )
    _logo = Path(__file__).resolve().parent.parent / "SVBenchAI_Logo.png"
    if _logo.exists():
        _b64 = base64.b64encode(_logo.read_bytes()).decode()
        st.markdown(
            f'<div style="text-align:center;margin:6px 0 26px">'
            f'<img src="data:image/png;base64,{_b64}" '
            f'style="width:480px;max-width:82%;height:auto;border-radius:14px"/>'
            f'<div style="max-width:920px;margin:22px auto 0;font-size:23px;'
            f'line-height:1.45;font-weight:500;letter-spacing:.2px;color:#d7deea">'
            f'<b style="color:#ffffff;font-weight:700">Every SV call gets a verdict.</b> '
            f'The <b style="color:#ffffff;font-weight:700">Claude verdict layer</b> helping '
            f'Structural Variant scientists separate <span style="color:#7fbf9a;'
            f'font-weight:700">real variants</span> from <span style="color:#f0a0a0;'
            f'font-weight:700">artifacts</span> — with or without a truth set.</div></div>',
            unsafe_allow_html=True,
        )
    else:
        st.title("SVBench AI")

    demos = _demos()
    up = st.file_uploader("Upload a caller VCF (.vcf / .vcf.gz)", type=["vcf", "gz"])

    # Pick which bundled caller the demo runs (Sniffles, SVIM, …).
    if len(demos) > 1:
        names = [d[1] for d in demos]
        pick = st.radio("Demo caller", names, horizontal=True,
                        format_func=lambda k: _CALLER_LABELS.get(k, k),
                        help="Bundled example callsets. Different callers → different "
                             "precision and different discordances for Claude to review.")
        vcf_demo, caller_demo, bench_demo = demos[names.index(pick)]
    elif demos:
        vcf_demo, caller_demo, bench_demo = demos[0]
    else:
        vcf_demo = caller_demo = bench_demo = None

    # Peek the loaded VCF: validate the upload and derive the chromosome options.
    if up is not None:
        scan = _scan_vcf(up.getvalue(), up.name)
        for lvl, m in _validate_vcf(scan):
            (st.error if lvl == "error" else st.warning)(m)
        if scan["n_records"]:
            st.caption(f"Loaded **{up.name}** · {scan['n_records']:,} records · "
                       f"{len(scan['chroms'])} chromosomes")
        avail_chroms = scan["chroms"] or ["chr21"]
    elif vcf_demo is not None:
        avail_chroms = _scan_vcf(vcf_demo.read_bytes(), vcf_demo.name)["chroms"] or ["chr21"]
    else:
        avail_chroms = ["chr21"]

    with st.sidebar:
        st.header("Run settings")
        mode = st.radio("Execution", ["Replay cached (fast, no API)", "Live run"],
                        help="Live run needs Truvari, samplot, fetched GIAB data and "
                             "ANTHROPIC_API_KEY. It falls back to cached results if a stage can't run.")
        chrom_opts = ["All (whole benchmark)"] + avail_chroms
        chrom_choice = st.selectbox(
            "Chromosome", chrom_opts,
            index=chrom_opts.index("chr21") if "chr21" in chrom_opts else 0,
            help="Chromosomes found in the loaded VCF. Scopes a live run to that "
                 "chromosome, and filters the cached/review queue.")
        chrom = None if chrom_choice.startswith("All") else chrom_choice
        limit = st.slider("Max loci", 1, 100, 5,
                          help="Caps the review queue. Applies in both modes. Raise it to review "
                               "more (or all) false positives — the artifact-adjusted precision "
                               "becomes fully verified (no projection) once every FP is reviewed.")
        svtypes = st.multiselect("SV types", config.SV_TYPES, default=[],
                                 help="Filter the queue by SV type. Applies in both modes.")
        trio = st.checkbox("Trio / Mendelian evidence (HG003/HG004)", value=False,
                           help="Render parents so Claude can use inheritance as evidence. Live run only.")
        refine = st.checkbox("Truvari refine (slower, more accurate)", value=False,
                             help="Off = fast `truvari bench` (seconds). On = per-region MAFFT "
                                  "realignment — more accurate in repeats but can take many minutes. Live run only.")
        if refine and not config.REFERENCE_FASTA.exists():
            st.caption("↳ no reference FASTA found — refine will be **skipped**. "
                       "Run `svbench fetch --reference` to enable it.")

        # ---- Population evidence: known-SV corroboration --------------------
        st.divider()
        st.subheader("🧬 Population evidence")
        st.caption("Independent, orthogonal check: is a matching SV already known in "
                   "the population? A structurally matching call in a reference catalog "
                   "corroborates that a Truvari **FP** is a real variant (benchmark "
                   "artifact), raising Claude's confidence. Absence is neutral — never "
                   "counts against a call.")
        pop_avail = popfreq.available_catalogs()
        if pop_avail:
            counts = _catalog_counts(tuple(pop_avail))
            pop_sources = st.multiselect(
                "Reference databases", pop_avail, default=pop_avail,
                format_func=lambda k: f"{config.POP_CATALOG_LABELS.get(k, k)} · "
                                      f"{counts.get(k, 0):,} SVs",
                help="Only the selected databases contribute population evidence. "
                     "Applies in both cached and live modes (recomputed live — no API cost).")
        else:
            pop_sources = []
            st.caption("No reference databases loaded yet. Get the real ones with "
                       "`svbench fetch-catalogs --chrom chr21`, or build the GIAB "
                       "known-SV reference below.")
            if st.button("Build GIAB known-SV reference (chr21)"):
                from svbench import data
                with st.spinner("Building GIAB known-SV reference…"):
                    data.make_demo_catalog("chr21")
                st.rerun()
            st.caption("↳ *derived from the GIAB HG002 truth set — a curated known-SV "
                       "reference for the demo.*")
        st.divider()
        key_ok = bool(os.environ.get("ANTHROPIC_API_KEY"))
        st.caption("🔑 ANTHROPIC_API_KEY set" if key_ok else
                   "⚠️ no ANTHROPIC_API_KEY — live upload runs are blocked; the demo falls back to cached")

        from svbench import doctor
        c = doctor.check()
        ready = doctor._ok_required(c)
        with st.expander(("✅ Live-run ready" if ready else "❌ Live-run prerequisites"),
                         expanded=not ready):
            def _row(items):
                for n, ok in items.items():
                    st.write(("✅ " if ok else "❌ ") + n)
            st.caption("Required tools"); _row(c["tools_required"])
            st.caption("Required data (`svbench fetch`)"); _row(c["data_required"])
            st.caption("Environment"); _row(c["env"])
            if not ready:
                st.caption("Run `svbench doctor` in a terminal for full details + fixes. "
                           "The **cached demo** needs none of this.")

    col_run, col_demo = st.columns([1, 1])
    run_custom = col_run.button("▶ Run on uploaded VCF", disabled=up is None, width="stretch")
    run_demo = col_demo.button(f"▶ Run demo ({caller_demo or 'n/a'})",
                               disabled=vcf_demo is None, width="stretch")

    live = mode == "Live run"

    has_cache = vcf_demo is not None and (bench_demo / "reviews.json").exists()

    # ---- Run demo -----------------------------------------------------------
    if run_demo and vcf_demo is not None:
        bench_dir = reviewed = summary = None
        if live:
            with st.status("Running the pipeline…", expanded=True) as status:
                try:
                    bench_dir, reviewed, summary = _run_live(
                        vcf_demo, caller_demo, chrom, limit, svtypes or None, trio, status,
                        refine, pop_sources=pop_sources)
                    status.update(label="Done ✓", state="complete")
                except Exception as e:
                    if has_cache:
                        status.update(label="Live run unavailable — showing cached results", state="error")
                        st.warning(f"Live run couldn't complete here ({e}). Showing pre-computed results.")
                        reviewed = _load_reviewed(bench_demo); summary = _load_summary(bench_demo)
                        bench_dir = bench_demo
                        _apply_support(reviewed, pop_sources)
                        _stream(reviewed, summary, svtypes, limit, chrom)
                    else:
                        status.update(label="Run failed", state="error")
                        st.error(f"Live run failed ({e}).")
        elif has_cache:
            with st.status("Loading cached demo results…", expanded=False):
                reviewed = _load_reviewed(bench_demo); summary = _load_summary(bench_demo)
                bench_dir = bench_demo
            _apply_support(reviewed, pop_sources)
            _stream(reviewed, summary, svtypes, limit, chrom)
        else:
            st.warning(f"**{caller_demo}** has a benchmark but no cached AI review yet. "
                       f"Truvari metrics are ready — run the review once (needs `ANTHROPIC_API_KEY`):\n\n"
                       f"```\nsvbench review outputs/bench_{caller_demo} --caller {caller_demo}\n"
                       f"svbench report outputs/bench_{caller_demo} --caller {caller_demo}\n```\n\n"
                       f"…or switch Execution to **Live run**.")
        if bench_dir is not None and reviewed is not None:
            _show_region_breakdown(bench_dir, reviewed)
            _handoff(bench_dir, caller_demo)

    # ---- Run custom upload --------------------------------------------------
    elif run_custom and up is not None:
        caller = Path(up.name).stem.replace(".vcf", "") or "uploaded"
        dest = config.OUTPUT_DIR / up.name
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(up.getbuffer())
        if not live:
            st.warning("Custom VCFs need **Live run** mode (there are no cached results for them). "
                       "Switch Execution to 'Live run' in the sidebar.")
        elif not os.environ.get("ANTHROPIC_API_KEY"):
            st.error("Live review needs **ANTHROPIC_API_KEY**. Set it and restart the app:\n\n"
                     "```\nexport ANTHROPIC_API_KEY=sk-...\nsvbench app\n```\n\n"
                     "Or try **Replay cached** + **Run demo** for an instant, key-free result.")
        else:
            with st.status("Running the pipeline on your VCF…", expanded=True) as status:
                try:
                    bench_dir, reviewed, summary = _run_live(
                        dest, caller, chrom, limit, svtypes or None, trio, status, refine,
                        pop_sources=pop_sources)
                    status.update(label="Done ✓", state="complete")
                    _show_region_breakdown(bench_dir, reviewed)
                    _handoff(bench_dir, caller)
                except Exception as e:
                    status.update(label="Run failed", state="error")
                    st.error(f"Pipeline failed: {e}\n\nCheck: GRCh38 HG002 VCF? "
                             "`svbench fetch` run? Truvari/samplot installed? ANTHROPIC_API_KEY set?")
    else:
        st.info("Pick **Run demo** for the bundled example, or upload a VCF and choose **Live run**.")


main()
