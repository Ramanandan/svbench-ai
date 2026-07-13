"""Central configuration: paths, data URLs, and verified tool parameters.

All coordinates are GRCh38. The #1 failure mode for this project is mixing a
GRCh37/hs37d5 caller VCF against the GRCh38 truth set, which silently destroys
recall -- so everything here is pinned to GRCh38 and the reference is explicit.
"""
from __future__ import annotations

import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Layout
# ---------------------------------------------------------------------------
# Project root = the directory containing the `svbench` package.
ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = Path(os.environ.get("SVBENCH_DATA", ROOT / "data"))
OUTPUT_DIR = Path(os.environ.get("SVBENCH_OUT", ROOT / "outputs"))

REFERENCE_FASTA = DATA_DIR / "GRCh38.fasta"  # needed by truvari (--pctseq) and CRAM decode

# GIAB v5.0q (Q100) truth set -- current canonical HG002 SV benchmark.
TRUTH_VCF = DATA_DIR / "HG002_GRCh38_v5.0q_stvar.vcf.gz"
BENCHMARK_BED = DATA_DIR / "HG002_GRCh38_v5.0q_stvar.benchmark.bed"

# A HiFi BAM sliced to the benchmark regions (built by `svbench fetch`).
SLICED_BAM = DATA_DIR / "HG002_hifi_svregions.bam"

# ---------------------------------------------------------------------------
# Remote data sources (GRCh38)
# ---------------------------------------------------------------------------
GIAB_V50Q_DIR = (
    "https://ftp.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/"
    "AshkenazimTrio/HG002_NA24385_son/v5.0q"
)
TRUTH_VCF_URL = f"{GIAB_V50Q_DIR}/HG002_GRCh38_v5.0q_stvar.vcf.gz"
TRUTH_TBI_URL = f"{TRUTH_VCF_URL}.tbi"
BENCHMARK_BED_URL = f"{GIAB_V50Q_DIR}/HG002_GRCh38_v5.0q_stvar.benchmark.bed"

# GRCh38 reference (GIAB analysis FASTA, matches the truth-set coordinates).
REFERENCE_FASTA_URL = (
    "https://ftp.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/references/"
    "GRCh38/GCA_000001405.15_GRCh38_no_alt_analysis_set.fasta.gz"
)

# HiFi alignment to slice for visualization. This is a large indexed BAM served
# over https; we never download it whole -- `samtools view -M -L bed <url>`
# streams only the benchmark-region reads. Confirm the exact current path with
# `svbench fetch --list-bams` before a run (GIAB reorganizes occasionally).
HIFI_BAM_URL = os.environ.get(
    "SVBENCH_HIFI_BAM_URL",
    "https://ftp.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio/"
    "HG002_NA24385_son/PacBio_CCS_15kb_20kb_chemistry2/GRCh38/"
    "HG002.SequelII.merged_15kb_20kb.pbmm2.GRCh38.haplotag.10x.bam",
)

# Trio / Mendelian evidence. For a child sample, the parents' aligned HiFi BAMs
# let us render a 3-sample samplot and check inheritance: a variant present in a
# parent is inherited => almost certainly real (independent of any truth set).
# This is the single strongest orthogonal validator in the SV field.
_ASHK = ("https://ftp.ncbi.nlm.nih.gov/ReferenceSamples/giab/data/AshkenazimTrio")
TRIOS = {
    "HG002": {
        "father": f"{_ASHK}/HG003_NA24149_father/PacBio_CCS_15kb_20kb_chemistry2/"
                  "GRCh38/HG003.SequelII.merged_15kb_20kb.pbmm2.GRCh38.haplotag.10x.bam",
        "mother": f"{_ASHK}/HG004_NA24143_mother/PacBio_CCS_15kb_20kb_chemistry2/"
                  "GRCh38/HG004.SequelII.merged_15kb_20kb.pbmm2.GRCh38.haplotag.10x.bam",
        "child_label": "HG002 (child)", "father_label": "HG003 (father)",
        "mother_label": "HG004 (mother)",
    },
    # HG005 (Chinese trio) parents exist as HiFi; exact GRCh38 BAM paths TBD.
}

# GIAB genome stratifications v3 (GRCh38) -- purpose-built for explaining
# benchmark discordance. Keyed by evidence-packet field name.
# NB: the reference dir is "GRCh38@all" -- '@' is URL-encoded as %40 over HTTP.
STRATIFICATION_BASE = (
    "https://ftp-trace.ncbi.nlm.nih.gov/ReferenceSamples/giab/release/"
    "genome-stratifications/v3.5/GRCh38%40all"
)
STRATIFICATION_BEDS = {
    "low_mappability": f"{STRATIFICATION_BASE}/Mappability/GRCh38_lowmappabilityall.bed.gz",
    "segdup": f"{STRATIFICATION_BASE}/SegmentalDuplications/GRCh38_segdups.bed.gz",
    "tandem_repeat": f"{STRATIFICATION_BASE}/LowComplexity/GRCh38_AllTandemRepeats.bed.gz",
    "homopolymer": f"{STRATIFICATION_BASE}/LowComplexity/GRCh38_AllHomopolymers_ge7bp_imperfectge11bp_slop5.bed.gz",
}
# GENCODE gene models for gene-overlap annotation.
GENCODE_GTF_URL = (
    "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/"
    "release_46/gencode.v46.annotation.gtf.gz"
)

# ---------------------------------------------------------------------------
# Population SV catalogs (GRCh38) -- orthogonal "is this a known SV?" evidence.
# ---------------------------------------------------------------------------
# All four are GRCh38-native (no liftover). `svbench fetch-catalogs` downloads
# each and normalizes it to  pop_<key>.bed.gz  with columns:
#     chrom  start  end  svtype  af  source  id      (af = -1 => presence-only)
# The feature is a NO-OP unless at least one of these files is present, so a run
# never depends on them. URLs can drift (NCBI/EBI reorganize) -- fetch-catalogs
# tolerates a failed source and logs it, exactly like the HiFi-BAM path.
POP_CATALOG_KEYS = ["gnomad", "dbvar", "dgv", "hgsvc"]
POP_CATALOG_LABELS = {
    "gnomad": "gnomAD-SV", "dbvar": "dbVar", "dgv": "DGV", "hgsvc": "HGSVC",
    "demo": "GIAB known SVs",
}

# Structural-match thresholds (see popfreq.py).
POP_MIN_RECIP_OVERLAP = 0.5   # DEL / DUP / INV reciprocal-overlap floor
POP_INS_MAX_DIST = 250        # bp; INS are point-ish, match by breakpoint proximity

# gnomAD-SV v4.1 joint sites VCF (GRCh38, carries AF). ~large; subset with --chrom.
GNOMAD_SV_URL = (
    "https://storage.googleapis.com/gcp-public-data--gnomad/release/4.1/"
    "genome_sv/gnomad.v4.1.sv.sites.vcf.gz"
)
# dbVar non-redundant variant REGIONS (GRCh38), all studies merged. Presence-only
# (SVTYPE; no population AF). Streamed by contig via tabix. NB: dbVar contigs are
# un-prefixed ('21', not 'chr21') -- the loader resolves that automatically.
DBVAR_SV_URL = (
    "https://ftp.ncbi.nlm.nih.gov/pub/dbVar/data/Homo_sapiens/by_assembly/"
    "GRCh38/vcf/GRCh38.variant_region.all.vcf.gz"
)
# DGV full variant table (GRCh38/hg38). Tab-delimited with a header; presence-only.
# NB: dgv.tcag.ca is frequently unreachable; this source skips gracefully if so.
DGV_VARIANTS_URL = (
    "http://dgv.tcag.ca/dgv/docs/GRCh38_hg38_variants_2020-02-25.txt"
)
# HGSVC3 long-read SV freeze (GRCh38) -- long-read panel, most comparable to ONT
# calls. Override with SVBENCH_HGSVC_URL if the release path moves.
HGSVC_SV_URL = os.environ.get(
    "SVBENCH_HGSVC_URL",
    "https://ftp.1000genomes.ebi.ac.uk/vol1/ftp/data_collections/HGSVC3/release/"
    "Variant_Calls/1.0/GRCh38/variants_GRCh38_sv_insdel_alt_HGSVC2024v1.0.vcf.gz",
)

# ---------------------------------------------------------------------------
# Truvari parameters (verified defaults for the v5.0q benchmark)
# ---------------------------------------------------------------------------
TRUVARI_BENCH_ARGS = [
    "--refdist", "500",
    "--pctseq", "0.7",
    "--pctsize", "0.7",
    "--sizemin", "50",
    "--passonly",
]
# `truvari refine` harmonizes repeat-region representations so we don't
# over-report tandem-repeat calls as FP/FN. Requires the reference FASTA.
RUN_TRUVARI_REFINE = True

# Scope is deliberately limited to the three well-benchmarked copy/sequence
# variant classes. INV and BND are excluded (sparse in the truth set, and their
# read signatures are far noisier to adjudicate reliably).
SV_TYPES = ["DEL", "INS", "DUP"]

# ---------------------------------------------------------------------------
# Claude / model config (verified against the claude-api skill, Opus 4.8)
# ---------------------------------------------------------------------------
MODEL = "claude-opus-4-8"
EFFORT = "high"          # output_config.effort
MAX_TOKENS = 4000
# NOTE: never pass `budget_tokens` or `temperature` on Opus 4.8 (both 400).


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
