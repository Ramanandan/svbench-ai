"""Population SV catalog support -- orthogonal corroboration for benchmark_artifact.

For each discordant locus we ask a question the truth set can't answer alone:
*is a structurally-matching SV already known to recur in the human population?*
A hit in gnomAD-SV / dbVar / DGV / HGSVC means "a real SV lives at this locus in
many people", which RAISES confidence that a Truvari FP is actually a benchmark
artifact (a real variant Truvari mis-matched) rather than a genuine caller error.

ASYMMETRY (deliberate, do not remove): a catalog hit is *corroborating* evidence;
ABSENCE is NEUTRAL, never disconfirming -- these catalogs are incomplete and
biased against exactly the hard repeat regions we care about. Downstream code and
the model prompt treat it that way.

Matching is structural, not naive overlap (repeat regions are saturated with
catalog entries, so "any overlap" would fire everywhere):
  * DEL / DUP / INV : reciprocal overlap >= POP_MIN_RECIP_OVERLAP AND type-compatible
  * INS             : breakpoint within POP_INS_MAX_DIST bp (INS are point-ish),
                      type-compatible

Catalogs are consumed as normalized, bgzipped + tabixed BEDs produced by
`svbench fetch-catalogs`:
    chrom \t start \t end \t svtype \t af \t source \t id
(af = -1 when the catalog is presence-only). The whole feature is a NO-OP until at
least one pop_<key>.bed.gz exists in DATA_DIR -- nothing breaks if none are present.
"""
from __future__ import annotations

from typing import Optional

import pysam

from . import config
from .schema import EvidencePacket

# Canonical -> compatible catalog svtypes. gnomAD/dbVar/DGV spell the same event
# many ways (a deletion is DEL / loss / CNV; a duplication is DUP / gain / CNV;
# an insertion may be a mobile-element class).
_TYPE_GROUPS = {
    "DEL": {"DEL", "LOSS", "CNV"},
    "DUP": {"DUP", "GAIN", "CNV"},
    "INS": {"INS", "MEI", "ALU", "LINE1", "SVA", "MOBILE"},
    "INV": {"INV"},
}


def _type_compatible(call_type: str, cat_type: str) -> bool:
    a = (call_type or "").upper()
    b = (cat_type or "").upper()
    if not a or not b:
        return False
    if a == b:
        return True
    return b in _TYPE_GROUPS.get(a, {a})


def _recip_overlap(a0: int, a1: int, b0: int, b1: int) -> float:
    """Reciprocal overlap fraction of two intervals (0..1)."""
    inter = min(a1, b1) - max(a0, b0)
    if inter <= 0:
        return 0.0
    la, lb = a1 - a0, b1 - b0
    if la <= 0 or lb <= 0:
        return 0.0
    return min(inter / la, inter / lb)


class PopCatalogs:
    """Lazily-opened tabix handles for the normalized population-catalog BEDs.

    Mirror of annotate._RegionFlags: one handle per catalog, absent files are
    simply skipped so the feature degrades to a no-op.
    """

    def __init__(self, sources: Optional[list[str]] = None) -> None:
        self._cats: dict[str, Optional[pysam.TabixFile]] = {}
        # "demo" is a truth-derived plumbing catalog (see data.make_demo_catalog);
        # loaded when present but never part of the real download default.
        # sources=None -> every present catalog; a list -> only those keys (the
        # UI selection). An empty list means "no population support".
        keys = [*config.POP_CATALOG_KEYS, "demo"] if sources is None else list(sources)
        for key in keys:
            p = config.DATA_DIR / f"pop_{key}.bed.gz"
            self._cats[key] = pysam.TabixFile(str(p)) if p.exists() else None

    @property
    def available(self) -> bool:
        return any(tb is not None for tb in self._cats.values())

    def match(self, chrom: str, start: int, end: int, svtype: str
              ) -> tuple[list[str], Optional[float]]:
        """Return (catalog labels with a structural match, highest population AF).

        AF is None when every matching catalog is presence-only (no frequency).
        """
        is_ins = (svtype or "").upper() == "INS"
        pad = config.POP_INS_MAX_DIST if is_ins else 0
        hits: list[str] = []
        max_af: Optional[float] = None

        for key, tb in self._cats.items():
            if tb is None:
                continue
            best_af: Optional[float] = None
            matched = False
            try:
                rows = tb.fetch(chrom, max(0, start - pad - 1), end + pad)
            except (ValueError, OSError):
                continue  # contig absent from this catalog
            for line in rows:
                f = line.rstrip("\n").split("\t")
                if len(f) < 6:
                    continue
                try:
                    c_start, c_end = int(f[1]), int(f[2])
                except ValueError:
                    continue
                c_type = f[3]
                if not _type_compatible(svtype, c_type):
                    continue
                if is_ins:
                    d = min(abs(c_start - start), abs(c_start - end), abs(c_end - start))
                    if d > config.POP_INS_MAX_DIST:
                        continue
                elif _recip_overlap(start, end, c_start, c_end) < config.POP_MIN_RECIP_OVERLAP:
                    continue
                matched = True
                try:
                    af = float(f[4])
                except (ValueError, IndexError):
                    af = -1.0
                if af >= 0:
                    best_af = af if best_af is None else max(best_af, af)
            if matched:
                hits.append(config.POP_CATALOG_LABELS.get(key, key))
                if best_af is not None:
                    max_af = best_af if max_af is None else max(max_af, best_af)
        return hits, max_af


def annotate_population(packet: EvidencePacket, cats: PopCatalogs) -> EvidencePacket:
    """Populate packet.pop_catalog_hits / pop_max_af in place."""
    hits, max_af = cats.match(packet.chrom, packet.start, packet.end, packet.svtype)
    packet.pop_catalog_hits = hits
    packet.pop_max_af = max_af
    return packet


def available_catalogs() -> list[str]:
    """Catalog keys whose normalized pop_<key>.bed.gz is present on disk -- the
    set the UI can offer for selection."""
    keys = [*config.POP_CATALOG_KEYS, "demo"]
    return [k for k in keys if (config.DATA_DIR / f"pop_{k}.bed.gz").exists()]


def catalog_size(key: str) -> int:
    """Number of SV records in a normalized catalog (0 if absent)."""
    import gzip
    p = config.DATA_DIR / f"pop_{key}.bed.gz"
    if not p.exists():
        return 0
    try:
        with gzip.open(p, "rt") as fh:
            return sum(1 for _ in fh)
    except OSError:
        return 0


def reannotate_population(reviewed, sources: Optional[list[str]] = None) -> int:
    """Recompute pop_catalog_hits / pop_max_af on already-reviewed loci using the
    selected catalogs. Pure tabix lookups (no API), so cached demo results can
    reflect a live UI catalog selection without re-running Claude. Returns the
    number of loci that gained a population match."""
    cats = PopCatalogs(sources)
    n = 0
    for r in reviewed:
        annotate_population(r.packet, cats)
        if r.packet.pop_catalog_hits:
            n += 1
    return n
