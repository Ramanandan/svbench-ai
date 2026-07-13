"""svbench CLI -- orchestrates the pipeline.

    svbench fetch   [--reference] [--no-bam] [--bam-url URL]
    svbench bench   CALLER.vcf.gz --caller NAME [--out DIR] [--no-reference]
    svbench review  BENCH_DIR --caller NAME [--svtype DEL ...] [--limit N] [--batch]
    svbench report  BENCH_DIR --caller NAME
    svbench serve   BENCH_DIR --caller NAME [--port 8000] [--no-browser]
    svbench run     CALLER.vcf.gz --caller NAME [--svtype DEL ...] [--limit N] [--batch]
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from . import config


def _default_bench_dir(caller: str) -> Path:
    return config.OUTPUT_DIR / f"bench_{caller}"


def cmd_fetch(args) -> None:
    from . import data
    data.fetch_all(reference=args.reference, bam=not args.no_bam)


def cmd_fetch_catalogs(args) -> None:
    from . import data
    data.fetch_catalogs(chrom=args.chrom, sources=args.source, demo=args.demo)


def cmd_bench(args) -> None:
    from . import benchmark
    config.ensure_dirs()
    out = Path(args.out) if args.out else _default_bench_dir(args.caller)
    benchmark.run_bench(Path(args.caller_vcf), out,
                        use_reference=not args.no_reference,
                        chrom=getattr(args, "chrom", None))
    summary = benchmark.read_summary(out)
    print(f"[bench] {args.caller}: "
          f"precision={summary.get('precision')} recall={summary.get('recall')} "
          f"f1={summary.get('f1')}  ->  {out}")


def cmd_review(args) -> None:
    from . import annotate, data, visualize, review
    bench_dir = Path(args.bench_dir)
    img_dir = bench_dir / "images"
    packets = annotate.load_discordant_loci(
        bench_dir, args.caller, svtypes=args.svtype, limit=args.limit
    )
    if not packets:
        sys.exit("[review] no discordant loci found (check svtype filter / bench dir).")
    trio = getattr(args, "trio", None)
    # Slice the remote HiFi BAM once, only around these loci (see data.py).
    if not getattr(args, "no_images", False):
        child_bam = data.slice_bam_for_loci(packets, bam_url=getattr(args, "bam_url", None))
        if trio:
            parents = data.slice_parents_for_loci(packets, trio)
            t = config.TRIOS[trio]
            labels = (t["child_label"], t["father_label"], t["mother_label"])
            packets = [visualize.render_locus_trio(
                p, img_dir, child_bam, parents["father"], parents["mother"], labels)
                for p in packets]
        else:
            packets = visualize.render_all(packets, img_dir, bam=child_bam)

    if getattr(args, "dry_run", False):
        import json as _json
        print("[review] DRY RUN — request assembled but NOT sent (no credits spent):")
        print(_json.dumps(review.preview_request(packets[0]), indent=2)[:1400])
        return

    if args.batch:
        by_id = dict(zip(review.batch_ids(packets), packets))
        batch_id = review.submit_batch(packets)
        print(f"[review] submitted batch {batch_id}; polling...")
        while review.batch_status(batch_id) != "ended":
            time.sleep(30)
            print(f"  status={review.batch_status(batch_id)}")
        reviewed = review.collect_batch(batch_id, by_id)
    else:
        reviewed = [review.review_locus(p, mode="benchmark", trio=bool(trio)) for p in packets]

    review.save_reviews(reviewed, bench_dir / "reviews.json")
    print(f"[review] {len(reviewed)} verdicts -> {bench_dir/'reviews.json'}")


def cmd_qc(args) -> None:
    """Truth-free QC: review a raw caller VCF with no truth set (Path B)."""
    from . import annotate, data, visualize, review
    out_dir = Path(args.out) if args.out else (config.OUTPUT_DIR / f"qc_{args.caller}")
    out_dir.mkdir(parents=True, exist_ok=True)
    packets = annotate.load_callset_loci(
        Path(args.caller_vcf), args.caller, svtypes=args.svtype, limit=args.limit
    )
    if not packets:
        sys.exit("[qc] no calls found (check svtype filter / VCF).")
    if not getattr(args, "no_images", False):
        bam = data.slice_bam_for_loci(packets, bam_url=getattr(args, "bam_url", None),
                                      out=out_dir / "qc_loci.bam")
        packets = visualize.render_all(packets, out_dir / "images", bam=bam)
    if getattr(args, "dry_run", False):
        import json as _json
        print("[qc] DRY RUN — request assembled but NOT sent:")
        print(_json.dumps(review.preview_request(packets[0]), indent=2)[:1200])
        return
    reviewed = [review.review_locus(p, mode="qc") for p in packets]
    review.save_reviews(reviewed, out_dir / "reviews.json")
    from . import report
    report.write_report_md(reviewed, {}, args.caller, out_dir)
    report.write_dashboard_html(reviewed, args.caller, out_dir)
    print(f"[qc] {len(reviewed)} verdicts -> {out_dir}")


def cmd_report(args) -> None:
    import json
    from . import benchmark, report
    from .schema import ReviewedLocus
    bench_dir = Path(args.bench_dir)
    raw = json.loads((bench_dir / "reviews.json").read_text())
    reviewed = [ReviewedLocus.model_validate(r) for r in raw]
    summary = benchmark.read_summary(bench_dir)
    md = report.write_report_md(reviewed, summary, args.caller, bench_dir)
    dash = report.write_dashboard_html(reviewed, args.caller, bench_dir, summary)
    print(f"[report] {md}\n[report] {dash}")


def cmd_doctor(args) -> None:
    """Preflight: check tools, data, and env for a live run."""
    from . import doctor
    sys.exit(doctor.report())


def cmd_app(args) -> None:
    """Launch the Streamlit run console (`streamlit run svbench/app.py`)."""
    import importlib.util
    import subprocess
    if importlib.util.find_spec("streamlit") is None:
        sys.exit('[app] streamlit not installed. Install with: pip install -e ".[app]"  '
                 "(or: pip install streamlit)")
    # Skip Streamlit's first-run interactive email prompt (it hangs a subprocess
    # with no TTY). This is exactly the (opted-out) file Streamlit writes itself.
    cred = Path.home() / ".streamlit" / "credentials.toml"
    if not cred.exists():
        cred.parent.mkdir(parents=True, exist_ok=True)
        cred.write_text('[general]\nemail = ""\n')
    app_path = Path(__file__).with_name("app.py")
    cmd = [sys.executable, "-m", "streamlit", "run", str(app_path),
           "--server.port", str(args.port)]
    if args.no_browser:
        cmd += ["--server.headless", "true"]
    # Use the current interpreter's streamlit so it works without activating the venv.
    subprocess.run(cmd, check=True)


def cmd_serve(args) -> None:
    """Launch the local review web app over an existing review dir."""
    from . import server
    server.serve(Path(args.bench_dir), args.caller,
                 port=args.port, open_browser=not args.no_browser)


def cmd_run(args) -> None:
    args.out = None
    cmd_bench(args)
    args.bench_dir = str(_default_bench_dir(args.caller))
    cmd_review(args)
    cmd_report(args)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="svbench", description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="command", required=True)

    f = sub.add_parser("fetch", help="download truth/annotations + slice HiFi BAM")
    f.add_argument("--reference", action="store_true", help="also fetch GRCh38 FASTA (large)")
    f.add_argument("--no-bam", action="store_true", help="skip slicing the HiFi BAM")
    f.add_argument("--bam-url", default=None)
    f.set_defaults(func=cmd_fetch)

    fc = sub.add_parser("fetch-catalogs",
                        help="download + normalize population SV catalogs "
                             "(gnomAD-SV / dbVar / DGV / HGSVC) for known-SV corroboration")
    fc.add_argument("--chrom", default=None,
                    help="subset catalogs to one contig (e.g. chr21) to stay lightweight")
    fc.add_argument("--source", nargs="*", default=None, choices=config.POP_CATALOG_KEYS,
                    help="limit to specific catalogs (default: all)")
    fc.add_argument("--demo", action="store_true",
                    help="also build a truth-derived demo catalog (plumbing/UI test only, "
                         "NOT scientific evidence)")
    fc.set_defaults(func=cmd_fetch_catalogs)

    b = sub.add_parser("bench", help="truvari bench+refine a caller VCF")
    b.add_argument("caller_vcf")
    b.add_argument("--caller", required=True)
    b.add_argument("--out", default=None)
    b.add_argument("--chrom", default=None, help="restrict evaluation to one chromosome")
    b.add_argument("--no-reference", action="store_true")
    b.set_defaults(func=cmd_bench)

    r = sub.add_parser("review", help="annotate + samplot + Claude verdicts")
    r.add_argument("bench_dir")
    r.add_argument("--caller", required=True)
    r.add_argument("--svtype", nargs="*", default=None, choices=config.SV_TYPES)
    r.add_argument("--limit", type=int, default=None)
    r.add_argument("--batch", action="store_true", help="use the Batches API")
    r.add_argument("--no-images", action="store_true", help="skip samplot (text-only verdicts)")
    r.add_argument("--bam-url", default=None, help="child alignment source for images")
    r.add_argument("--trio", default=None, choices=list(config.TRIOS),
                   help="add Mendelian evidence: render child+parents and use the trio rubric")
    r.add_argument("--dry-run", action="store_true", help="assemble the request but don't call the API")
    r.set_defaults(func=cmd_review)

    q = sub.add_parser("qc", help="truth-free QC of a raw caller VCF (no truth set) — Path B")
    q.add_argument("caller_vcf")
    q.add_argument("--caller", required=True)
    q.add_argument("--out", default=None)
    q.add_argument("--svtype", nargs="*", default=None, choices=config.SV_TYPES)
    q.add_argument("--limit", type=int, default=None)
    q.add_argument("--no-images", action="store_true")
    q.add_argument("--bam-url", default=None)
    q.add_argument("--dry-run", action="store_true")
    q.set_defaults(func=cmd_qc)

    rp = sub.add_parser("report", help="write report.md + dashboard.html")
    rp.add_argument("bench_dir")
    rp.add_argument("--caller", required=True)
    rp.set_defaults(func=cmd_report)

    sv = sub.add_parser("serve", help="launch the local review web app (no deps, localhost)")
    sv.add_argument("bench_dir")
    sv.add_argument("--caller", required=True)
    sv.add_argument("--port", type=int, default=8000)
    sv.add_argument("--no-browser", action="store_true", help="don't auto-open a browser")
    sv.set_defaults(func=cmd_serve)

    ap = sub.add_parser("app", help="launch the Streamlit run console (upload + live run)")
    ap.add_argument("--port", type=int, default=8501)
    ap.add_argument("--no-browser", action="store_true", help="don't auto-open a browser")
    ap.set_defaults(func=cmd_app)

    dc = sub.add_parser("doctor", help="preflight check of tools, data, and env for a live run")
    dc.set_defaults(func=cmd_doctor)

    ra = sub.add_parser("run", help="bench + review + report")
    ra.add_argument("caller_vcf")
    ra.add_argument("--caller", required=True)
    ra.add_argument("--svtype", nargs="*", default=None, choices=config.SV_TYPES)
    ra.add_argument("--limit", type=int, default=None)
    ra.add_argument("--batch", action="store_true")
    ra.add_argument("--chrom", default=None, help="restrict evaluation to one chromosome")
    ra.add_argument("--no-images", action="store_true")
    ra.add_argument("--bam-url", default=None)
    ra.add_argument("--no-reference", action="store_true")
    ra.set_defaults(func=cmd_run)
    return p


def main(argv=None) -> None:
    args = build_parser().parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
