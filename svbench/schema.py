"""Structured types shared across the pipeline.

`SVVerdict` is the schema Claude is forced to return (via messages.parse). Keep
it small and unambiguous -- every field must be gradeable against the image and
the evidence packet so we can hand-verify the model's output.
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

# What Truvari said about the call, before Claude looks at it.
# "QC" = truth-free mode: no benchmark, judging a raw callset on evidence alone.
TruvariLabel = Literal["FP", "FN", "TP", "QC"]

# What Claude concludes after reviewing image + evidence.
Classification = Literal[
    "true_positive",      # a real variant the caller got right
    "false_positive",     # caller reported a variant that isn't supported
    "false_negative",     # a real variant the caller missed
    "benchmark_artifact",  # apparent discordance is a representation / repeat-region issue, not a caller error
    "uncertain",          # evidence is insufficient to decide
]

EvidenceTag = Literal[
    "read_depth", "split_reads", "discordant_pairs", "soft_clips",
    "segdup", "low_mappability", "tandem_repeat", "homopolymer",
    "gene_overlap", "breakpoint_ambiguity", "size_mismatch",
    "truvari_refine", "caller_quality",
    # trio / Mendelian
    "mendelian_inheritance", "parental_support", "de_novo",
    # population catalogs (gnomAD-SV / dbVar / DGV / HGSVC): a structurally
    # matching known SV corroborates that a real variant recurs at this locus.
    "population_support",
]


class EvidencePacket(BaseModel):
    """Deterministic genomic context assembled by the annotation agent and fed
    to Claude alongside the samplot image."""
    locus_id: str
    chrom: str
    start: int
    end: int
    svtype: str
    svlen: Optional[int] = None
    caller: str
    truvari_label: TruvariLabel
    caller_qual: Optional[float] = None
    # region flags from bedtools intersect against GIAB stratifications
    in_segdup: bool = False
    in_low_mappability: bool = False
    in_tandem_repeat: bool = False
    in_homopolymer: bool = False
    repeatmasker_class: Optional[str] = None
    gene_overlap: Optional[str] = None  # e.g. "intronic(GENEX)" or "intergenic"
    nearest_truth_dist: Optional[int] = None  # bp to closest truth call of same type
    # Population SV catalogs (orthogonal to the truth set). A hit = a structurally
    # matching SV is already known in humans, which RAISES confidence that a
    # Truvari FP is a benchmark artifact (real, mis-matched) rather than a caller
    # error. Absence is NEUTRAL (catalogs are incomplete), never disconfirming.
    pop_catalog_hits: list[str] = []          # e.g. ["gnomAD-SV", "dbVar", "DGV"]
    pop_max_af: Optional[float] = None        # highest population allele frequency among matches
    image_path: Optional[str] = None

    def as_prompt_block(self) -> str:
        """Compact one-line-per-field summary handed to the model as text."""
        flags = [k for k, v in {
            "segdup": self.in_segdup,
            "low_mappability": self.in_low_mappability,
            "tandem_repeat": self.in_tandem_repeat,
            "homopolymer": self.in_homopolymer,
        }.items() if v] or ["none"]
        lines = [
            f"locus_id: {self.locus_id}",
            f"region: {self.chrom}:{self.start:,}-{self.end:,}",
            f"caller: {self.caller}",
            f"SVTYPE: {self.svtype}   SVLEN: {self.svlen}",
            f"truvari_label: {self.truvari_label}",
            f"caller_qual: {self.caller_qual}",
            f"region_flags: {', '.join(flags)}",
            f"repeatmasker: {self.repeatmasker_class or 'n/a'}",
            f"gene_overlap: {self.gene_overlap or 'n/a'}",
            f"nearest_truth_call_dist_bp: {self.nearest_truth_dist}",
        ]
        if self.pop_catalog_hits:
            af = f"{self.pop_max_af:.3f}" if self.pop_max_af is not None else "n/a"
            lines.append(
                f"population_known_sv: MATCH in {', '.join(self.pop_catalog_hits)} "
                f"(max_pop_AF={af}) -- corroborating evidence a real SV recurs here"
            )
        else:
            lines.append(
                "population_known_sv: none found "
                "(NEUTRAL -- catalogs are incomplete, absence is not disconfirming)"
            )
        return "\n".join(lines)


class SVVerdict(BaseModel):
    """Claude's structured review of a single discordant locus."""
    # extra="forbid" makes pydantic emit `additionalProperties: false`, which
    # the Messages API structured-output layer requires.
    model_config = ConfigDict(extra="forbid")

    classification: Classification
    confidence: float = Field(ge=0.0, le=1.0)
    primary_reason: str = Field(description="One phrase naming the dominant factor")
    evidence_used: list[EvidenceTag] = Field(
        description="Which signals the verdict actually relied on"
    )
    explanation: str = Field(
        description="2-4 sentences of scientific rationale grounded in the image and packet"
    )


class ReviewedLocus(BaseModel):
    """An evidence packet joined with Claude's verdict -- the report unit."""
    packet: EvidencePacket
    verdict: SVVerdict
