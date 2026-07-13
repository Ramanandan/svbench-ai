"""svbench doctor -- preflight check of tools, data, and environment.

Tells you exactly what's present and what's missing before a live run, so you
never sit through a stalled pipeline wondering what went wrong. The cached demo
needs none of this; these are the prerequisites for a *live* run.
"""
from __future__ import annotations

import os
import shutil
from pathlib import Path

from . import config
from .shell import _augmented_path


def _tool(name: str) -> bool:
    return shutil.which(name, path=_augmented_path()) is not None


def _exists(p) -> bool:
    return Path(p).exists()


def check() -> dict:
    """Structured readiness report (also used by the Streamlit sidebar)."""
    strat = {k: config.DATA_DIR / f"strat_{k}.bed.gz" for k in config.STRATIFICATION_BEDS}
    reads = list(config.DATA_DIR.glob("*.bam"))
    return {
        "tools_required": {t: _tool(t) for t in
                           ["truvari", "samplot", "samtools", "bedtools", "bcftools", "tabix", "bgzip"]},
        "tools_optional": {"mafft": _tool("mafft")},
        "data_required": {
            "truth VCF": _exists(config.TRUTH_VCF),
            "truth VCF index (.tbi)": _exists(str(config.TRUTH_VCF) + ".tbi"),
            "benchmark BED": _exists(config.BENCHMARK_BED),
        },
        "data_recommended": {
            **{f"stratification: {k}": _exists(p) for k, p in strat.items()},
            "GENCODE GTF": _exists(config.DATA_DIR / "gencode.annotation.gtf.gz"),
            "reads BAM present": bool(reads),
        },
        "data_optional": {
            "reference FASTA (for refine)": _exists(config.REFERENCE_FASTA),
        },
        "env": {"ANTHROPIC_API_KEY": bool(os.environ.get("ANTHROPIC_API_KEY"))},
    }


def _ok_required(c: dict) -> bool:
    return (all(c["tools_required"].values())
            and all(c["data_required"].values())
            and c["env"]["ANTHROPIC_API_KEY"])


_REMEDY = {
    "tools_required": "→ install: `make setup` (htslib/bedtools) + `pip install -e \".[app]\"`",
    "data_required": "→ download: `svbench fetch`",
    "data_recommended": "→ download: `svbench fetch` (annotations + reads)",
    "data_optional": "→ enable refine: `svbench fetch --reference` and install `mafft`",
    "env": "→ set: `export ANTHROPIC_API_KEY=sk-...`",
}


def report() -> int:
    """Print a human checklist. Returns 0 if all *required* items are present."""
    c = check()
    mark = {True: "✅", False: "❌"}
    sections = [
        ("Required CLI tools", "tools_required", "tools_required"),
        ("Optional CLI tools (refine only)", "tools_optional", "data_optional"),
        ("Required data  (svbench fetch)", "data_required", "data_required"),
        ("Recommended data (annotations + reads)", "data_recommended", "data_recommended"),
        ("Optional data (refine only)", "data_optional", "data_optional"),
        ("Environment", "env", "env"),
    ]
    print("SVBench AI — preflight (live-run prerequisites)\n")
    for title, key, remedy_key in sections:
        items = c[key]
        allok = all(items.values())
        print(f"{title}")
        for name, ok in items.items():
            optional = key.endswith("optional")
            m = mark[ok] if not (optional and not ok) else "➖"
            print(f"  {m} {name}")
        if not allok and not key.endswith("optional"):
            print(f"  {_REMEDY[remedy_key]}")
        print()

    ready = _ok_required(c)
    print("Cached demo / dashboard: ✅ always works (no prerequisites).")
    print(f"Live run readiness:      {'✅ ready' if ready else '❌ missing required items above'}")
    return 0 if ready else 1
