"""Truvari wrapper -- the commodity metrics layer.

Runs `truvari bench` (+ optional `truvari refine`) of a caller VCF against the
GIAB HG002 v5.0q truth set, producing tp/fp/fn VCFs and a summary.json. The
FP/FN calls are the discordances the Review agent then explains.
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from . import config
from .shell import require, run


def prepare_vcf(vcf: Path) -> Path:
    """Ensure a VCF is bgzipped + tabix-indexed (truvari requires both)."""
    require("bcftools", "tabix", "bgzip")
    vcf = Path(vcf)
    if vcf.suffix != ".gz":
        gz = vcf.with_suffix(vcf.suffix + ".gz")
        with open(gz, "wb") as fout:
            run(["bgzip", "-c", str(vcf)], stdout=fout)
        vcf = gz
    if not Path(str(vcf) + ".tbi").exists():
        # bcftools index -t is tolerant of unsorted input via a sort first.
        try:
            run(["tabix", "-p", "vcf", str(vcf)])
        except Exception:
            sortd = vcf.with_suffix(".sorted.vcf.gz")
            run(["bcftools", "sort", "-Oz", "-o", str(sortd), str(vcf)])
            run(["tabix", "-p", "vcf", str(sortd)])
            vcf = sortd
    return vcf


def _chrom_subset_bed(chrom: str) -> Path:
    """Write a benchmark-BED subset for one chromosome (for chromosome-scoped
    demo runs, so off-chrom truth calls aren't all counted as false negatives)."""
    out = config.DATA_DIR / f"benchmark_{chrom}.bed"
    with open(config.BENCHMARK_BED) as fin, open(out, "w") as fout:
        for line in fin:
            if line.startswith(f"{chrom}\t"):
                fout.write(line)
    return out


def run_bench(caller_vcf: Path, out_dir: Path, use_reference: bool = True,
              chrom: str | None = None, refine: bool | None = None) -> Path:
    """Run truvari bench. Returns the output directory holding fp/fn/tp VCFs.

    If `chrom` is given, evaluation is restricted to that chromosome's benchmark
    regions -- use this when the caller VCF only covers one chromosome.

    `refine` overrides config.RUN_TRUVARI_REFINE: refine does per-region MAFFT
    realignment (accurate but slow -- minutes); pass refine=False for a fast run.
    """
    require("truvari")
    caller_vcf = prepare_vcf(Path(caller_vcf))
    out_dir = Path(out_dir)
    if out_dir.exists():
        shutil.rmtree(out_dir)  # truvari refuses to write into an existing dir

    include_bed = _chrom_subset_bed(chrom) if chrom else config.BENCHMARK_BED
    cmd = [
        "truvari", "bench",
        "-b", str(config.TRUTH_VCF),
        "-c", str(caller_vcf),
        "--includebed", str(include_bed),
        "-o", str(out_dir),
        *config.TRUVARI_BENCH_ARGS,
    ]
    if use_reference and config.REFERENCE_FASTA.exists():
        cmd += ["-f", str(config.REFERENCE_FASTA)]
    run(cmd)

    do_refine = config.RUN_TRUVARI_REFINE if refine is None else refine
    if do_refine and config.REFERENCE_FASTA.exists():
        # refine harmonizes repeat-region representations; without it we would
        # over-report tandem-repeat calls as FP/FN.
        try:
            run(["truvari", "refine",
                 "--reference", str(config.REFERENCE_FASTA),
                 "--regions", str(out_dir / "candidate.refine.bed"),
                 str(out_dir)])
        except Exception as exc:  # noqa: BLE001
            print(f"[warn] truvari refine skipped: {exc}", file=sys.stderr)
    elif do_refine:
        print("[warn] no reference FASTA -> skipping `truvari refine`. "
              "Repeat-region discordances may be over-reported; the Review "
              "agent will still flag them as benchmark_artifact.", file=sys.stderr)
    return out_dir


def read_summary(out_dir: Path) -> dict:
    p = Path(out_dir) / "summary.json"
    if not p.exists():
        return {}
    return json.loads(p.read_text())
