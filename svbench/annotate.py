"""Annotation agent -- deterministic evidence packets.

Reads Truvari's fp.vcf.gz / fn.vcf.gz, and for each discordant call assembles an
`EvidencePacket`: the call's coordinates + genomic-context flags (segdup,
low-mappability, tandem-repeat, homopolymer) from the GIAB stratifications, plus
the distance to the nearest truth call of the same type. These flags are what let
Claude distinguish a genuine caller error from a repeat-region benchmark artifact.

Pure lookups (tabix), no model calls.
"""
from __future__ import annotations

import sys
from pathlib import Path
from typing import Iterator, Optional

import pysam

from . import config
from .popfreq import PopCatalogs, annotate_population
from .schema import EvidencePacket, TruvariLabel

# fp.vcf.gz = comparison calls with no truth match  -> false positives
# fn.vcf.gz = truth calls the caller missed          -> false negatives
_DISCORDANT_FILES: dict[str, TruvariLabel] = {"fp.vcf.gz": "FP", "fn.vcf.gz": "FN"}


def _svtype(rec: pysam.VariantRecord) -> str:
    st = rec.info.get("SVTYPE")
    if st:
        return st if isinstance(st, str) else st[0]
    alt = rec.alts[0] if rec.alts else ""
    if alt.startswith("<") and alt.endswith(">"):
        return alt.strip("<>").split(":")[0]
    # resolved alleles: infer from length delta
    if rec.alts and len(rec.ref) > len(rec.alts[0]):
        return "DEL"
    if rec.alts and len(rec.ref) < len(rec.alts[0]):
        return "INS"
    return "UNK"


def _svlen(rec: pysam.VariantRecord) -> Optional[int]:
    sl = rec.info.get("SVLEN")
    if sl is not None:
        sl = sl[0] if isinstance(sl, (list, tuple)) else sl
        return abs(int(sl))
    end = rec.info.get("END")
    if end:
        return abs(int(end) - rec.pos)
    if rec.alts:
        return abs(len(rec.ref) - len(rec.alts[0]))
    return None


def _end(rec: pysam.VariantRecord, svtype: str, svlen: Optional[int]) -> int:
    end = rec.info.get("END")
    if end:
        return int(end)
    if svtype == "INS":
        return rec.pos + 1
    return rec.pos + (svlen or 1)


class _RegionFlags:
    """Lazily-opened tabix handles for the stratification BEDs + truth VCF."""

    def __init__(self, pop_sources: Optional[list[str]] = None) -> None:
        self._beds: dict[str, Optional[pysam.TabixFile]] = {}
        for name in config.STRATIFICATION_BEDS:
            p = config.DATA_DIR / f"strat_{name}.bed.gz"
            self._beds[name] = pysam.TabixFile(str(p)) if p.exists() else None
        self._truth = pysam.VariantFile(str(config.TRUTH_VCF)) if config.TRUTH_VCF.exists() else None
        # Population SV catalogs (no-op if no pop_*.bed.gz present). pop_sources
        # restricts to the UI-selected catalogs; None = every present catalog.
        self._pop = PopCatalogs(pop_sources)

    def _overlaps(self, name: str, chrom: str, start: int, end: int) -> bool:
        tb = self._beds.get(name)
        if tb is None:
            return False
        try:
            return any(True for _ in tb.fetch(chrom, max(0, start - 1), end))
        except (ValueError, OSError):
            return False  # contig absent from this bed

    def nearest_truth(self, chrom: str, start: int, end: int, svtype: str,
                      window: int = 2000) -> Optional[int]:
        if self._truth is None:
            return None
        best: Optional[int] = None
        try:
            for rec in self._truth.fetch(chrom, max(0, start - window), end + window):
                if _svtype(rec) != svtype:
                    continue
                d = min(abs(rec.pos - start), abs(rec.pos - end))
                best = d if best is None else min(best, d)
        except (ValueError, OSError):
            return None
        return best

    def annotate(self, packet: EvidencePacket) -> EvidencePacket:
        c, s, e = packet.chrom, packet.start, packet.end
        packet.in_segdup = self._overlaps("segdup", c, s, e)
        packet.in_low_mappability = self._overlaps("low_mappability", c, s, e)
        packet.in_tandem_repeat = self._overlaps("tandem_repeat", c, s, e)
        packet.in_homopolymer = self._overlaps("homopolymer", c, s, e)
        packet.nearest_truth_dist = self.nearest_truth(c, s, e, packet.svtype)
        annotate_population(packet, self._pop)
        return packet


def load_discordant_loci(
    bench_dir: Path,
    caller: str,
    svtypes: Optional[list[str]] = None,
    limit: Optional[int] = None,
    pop_sources: Optional[list[str]] = None,
) -> list[EvidencePacket]:
    """Build annotated evidence packets from a truvari output directory.

    pop_sources restricts population-catalog corroboration to the selected
    catalogs (e.g. the Streamlit selection); None uses every present catalog."""
    bench_dir = Path(bench_dir)
    flags = _RegionFlags(pop_sources)
    packets: list[EvidencePacket] = []

    for fname, label in _DISCORDANT_FILES.items():
        vpath = bench_dir / fname
        if not vpath.exists():
            print(f"[warn] {vpath} missing", file=sys.stderr)
            continue
        vf = pysam.VariantFile(str(vpath))
        for i, rec in enumerate(vf):
            st = _svtype(rec)
            if svtypes and st not in svtypes:
                continue
            svlen = _svlen(rec)
            packet = EvidencePacket(
                locus_id=f"{caller}:{label}:{rec.chrom}:{rec.pos}:{st}",
                chrom=rec.chrom, start=rec.pos, end=_end(rec, st, svlen),
                svtype=st, svlen=svlen, caller=caller, truvari_label=label,
                caller_qual=(rec.qual if rec.qual is not None else None),
            )
            packets.append(flags.annotate(packet))

    if limit:
        packets = packets[:limit]
    print(f"[annotate] {len(packets)} discordant loci "
          f"(svtypes={svtypes or 'all'})", file=sys.stderr)
    return packets


def load_callset_loci(
    vcf_path: Path,
    caller: str,
    svtypes: Optional[list[str]] = None,
    limit: Optional[int] = None,
    pop_sources: Optional[list[str]] = None,
) -> list[EvidencePacket]:
    """Truth-free QC: build packets from EVERY call in a raw caller VCF (no
    Truvari, no truth set). Region flags (segdup/tandem/mappability) are
    reference-based and valid for any GRCh38 sample; truth distance is left None
    because the sample has no matched truth set."""
    flags = _RegionFlags(pop_sources)
    packets: list[EvidencePacket] = []
    vf = pysam.VariantFile(str(vcf_path))
    for rec in vf:
        st = _svtype(rec)
        if svtypes and st not in svtypes:
            continue
        svlen = _svlen(rec)
        p = EvidencePacket(
            locus_id=f"{caller}:QC:{rec.chrom}:{rec.pos}:{st}",
            chrom=rec.chrom, start=rec.pos, end=_end(rec, st, svlen),
            svtype=st, svlen=svlen, caller=caller, truvari_label="QC",
            caller_qual=(rec.qual if rec.qual is not None else None),
        )
        # region flags only; no nearest-truth (different/absent truth set)
        p.in_segdup = flags._overlaps("segdup", p.chrom, p.start, p.end)
        p.in_low_mappability = flags._overlaps("low_mappability", p.chrom, p.start, p.end)
        p.in_tandem_repeat = flags._overlaps("tandem_repeat", p.chrom, p.start, p.end)
        p.in_homopolymer = flags._overlaps("homopolymer", p.chrom, p.start, p.end)
        annotate_population(p, flags._pop)  # known-SV corroboration is truth-free
        packets.append(p)
    if limit:
        packets = packets[:limit]
    print(f"[annotate] QC: {len(packets)} calls loaded (svtypes={svtypes or 'all'})",
          file=sys.stderr)
    return packets
