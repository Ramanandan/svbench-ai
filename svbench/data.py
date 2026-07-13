"""Data acquisition -- the Day-1 'data spine'.

Downloads the GIAB HG002 v5.0q truth set + benchmark BED, the GIAB genome
stratifications used for the evidence packets, and slices a HiFi BAM to the
benchmark regions (streaming, never a full 50-100 GB download).

Everything is GRCh38. The reference FASTA is optional -- only `truvari refine`
and sequence-level (`--pctseq`) matching need it; skip it for a fast first run.
"""
from __future__ import annotations

import gzip
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Iterable, Optional

import pysam

from . import config
from .shell import _augmented_path, curl, require, run


def fetch_truth() -> None:
    config.ensure_dirs()
    curl(config.TRUTH_VCF_URL, config.TRUTH_VCF)
    curl(config.TRUTH_TBI_URL, config.TRUTH_VCF.with_suffix(config.TRUTH_VCF.suffix + ".tbi"))
    curl(config.BENCHMARK_BED_URL, config.BENCHMARK_BED)


def fetch_stratifications() -> None:
    config.ensure_dirs()
    for name, url in config.STRATIFICATION_BEDS.items():
        dest = config.DATA_DIR / f"strat_{name}.bed.gz"
        curl(url, dest)
        # tabix-index for fast per-locus intersect (bgzipped already)
        tbi = dest.with_suffix(dest.suffix + ".tbi")
        if not tbi.exists():
            try:
                run(["tabix", "-p", "bed", str(dest)])
            except Exception as exc:  # noqa: BLE001
                print(f"[warn] could not tabix {dest.name}: {exc}", file=sys.stderr)


def fetch_gencode() -> None:
    config.ensure_dirs()
    curl(config.GENCODE_GTF_URL, config.DATA_DIR / "gencode.annotation.gtf.gz")


def fetch_reference() -> None:
    """Download + decompress + faidx the GRCh38 reference (large; optional)."""
    require("samtools")
    config.ensure_dirs()
    gz = config.DATA_DIR / "GRCh38.fasta.gz"
    curl(config.REFERENCE_FASTA_URL, gz)
    if not config.REFERENCE_FASTA.exists():
        print("[data] decompressing reference...", file=sys.stderr)
        with gzip.open(gz, "rb") as fin, open(config.REFERENCE_FASTA, "wb") as fout:
            shutil.copyfileobj(fin, fout)
    if not Path(str(config.REFERENCE_FASTA) + ".fai").exists():
        run(["samtools", "faidx", str(config.REFERENCE_FASTA)])


def verify_bam(bam_url: str | None = None) -> bool:
    """Confirm the remote HiFi BAM and its index are reachable (HEAD 200).

    The v5.0q benchmark spans ~2.76 Gbp (essentially the whole genome), so we
    never slice the *whole* benchmark -- that would pull the entire ~50 GB BAM.
    Instead we slice per-locus after Truvari (`slice_bam_for_loci`).
    """
    url = bam_url or config.HIFI_BAM_URL
    import subprocess
    ok = True
    for u in (url, url + ".bai"):
        code = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-I", "-L", u],
            capture_output=True, text=True,
        ).stdout.strip()
        print(f"[data] {code}  {u}", file=sys.stderr)
        ok = ok and code == "200"
    return ok


def slice_bam_for_loci(loci, bam_url: str | None = None, pad: int = 3000,
                       out: Path | None = None) -> Path:
    """Stream only the reads around a set of discordant loci from the remote
    indexed HiFi BAM into a small local BAM. `loci` is any iterable of objects
    with .chrom/.start/.end (e.g. EvidencePacket). Slice once, reuse for all
    samplot images -- avoids live remote reads during the demo.
    """
    require("samtools")
    url = bam_url or config.HIFI_BAM_URL
    out = Path(out or config.SLICED_BAM)
    loci = list(loci)
    if not loci:
        sys.exit("[data] no loci to slice for.")
    bed = config.DATA_DIR / "discordant_loci.bed"
    with open(bed, "w") as fh:
        for lo in loci:
            fh.write(f"{lo.chrom}\t{max(0, lo.start - pad)}\t{lo.end + pad}\n")
    print(f"[data] slicing HiFi reads for {len(loci)} loci (pad={pad}) from:\n"
          f"       {url}", file=sys.stderr)
    with open(out, "wb") as fout:
        run(["samtools", "view", "-b", "-M", "-L", str(bed), url], stdout=fout)
    run(["samtools", "index", str(out)])
    print(f"[data] locus BAM: {out} ({out.stat().st_size/1e6:.1f} MB)", file=sys.stderr)
    return out


def slice_parents_for_loci(loci, sample: str, pad: int = 3000) -> dict:
    """Slice the father's and mother's reads around the given loci from their
    remote HiFi BAMs. Returns {'father': path, 'mother': path} of small local
    BAMs for trio samplot rendering. Requires `sample` to be in config.TRIOS.
    """
    require("samtools")
    trio = config.TRIOS.get(sample)
    if not trio:
        sys.exit(f"[data] no trio configured for sample '{sample}' "
                 f"(available: {list(config.TRIOS)})")
    loci = list(loci)
    bed = config.DATA_DIR / f"{sample}_trio_loci.bed"
    with open(bed, "w") as fh:
        for lo in loci:
            fh.write(f"{lo.chrom}\t{max(0, lo.start - pad)}\t{lo.end + pad}\n")
    out = {}
    for role in ("father", "mother"):
        dest = config.DATA_DIR / f"{sample}_{role}_loci.bam"
        print(f"[data] slicing {role} ({sample}) reads for {len(loci)} loci...",
              file=sys.stderr)
        with open(dest, "wb") as fout:
            run(["samtools", "view", "-b", "-M", "-L", str(bed), trio[role]], stdout=fout)
        run(["samtools", "index", str(dest)])
        out[role] = dest
    return out


# ---------------------------------------------------------------------------
# Population SV catalogs (gnomAD-SV / dbVar / DGV / HGSVC) -> normalized BEDs.
# Each normalizer yields rows (chrom, start0, end, svtype, af, source, id); af=-1
# means presence-only. Everything is wrapped so one broken source can't sink a run.
# ---------------------------------------------------------------------------
Row = tuple

_SVTYPE_MAP = {
    "DEL": "DEL", "DELETION": "DEL", "LOSS": "DEL", "COPY_NUMBER_LOSS": "DEL",
    "DUP": "DUP", "DUPLICATION": "DUP", "GAIN": "DUP", "COPY_NUMBER_GAIN": "DUP",
    "TANDEM_DUPLICATION": "DUP",
    "INS": "INS", "INSERTION": "INS", "MOBILE_ELEMENT_INSERTION": "INS",
    "NOVEL_SEQUENCE_INSERTION": "INS", "ALU": "INS", "LINE1": "INS", "SVA": "INS",
    "INV": "INV", "INVERSION": "INV", "CNV": "CNV", "COPY_NUMBER_VARIATION": "CNV",
}


def _norm_svtype(raw: str) -> Optional[str]:
    """Map a catalog SVTYPE spelling to DEL/INS/DUP/INV/CNV, or None to skip."""
    if not raw:
        return None
    t = raw.upper().split(":")[0].strip()  # 'INS:ME:ALU' -> 'INS'
    return _SVTYPE_MAP.get(t) or (t if t in {"DEL", "INS", "DUP", "INV", "CNV"} else None)


def _write_catalog(key: str, rows: Iterable[Row]) -> Optional[Path]:
    """Sort rows, write a BED, then bgzip + tabix it to pop_<key>.bed.gz."""
    rows = [r for r in rows if r]
    if not rows:
        print(f"[catalog] {key}: 0 rows -- skipped", file=sys.stderr)
        return None
    rows.sort(key=lambda r: (r[0], int(r[1])))
    plain = config.DATA_DIR / f"pop_{key}.bed"
    with open(plain, "w") as fh:
        for c, s, e, svt, af, src, vid in rows:
            fh.write(f"{c}\t{int(s)}\t{int(e)}\t{svt}\t{af}\t{src}\t{vid}\n")
    # pysam bgzips in place and writes the .tbi (no external bgzip/tabix needed).
    pysam.tabix_index(str(plain), preset="bed", force=True)
    out = config.DATA_DIR / f"pop_{key}.bed.gz"
    print(f"[catalog] {key}: {len(rows)} SVs -> {out.name}", file=sys.stderr)
    return out


def _tabix_lines(url: str, region: str) -> list[str]:
    """Stream one tabix region from a (remote) bgzipped+indexed VCF as text lines.
    Returns [] on any failure so a source degrades gracefully."""
    require("tabix")
    env = {**os.environ, "PATH": _augmented_path()}
    try:
        p = subprocess.run(["tabix", url, region], capture_output=True, text=True, env=env)
    except Exception:  # noqa: BLE001
        return []
    return p.stdout.splitlines() if p.returncode == 0 else []


def _contig_variants(chrom: str) -> list[str]:
    """Both spellings of a contig, so we can query whichever the VCF uses."""
    return [chrom, chrom[3:]] if chrom.startswith("chr") else [chrom, f"chr{chrom}"]


def _parse_info(info: str) -> dict:
    d: dict[str, str] = {}
    for kv in info.split(";"):
        if not kv:
            continue
        k, _, v = kv.partition("=")
        d[k] = v if _ else "True"
    return d


def _vcf_line_to_row(line: str, source: str) -> Optional[Row]:
    """Parse one VCF data line into a normalized catalog row (chr-prefixed)."""
    f = line.rstrip("\n").split("\t")
    if len(f) < 8:
        return None
    try:
        pos = int(f[1])
    except ValueError:
        return None
    info = _parse_info(f[7])
    svt = _norm_svtype(info.get("SVTYPE", ""))
    if svt is None:  # fall back to a symbolic ALT like <DEL> / <INS:ME:ALU>
        alt = f[4]
        if alt.startswith("<") and ">" in alt:
            svt = _norm_svtype(alt.strip("<>").split(":")[0])
    if svt is None:
        return None
    chrom = f[0]
    oc = chrom if chrom.startswith("chr") else f"chr{chrom}"
    if svt == "INS":
        end = pos + 1
    else:
        e = info.get("END", "")
        if e.lstrip("-").isdigit():
            end = int(e)
        else:
            sl = info.get("SVLEN", "")
            end = pos + abs(int(sl)) if sl.lstrip("-").isdigit() else pos + 1
    af_s = info.get("AF")
    try:
        af = float(af_s.split(",")[0]) if af_s is not None else -1.0
    except ValueError:
        af = -1.0
    vid = f[2] if f[2] != "." else "."
    return (oc, pos - 1, end, svt, af, source, vid)


def _iter_vcf_svs(url: str, source: str, chrom: Optional[str]) -> Iterable[Row]:
    """Stream SVs from a (remote, tabix-indexed) VCF for one contig, tolerant of
    chr-prefix differences. Uses the tabix CLI rather than pysam.fetch because
    some catalog VCFs (dbVar, HGSVC) carry headers pysam rejects mid-fetch."""
    if chrom:
        for contig in _contig_variants(chrom):
            lines = _tabix_lines(url, contig)
            if lines:
                for ln in lines:
                    if ln[:1] == "#":
                        continue
                    row = _vcf_line_to_row(ln, source)
                    if row:
                        yield row
                return
        return
    # whole-file (no contig subset): sequential pysam iteration, reuse the parser
    vf = pysam.VariantFile(url)
    for rec in vf:
        row = _vcf_line_to_row(str(rec), source)
        if row:
            yield row


def _normalize_gnomad(chrom: Optional[str]) -> Optional[Path]:
    return _write_catalog("gnomad", _iter_vcf_svs(config.GNOMAD_SV_URL, "gnomAD-SV", chrom))


def _normalize_hgsvc(chrom: Optional[str]) -> Optional[Path]:
    return _write_catalog("hgsvc", _iter_vcf_svs(config.HGSVC_SV_URL, "HGSVC", chrom))


def _normalize_dbvar(chrom: Optional[str]) -> Optional[Path]:
    """dbVar non-redundant variant regions (presence-only, af=-1)."""
    return _write_catalog("dbvar", _iter_vcf_svs(config.DBVAR_SV_URL, "dbVar", chrom))


def _normalize_dgv(chrom: Optional[str]) -> Optional[Path]:
    """DGV variant table (tab-delimited, header row; presence-only, af=-1)."""
    dest = config.DATA_DIR / "dgv_variants.txt"
    curl(config.DGV_VARIANTS_URL, dest)
    rows: list[Row] = []
    with open(dest, "rt") as fh:
        header = fh.readline().rstrip("\n").split("\t")
        idx = {name: i for i, name in enumerate(header)}
        cc, cs, ce = idx.get("chr"), idx.get("start"), idx.get("end")
        ct = idx.get("varianttype")
        cst = idx.get("variantsubtype")
        cid = idx.get("variantaccession", 0)
        if None in (cc, cs, ce):
            print("[catalog] DGV: unexpected header -- skipped", file=sys.stderr)
            return None
        for line in fh:
            f = line.rstrip("\n").split("\t")
            if len(f) <= max(cc, cs, ce):
                continue
            c = f[cc] if f[cc].startswith("chr") else f"chr{f[cc]}"
            if chrom and c != chrom:
                continue
            svt = _norm_svtype(f[cst] if cst is not None and cst < len(f) else "") \
                or _norm_svtype(f[ct] if ct is not None and ct < len(f) else "")
            if svt is None:
                continue
            try:
                rows.append((c, int(f[cs]), int(f[ce]), svt, -1.0, "DGV", f[cid]))
            except ValueError:
                continue
    return _write_catalog("dgv", rows)


_NORMALIZERS = {
    "gnomad": _normalize_gnomad, "dbvar": _normalize_dbvar,
    "dgv": _normalize_dgv, "hgsvc": _normalize_hgsvc,
}


def make_demo_catalog(chrom: str = "chr21") -> Optional[Path]:
    """Build a GIAB known-SV reference (from the HG002 truth set) so the
    population-evidence path is usable in the demo WITHOUT the large real
    downloads. It is derived from the truth set (circular with benchmarking), so
    it is written to pop_demo.bed.gz and labelled 'GIAB known SVs'. Use for the
    demo UI, not as an independent benchmark of the truth set itself.
    """
    if not config.TRUTH_VCF.exists():
        sys.exit("[catalog] demo needs the truth VCF -- run `svbench fetch` first.")
    vf = pysam.VariantFile(str(config.TRUTH_VCF))
    rows: list[Row] = []
    try:
        recs = vf.fetch(chrom)
    except (ValueError, OSError):
        recs = vf
    for rec in recs:
        if rec.chrom != chrom:
            continue
        raw = rec.info.get("SVTYPE")
        raw = raw[0] if isinstance(raw, (list, tuple)) else raw
        svt = _norm_svtype(raw or "")
        if svt is None:
            continue
        end = rec.info.get("END") or rec.stop
        end = rec.pos + 1 if svt == "INS" else int(end)
        # deterministic pseudo-AF (no RNG): stable, in [0.02, 0.99).
        af = round(0.02 + (rec.pos % 97) / 100.0, 3)
        rows.append((rec.chrom, rec.pos - 1, end, svt, af, "demo", rec.id or "."))
    return _write_catalog("demo", rows)


def fetch_catalogs(chrom: Optional[str] = None,
                   sources: Optional[list[str]] = None,
                   demo: bool = False) -> None:
    """Download + normalize population SV catalogs to pop_<key>.bed.gz.

    chrom subsets each catalog (e.g. 'chr21') to stay lightweight -- strongly
    recommended for the chr21 demo. Any source that fails (moved URL, network) is
    logged and skipped; the rest still produce usable files.
    """
    config.ensure_dirs()
    keys = sources or config.POP_CATALOG_KEYS
    for key in keys:
        fn = _NORMALIZERS.get(key)
        if fn is None:
            print(f"[catalog] unknown source '{key}' -- skipped", file=sys.stderr)
            continue
        try:
            fn(chrom)
        except Exception as exc:  # noqa: BLE001
            print(f"[catalog] {key}: FAILED ({type(exc).__name__}: {exc}) -- "
                  f"skipped. Check the URL in config.py (sources reorganize).",
                  file=sys.stderr)
    if demo:
        make_demo_catalog(chrom or "chr21")
    print("[catalog] done. Present catalogs are used automatically at review time.",
          file=sys.stderr)


def fetch_all(reference: bool = False, bam: bool = True) -> None:
    """Download truth + annotations. Does NOT slice the BAM (that happens
    per-locus after benchmarking); `bam=True` just verifies reachability."""
    fetch_truth()
    fetch_stratifications()
    fetch_gencode()
    if reference:
        fetch_reference()
    if bam:
        verify_bam()
    print("[data] fetch complete. (BAM sliced per-locus at review time.)", file=sys.stderr)
