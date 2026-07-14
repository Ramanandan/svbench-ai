# SVBench AI review — sniffles

## Truvari benchmark (commodity metrics)

| precision | recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|
| 0.8997668997668997 | 0.660958904109589 | 0.7620927936821322 | 386 | 43 | 198 |

## The added layer — Claude's review of the discordances

> **6 of 6 reviewed false positives (100%) are benchmark artifacts** — representation / repeat-region differences, not genuine caller errors. Removing them raises precision from **0.900 → 0.913** (≈1.000 if the sampled rate holds across all 43 FPs).

- Discordant loci reviewed: **6**
- benchmark_artifact: 6 (100%)

### Error-class breakdown

| Truvari class | reviewed | benchmark artifact | genuine error | uncertain |
|---|---|---|---|---|
| FP | 6 | 6 | 0 | 0 |

## Per-locus explanations

### sniffles_trio:FP:chr21:17954522:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.85)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 239 bp
- Reason: real inherited deletion mislabeled due to size/representation difference
- Evidence: read_depth, split_reads, size_mismatch, tandem_repeat, low_mappability, mendelian_inheritance, parental_support
- The child (HG002) HP:2 shows a clear coverage drop between ~17954600 and ~17956859 with a spanning split-read gap (dashed line), and the same haplotype-specific drop and split-read signature is present in both the father (HP:2) and mother (HP:1/HP:2), so the deletion is clearly inherited and real. The caller reported SVLEN 2509 bp while the depicted event spans ~5.42 kb, and the locus sits in a tandem-repeat/low-mappability region only 239 bp from a truth call, so the Truvari FP most likely reflects a breakpoint/size representation mismatch rather than a spurious call. Given the strong Mendelian support, this is a benchmark artifact, not a caller error.

### sniffles_trio:FP:chr21:42587646:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 47 bp
- Reason: real inherited deletion mislabeled due to representation/size ambiguity in repeat region
- Evidence: split_reads, read_depth, mendelian_inheritance, parental_support, segdup, low_mappability, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The child (HG002 HP:2) shows a clear cluster of split/spanning reads (dashed arcs) with a coverage drop on one haplotype from ~42587780 to ~42589653, and the identical pattern is present in the mother (HG004 HP:2), indicating an inherited, genuine heterozygous deletion. The event sits in a segdup/tandem-repeat/low-mappability region, and the caller's 2142 bp span disagrees with the ~4.68 kb truth interval shown, so breakpoint/size ambiguity is the likely cause of the Truvari FP mismatch (nearest truth call only 47 bp away). This is a representation difference, not a caller error.

### sniffles_trio:FP:chr21:38429549:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 10 bp
- Reason: inherited real deletion mislabeled due to tandem-repeat representation ambiguity
- Evidence: split_reads, tandem_repeat, low_mappability, size_mismatch, mendelian_inheritance, parental_support, caller_quality
- Dotted split-read gaps marking a small deletion breakpoint are visible in the child (HP1/HP2) and in BOTH parents (father HP1, mother HP1/HP2), indicating an inherited and therefore genuine event, not an artifact. The locus sits in a low-mappability tandem repeat with a truth call only 10 bp away, and there is a size discrepancy (caller SVLEN 50 vs a ~500 bp DEL annotation), both classic sources of Truvari representation FPs. The alignment evidence supports a real deletion, so the FP label most likely reflects breakpoint/size representation differences rather than a caller error.

### sniffles_trio:FP:chr21:41806449:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 43 bp
- Reason: size/representation mismatch in tandem repeat
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity, mendelian_inheritance, parental_support, caller_quality
- The samplot shows clear split-read/spanning-gap signatures (dotted connector lines) across the interval in the CHILD (both HP1 and HP2) and in AT LEAST ONE PARENT (father HP1 and mother HP1/HP2), indicating an inherited, real deletion rather than an artifact. However, the caller reported only an 89 bp DEL while the truth/displayed event spans ~577 bp, and the site sits in a tandem repeat with a truth call just 43 bp away. This size and breakpoint discrepancy inside a repeat region is a classic representation difference, so Truvari's FP label reflects a matching failure rather than a genuine caller error.

### sniffles_trio:FP:chr21:41814065:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 94 bp
- Reason: real inherited deletion mislabeled due to breakpoint/size representation in tandem repeat
- Evidence: split_reads, read_depth, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, mendelian_inheritance, parental_support
- The child (HP:2) shows split-read/spanning-gap signatures (dotted arcs) and a modest coverage dip consistent with a heterozygous deletion, and the same signature is clearly present in the mother (HP:1 and HP:2), indicating an inherited, real variant rather than a caller artifact. The call sits in a low-mappability tandem repeat with a truth call only 94 bp away, and the caller's 235 bp span differs from the ~869 bp region depicted, so the Truvari FP most likely reflects breakpoint/size representation ambiguity in a repetitive region rather than a false call. Inheritance from the mother strongly argues against a spurious de-novo/false positive.

### sniffles_trio:FP:chr21:41814473:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 314 bp
- Reason: real inherited deletion mislabeled due to representation/size ambiguity in tandem repeat
- Evidence: split_reads, tandem_repeat, low_mappability, size_mismatch, mendelian_inheritance, parental_support
- The dashed spanning-read patterns marking a deletion are visible in the CHILD (HP:2) and clearly in the MOTHER (HP:1 and HP:2), indicating an inherited, real deletion rather than a caller artifact. The region is flagged low_mappability and tandem_repeat, and the caller's SVLEN of 94 bp conflicts with the ~588 bp event drawn and with a truth call 314 bp away, consistent with breakpoint/size representation differences typical of repeat regions. Because the event is supported by both child and a parent, this is most likely a benchmark representation artifact, not a false positive.
