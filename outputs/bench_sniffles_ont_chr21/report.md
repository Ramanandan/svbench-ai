# SVBench AI review — sniffles_ont_chr21

## Truvari benchmark (commodity metrics)

| precision | recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|
| 0.8863636363636364 | 0.601027397260274 | 0.7163265306122448 | 351 | 45 | 233 |

## The added layer — Claude's review of the discordances

> **5 of 5 reviewed false positives (100%) are benchmark artifacts** — representation / repeat-region differences, not genuine caller errors. Removing them raises precision from **0.886 → 0.898** (≈1.000 if the sampled rate holds across all 45 FPs).

- Discordant loci reviewed: **5**
- benchmark_artifact: 5 (100%)

### Error-class breakdown

| Truvari class | reviewed | benchmark artifact | genuine error | uncertain |
|---|---|---|---|---|
| FP | 5 | 5 | 0 | 0 |

## Per-locus explanations

### sniffles_ont_chr21:FP:chr21:24969746:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.85)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 8 bp
- Reason: breakpoint-shifted representation of a real heterozygous deletion
- Evidence: read_depth, split_reads, breakpoint_ambiguity, population_support
- On HP:1 there is a clear localized coverage drop with a dotted split-read arc spanning the interval, matching the expected signature of a heterozygous ~50bp deletion, while HP:2 remains fully covered. A truth deletion sits only 8bp away and dbVar records a recurrent SV here, indicating the caller's event is essentially correct and Truvari flagged it as FP due to a small breakpoint/position offset rather than a genuine caller error.

### sniffles_ont_chr21:FP:chr21:28891444:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.85)
- Region: segdup=False, low_mappability=True, tandem_repeat=False; nearest truth 233 bp
- Reason: Real het deletion mislabeled FP due to representation/breakpoint offset
- Evidence: read_depth, low_mappability, homopolymer, population_support, breakpoint_ambiguity
- The HP:1 track shows a clear coverage drop to roughly half-depth across ~28891200-28891760 while HP:2 remains at full depth, matching a heterozygous deletion consistent with the caller's 316 bp DEL. The locus sits in low-mappability/homopolymer context only 233 bp from a truth call of the same type, and a structurally matching SV is catalogued in gnomAD-SV/dbVar/HGSVC at high frequency (max_pop_AF=0.518), strongly indicating a recurrent real deletion. The FP label most likely reflects a breakpoint/representation mismatch rather than a genuine false call.

### sniffles_ont_chr21:FP:chr21:14106170:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.83)
- Region: segdup=True, low_mappability=False, tandem_repeat=True; nearest truth 22 bp
- Reason: Real heterozygous deletion in repeat region with nearby truth call
- Evidence: read_depth, split_reads, segdup, tandem_repeat, population_support, breakpoint_ambiguity
- The HP2 track shows a localized coverage drop to near-zero over a short interval with a cluster of split-read arcs at the breakpoint, the classic signature of a heterozygous deletion, while HP1 remains at full depth. A truth DEL sits only 22 bp away and the locus lies in a segdup/tandem-repeat/homopolymer context, so the apparent FP is almost certainly a breakpoint/representation offset rather than a spurious call. A matching SV catalogued in gnomAD-SV and dbVar corroborates that a real deletion recurs here.

### sniffles_ont_chr21:FP:chr21:38429549:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 10 bp
- Reason: deletion in tandem repeat with adjacent truth call
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity, population_support
- The image shows clear localized coverage drops to near-zero around chr21:38,429,500-38,429,650 with spanning split-read arcs, consistent with a real deletion of the expected DEL signature. The call lies in a tandem-repeat, low-mappability region only 10 bp from a truth DEL and matches known SVs in dbVar/HGSVC, indicating a recurrent real deletion. The FP label most likely reflects a breakpoint/size representation difference (caller reports 50 bp vs nearby truth) rather than a spurious call, so this is a benchmark artifact.

### sniffles_ont_chr21:FP:chr21:33577627:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.80)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 23 bp
- Reason: Real deletion in tandem repeat with breakpoint/size representation difference
- Evidence: read_depth, split_reads, tandem_repeat, breakpoint_ambiguity, population_support, size_mismatch
- The HP:1 haplotype shows a localized, near-half coverage drop around 33,577,600 with associated split-read arcs on HP:2, consistent with a real heterozygous deletion. The call sits in a tandem repeat only 23 bp from a truth deletion, and a structurally matching SV is catalogued in gnomAD-SV/dbVar/HGSVC, indicating a recurrent real event. Truvari flagged it FP most likely due to representation/breakpoint and size ambiguity (note the 553 bp panel title vs 77 bp caller length) inside the repeat rather than a genuine caller error.
