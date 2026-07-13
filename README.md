# SVBench AI

**Every SV call gets a verdict.** The **Claude verdict layer** helping Structural Variant scientists separate real variants from artifacts — with or without a truth set.
Turns a benchmark's wall of disagreements into an auditable, human-in-the-loop review queue — with a reason for every call.

## The user

**Meet Maya, an SV-caller developer at a genome center.** Every release, she benchmarks her caller against the [GIAB](https://www.nist.gov/programs-projects/genome-bottle) HG002 truth set and gets back *hundreds* of FP/FN loci. Today she opens IGV and eyeballs them one by one, asking the same question each time: **"is my caller wrong, or is the benchmark wrong?"** That triage takes hours and lives only in her head.

SVBench AI is the tool she's missing. She points it at any GIAB-benchmarked VCF and gets a confidence-sorted review queue: each discordant locus shows the read-alignment image beside **Claude Opus 4.8**'s verdict — TP / FP / FN / **benchmark_artifact** — with the evidence it used and a plain-language reason. She accepts or overrides each call from the keyboard, and exports a curated decision set (JSON/CSV) back into her pipeline. She runs it next release without us in the room.

> Built for the *Built with Claude: Life Sciences* hackathon (Builder Track). Uses only public GIAB/UCSC data; makes no clinical or diagnostic claims; does not implement a new SV caller or annotation algorithm. Apache-2.0.

## Why this is not "just another benchmark"

Metrics (precision/recall/F1) are a commodity — and they *lie* in repetitive regions, where a caller and the truth set describe the same event with different breakpoints and get scored as a false positive. SVBench AI's contribution is the **reviewer**: for every FP/FN, Claude looks at the samplot alignment image plus genomic-context annotations and returns a structured verdict —

```json
{
  "classification": "benchmark_artifact",
  "confidence": 0.82,
  "primary_reason": "Breakpoint falls inside a VNTR; representation differs from truth",
  "evidence_used": ["tandem_repeat", "split_reads", "truvari_refine"],
  "explanation": "The caller reports a 240 bp deletion 60 bp upstream of the truth call. Both lie inside an (AT)n tandem repeat where breakpoint placement is ambiguous; the split-read support and depth drop match the truth event. This is a representation difference, not a false positive."
}
```

**The headline it produces** (real numbers, ONT Sniffles on chr21):

> **8 of 10 reviewed false positives (80%) are benchmark artifacts**, not genuine caller errors. Removing them raises precision **0.886 → 0.905** (≈0.975 if the rate holds across all 45 FPs).

Existing SV ML tools (samplot-ml, DeepSVFilter, CSV-Filter) are black-box CNN *filters*: a label, no rationale, deletions only. SVBench AI **explains**, handles all SV types, flags Truvari's own repeat-region false discordances (`benchmark_artifact`), and keeps a human in the loop.

## The apps (the product)

Three surfaces, one review model — pick by the moment:

**`svbench app` — the Streamlit run console** (the "front door" for a scientist):

```bash
pip install -e ".[app]"     # adds streamlit
svbench app                 # opens http://localhost:8501
```

Upload an HG002 GRCh38 caller VCF (or hit **▶ Run demo**) and watch the pipeline run — Truvari → annotate → samplot → **Claude Opus review** — with live per-stage progress and verdicts streaming in, then a one-click handoff to the review dashboard. The bundled demo runs on cached data for a reliable ~seconds-long first look; a real **live run** executes when the full stack + `ANTHROPIC_API_KEY` are present, and degrades gracefully to cached results otherwise.

**`svbench serve` — the live review app** (stdlib only, no dependencies, runs on localhost):

**`svbench serve` — the live app** (stdlib only, no dependencies, runs on localhost):

```bash
svbench serve outputs/bench_mycaller --caller mycaller   # opens http://localhost:8000
```

- Streams samplot images **from disk**, so it scales to thousands of loci (the static file would balloon to hundreds of MB — the live page is ~30 KB).
- Decisions persist to `decisions.json` **on disk** — survive a restart, feed back into the pipeline.
- **Re-review** any locus live (`↻`) — re-runs Claude on that one call and updates the card in place.
- JSON/CSV export served straight from the endpoint. Nothing is uploaded; localhost only.

**`dashboard.html` — the static fallback** (self-contained, zero setup): the same confidence-sorted queue, chips, accept/override, keyboard triage (`j`/`k`/`a`/`o`), and export — with images base64-embedded and decisions in `localStorage`. Ideal as the artifact a reviewer opens with no install.

Both share one layout: the samplot image sits **beside** Claude's verdict, region + evidence as chips, trio/Mendelian panels badged, a live progress counter, and **Accept Claude** / **override-to-class + note** controls.

## Pipeline

```
truth VCF + caller VCF ─► truvari bench+refine ─► fp/fn loci
                                                      │
                     ┌────────────────────────────────┤
                     ▼                                 ▼
        annotation (bedtools)              samplot image (PNG)
                     └───────────────┬─────────────────┘
                                     ▼
              Claude Opus 4.8 (multimodal) review agent
                                     ▼
     headline.json + report.md + confidence-sorted review dashboard
```

## Quick start

```bash
make setup                              # venv + brew tools (see Makefile)
svbench fetch                           # GIAB HG002 v5.0q truth + annotations + a sliced HiFi BAM
svbench run CALLER.vcf.gz --caller mycaller --chrom chr21   # bench + review + report, end to end
svbench serve outputs/bench_mycaller --caller mycaller      # live review app (or open dashboard.html)
```

Works on **any** GIAB-benchmarked VCF, from any caller — swap `CALLER.vcf.gz` and go. Individual stages (`bench`, `review`, `report`) and a truth-free `qc` mode are also exposed; run `svbench -h`.

## Prerequisites

The **cached demo and the dashboards need nothing** — open them and go. A **live run** (real Truvari → samplot → Claude on your VCF) needs the following. Run **`svbench doctor`** any time to see exactly what's present and what's missing:

```bash
svbench doctor        # ✅/❌ checklist of tools, data, and env + how to fix each
```

**1. Command-line tools** (`make setup` + `pip install -e ".[app]"`)

| Tool | For |
|---|---|
| `truvari`, `samplot` | benchmarking + alignment images (installed into the venv) |
| `bedtools` | region annotation |
| `bcftools`, `tabix`, `bgzip` | VCF sort / bgzip / index |
| `mafft` | *optional* — only for `truvari refine` |

> The tools live in `.venv/bin`; the CLI adds that to `PATH` automatically, so you don't need to `source .venv/bin/activate`.

**2. Reference data** (`svbench fetch` — one time, downloads to `data/`)

- Truth VCF `HG002_GRCh38_v5.0q_stvar.vcf.gz` (+ `.tbi`) and `.benchmark.bed` — **required**
- GIAB stratification BEDs + GENCODE GTF — annotations
- HG002 reads BAM (HiFi/ONT), sliced to the benchmark regions — for samplot
- Reference FASTA (`svbench fetch --reference`) — *optional*, only for `truvari refine`
- HG003/HG004 parent BAMs — *optional*, only for trio/Mendelian mode

**3. Environment & input**

- `export ANTHROPIC_API_KEY=sk-...` — the Claude review stage
- Input must be a **GRCh38 HG002** caller VCF (an SV caller's output) — **not** the truth VCF.

## Data (all GRCh38)

- Truth: GIAB **v5.0q** (Q100) `HG002_GRCh38_v5.0q_stvar.vcf.gz` + `.benchmark.bed`.
- Annotations: GIAB stratifications v3, UCSC repeats/segdups, GENCODE genes.
- Reads: HiFi/ONT BAM remote-sliced to the benchmark regions (<1 GB). Trio mode adds HG003/HG004 for Mendelian evidence.

See `svbench/config.py` for exact URLs and Truvari parameters.
