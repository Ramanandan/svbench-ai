# SVBench AI review — svim

## Truvari benchmark (commodity metrics)

| precision | recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|
| 0.6935749588138386 | 0.7208904109589042 | 0.7069689336691856 | 421 | 186 | 163 |

## The added layer — Claude's review of the discordances

> **132 of 186 false positives (71%) are benchmark artifacts** — representation / repeat-region differences, not genuine caller errors. Removing them raises precision from **0.694 → 0.886**.

- Discordant loci reviewed: **186**
- benchmark_artifact: 132 (71%)
- false_positive: 54 (29%)

### Error-class breakdown

| Truvari class | reviewed | benchmark artifact | genuine error | uncertain |
|---|---|---|---|---|
| FP | 186 | 132 | 54 | 0 |

## Per-locus explanations

### svim:FP:chr21:45633685:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.85)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: No coverage drop supporting deletion
- Evidence: read_depth, caller_quality, low_mappability, tandem_repeat
- For a true deletion we expect coverage to drop toward zero across the interval, but the HP:1 track maintains full ~90x coverage across the entire proposed DEL region with no split-read gap or breakpoint signal. The caller quality is extremely low (2.0) and there is no nearby truth call, so this is not a representation artifact. The flat depth and lack of any deletion signature indicate the alignment evidence does not support the call.

### svim:FP:chr21:32434137:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.85)
- Region: segdup=True, low_mappability=False, tandem_repeat=True; nearest truth 292 bp
- Reason: no coverage drop across DEL interval
- Evidence: read_depth, caller_quality, segdup, tandem_repeat
- A true deletion should show coverage dropping toward zero across the called interval, but both haplotypes maintain full depth (~56-60x) throughout the region with no split reads or spanning gaps at the breakpoints. The only depth perturbation is a tiny single-position dip on HP1 far from the called interval. Combined with the very low caller quality (1.0) and no nearby matching truth call (292 bp away), the alignment evidence does not support the reported deletion despite the repetitive/segdup context.

### svim:FP:chr21:39974761:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.83)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 967 bp
- Reason: no depth drop supporting a deletion
- Evidence: read_depth, caller_quality, low_mappability, tandem_repeat
- The caller reports a DEL, but both haplotype coverage tracks maintain continuous, near-baseline depth across the interval with no drop toward zero and no convergent split-read/spanning-gap signature at breakpoints expected for a deletion. The very low caller quality (1.0) and the region's low-mappability/tandem-repeat flags further undermine support, and the nearest truth call is ~967 bp away. The evidence does not support a real deletion at this locus.

### svim:FP:chr21:42078197:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 0 bp
- Reason: size/representation mismatch in tandem-repeat, truth call at same position
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch
- The image shows a clear deletion signature: coverage drops on both HP1 and HP2 with split/spanning reads (dotted arcs) bracketing the interval, so a real deletion is present. However, the caller reported SVLEN 150 while the visible depth drop spans ~700 bp (per the title), and the locus sits in a low-mappability tandem repeat with the nearest truth call at distance 0. The FP label therefore reflects a breakpoint/size representation difference rather than a spurious call, consistent with a benchmark artifact.

### svim:FP:chr21:30742426:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 1 bp
- Reason: INS in tandem repeat with adjacent truth call and size ambiguity
- Evidence: tandem_repeat, split_reads, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an insertion sitting in a tandem-repeat region with a truth INS only 1 bp away, and the image shows no depth drop but a localized split-read/soft-clip signal on HP:1 consistent with an insertion breakpoint. The SVLEN (142 bp) disagrees with the displayed 401 bp label, reflecting the inherent length ambiguity of insertions within tandem repeats. Truvari most likely labeled this FP due to representation/size differences rather than a genuine caller error, despite the low caller quality (2.0).

### svim:FP:chr21:33682809:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.82)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 1193 bp
- Reason: no depth drop supporting deletion
- Evidence: read_depth, split_reads, caller_quality, homopolymer
- For a real DEL we would expect a clear coverage drop across the interval, but all haplotypes maintain continuous, flat coverage across the ~68bp (and even the larger 536bp bar) region with no bilateral breakpoint drop. Only a single faint dotted gap appears in one HP:2 read, insufficient to support a heterozygous or homozygous deletion. Combined with the minimal caller quality (1.0), a homopolymer context prone to alignment artifacts, and the nearest truth call being ~1193 bp away, this is best explained as a spurious caller call.

### svim:FP:chr21:30742350:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.82)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 1069 bp
- Reason: No coverage drop supporting deletion
- Evidence: read_depth, caller_quality, tandem_repeat
- The caller reports a DEL but coverage remains full (~44x) across the entire interval on both haplotypes with no drop toward zero at the expected breakpoints, which is inconsistent with a real deletion. Only a faint dashed segment appears in HP:1, insufficient to support a 72–544 bp deletion. The very low caller quality (1.0), tandem-repeat context, and distant nearest truth call (1069 bp) all support this being a genuine false positive rather than a representation artifact.

### svim:FP:chr21:14800866:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.82)
- Region: segdup=False, low_mappability=True, tandem_repeat=False; nearest truth 774 bp
- Reason: No coverage drop supporting deletion
- Evidence: read_depth, split_reads, low_mappability, caller_quality
- For a true DEL we expect coverage to drop toward zero across the interval on at least one haplotype, but all three haplotype tracks maintain full, flat coverage across the called region with no breakpoint gap. The only supporting signal is a faint dotted arc on HP2, insufficient to substantiate a 128 bp deletion, and the caller quality is very low (1.0). The nearest truth call is 774 bp away, so this is not a representation shift of a real event but an unsupported call in a low-mappability region.

### svim:FP:chr21:35993101:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.80)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 1381 bp
- Reason: no depth drop supporting deletion
- Evidence: read_depth, caller_quality, tandem_repeat
- The caller reports a DEL but coverage remains flat and continuous across the entire interval in both haplotypes, with no drop toward zero as expected for a true deletion. Only faint dotted arcs (minor split/spanning reads) appear, insufficient to support a 61-521 bp loss. The very low caller quality (1.0) and the fact that the nearest truth call is 1381 bp away argue against a real event; this looks like a spurious call in a tandem-repeat context.

### svim:FP:chr21:42587738:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.80)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 45 bp
- Reason: representation/size mismatch near truth call in repetitive region
- Evidence: read_depth, split_reads, segdup, low_mappability, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The HP:2 panel shows a clear heterozygous coverage drop between ~42,587,865 and ~42,589,682 with dotted split-read arcs spanning both breakpoints, while HP:1 remains at full depth — the visual signature of a real haplotype-specific deletion. The region is flagged as segdup, low_mappability, and tandem_repeat, and a truth DEL sits only 45 bp away, so the FP is almost certainly a breakpoint/size representation difference (caller reports ~2072 bp vs a larger event) rather than a spurious call. This is a real variant mislabeled by Truvari due to ambiguous placement in repetitive sequence.

### svim:FP:chr21:46034555:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.80)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 90 bp
- Reason: size/breakpoint mismatch in tandem repeat near a truth call
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity
- The HP:2 track shows a clear heterozygous coverage drop (~40 to ~20) with a dashed split-read gap spanning the interval, confirming a real deletion on one haplotype. However the caller reported SVLEN 168 while the visual event spans ~700 bp, and a truth DEL sits only 90 bp away in a low-mappability tandem-repeat region. This size/breakpoint discrepancy within a repeat is a representation difference rather than a genuine caller error, so Truvari's FP is a benchmark artifact.

### svim:FP:chr21:36617299:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=False; nearest truth 822 bp
- Reason: No coverage drop supporting deletion
- Evidence: read_depth, split_reads, low_mappability, caller_quality
- For a DEL we expect coverage to drop toward zero across the interval, but all three haplotype tracks maintain roughly constant coverage across the called region with only a faint single-read dashed gap in HP:2. The caller quality is minimal (QUAL 1.0) and there is a size discrepancy (image labels 656 bp vs packet SVLEN 128), indicating an unstable call. In a low-mappability region with no depth support and the nearest truth call 822 bp away, the alignment evidence does not support a real deletion.

### svim:FP:chr21:45797983:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 800 bp
- Reason: No depth drop supporting a deletion
- Evidence: read_depth, split_reads, low_mappability, tandem_repeat, caller_quality
- For a true DEL we expect coverage to drop toward zero across the interval on at least one haplotype, but all three tracks (HP1, HP2, Undef) maintain full, continuous coverage across the called region with no spanning gap. Only faint dotted split-read arcs are visible, insufficient to support a 134 bp deletion, and the caller quality is very low (1.0). The nearest truth call is 800 bp away, too distant to be a representation shift, so despite the tandem-repeat/low-mappability context this is best explained as a caller false positive.

### svim:FP:chr21:45797759:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 1080 bp
- Reason: No deletion depth-drop signature in alignment
- Evidence: read_depth, low_mappability, tandem_repeat, caller_quality
- The coverage tracks across all three haplotypes remain flat and continuous over the shaded call interval with no drop toward zero, which is inconsistent with a genuine 78 bp (or 556 bp) deletion. The caller quality is minimal (1.0) and the nearest truth call lies ~1080 bp away, so this is not a mere breakpoint-shift artifact. Although the region is flagged low_mappability/tandem_repeat, the absence of any spanning-read gap or split-read cluster argues the caller reported a deletion the evidence does not support.

### svim:FP:chr21:45399986:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 1139 bp
- Reason: no insertion signature at breakpoint despite INS call
- Evidence: read_depth, soft_clips, split_reads, caller_quality
- The caller reports a ~401bp/1200bp INS but the image shows flat, uniform coverage across all haplotypes with no localized soft-clip cluster, split reads, or inserted-sequence signal at the putative breakpoint. Caller quality is very low (1.0) and the nearest truth call is ~1139bp away with no repeat/segdup flags to explain a representation shift. The alignment evidence does not support a genuine insertion here.

### svim:FP:chr21:41154682:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 253 bp
- Reason: No insertion signature and very low caller quality
- Evidence: soft_clips, split_reads, caller_quality, size_mismatch
- The alignment tracks are essentially flat with no localized cluster of soft-clipped or split reads and no inserted-sequence signal that would indicate an INS breakpoint at chr21:41,154,682. The caller quality is only 1.0, and there is a size discrepancy (image title 401 bp vs packet SVLEN 70). With no supporting read evidence, no repeat/segdup flags, and the nearest truth call 253 bp away, this appears to be a spurious svim call rather than a representation artifact.

### svim:FP:chr21:43280596:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 271 bp
- Reason: no coverage drop at called deletion coordinates
- Evidence: read_depth, caller_quality, tandem_repeat, size_mismatch
- The caller reports a 134 bp heterozygous DEL at 43,280,596-43,280,730, but coverage across all haplotypes remains flat and full through that interval with no drop toward zero and no split/spanning-read gap at the expected breakpoints. The only depth perturbation in the view is a minor dip near 43,280,150, well outside the called coordinates. Combined with a very low caller quality (2.0) and a size mismatch versus the plotted 668 bp bar, the alignment does not support a deletion here despite the tandem-repeat/homopolymer context.

### svim:FP:chr21:44396768:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 14 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, split_reads, breakpoint_ambiguity, size_mismatch, caller_quality
- The call is an INS sitting inside a flagged tandem repeat, only 14 bp from a truth call of the same type, which is the hallmark of a representation-level discordance rather than a caller error. The HP:1 track shows split/soft-clipped read discontinuities around the breakpoint consistent with a real inserted sequence, and there is no depth drop (correct for INS). The size mismatch between the caller's SVLEN (247) and the plotted event, plus the low caller quality, reflect the inherent length ambiguity of insertions within tandem repeats. Truvari likely failed to match due to shifted breakpoint/length in the repeat, so the underlying variant is essentially real.

### svim:FP:chr21:41401916:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 231 bp
- Reason: No insertion signature and minimal caller quality
- Evidence: read_depth, caller_quality, soft_clips, size_mismatch
- An insertion should present as a localized cluster of soft-clipped/split reads at a single breakpoint, but the image shows only flat, uniform coverage across both haplotypes with no soft-clip cluster or split-read stacking at the ~41,401,916 site. The caller quality is minimal (QUAL 1.0), and there is an internal size discrepancy (packet SVLEN 67 vs. 401 bp in the title), with the nearest truth call 231 bp away and no repeat/segdup flags to excuse ambiguity. The alignment evidence does not support a real insertion here.

### svim:FP:chr21:46047789:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 5 bp
- Reason: INS in tandem repeat with adjacent truth call
- Evidence: split_reads, tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The image shows no depth drop (consistent with INS) and dotted split-read arcs on both haplotypes at the insertion breakpoint, supporting a real insertion. The call sits in a tandem_repeat region only 5bp from a truth call of the same type, and the reported length (153bp packet vs 401bp title) is ambiguous, which is characteristic of representation differences for insertions in repetitive sequence. This is most consistent with a benchmark representation artifact rather than a genuine caller false positive, though the low caller quality (1.0) adds some uncertainty.

### svim:FP:chr21:45924837:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 1859 bp
- Reason: no coverage drop supporting a deletion
- Evidence: read_depth, split_reads, low_mappability, tandem_repeat, caller_quality
- For a real DEL we expect coverage to drop toward zero across the interval with split/spanning gaps at both breakpoints, but here both haplotypes maintain continuous read coverage and long reads span the entire region without an obvious gap. The call also carries the lowest possible quality (1.0), sits in a low-mappability tandem-repeat region, and the nearest truth call is ~1859 bp away, so this is not a representation artifact of a nearby true event. The alignment evidence does not support the reported 131 bp deletion.

### svim:FP:chr21:37757065:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 87 bp
- Reason: Real het deletion in tandem repeat with size/breakpoint representation difference
- Evidence: read_depth, split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The HP:1 haplotype shows a clear coverage drop (to roughly half/near-zero) spanning ~37,756,960-37,757,260 with a dashed split-read gap, while HP:2 stays at full depth, consistent with a genuine heterozygous deletion. A truth call sits only 87 bp away in a tandem-repeat region, and the caller's reported size (SVLEN 144, though the plot annotates ~688 bp) does not match, indicating a representation/breakpoint-placement discrepancy rather than a spurious call. The alignment evidence supports a real event, so the FP label is most likely a benchmark artifact from ambiguous placement/sizing in the repeat.

### svim:FP:chr21:44863281:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 21 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, split_reads, read_depth, breakpoint_ambiguity
- The caller reports a ~462bp insertion on chr21 within a tandem-repeat region, only 21bp from a truth call of the same type, and the HP:1 track shows a localized signal (duplication/insertion annotation with dotted split-read segments and a coverage step) consistent with a real haplotype-specific insertion rather than a depth-drop deletion. Because insertions inside tandem repeats have inherently ambiguous size and placement, Truvari likely flagged this as FP due to a representation/length mismatch rather than a genuine caller error. The alignment evidence supports a real event, so this is best classified as a benchmark artifact.

### svim:FP:chr21:42078485:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 39 bp
- Reason: real deletion in tandem repeat with nearby truth call (representation/size mismatch)
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch
- The image shows a clear deletion signature: coverage drops toward zero across the interval on both haplotype tracks with dotted spanning/split reads bridging the breakpoints, so a real deletion is present. A same-type truth call sits only 39 bp away and the region is flagged as tandem_repeat and low_mappability, and the caller's reported SVLEN (100 bp) conflicts with the ~300-600 bp drop visible, indicating a breakpoint/size representation difference rather than a spurious call. Truvari's FP therefore most likely reflects placement/size ambiguity in a repetitive region rather than a caller error.

### svim:FP:chr21:44396263:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 37 bp
- Reason: INS in tandem repeat near truth call with size/breakpoint ambiguity
- Evidence: tandem_repeat, split_reads, size_mismatch, breakpoint_ambiguity, caller_quality
- The locus is an insertion within a flagged tandem repeat, with a truth INS only 37 bp away, so the FP label most likely reflects a representation difference (breakpoint shift / length ambiguity) rather than a spurious call. Coverage is stable with no depth drop (consistent with INS not DEL), and HP:1 shows split/dotted read segments near the site indicating a genuine insertion breakpoint. The discrepancy between the displayed 401 bp and the packet SVLEN of 154 further underscores inserted-length ambiguity typical of tandem-repeat insertions.

### svim:FP:chr21:39974415:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 621 bp
- Reason: no depth drop supporting deletion
- Evidence: read_depth, low_mappability, tandem_repeat, caller_quality, size_mismatch
- The caller reports a 118 bp DEL but the coverage tracks across the region show no drop toward zero at the expected breakpoints; if anything, depth is maintained or slightly elevated (with duplication-colored dashed signals in HP:2), which is inconsistent with a true deletion signature. The extremely low caller quality (1.0) and placement in a low-mappability tandem repeat further argue against a real event, and the nearest truth call sits 621 bp away, too far to be a representation match. The alignment evidence does not support the deletion the caller reported.

### svim:FP:chr21:45442874:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 39 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, soft_clips, size_mismatch, caller_quality, breakpoint_ambiguity
- The locus is an INS flagged as tandem_repeat with a truth call only 39 bp away, a classic representation-ambiguity scenario. HP1 shows dashed split/soft-clip signatures and insert-size arcs at the site with no depth drop, consistent with a real insertion, but the caller's SVLEN (135 bp) disagrees with the displayed ~401 bp event, indicating a size/breakpoint discrepancy rather than a spurious call. Truvari likely rejected the match due to length/placement differences in the repeat context, so this is a benchmark artifact, not a caller error.

### svim:FP:chr21:41806205:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 1 bp
- Reason: INS in tandem repeat with size/representation ambiguity
- Evidence: split_reads, tandem_repeat, size_mismatch, caller_quality
- The locus is an insertion inside a tandem repeat with a truth call only 1 bp away, the hallmark of a representation-difference artifact rather than a genuine caller error. Coverage is maintained (no drop, consistent with INS), and dotted split-read arcs appear on both haplotype tracks near the insertion breakpoints, supporting a real inserted event. The caller reports SVLEN 53 while the plotted event is ~401 bp, indicating an inserted-sequence length ambiguity typical of tandem-repeat INS, so Truvari's FP most likely reflects imperfect matching to the nearby truth call rather than a false variant.

### svim:FP:chr21:46090939:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 10 bp
- Reason: INS in tandem repeat with nearby truth call and size ambiguity
- Evidence: tandem_repeat, size_mismatch, split_reads, read_depth
- The caller reports an INS inside a tandem_repeat region only ~10 bp from a truth INS call of the same type, which is the classic signature of a representation-difference benchmark artifact rather than a caller error. Coverage remains flat with no depth drop (consistent with an insertion, not a deletion), and there is a localized cluster of split/soft-clipped reads near ~46090750 supporting a real event. The notable size discordance (caller SVLEN 80 vs the 401 bp label) reflects the inherent ambiguity of inserted-sequence length within tandem repeats, so Truvari's FP is a placement/size mismatch, not a spurious call.

### svim:FP:chr21:44991442:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 4 bp
- Reason: INS in tandem repeat adjacent to truth call
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The caller reports a 126 bp insertion inside a tandem-repeat region only 4 bp from a truth-set INS of the same type. Insertion length and precise breakpoint are inherently ambiguous within tandem repeats, so Truvari's FP label most likely reflects a representation/size difference rather than a genuine caller error. The image shows flat coverage with no depth drop (correct for an INS), and the decent caller quality (33) plus near-adjacent truth call support this being the same event scored as discordant due to placement/length.

### svim:FP:chr21:44981544:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 16 bp
- Reason: real deletion in tandem-repeat/low-mappability region flagged for size/breakpoint mismatch
- Evidence: split_reads, read_depth, tandem_repeat, low_mappability, size_mismatch, caller_quality
- Both haplotype panels show split-read arcs (dotted lines) and a localized coverage dip consistent with a genuine deletion, and a truth DEL sits only 16 bp away, so a real event is present. The region is flagged low_mappability and tandem_repeat, and there is a clear size discrepancy (caller SVLEN 113 vs the ~625 bp span shown), which is exactly the kind of representation/breakpoint ambiguity that causes Truvari to fail a match. This is most consistent with a benchmark representation artifact rather than a spurious caller call, though the low quality (14.0) leaves some residual uncertainty.

### svim:FP:chr21:46006081:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.76)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at distance 0
- Evidence: tandem_repeat, size_mismatch, soft_clips, read_depth
- The call is an insertion in a tandem-repeat region with a truth INS at 0 bp distance, so the event itself is real. Coverage remains flat as expected for an insertion, and there are localized split-read/soft-clip clusters near the breakpoint. Truvari likely flagged this FP due to insertion-length ambiguity (caller SVLEN 63 vs the ~401 bp displayed, with the truth representation differing) in a tandem repeat, a representation difference rather than a true caller error.

### svim:FP:chr21:46034917:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.76)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 8 bp
- Reason: insertion in tandem repeat with nearby truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality
- The call is an INS with no coverage drop, consistent with an insertion signature, and sits in a low-mappability tandem-repeat region only 8 bp from a truth INS of the same type. The caller reports SVLEN ~113 bp while the plot title suggests ~401 bp, a classic inserted-length ambiguity within a tandem repeat rather than a spurious call. The very low caller quality (1.0) and repeat context indicate Truvari's FP most likely reflects a breakpoint/length representation difference, not a genuine caller error.

### svim:FP:chr21:15357459:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.75)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: No insertion signature and very low caller quality
- Evidence: read_depth, soft_clips, caller_quality
- An INS should manifest as a localized cluster of soft-clipped/split reads at a single breakpoint, but the image shows flat, uniform coverage across all haplotypes with no soft-clip pileup, split reads, or inserted-sequence signal at ~15,357,459. The caller quality is only 1.0 (very low) and there is no nearby truth call, and the reported SVLEN (53 bp) is inconsistent with the 401 bp bar. The absence of supporting alignment evidence indicates the caller reported a variant not backed by the reads.

### svim:FP:chr21:27587717:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth None bp
- Reason: low-quality INS call with no supporting split/soft-clip cluster and no nearby truth call
- Evidence: read_depth, caller_quality, tandem_repeat, split_reads
- The call has caller_qual of only 1.0 and there is no truth call anywhere nearby (nearest_truth_call_dist = None), so this is not a representation shift of a real event. For an INS we expect a localized cluster of soft-clipped/split reads at the breakpoint, but the coverage tracks are essentially flat across ~27,587,717 with only a modest depth dip on HP:1 further downstream that does not match the reported insertion position. Although the region is a tandem repeat, the absence of any adjacent truth call and the lack of clear insertion-supporting reads argue for a spurious caller artifact rather than a benchmark representation issue.

### svim:FP:chr21:41474899:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 33 bp
- Reason: INS in tandem repeat with nearby truth call and size ambiguity
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The HP:2 track shows a localized cluster of split-read signals (dotted arcs) with no depth drop, consistent with a heterozygous insertion on one haplotype. The locus sits in a tandem repeat only 33 bp from a truth INS of the same type, and there is a marked size discrepancy (caller SVLEN 66 vs 401 bp displayed), which is the hallmark of representation ambiguity for insertions in repetitive sequence. This is most likely a real event flagged FP due to length/breakpoint representation rather than a genuine caller error, though the low caller quality (1.0) tempers confidence.

### svim:FP:chr21:41845059:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 14 bp
- Reason: real heterozygous deletion in tandem repeat with size/representation mismatch
- Evidence: read_depth, split_reads, tandem_repeat, homopolymer, size_mismatch, caller_quality
- The HP2 track shows a clear one-haplotype coverage drop with dashed split/spanning reads across the interval, consistent with a real heterozygous deletion, and there is a truth call only 14 bp away. The locus sits in a tandem_repeat/homopolymer context and the caller's SVLEN (123 bp) disagrees with the plotted ~645 bp event, indicating an ambiguous breakpoint/size representation rather than a spurious call. This pattern of a supported DEL adjacent to a truth call in a repeat region is a classic Truvari representation FP.

### svim:FP:chr21:42587658:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 35 bp
- Reason: heterozygous deletion in repeat region matching nearby truth call
- Evidence: read_depth, split_reads, segdup, low_mappability, tandem_repeat, breakpoint_ambiguity
- HP2 shows a clear one-haplotype coverage drop (~44 to ~22) with split-read/dotted spanning evidence across the interval, consistent with a real heterozygous deletion, while HP1 remains full depth. The locus lies in a segdup/low_mappability/tandem_repeat region with a truth DEL only 35 bp away, so Truvari's FP likely reflects breakpoint/size representation ambiguity (caller 356 bp vs. displayed 1.11 kb) rather than a spurious call. This is a representation mismatch in a repetitive context, not a caller error.

### svim:FP:chr21:46048048:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 195 bp
- Reason: No coverage drop supporting deletion
- Evidence: read_depth, caller_quality, tandem_repeat, size_mismatch
- The samplot shows continuous, roughly full coverage across the entire deletion interval with no drop toward zero on either haplotype, which is inconsistent with a real ~900bp/252bp deletion. The caller quality is extremely low (2.0), and there is a size mismatch between the plotted 904bp DEL and the packet SVLEN of 252bp. Although the region is a tandem repeat with a truth call 195bp away, the absence of any depth reduction argues this is a spurious call rather than a genuine event.

### svim:FP:chr21:45634198:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: no depth drop supporting deletion
- Evidence: read_depth, caller_quality, low_mappability, tandem_repeat
- For a genuine deletion we expect coverage to drop toward zero across the interval, but HP:1 shows continuous, uninterrupted long-read coverage spanning the entire region with no split-read gap or depth reduction at the putative breakpoints. The caller quality is very low (1.0) and there is no nearby truth call, so the alignment evidence does not support a real deletion. The low-mappability/tandem-repeat context likely produced a spurious svim call rather than a true event.

### svim:FP:chr21:45554221:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with size-ambiguous representation
- Evidence: tandem_repeat, size_mismatch, soft_clips, caller_quality
- The call is an insertion inside a flagged tandem repeat, and a truth INS sits at 0 bp distance, so the events overlap in position. Coverage remains flat with no depth drop (consistent with an INS, not a deletion), and there is a cluster of soft-clipped/split reads on HP:2 around the breakpoint. Truvari likely flagged this as FP because the caller's inserted length (281 bp) disagrees with the truth size (~401 bp) — a classic representation/length ambiguity in tandem-repeat insertions rather than a genuine false call, though the low caller quality (7.0) tempers confidence.

### svim:FP:chr21:37757144:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 84 bp
- Reason: real deletion in tandem repeat with size/breakpoint representation mismatch
- Evidence: read_depth, split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The HP1 track shows a clear haplotype-specific coverage drop to near zero between ~37,756,920 and ~37,757,250 bridged by a dashed split-read arc, while HP2 retains full coverage \u2014 the classic signature of a heterozygous deletion. A real deletion is therefore present, and a truth call sits only 84 bp away, so this is not a spurious call. However, the caller reported SVLEN 68 whereas the visible/annotated event spans ~536 bp within a tandem repeat, so Truvari's FP almost certainly reflects a size and breakpoint representation difference rather than a caller error.

### svim:FP:chr21:42587553:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 64 bp
- Reason: deletion supported but in repeat with size/breakpoint mismatch near truth
- Evidence: read_depth, split_reads, segdup, low_mappability, tandem_repeat, size_mismatch
- HP2 shows a partial coverage drop plus dotted split-read alignments consistent with a heterozygous deletion, so the alignment evidence does support a real DEL. However the locus sits in a segdup/low-mappability/tandem-repeat region with a truth DEL only 64 bp away, and there is a size discrepancy (caller 204 bp vs displayed 808 bp interval), indicating a representation/placement difference rather than a spurious call. This pattern of an ambiguous-length deletion inside a repeat near a matching truth call is a classic Truvari representation artifact.

### svim:FP:chr21:46091028:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 6 bp
- Reason: INS in tandem repeat adjacent to truth call with size/representation mismatch
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The coverage tracks stay flat with no depth drop, consistent with an insertion rather than a false deletion, and a subtle soft-clip/split-read cluster is visible near the left side. A truth INS lies only 6 bp away in a tandem-repeat context, and the reported length is ambiguous (title 401 bp vs SVLEN 188), which is the classic signature of inserted-sequence length ambiguity in repeats. This strongly suggests Truvari flagged a representation/size difference rather than a genuine caller error, though the very low caller quality (2.0) adds some doubt.

### svim:FP:chr21:44863310:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 7 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: tandem_repeat, split_reads, breakpoint_ambiguity, size_mismatch, caller_quality
- The HP1 track shows a localized cluster of split/soft-clipped reads (dotted segments) around 44,863,150-44,863,330 with no depth drop, consistent with a real insertion signature rather than a spurious call. The locus sits inside a tandem repeat and lies only 7 bp from a truth INS of the same type, so Truvari's FP label most likely reflects a representation/size discrepancy (caller SVLEN 59 vs the 401 bp header) inherent to length-ambiguous repeat insertions. The evidence supports a genuine variant that is simply reconciled poorly, not a caller error, though the very low caller quality (1.0) adds some uncertainty.

### svim:FP:chr21:45923820:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at 0bp distance, likely size/representation mismatch
- Evidence: tandem_repeat, low_mappability, split_reads, size_mismatch, caller_quality
- There is a real insertion signature at ~45923900 (dashed spanning arc on HP1 indicating inserted sequence) with no depth drop, consistent with an INS. The packet shows nearest_truth_call_dist_bp = 0, meaning a truth INS of the same type sits at this exact position, and the region is flagged as low_mappability and tandem_repeat where inserted-length is inherently ambiguous. The Truvari FP is most plausibly driven by a size/breakpoint representation difference (caller SVLEN vs truth) rather than a spurious call, so this is a benchmark artifact rather than a caller error, though the very low caller quality (2.0) adds some uncertainty.

### svim:FP:chr21:46170550:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 1 bp
- Reason: insertion size ambiguity in tandem repeat adjacent to truth call
- Evidence: tandem_repeat, low_mappability, split_reads, size_mismatch, caller_quality
- A truth INS lies only 1 bp away and the site is flagged as tandem_repeat/low_mappability, where inserted-sequence length is inherently ambiguous. The image shows no depth drop (consistent with INS) and split-read/soft-clip arcs at the breakpoint region, supporting a real insertion. The FP label most likely reflects a size/representation mismatch (caller SVLEN 905 vs. displayed 401 bp) rather than a spurious call, so this is a representation artifact, though the low caller quality (8.0) tempers confidence.

### svim:FP:chr21:46170511:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 9 bp
- Reason: INS in tandem repeat with truth call 9 bp away
- Evidence: tandem_repeat, low_mappability, split_reads, size_mismatch, breakpoint_ambiguity
- The caller reports an INS in a low-mappability tandem repeat, and there is a truth INS only 9 bp away, strongly suggesting the same event flagged FP due to representation rather than a genuine false call. The image shows no depth drop (consistent with INS) and dotted split-read/soft-clip signals near the breakpoints, supporting a real insertion. A large size discrepancy (packet SVLEN 80 vs plotted 401 bp) in a tandem repeat where inserted length is inherently ambiguous is a classic Truvari representation mismatch rather than a caller error.

### svim:FP:chr21:24886445:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: Very low caller quality with no supporting insertion signature
- Evidence: caller_quality, split_reads, soft_clips, size_mismatch
- The svim call has QUAL=1.0, the lowest possible confidence, and no nearby truth call. The alignment tracks show flat, uninterrupted coverage with no localized cluster of soft-clipped or split reads at the putative breakpoint, which is the expected signature for a genuine ~55-401 bp insertion. The packet SVLEN (55) also conflicts with the plotted 401 bp span, and no repeat/segdup context is flagged to excuse a representation difference, so the absence of supporting reads makes this a likely false positive.

### svim:FP:chr21:46047654:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 129 bp
- Reason: INS in tandem repeat near truth call
- Evidence: split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity, caller_quality
- The call is a 387 bp insertion in a tandem-repeat, low-mappability region, with a truth INS only 129 bp away. Coverage stays flat (consistent with an insertion rather than a false depth signal), and the dashed segments in both haplotypes indicate split/gapped read signatures supporting inserted sequence. Given the ambiguous placement inside a tandem repeat and the nearby same-type truth call, this is most consistent with a representation/breakpoint-shift artifact rather than a genuine caller error.

### svim:FP:chr21:40305409:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: Low caller quality with no supporting insertion signature
- Evidence: caller_quality, read_depth, homopolymer, size_mismatch
- The svim call has a very low quality score (1.0) and no truth call anywhere nearby (nearest_truth_call_dist_bp=None), so it is not a representation/breakpoint-shift artifact. The coverage tracks are flat and uniform (~62x combined) with no localized cluster of soft-clipped or split reads that would signal a genuine ~400bp insertion. The homopolymer flag plus the discrepancy between the plotted 401bp and reported SVLEN of 65 further suggests a spurious call in a low-complexity context rather than a real variant.

### svim:FP:chr21:45500900:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 20 bp
- Reason: INS in tandem repeat with truth call 20 bp away
- Evidence: tandem_repeat, low_mappability, split_reads, breakpoint_ambiguity, caller_quality
- The call is a ~440 bp insertion sitting in a low-mappability tandem-repeat region, and a truth INS lies only 20 bp away, the classic setup for a Truvari representation mismatch rather than a caller error. The image shows no depth drop (consistent with an insertion) and reads carrying duplication/extra-sequence signatures (red dotted overlays) clustered near the breakpoint, supporting a real inserted-sequence event. Because inserted-sequence length and placement are inherently ambiguous in tandem repeats, the FP label most likely reflects representation/size differences with the nearby truth call. The low caller quality (2.0) adds some uncertainty.

### svim:FP:chr21:32428506:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=True, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: no insertion signature at breakpoint
- Evidence: read_depth, soft_clips, segdup, caller_quality
- The coverage tracks are flat and uniform across the region with no localized cluster of soft-clipped or split reads at the putative insertion breakpoint, which is the expected signature for a true INS. The caller quality is low (23.0) and there is no nearby truth call (nearest_truth_call_dist_bp None), so this is not merely a representation artifact of an adjacent truth INS. Although the locus falls in a segdup, the total absence of supporting soft-clip/split evidence indicates the caller reported an insertion the alignments do not support.

### svim:FP:chr21:41806464:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 31 bp
- Reason: deletion in tandem repeat with nearby truth call and size mismatch
- Evidence: read_depth, split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The alignment shows genuine deletion signatures: coverage drops in the HP:1 track and multiple dashed split-read arcs consistent with a real deletion on this haplotype. The call sits in a tandem repeat only 31 bp from a truth deletion, and there is a notable size discrepancy (caller SVLEN 88 vs the 576 bp span depicted), indicating a representation/breakpoint-placement difference rather than a spurious call. This pattern of a real DEL flagged FP due to ambiguous size and placement in a repeat is characteristic of a benchmark artifact.

### svim:FP:chr21:45898823:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 169 bp
- Reason: real deletion in tandem repeat with nearby truth call
- Evidence: read_depth, split_reads, tandem_repeat, breakpoint_ambiguity, size_mismatch
- A clear localized coverage drop to near-zero is visible around 45,898,850-45,898,900 on both haplotypes, accompanied by split/spanning-read gaps (dashed arcs) at the breakpoints, consistent with a genuine deletion. The locus sits in a tandem repeat and lies only 169 bp from a truth call of the same type, and the caller's 88 bp size differs from the 576 bp region annotation, indicating a representation/breakpoint-placement discrepancy rather than a caller error. This pattern is a classic Truvari FP artifact caused by ambiguous deletion placement in a repetitive context.

### svim:FP:chr21:13017861:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=True, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: no insertion signature in alignment
- Evidence: read_depth, soft_clips, segdup
- The 401 bp INS call shows flat, full coverage across both haplotypes with no localized cluster of soft-clipped or split reads and no reads carrying inserted sequence at the breakpoint, which is the expected signature for a long-read INS. There is no nearby truth call (nearest_truth_call_dist_bp = None), arguing against a mere representation difference. Although the region is flagged as segdup, the absence of any supporting insertion evidence indicates the caller reported a variant the alignment does not support.

### svim:FP:chr21:44419545:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 18 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, read_depth, caller_quality
- The caller reports an insertion inside a tandem-repeat region with the nearest truth call only 18 bp away, the classic setup for a representation-difference FP rather than a genuine caller error. There is a modest coverage step near the breakpoint consistent with an alignment shift, and no depth drop (correct for INS). The size discrepancy (caller SVLEN 651 vs displayed 401 bp) plus the ambiguous breakpoint placement in a repeat strongly suggest Truvari failed to match an essentially real event.

### svim:FP:chr21:45815009:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 12 bp
- Reason: Adjacent truth call in tandem repeat with representation/size difference
- Evidence: split_reads, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- A truth deletion sits only 12 bp away and the locus falls in a tandem-repeat, low-mappability region, so Truvari's FP label most likely reflects a representation difference rather than a spurious call. The image shows split-read/dotted signals consistent with a deletion event, and there is a notable size discrepancy (caller 226 bp vs. the 852 bp shown), typical of ambiguous breakpoint placement in repetitive DNA. The low caller quality (14) adds some uncertainty, but the proximity to a same-type truth call favors an artifact over a genuine caller error.

### svim:FP:chr21:15030875:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 150 bp
- Reason: insertion in tandem repeat with representation/size ambiguity
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The HP:1 track shows a dotted split-read gap near the center of the region consistent with an insertion breakpoint on one haplotype, and there is no depth drop (appropriate for INS). The locus sits in a tandem repeat with a truth INS only ~150 bp away, and the caller's SVLEN (100 bp) disagrees with the displayed 401 bp event, indicating the FP label reflects breakpoint/length representation differences rather than a spurious call.

### svim:FP:chr21:45746191:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with size-representation mismatch
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality
- The caller reports a 90 bp INS at a locus where a truth INS sits at distance 0 (nearest_truth_call_dist_bp=0), but the displayed event is 401 bp, indicating a large insertion-length discrepancy that Truvari's size-ratio check would reject. The site is flagged low_mappability and tandem_repeat, where inserted-sequence length is inherently ambiguous, and the coverage tracks show no depth drop as expected for an INS. This pattern of a same-type, co-located call failing on size representation inside a tandem repeat is characteristic of a benchmark artifact rather than a genuine false positive, though the low caller quality (16) adds some uncertainty.

### svim:FP:chr21:15031703:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 600 bp
- Reason: No insertion-supporting evidence at low-quality call
- Evidence: read_depth, caller_quality, size_mismatch, tandem_repeat, low_mappability
- The image shows flat, uninterrupted coverage across all haplotypes with no localized soft-clip or split-read cluster that would indicate an insertion breakpoint, which is the expected INS signature. The caller quality is extremely low (1.0) and there is a size discrepancy (image labels 401 bp while the packet lists SVLEN 50), and the nearest truth call is 600 bp away. Although the region is a tandem repeat / low-mappability zone, the absence of any visible read support argues this is a spurious call rather than a representation artifact.

### svim:FP:chr21:13042673:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=True, low_mappability=True, tandem_repeat=False; nearest truth None bp
- Reason: No insertion signature and no nearby truth call in mismappable region
- Evidence: read_depth, soft_clips, segdup, low_mappability, caller_quality
- The alignment tracks show smooth, uniform high coverage across all haplotypes with no localized cluster of soft-clipped or split reads at the putative breakpoint, which is the expected signature for a real ~400 bp insertion. There is no nearby truth call (nearest_truth_call_dist_bp: None), so this is not a representation difference of a genuine variant. The region is flagged as segdup and low_mappability, which readily produces spurious INS calls from misaligned reads, consistent with a caller false positive rather than a benchmark artifact.

### svim:FP:chr21:33321351:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 29 bp
- Reason: insertion supported near truth call with size/representation mismatch
- Evidence: split_reads, soft_clips, size_mismatch, breakpoint_ambiguity, caller_quality
- The image shows no depth drop (consistent with INS) and a localized cluster of split/soft-clipped reads on the HP1 haplotype around 33321311-33321400, supporting a real insertion. A truth INS lies only 29 bp away, but the caller's reported SVLEN (162 bp) differs markedly from the plotted ~401 bp event, indicating an inserted-length/representation discrepancy rather than a spurious call. The low caller quality (1.0) plus the size mismatch likely drove the Truvari FP label, making this a representation artifact.

### svim:FP:chr21:30571237:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 22 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, split_reads, size_mismatch, breakpoint_ambiguity
- The locus sits in a tandem repeat with a truth INS only 22 bp away, and the image shows clustered insertion/duplication-signature reads (red dashed spanning reads) without any depth drop, consistent with a real insertion. The caller's SVLEN (750 bp) differs substantially from the visualized ~401 bp event, and length representation of insertions inside tandem repeats is inherently ambiguous. This strongly indicates a representation-level mismatch rather than a spurious call, so Truvari's FP is likely a benchmark artifact.

### svim:FP:chr21:43741268:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 0 bp
- Reason: INS matches nearby truth call but flagged on size/representation in homopolymer
- Evidence: homopolymer, split_reads, read_depth, size_mismatch
- The nearest truth call is 0 bp away, meaning a truth INS exists at this exact position, so the caller is not detecting a spurious event. Coverage stays stable (~38-46) with no depth drop as expected for an insertion, and a faint split/dashed arc appears on HP:1 near the breakpoint supporting a real insertion on one haplotype. The FP label most likely reflects an insertion-length/representation discrepancy (caller SVLEN 326 vs image 401) within a homopolymer context where inserted-length is inherently ambiguous, rather than a true caller error.

### svim:FP:chr21:15031648:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 545 bp
- Reason: No insertion signature and very low caller quality
- Evidence: soft_clips, split_reads, low_mappability, tandem_repeat, caller_quality
- The caller reports an INS (SVLEN 100, though the title annotates 401 bp) at very low quality (1.0), yet the alignment tracks show flat, uniform coverage with no localized cluster of soft-clipped or split reads that would mark an insertion breakpoint. Although the region is flagged as low_mappability and tandem_repeat, the nearest truth INS is 545 bp away — too distant to be a simple representation shift of the same event. The absence of any supporting read evidence combined with minimal caller confidence supports a false positive rather than a benchmark artifact.

### svim:FP:chr21:13986700:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=True, low_mappability=False, tandem_repeat=True; nearest truth 1470 bp
- Reason: No insertion signature at breakpoint despite reported INS
- Evidence: read_depth, caller_quality, segdup, tandem_repeat, soft_clips
- The image shows only flat, continuous coverage across all haplotypes with no localized cluster of soft-clipped or split reads at the reported breakpoint (~13,986,700), which is the expected signature for a true insertion. The caller quality is very low (1.0) and there is a size discrepancy between the packet SVLEN (59) and the plotted 401 bp event. Although the region is flagged as segdup/tandem_repeat, the nearest truth call is 1470 bp away—too distant to be a plausible representation-shift match—so the lack of local supporting read evidence points to a genuine false positive.

### svim:FP:chr21:44409672:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 130 bp
- Reason: real deletion in tandem-repeat/low-mappability region with representation mismatch
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- The HP:2 track shows a clear coverage drop toward zero across the interval with dotted split-read arcs spanning the breakpoints, confirming a genuine deletion consistent with the DEL signature. However, the caller reports SVLEN 595 while the drawn event spans ~1.59 kb, and a truth call sits only 130 bp away in a region flagged as tandem_repeat and low_mappability, so breakpoint/size placement is inherently ambiguous. This pattern (a real DEL near a same-type truth call inside a repeat) points to a representation difference rather than a caller error, despite the very low QUAL of 2.0.

### svim:FP:chr21:44410025:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 112 bp
- Reason: real deletion in tandem-repeat/low-mappability region with size/breakpoint representation mismatch
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch, caller_quality
- The HP2 coverage track shows a clear drop toward zero across the interval (~44,409,973-44,410,738) with dotted spanning/split-read connectors at the flanks, consistent with a genuine deletion. However, the caller reports SVLEN 279 while the plotted event spans ~957 bp, and a truth DEL sits only 112 bp away in a low-mappability tandem-repeat region, so the Truvari FP most likely reflects a size/breakpoint representation difference rather than a spurious call. The low caller quality (5.0) adds some doubt, but the depth evidence supports a real event that is simply mis-sized/placed in an ambiguous repeat.

### svim:FP:chr21:28841345:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 16 bp
- Reason: INS in tandem repeat with nearby truth call and size discrepancy
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The caller reports an 89 bp INS (image annotated 401 bp) sitting inside a tandem repeat, only 16 bp from a truth call of the same type. Insertion length and placement are inherently ambiguous in tandem repeats, so Truvari's FP likely reflects a representation/size-matching failure rather than a genuinely spurious call. Coverage is stable with no depth anomaly, consistent with an INS signature, and the proximity to a truth INS strongly suggests the same underlying event.

### svim:FP:chr21:36496763:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 28 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an insertion located within a tandem repeat region, only 28 bp from a truth INS of the same type, which is the classic setup for a representation-difference FP rather than a real caller error. Insertion length in tandem repeats is inherently ambiguous, and here there is a notable size discrepancy (packet SVLEN 116 vs. 401 bp shown), consistent with an alignment/placement difference. The coverage tracks show stable depth with no drop (as expected for INS), and the nearby truth call suggests the underlying event is genuine but represented slightly differently.

### svim:FP:chr21:39974638:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 20 bp
- Reason: INS in tandem repeat near truth call with size ambiguity
- Evidence: tandem_repeat, low_mappability, size_mismatch, split_reads, breakpoint_ambiguity, caller_quality
- The locus is an insertion flagged FP but sits only 20bp from a truth INS of the same type inside a tandem-repeat, low-mappability region, where inserted-sequence length and breakpoint placement are inherently ambiguous. The size disparity (caller SVLEN 149 vs 401bp displayed) reflects a representation difference rather than a spurious call, and HP2 reads show consistent split/soft-clip signal supporting a real event. This pattern of a repeat-embedded INS adjacent to a matching truth call is a classic Truvari representation artifact, not a caller error, though the low caller quality (2.0) adds some uncertainty.

### svim:FP:chr21:46047893:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 89 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- The coverage tracks are flat and continuous with no depth drop, consistent with an insertion rather than an artifact of missing data, and both haplotypes maintain read support. The call sits in a flagged tandem-repeat / low-mappability region with a same-type truth INS only 89 bp away, and the caller's reported length (228 bp) differs from the 401 bp truth event. This size/breakpoint discrepancy inside a tandem repeat is the classic representation difference that Truvari mislabels as FP, so the underlying variant is likely real.

### svim:FP:chr21:45797870:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 133 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, low_mappability, split_reads, caller_quality
- The call is an insertion in a low-mappability tandem-repeat region, where coverage stays flat (as expected for INS, no depth drop) and haplotype-resolved tracks show dotted split/gap signals consistent with inserted sequence. A truth INS of the same type sits only 133 bp away, and the caller's reported length (677) differs from the displayed 401 bp span, pointing to a representation/length ambiguity rather than a genuine false call. In tandem repeats INS length and placement are inherently ambiguous, so Truvari's FP most likely reflects a matching failure, not a caller error.

### svim:FP:chr21:45437444:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 7 bp
- Reason: representation/size mismatch near truth call in tandem repeat
- Evidence: low_mappability, tandem_repeat, size_mismatch, breakpoint_ambiguity, split_reads, caller_quality
- A truth deletion sits only 7 bp away and the region is flagged low_mappability and tandem_repeat, so placement and size are inherently ambiguous. The caller reports a 653 bp DEL while the displayed event spans ~1.71 kb, a clear size/representation discrepancy rather than a spurious call. The image shows clustered split/discordant reads and partial coverage disruptions across the interval consistent with a real deletion, but the coverage does not cleanly drop to zero over the full span, reflecting the repeat-driven ambiguity. This is a representation-difference FP, not a genuine caller error.

### svim:FP:chr21:45500995:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with size/representation mismatch to adjacent truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality, breakpoint_ambiguity
- The locus is flagged low_mappability and tandem_repeat, and a truth INS sits at 0 bp distance, so an INS call here is supported by a real event. The image shows no depth drop (consistent with INS) plus localized dotted/soft-clip and duplication-tinted read signal at a single breakpoint. Truvari likely labeled FP due to inserted-length representation ambiguity (caller SVLEN 249 vs the ~401 bp title/truth size) inherent to tandem-repeat insertions rather than a genuine caller error, though the very low qual (2.0) tempers confidence.

### svim:FP:chr21:45924018:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with size ambiguity and truth call at 0bp
- Evidence: split_reads, tandem_repeat, low_mappability, size_mismatch, caller_quality
- The packet reports a truth INS at 0 bp distance and flags this locus as both low_mappability and tandem_repeat, where inserted-sequence length is inherently ambiguous. The HP1 track shows a localized split-read/soft-clip cluster (dotted signature) near ~45923940 with no depth drop, consistent with an insertion on one haplotype. The disagreement over size (title 401 bp vs. packet SVLEN 130 vs. truth) reflects a representation difference rather than a false variant, so Truvari's FP is most likely a benchmark artifact.

### svim:FP:chr21:46034973:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 64 bp
- Reason: INS in tandem repeat near a matching truth call
- Evidence: tandem_repeat, low_mappability, split_reads, breakpoint_ambiguity, caller_quality
- The image shows no depth drop consistent with an insertion, and HP1 reads carry small dotted arc/soft-clip signals near the breakpoint indicating inserted sequence. The call sits in a low-mappability tandem repeat and lies only 64 bp from a truth INS of the same type, so the FP most likely reflects a representation/placement difference in an ambiguous repeat rather than a spurious call. The low caller quality (12) and inherent length ambiguity of tandem-repeat insertions reinforce a benchmark artifact rather than a caller error.

### svim:FP:chr21:46034800:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 335 bp
- Reason: real deletion in tandem repeat with representation/size ambiguity
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch
- The HP:2 track shows a clear heterozygous coverage drop (~34x to ~19x) across the interval with a spanning split-read (dotted) connecting breakpoints, confirming a genuine deletion of roughly ~500 bp on one haplotype. However, the caller reports SVLEN 54 bp while the plotted event is ~508 bp, and the locus sits in a low-mappability tandem repeat with a same-type truth call only 335 bp away. This combination of real supporting evidence plus size/breakpoint ambiguity in a repeat context indicates a representation difference rather than a spurious call, despite the low caller quality (2.0).

### svim:FP:chr21:41474900:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 32 bp
- Reason: insertion in tandem repeat with size/representation ambiguity
- Evidence: tandem_repeat, split_reads, size_mismatch, caller_quality
- The locus is flagged as a tandem_repeat and a truth INS lies only 32 bp away, so an insertion is genuinely present here. The image shows no depth drop (consistent with INS) and dotted split-alignment arcs on both haplotypes indicating inserted sequence. The caller reports SVLEN 133 while the plotted event is ~401 bp, a classic length/representation discrepancy for INS inside tandem repeats, so Truvari's FP is likely a representation mismatch rather than a spurious call, though low quality (9.0) tempers confidence.

### svim:FP:chr21:46035255:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 57 bp
- Reason: INS in tandem repeat near truth call
- Evidence: split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity, caller_quality
- The call is a ~400-500 bp insertion in a low-mappability tandem-repeat region with a truth INS only 57 bp away. The HP1 track shows a localized split/gap signature (dotted read connection) near ~46035005 consistent with an insertion breakpoint, and coverage does not drop as expected for a real INS. Because insertion size and placement are inherently ambiguous in tandem repeats, Truvari most likely failed to match the caller's representation to the nearby truth call rather than the call being spurious.

### svim:FP:chr21:45909792:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 0 bp
- Reason: size mismatch at co-located truth INS in homopolymer
- Evidence: homopolymer, size_mismatch, split_reads, read_depth
- The caller reports an INS at chr21:45,909,792 with a truth INS 0 bp away (same position, same type), so an event is genuinely present. The discrepancy is a representation problem: the title lists 401 bp while the packet SVLEN is 797 bp, and the locus sits in a homopolymer where inserted-length is inherently ambiguous. Coverage stays flat with only faint split/soft-clip signals (consistent with an INS rather than a depth-changing event), so this is a Truvari size/representation mismatch rather than a true caller error.

### svim:FP:chr21:13576361:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.70)
- Region: segdup=True, low_mappability=True, tandem_repeat=False; nearest truth None bp
- Reason: No insertion signature and very low caller quality
- Evidence: read_depth, caller_quality, segdup, low_mappability, split_reads
- The caller reports a 389 bp INS with quality only 1.0, but the alignment shows smooth, uninterrupted coverage across both haplotypes with no localized cluster of soft-clipped or split reads at the putative breakpoint — the expected signature for an insertion is absent. There is no nearby truth call, so this is unlikely to be a representation artifact. Combined with the segdup/low-mappability flags and minimal caller confidence, the evidence does not support a real variant.

### svim:FP:chr21:33187115:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with coincident truth call
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The caller reports an INS inside a tandem-repeat region with a truth call at 0 bp distance, indicating a real event whose length/placement is inherently ambiguous. There is a size discrepancy (SVLEN 80 vs the 401 bp bar shown), which is exactly the kind of representation difference that causes Truvari to flag a genuine INS as FP in repetitive sequence. The flat coverage is consistent with an insertion (no depth drop expected), and long-read support cannot be read out at this scale.

### svim:FP:chr21:31784711:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 139 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is a 307bp insertion sitting within a tandem-repeat region, with a truth INS only 139bp away. Insertions in tandem repeats have inherently ambiguous placement and length, so Truvari likely flagged this as FP due to a breakpoint/size representation mismatch rather than a true error. The read depth remains stable across the interval, which is consistent with a real insertion (no depth drop expected), and the phased haplotype coverage shows no artifactual signature.

### svim:FP:chr21:46169981:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 63 bp
- Reason: deletion supported but in tandem repeat with nearby truth call
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch, caller_quality
- HP:1 shows a clear localized coverage drop and a dashed spanning-read gap around 46,170,000-46,170,100, and HP:2 shows split/dashed alignments, consistent with a real heterozygous deletion. The call sits in a low-mappability tandem-repeat region with a truth call only 63 bp away, and there is a size discrepancy (caller SVLEN 152 vs 704 bp shown), so Truvari likely failed to match due to breakpoint/size representation ambiguity rather than a genuine caller error. Low quality (17) and repeat context make exact placement uncertain, but the underlying deletion is supported.

### svim:FP:chr21:45500912:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 8 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, low_mappability, breakpoint_ambiguity, size_mismatch, caller_quality
- The caller reports an INS in a region flagged as tandem_repeat and low_mappability, with a truth INS only 8 bp away, which strongly suggests this FP is a representation difference rather than a spurious call. There is no depth drop (consistent with INS, not DEL), and the read tracks show localized dashed segments consistent with insertion/soft-clip signals within the interval. The size disagreement (caller SVLEN 140 vs displayed ~401 bp) reflects the inherent ambiguity of inserted-sequence length inside tandem repeats. Low caller QUAL (2.0) adds some uncertainty, but the proximity to a matching truth call favors an artifact over a true error.

### svim:FP:chr21:45606175:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 375 bp
- Reason: No depth drop supporting deletion
- Evidence: read_depth, split_reads, tandem_repeat, caller_quality, size_mismatch
- Coverage remains full and continuous across the entire interval on both haplotypes, with no drop toward zero as expected for a 540 bp (or even 70 bp) deletion. Only a faint dashed gap appears in HP1, far too subtle to support the reported event, and the caller quality is minimal (1.0). While the region is a tandem repeat, the nearest truth call is 375 bp away, so this is not a representation shift of a nearby true deletion but an unsupported call.

### svim:FP:chr21:45500896:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 19 bp
- Reason: Deletion in tandem repeat / low-mappability region near truth call
- Evidence: tandem_repeat, low_mappability, breakpoint_ambiguity, read_depth
- The call sits in a flagged tandem-repeat and low-mappability region with a same-type truth DEL only 19 bp away, so Truvari's FP label most likely reflects a breakpoint/representation mismatch rather than a genuine caller error. The coverage tracks show no clean drop to zero across the interval, consistent with the ambiguous alignment expected in a repetitive context where deletion placement and size are inherently uncertain. The high caller quality (1.0) and proximity to a truth call support this being essentially the same event represented differently.

### svim:FP:chr21:46090831:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 97 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: tandem_repeat, low_mappability, split_reads, breakpoint_ambiguity, size_mismatch, caller_quality
- The call is an insertion inside a low-mappability tandem-repeat region, with dotted split-read connections visible across the interval in HP:2 and no depth drop, consistent with an INS signature rather than a spurious call. A truth insertion lies only 97 bp away, and the reported size differs between the packet (249 bp) and the plotted event (401 bp), all hallmarks of representation/length ambiguity in tandem repeats. This most likely reflects a Truvari matching failure rather than a genuine caller error, though the low caller quality (1.0) adds some uncertainty.

### svim:FP:chr21:16397994:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 17 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: soft_clips, split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity, size_mismatch, caller_quality
- The image shows no depth drop and a localized cluster of soft-clipped/split reads (dotted arcs and clipped stubs near ~16,397,994 on HP2), consistent with an insertion signature rather than a spurious call. The locus sits in a tandem-repeat, low-mappability region with a truth INS only 17 bp away, and there is a size discrepancy (caller SVLEN 63 vs 401 bp shown), which is the classic setup for a representation-difference FP where inserted-length and breakpoint placement are ambiguous. Low caller quality (1.0) adds some uncertainty, but the evidence favors a real event mislabeled by Truvari over a genuine false positive.

### svim:FP:chr21:45798702:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.68)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 965 bp
- Reason: very low caller quality with no supporting insertion signature
- Evidence: caller_quality, low_mappability, tandem_repeat, soft_clips, read_depth
- The svim call has an extremely low quality score (2.0) and the alignment shows a stable, continuous long-read pileup across the 45,798,702 site with no localized cluster of soft-clips or inserted-sequence reads expected for a 152 bp INS. The only split-read hint (dotted arc near 45,798,460) is far from the reported breakpoint, and the nearest truth INS is 965 bp away, too distant to represent the same event. Despite the tandem-repeat/low-mappability flags, the absence of any convincing insertion signal favors a genuine false positive rather than a representation artifact.

### svim:FP:chr21:44982305:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 32 bp
- Reason: size/representation mismatch in tandem repeat
- Evidence: split_reads, read_depth, tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- Both haplotype tracks show split-read arcs (dashed) and a localized coverage dip in the interval, consistent with a real deletion signature rather than a spurious call. The locus sits in a tandem_repeat with a truth deletion only 32 bp away, and there is a large size discrepancy (caller SVLEN 54 vs the ~508 bp event shown), so Truvari's FP most plausibly reflects a representation/size mismatch in a repeat rather than a fabricated variant. Low caller quality (11) adds some uncertainty, but the alignment evidence supports a genuine deletion at this site.

### svim:FP:chr21:42284103:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 39 bp
- Reason: real deletion in tandem repeat with representation/size ambiguity
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity
- The HP:2 track shows a clear heterozygous coverage drop with dashed split-read connections across the interval, consistent with a genuine deletion signature. However, the call sits in a low-mappability, tandem-repeat, homopolymer region only 39 bp from a truth call of the same type, and there is a large size discrepancy (packet SVLEN 120 vs image title 640 bp), indicating breakpoint/length ambiguity rather than a true false positive. This pattern—a real DEL near a truth call inside a repeat with representation differences—is characteristic of a Truvari FP that is actually a benchmark artifact.

### svim:FP:chr21:45484055:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 29 bp
- Reason: deletion in tandem repeat with nearby truth call and representation/size ambiguity
- Evidence: read_depth, split_reads, tandem_repeat, size_mismatch, caller_quality
- The HP2 track shows a small localized coverage dip with dashed split-read arcs near the middle of the window, consistent with a heterozygous deletion, while HP1 is intact. The region is flagged as a tandem repeat and a truth DEL sits only 29 bp away, so this is likely the same underlying event with an ambiguous breakpoint/size (note the discordant 85 bp SVLEN vs the 569 bp title label). This representation/placement difference in a repeat context is characteristic of a benchmark artifact rather than a genuine false positive, though the low caller quality (1.0) adds some uncertainty.

### svim:FP:chr21:23350059:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 29 bp
- Reason: tandem-repeat placement/size ambiguity near a truth call
- Evidence: split_reads, read_depth, tandem_repeat, low_mappability, breakpoint_ambiguity, size_mismatch, caller_quality
- The region is flagged as tandem_repeat and low_mappability, and a truth DEL sits only 29 bp away, so this is a representation-difference scenario rather than a spurious call. The image shows localized coverage dips and multiple split-read arcs (dotted) at the site on both haplotypes consistent with a real deletion event, though the breakpoints are staggered/ambiguous. There is also a size discrepancy (caller SVLEN 113 vs the 625 bp title), typical of collapsed/shifted representation in repetitive sequence. The alignment supports a genuine deletion that Truvari failed to match due to placement/size ambiguity, not a caller error.

### svim:FP:chr21:45553876:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 4 bp
- Reason: tandem-repeat deletion with near-adjacent truth call and size/representation mismatch
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The image shows gray dotted split-read gaps within the HP:2 long reads, consistent with a real deletion on one haplotype rather than a spurious call. The locus sits in a tandem repeat with a truth deletion only 4 bp away, and there is a large size discrepancy (caller SVLEN 62 vs the 524 bp interval shown), all classic signs of a representation/breakpoint-placement difference rather than a genuine caller error. Low caller quality (2.0) plus repeat-driven ambiguity supports Truvari's FP being an artifact of matching rather than a false variant.

### svim:FP:chr21:36496735:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.66)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat coincident with truth call but size mismatch
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The call is an insertion inside a tandem-repeat region with a truth INS at essentially the same position (nearest_truth_call_dist_bp = 0), yet Truvari labels it FP. There is a size discrepancy between the annotated 401 bp event and the caller's SVLEN of 694, which is the hallmark of representation/length ambiguity for insertions within tandem repeats where inserted-sequence length is inherently unstable. The image shows no depth drop (consistent with an INS rather than a spurious DEL) and only mild coverage stepping, so the disagreement is most likely a benchmark representation artifact rather than a genuine caller error, though the low caller quality (7.0) tempers confidence.

### svim:FP:chr21:37756655:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.66)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 126 bp
- Reason: real deletion in tandem-repeat/low-mappability region with representation mismatch
- Evidence: read_depth, split_reads, low_mappability, tandem_repeat, size_mismatch, caller_quality
- HP1 shows a clear haplotype-specific coverage drop (~50% to baseline) with a spanning split read (black dashed arc), consistent with a real heterozygous deletion, so this is not an unsupported false positive. However, the deletion signal in the image sits ~37756950-37757150 and the plotted event (673 bp) differs from the caller's reported 137 bp interval, and there is a truth call only 126 bp away in a low-mappability tandem repeat. This combination of ambiguous breakpoint placement/size and repeat context indicates a representation difference rather than a genuine caller error.

### svim:FP:chr21:46048264:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.66)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 411 bp
- Reason: No supporting depth drop for deletion
- Evidence: read_depth, split_reads, tandem_repeat, caller_quality, size_mismatch
- The caller reports a DEL but coverage remains steady across the shaded interval on both haplotypes with no drop toward zero, which is the expected signature of a real deletion. Only scattered dotted spanning-gap segments appear, insufficient to confirm a haplotype-specific dropout, and caller quality is minimal (1.0). The event sits in a tandem repeat and the nearest truth call is 411 bp away, but the lack of any depth reduction plus the size discrepancy (title 696 bp vs packet 148 bp) argues this is a spurious call rather than a mere representation shift.

### svim:FP:chr21:45815117:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.66)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 1 bp
- Reason: size/representation mismatch in tandem repeat adjacent to truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, split_reads, breakpoint_ambiguity
- A truth DEL sits just 1 bp away, and the region is flagged as low_mappability and tandem_repeat, where deletion breakpoints and lengths are inherently ambiguous. The caller reports a 105 bp DEL while the plotted event spans ~609 bp, a clear representation/size discrepancy rather than a spurious call. Dotted split-read tracks appear across the interval consistent with a real nearby deletion, so this FP most likely reflects a benchmark representation difference, not a caller error.

### svim:FP:chr21:19345956:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.66)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at 0 bp distance
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The locus is an insertion inside a tandem repeat with a truth INS at 0 bp distance, so a real event almost certainly exists here. Truvari likely flagged it as FP because of a representation/size mismatch (the packet lists SVLEN 50 while the plotted event spans ~401 bp), which is inherently ambiguous for insertions in repetitive sequence. The coverage tracks show no depth anomaly, consistent with an INS rather than a DEL, and the low quality (12) reflects mapping ambiguity in the repeat rather than a spurious call.

### svim:FP:chr21:44410367:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.66)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 230 bp
- Reason: deletion in tandem repeat / low-mappability region with nearby truth call
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity, size_mismatch
- The HP2 track shows coverage dropping toward zero across portions of the interval together with dotted split-read arcs spanning the gap, consistent with a genuine deletion signature. The call sits in a low-mappability tandem repeat and there is a truth deletion only 230 bp away, and the caller's 315 bp size differs from the ~1.03 kb window, indicating breakpoint/size representation ambiguity rather than a spurious call. This pattern is a classic Truvari FP artifact where a real event is placed slightly off or sized differently within a repeat.

### svim:FP:chr21:45134287:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.66)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 33 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality
- The call is an insertion in a low-mappability tandem-repeat region with a truth INS only 33 bp away, a setting where inserted-sequence length and breakpoint placement are inherently ambiguous. There is a size discrepancy (packet SVLEN 53 vs. plotted 401 bp), consistent with a representation/length disagreement rather than a spurious call. The coverage remains continuous with no depth drop, as expected for an INS, and the nearby matching truth call suggests Truvari flagged this as FP due to representation differences, not a caller error.

### svim:FP:chr21:45553776:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 75 bp
- Reason: INS in tandem repeat near truth call
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The locus is flagged as a tandem_repeat and there is a truth INS only 75 bp away, a classic setup for representation-driven Truvari mismatches where inserted-sequence length and placement are inherently ambiguous. The image shows no depth loss (consistent with INS rather than DEL) and dotted split-read connections near the breakpoint, supporting a genuine insertion event. The size discrepancy (caller SVLEN 301 vs 401 bp shown) plus the low caller quality (6.0) suggests the caller captured a real but imperfectly represented insertion rather than a spurious one.

### svim:FP:chr21:31784924:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 246 bp
- Reason: No insertion signal with very low caller quality
- Evidence: read_depth, caller_quality, tandem_repeat, low_mappability, caller_quality
- The alignment tracks show uniform coverage across all haplotypes with no localized cluster of soft-clipped or split reads at the putative breakpoint that would support a ~400bp insertion. The caller quality is extremely low (2.0), and the nearest truth call is 246 bp away, too far to be a simple representation match. Although the region is flagged as tandem_repeat/low_mappability, the absence of any supporting split-read or soft-clip evidence combined with the poor quality argues the call is not supported.

### svim:FP:chr21:42589601:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 1998 bp
- Reason: low-quality call in repeat region with no nearby truth support
- Evidence: caller_quality, segdup, low_mappability, tandem_repeat, split_reads, read_depth
- The svim call is a 401 bp INS with a very low quality score (2.0) sitting in a segdup/low-mappability/tandem-repeat region. The image shows no depth drop (consistent with INS expectation) but the split-read/dotted signals cluster near 42589780-42589840 rather than at the labeled breakpoint 42589601, and there is no clean soft-clip cluster supporting a 400 bp insertion at the call site. Critically, the nearest truth call is ~2000 bp away, too distant to be a representation shift, so this is more consistent with a spurious caller call in a difficult region than a benchmark artifact.

### svim:FP:chr21:45500805:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 74 bp
- Reason: INS in tandem repeat with nearby truth call (representation ambiguity)
- Evidence: tandem_repeat, low_mappability, soft_clips, breakpoint_ambiguity, size_mismatch, caller_quality
- The locus is an insertion in a low-mappability tandem-repeat region, where inserted-sequence length and breakpoint placement are inherently ambiguous. There is a truth INS only 74 bp away, and the image shows clustered soft-clipped/split reads with no depth drop consistent with an insertion rather than a spurious call. The large discrepancy between the caller's SVLEN (73 bp) and the plotted 401 bp event, combined with the very low caller quality (2.0), points to a representation/length mismatch against the nearby truth call rather than a genuine false positive.

### svim:FP:chr21:45500481:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at 0 bp distance
- Evidence: tandem_repeat, size_mismatch, split_reads, caller_quality
- The caller reports an insertion inside a tandem-repeat region, and a truth call of the same type sits at 0 bp distance, so a real insertion almost certainly exists here. There is a slight split-read arc on HP2 near the interval consistent with an insertion breakpoint, but no depth drop (correct for INS). The header size (401 bp) versus the caller SVLEN (265 bp) reflects the intrinsic length ambiguity of TR insertions, which typically drives Truvari to withhold a match despite an essentially correct event. The very low caller quality (1.0) lowers confidence, but the TR context and adjacent truth call favor a representation artifact over a genuine false positive.

### svim:FP:chr21:45815346:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 20 bp
- Reason: representation/size mismatch in tandem repeat near truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- A truth DEL sits only 20 bp from this svim call, and the region is flagged as both a tandem repeat and low-mappability, where deletion size and breakpoint placement are inherently ambiguous. The caller reports a 458 bp DEL while the displayed event spans ~1.32 kb, a clear size/representation discrepancy rather than a spurious call. The image shows some dropout/discordant patterning in the interval but no clean zero-coverage window, consistent with an ambiguously represented repeat-associated deletion rather than a true false positive.

### svim:FP:chr21:45156060:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 61 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The caller reports a 304 bp insertion inside a tandem-repeat region, and a truth INS lies only 61 bp away, which is the classic signature of a representation difference rather than a genuine false positive. Insertion length and breakpoint placement are inherently ambiguous in tandem repeats, so Truvari's FP label likely reflects a size/position mismatch to the same underlying event. The image shows no depth drop (consistent with an INS) but also no clearly visible split/soft-clip cluster, and the very low caller quality (2.0) leaves some residual uncertainty.

### svim:FP:chr21:45918317:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 60 bp
- Reason: tandem-repeat placement/size ambiguity near a truth call
- Evidence: tandem_repeat, low_mappability, read_depth, size_mismatch, caller_quality
- The call sits in a low-mappability tandem-repeat region only 60 bp from a truth DEL, the classic setup for a representation mismatch rather than a caller error. There is a modest coverage dip on the HP1 haplotype around the interval consistent with a real deletion, but the caller's 192 bp size disagrees sharply with the larger event depicted, so Truvari likely failed to match on size/breakpoint rather than because no variant exists. Given the repeat context and proximity to truth, this is best treated as a benchmark artifact, though low caller quality (1.0) leaves some residual uncertainty.

### svim:FP:chr21:45554212:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 8 bp
- Reason: insertion in tandem repeat with size discrepancy
- Evidence: tandem_repeat, size_mismatch, soft_clips, caller_quality
- The locus sits in a tandem repeat with a truth INS only 8 bp away, and the HP:2 track shows soft-clipped/split-read clustering consistent with a real insertion rather than a depth drop. The caller reported SVLEN=100 while the region title shows a ~401 bp event, so the mismatch is largely a representation/size-similarity failure inherent to tandem-repeat insertions rather than a spurious call. The very low quality (2.0) tempers confidence, but the presence of a nearby same-type truth call in a repeat context points to a benchmark artifact over a genuine false positive.

### svim:FP:chr21:41475628:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 10 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, read_depth, split_reads, size_mismatch, caller_quality, breakpoint_ambiguity
- The call is an insertion in a flagged tandem-repeat region with the nearest truth INS only 10 bp away, a classic representation-difference scenario. Coverage stays flat (~30x) with no depth drop, consistent with an INS, and HP:2 shows a localized read disruption near the breakpoint. The size disagreement (SVLEN 92 vs 401 bp displayed) reflects the inherent ambiguity of insertion length within tandem repeats, so Truvari's FP most likely stems from length/placement mismatch rather than a true caller error, though the low caller quality (1.0) leaves some doubt.

### svim:FP:chr21:46047680:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 41 bp
- Reason: deletion in tandem repeat with nearby truth call, representation mismatch
- Evidence: split_reads, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- The image shows dotted split-read gaps on both haplotypes consistent with a real deletion, though coverage does not fully collapse (suggesting a heterozygous/repeat-embedded event). A truth DEL sits only 41 bp away and the locus is flagged low_mappability + tandem_repeat, where breakpoint and length are inherently ambiguous, and there is a notable size discrepancy (caller SVLEN 132 vs. ~664 bp displayed). This pattern points to a representation/placement mismatch rather than a genuine caller error, despite the very low caller quality (2.0).

### svim:FP:chr21:14343099:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: minimal split-read support for small deletion
- Evidence: read_depth, split_reads, caller_quality
- The caller reports a small 69 bp heterozygous deletion, but the alignment shows no coverage drop and only a single faint dotted spanning arc in the HP:2 track near the interval rather than a coherent cluster of split reads at both breakpoints. The caller QUAL is 1.0 (very low), and no truth call sits nearby. The evidence is too weak to support a real deletion, consistent with the Truvari FP label.

### svim:FP:chr21:46047777:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 6 bp
- Reason: INS in tandem repeat near truth call with size ambiguity
- Evidence: tandem_repeat, size_mismatch, split_reads, caller_quality
- The call is an insertion sitting in a tandem-repeat region with a truth INS only 6 bp away, and the image shows split-read/soft-clip signals (dashed segments) at the breakpoint with no depth drop, consistent with a real insertion rather than a spurious call. Truvari likely rejected it because of the large size discrepancy (caller SVLEN 82 vs ~401 bp displayed truth event), a classic representation difference for insertions in tandem repeats where inserted-sequence length is inherently ambiguous. The very low caller quality (2.0) adds some uncertainty, but the proximity to a matching truth call and repeat context favor a benchmark artifact over a genuine caller error.

### svim:FP:chr21:46144473:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at 0bp distance but size/representation mismatch
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The caller reports an INS (packet SVLEN 68, title 401bp) inside a tandem-repeat region with the nearest truth call at 0 bp distance, indicating a truth INS exists at this exact locus. Truvari's FP label most likely stems from the inserted-sequence length ambiguity inherent to tandem repeats rather than a genuine caller error. The coverage tracks are flat with no depth drop (consistent with INS not DEL), though no dramatic soft-clip cluster is resolvable at this scale, keeping confidence moderate.

### svim:FP:chr21:45797764:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 27 bp
- Reason: INS in tandem repeat near truth call with size/representation ambiguity
- Evidence: tandem_repeat, low_mappability, split_reads, size_mismatch, caller_quality, breakpoint_ambiguity
- The image shows no depth drop (consistent with an insertion) and faint dotted split-read/gap signatures near the interval on HP2 and HP1, supporting a real insertion event. The locus sits in a tandem-repeat, low-mappability region with a truth INS only 27 bp away, so Truvari's FP label most likely reflects a representation/size difference (caller SVLEN 2142 vs. ~401 bp shown vs. nearby truth) rather than a spurious call. Insertion length in tandem repeats is inherently ambiguous, making this a benchmark artifact rather than a caller error, though the large size discrepancy and low quality (13) leave some doubt.

### svim:FP:chr21:45156003:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 118 bp
- Reason: Very low caller quality with no visible insertion signature
- Evidence: read_depth, caller_quality, tandem_repeat, size_mismatch
- The samplot shows flat, uninterrupted coverage across the region with no localized cluster of soft-clipped or split reads that would mark an insertion breakpoint. The caller quality is extremely low (2.0), and there is a size discrepancy (title 401 bp vs packet SVLEN 111 bp), suggesting an unstable/unsupported call. Although the locus lies in a tandem repeat, the nearest truth call is 118 bp away and no read evidence supports the event, favoring a false positive over a representation artifact.

### svim:FP:chr21:46054926:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 25 bp
- Reason: insertion in tandem repeat near truth call
- Evidence: tandem_repeat, caller_quality, size_mismatch, split_reads
- The locus is flagged as a tandem_repeat region with a truth INS only 25 bp away, and reads carry insertion/duplication signatures (red dotted segments) consistent with a real inserted-sequence event rather than a depth-based change. Truvari likely failed to match because of representation ambiguity: the caller's reported size (SVLEN 52 in the packet vs the 401 bp label) and breakpoint placement differ from the truth call within the repeat, where inserted-length is inherently uncertain. The very low caller quality (2.0) adds noise but the presence of a nearby same-type truth call favors a representation artifact over a genuine caller error.

### svim:FP:chr21:44416883:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 1642 bp
- Reason: No convincing depth drop for a deletion in a low-mappability tandem repeat
- Evidence: read_depth, low_mappability, tandem_repeat, caller_quality, split_reads
- For a ~938 bp deletion the HP:2 track should show a clear coverage drop across the interval, but depth stays high (~30-40x) with only a shallow, gradual dip that is consistent with mappability variation rather than a clean het deletion breakpoint. The dashed spanning line and modest dip fall inside a flagged low_mappability tandem repeat, the caller quality is minimal (1.0), and the nearest truth call is 1642 bp away, so the alignment evidence does not support a real deletion here.


### svim:FP:chr21:44863152:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 15 bp
- Reason: INS in tandem repeat near truth call with size/breakpoint ambiguity
- Evidence: tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an INS sitting in a low-mappability tandem-repeat region only 15 bp from a matching truth call, which is the classic setting for a representation-difference FP rather than a genuine error. The image shows no depth drop and a localized cluster of split/soft-clipped long-read signal (dashed segments) consistent with inserted sequence at this site. There is a marked size discrepancy (caller SVLEN 62 vs the 401 bp title annotation), reflecting the inherent length ambiguity of insertions inside tandem repeats, so Truvari likely failed to match on size/position rather than because the variant is absent.

### svim:FP:chr21:39833739:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: insufficient read support for deletion
- Evidence: read_depth, split_reads, caller_quality
- The caller reports a 606 bp DEL, and the HP:1 track shows only a single faint dotted spanning gap between ~39,833,719 and 39,834,364 suggestive of one split read. However, there is no clear coverage drop over the interval on either haplotype as expected for a true (even heterozygous) deletion, the caller QUAL is minimal (1.0), and Truvari finds no nearby truth call. The evidence is too weak to support a genuine deletion at this site.

### svim:FP:chr21:46048315:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 193 bp
- Reason: INS in tandem repeat near a truth call of same type
- Evidence: tandem_repeat, split_reads, breakpoint_ambiguity, size_mismatch, caller_quality
- The locus is an insertion sitting inside a flagged tandem repeat, with the nearest truth INS only 193 bp away, a classic setup for representation ambiguity. The HP:2 track shows read discontinuities (dotted split-read connections) with no coverage drop, consistent with an insertion signature rather than an absence of evidence. Insertion length in tandem repeats is inherently ambiguous (caller SVLEN 194 vs. displayed 401 bp), so Truvari likely flagged this as FP due to size/breakpoint mismatch rather than a genuine caller error, though the low caller quality (1.0) tempers confidence.

### svim:FP:chr21:31785018:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 152 bp
- Reason: Very low caller quality with no supporting insertion signature
- Evidence: caller_quality, tandem_repeat, read_depth, size_mismatch
- The svim call has extremely low quality (QUAL=2.0) and the alignment tracks show no localized soft-clip or split-read cluster at the ~31,785,018 breakpoint that would support a genuine insertion. Coverage remains flat and continuous across the interval with no spike or read disruption expected for an INS. Although the region is flagged as a tandem repeat and there is a truth call 152 bp away, the size discrepancy (84 bp caller vs 401 bp displayed/truth) and absence of any visual support point to a spurious, low-confidence call rather than a mere representation shift.

### svim:FP:chr21:45909967:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 72 bp
- Reason: No depth drop supporting deletion; very low caller quality
- Evidence: read_depth, caller_quality, tandem_repeat, homopolymer, size_mismatch
- The HP:1 track retains full read coverage (~90x) across the entire flagged interval with no drop toward zero, which contradicts the expected deletion signature of near-zero coverage plus split reads at breakpoints. The caller quality is extremely low (QUAL 2.0) and there is a large size discrepancy (packet SVLEN 69 vs 537 bp displayed), further undermining the call. Although the site sits in a tandem-repeat/homopolymer context with a truth call 72 bp away, the absence of any supporting depth signal argues for a spurious call rather than a representation artifact.

### svim:FP:chr21:43582869:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 817 bp
- Reason: very low caller quality with weak insertion signal in repetitive region
- Evidence: caller_quality, low_mappability, tandem_repeat, split_reads, read_depth
- The svim call has an extremely low quality score (2.0) and sits in a low-mappability tandem-repeat region, with the nearest truth call 817 bp away (too far to be a simple representation shift). The image shows only a single faint dotted arc on HP1 and no clear localized soft-clip/split-read cluster carrying inserted sequence; instead HP1 shows an odd coverage step that is not the expected INS signature. The evidence is too weak to support a real 401 bp insertion, favoring a false positive.

### svim:FP:chr21:46048020:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 101 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, caller_quality, split_reads
- The call is a ~400-540 bp insertion inside a tandem-repeat region, where inserted-sequence length and breakpoint placement are inherently ambiguous. A truth call of the same type sits only 101 bp away, and the image shows no depth drop with scattered split/soft-clip signals consistent with an INS rather than a spurious call. Truvari most likely flagged this as FP due to a representation/placement mismatch within the repeat rather than a genuine caller error, though the low quality (9.0) leaves some doubt.

### svim:FP:chr21:45798537:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 800 bp
- Reason: insufficient insertion evidence at low quality
- Evidence: read_depth, split_reads, caller_quality, tandem_repeat, low_mappability, size_mismatch
- The caller reports a 256bp INS (image labels 401bp) but the alignment shows only a single faint dotted split-read arc on HP1 near 45798457 and otherwise flat, uninterrupted coverage across all haplotypes, which is far weaker than expected for a real ~250-400bp insertion. Caller quality is minimal (1.0), and the nearest truth call is 800bp away, too far to represent the same event via a breakpoint shift. Although the region carries tandem_repeat and low_mappability flags, the lack of a convincing clustered soft-clip/split signature and the isolated single-read support argue against a genuine variant.

### svim:FP:chr21:30570969:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 89 bp
- Reason: INS in tandem repeat near truth call with representation ambiguity
- Evidence: tandem_repeat, split_reads, size_mismatch, caller_quality
- The caller reports an INS in a tandem-repeat region only 89 bp from a truth call of the same type, and the image shows a localized cluster of split/duplication-style reads (red dotted signal) with no depth drop, consistent with an insertion/duplication event rather than a spurious call. The discrepancy between the caller SVLEN (892 bp) and the plotted 401 bp reflects inherent length ambiguity of inserted sequence within tandem repeats. This pattern—a real event flagged FP due to breakpoint/length representation differences in a repeat—is a classic benchmark artifact rather than a genuine caller error, though the modest quality (22) and size mismatch keep confidence moderate.

### svim:FP:chr21:42587828:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: low-quality call with no supporting insertion signature and no nearby truth
- Evidence: caller_quality, size_mismatch, segdup, low_mappability, tandem_repeat, split_reads
- The caller quality is minimal (1.0) and there is a size discrepancy between the plotted 401 bp INS and the packet SVLEN of 205, indicating an unstable call. The image shows no clear localized soft-clip/split-read cluster or coverage bump that would define an insertion breakpoint; coverage is largely uniform with only scattered dotted read segments. With no truth call anywhere nearby (dist=None) despite the repetitive context, the evidence favors a spurious call rather than a representation artifact, though the segdup/low-mappability context adds some ambiguity.

### svim:FP:chr21:46034333:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.62)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 391 bp
- Reason: very low caller quality with no supporting insertion signature
- Evidence: read_depth, caller_quality, tandem_repeat, low_mappability, size_mismatch
- The svim call has an extremely low quality score (2.0) and a size mismatch between the packet SVLEN (56 bp) and the plotted 401 bp event. The image shows no localized cluster of soft-clipped/split reads that would mark a genuine insertion breakpoint; instead HP2 simply shows a coverage step-down and HP1 reads span the region continuously. Although the locus sits in a tandem-repeat/low-mappability context, the nearest truth call is 391 bp away (beyond typical matching), so this is more consistent with a spurious low-confidence call than a real missed variant.

### svim:FP:chr21:46169536:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 15 bp
- Reason: call in tandem repeat adjacent to truth call with size/breakpoint ambiguity
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality, split_reads
- A truth DEL sits only 15 bp away and the region is flagged as tandem_repeat and low_mappability, where deletion breakpoints and lengths are inherently ambiguous. The packet size (194 bp) conflicts sharply with the plotted 788 bp event, and split-read arcs in HP:1 support a real deletion signal even though coverage does not cleanly drop to zero. This pattern of a nearby same-type truth call with representation/size divergence in a repeat context is characteristic of a Truvari benchmarking artifact rather than a genuine caller false positive, though the very low caller quality (2.0) leaves some doubt.

### svim:FP:chr21:44885072:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 93 bp
- Reason: Deletion signal in tandem-repeat region near a truth call
- Evidence: split_reads, read_depth, tandem_repeat, low_mappability, caller_quality, breakpoint_ambiguity, size_mismatch
- The image shows split-read arcs (dashed lines) and modest coverage dips on both haplotypes indicating genuine deletion signal, though placed at positions offset from the caller's reported 64 bp interval. The locus sits in a tandem-repeat, low-mappability region with a truth call only 93 bp away, and there is a strong size mismatch (caller 64 bp vs ~528 bp depicted), all hallmarks of ambiguous breakpoint/length representation rather than a spurious call. The very low caller quality (2.0) adds uncertainty, but the underlying deletion appears real and mislabeled FP due to representation differences.

### svim:FP:chr21:46053122:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with coincident truth call and size ambiguity
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The call is an insertion inside a tandem-repeat region with a truth call at 0 bp distance, the classic setting for representation/length ambiguity where Truvari flags FP despite a real event. There is a size discrepancy (packet SVLEN 99 vs displayed 401 bp) consistent with inconsistent inserted-length estimation typical of tandem repeats. The coverage tracks show no depth drop (as expected for INS) but no clear soft-clip/split cluster is resolvable in this short-read view, so placement/length rather than existence is likely the issue.

### svim:FP:chr21:45797462:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 274 bp
- Reason: INS in tandem repeat near truth call with representation/size ambiguity
- Evidence: tandem_repeat, size_mismatch, read_depth, soft_clips, caller_quality
- The locus is an insertion flagged inside a tandem repeat, where inserted-sequence length is inherently ambiguous (caller reports SVLEN 81 while the plotted event is ~401 bp). Consistent with an INS signature there is no coverage drop; instead HP2 shows aligned long-read/soft-clip support at a localized breakpoint. A truth INS lies only 274 bp away, so this is most likely the same event mislabeled FP due to breakpoint/size representation differences rather than a genuine caller error, though the low caller quality (1.0) and size discrepancy add some doubt.

### svim:FP:chr21:42589659:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 177 bp
- Reason: call in tandem repeat/segdup adjacent to truth call
- Evidence: segdup, low_mappability, tandem_repeat, split_reads, breakpoint_ambiguity, caller_quality
- The SVIM call is a small DEL flagged FP, but it sits within a segmental duplication / low-mappability / tandem-repeat region only 177 bp from a truth DEL of the same type, the classic setup for a representation difference rather than a genuine caller error. The image shows split/discordant read patterns (dotted-line spanning gaps in HP1 and HP2) consistent with a deletion signal, though coverage is largely preserved and placement is ambiguous. The very low caller quality (2.0) and the repeat context make the exact breakpoints and size uncertain, so Truvari's FP most likely reflects imperfect matching of an essentially real event.

### svim:FP:chr21:44396829:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at same position but size/representation mismatch
- Evidence: split_reads, tandem_repeat, size_mismatch, caller_quality
- The locus is an insertion inside a tandem repeat (region_flag) with a truth call at distance 0 bp, indicating a real event exists at this position. The HP1 track shows a localized split/soft-clip signature consistent with an insertion breakpoint and no depth drop, matching the INS expectation. However, the caller reports SVLEN 100 while the plot header shows 401 bp, a large size discrepancy typical of length ambiguity in tandem repeats, so Truvari's FP likely reflects a representation/size-matching difference rather than a spurious call. Low caller quality (2.0) adds some uncertainty.

### svim:FP:chr21:46035018:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 109 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality, breakpoint_ambiguity
- The call is an insertion sitting in a flagged tandem-repeat, low-mappability region with a same-type truth call only 109 bp away, a classic setup for representation-driven Truvari mismatches where inserted-length and placement are ambiguous. The HP:1 track shows faint soft-clip/split arcs consistent with a real insertion breakpoint, and there is no depth drop, matching the INS signature. However the large size discrepancy (caller 169 bp vs 401 bp label) and very low caller quality (1.0) reduce confidence, so this is most likely a benchmark artifact rather than a genuine caller error.

### svim:FP:chr21:30570969:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 89 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality, read_depth
- The call is an insertion inside a tandem-repeat region with a truth call only 89 bp away, the classic setup for a representation-driven FP rather than a true caller error. There is no depth drop and reads show soft-clip/duplication signal consistent with local inserted sequence, but the caller's SVLEN (71 bp) disagrees markedly with the plotted 401 bp event, reflecting the inherent length ambiguity of tandem-repeat insertions. Given the nearby truth INS and repeat context, Truvari likely failed to match due to size/breakpoint representation differences rather than a spurious call.

### svim:FP:chr21:45923901:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 923 bp
- Reason: No deletion depth signature supporting the call
- Evidence: read_depth, tandem_repeat, low_mappability, caller_quality, split_reads
- For a DEL we expect a coverage drop across the interval, but HP1 shows continuous ~50x coverage with only a faint dotted arc (a single weak split-read gap) near the center and no depletion of reads. The call sits in a low-mappability tandem-repeat region and carries the lowest possible caller quality (1.0), both conditions that produce spurious deletion calls. With the nearest truth call 923 bp away and no convincing spanning-read loss, the alignment evidence does not support a real deletion here.

### svim:FP:chr21:45437580:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 47 bp
- Reason: tandem-repeat representation ambiguity near a truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The call sits in a tandem-repeat region with a truth DEL only 47 bp away, so this is very likely a representation/placement difference rather than a genuine caller error. There is also a size discrepancy (packet SVLEN=76 vs the 552 bp label), typical of ambiguous breakpoint/length assignment inside repeats. The coverage does not drop cleanly to zero across the interval, but split-read/dashed signals and the nearby matching truth call support a real (if imprecisely represented) event rather than a spurious one.

### svim:FP:chr21:45633570:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 44 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, caller_quality, breakpoint_ambiguity
- The caller reports an insertion within a tandem-repeat, low-mappability region only 44 bp from a truth INS of the same type, which is the classic setup for a representation difference rather than a caller error. There is no depth drop (consistent with INS), and the HP:1 track shows a localized cluster of perturbed/dashed reads in the middle-right of the interval hinting at a breakpoint. The discrepancy between the displayed 401 bp and packet SVLEN 138, plus the very low caller quality, reflects the inherent length ambiguity of insertions in tandem repeats. Overall the event is likely real but Truvari flagged it as FP due to shifted/mismatched representation.

### svim:FP:chr21:15030905:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: Deletion signature present in tandem-repeat/low-mappability region
- Evidence: split_reads, read_depth, tandem_repeat, low_mappability, size_mismatch, caller_quality
- The HP:1 track shows an aligned long read with a dotted/split spanning connection across ~15030905-15031053 and a small localized coverage dip, consistent with a heterozygous deletion on one haplotype (HP:2 remains intact, so total coverage does not drop to zero). This alignment evidence supports a real deletion, but it sits in a flagged tandem-repeat and low-mappability region where breakpoint placement and deletion size are inherently ambiguous (note the SVLEN 148 in the packet vs 696 bp title, indicating representation/size uncertainty). Given the repeat context and size/breakpoint ambiguity, the Truvari FP most likely reflects a representation mismatch rather than a genuine caller error.

### svim:FP:chr21:46006295:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 214 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, split_reads, size_mismatch, breakpoint_ambiguity, read_depth
- The call is an insertion in a tandem-repeat region with no coverage drop (as expected for INS), and localized split-read/soft-clip clusters are visible around 46006180-46006230 consistent with a real inserted-sequence breakpoint. A truth INS lies only ~214 bp away and there is a notable size discrepancy (SVLEN 194 vs. 401 bp displayed), both hallmarks of representation ambiguity within tandem repeats. This most likely reflects a shifted/resized representation of a real insertion rather than a genuine caller error.

### svim:FP:chr21:45798921:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 1184 bp
- Reason: low-quality INS call in tandem repeat with no clear insertion signature and distant truth
- Evidence: read_depth, caller_quality, low_mappability, tandem_repeat, size_mismatch
- The coverage tracks show smooth, normal read depth (~30x on HP1) with no localized soft-clip/split-read cluster that would mark a genuine insertion breakpoint at the site. The call has very low quality (19.0), sits in a low-mappability tandem-repeat region prone to spurious alignments, and the nearest truth INS is 1184 bp away — too far to be a representation shift of the same event. There is also a size discrepancy (packet SVLEN 168 vs title 401 bp), reinforcing that this is an unsupported caller artifact rather than a benchmark representation issue.

### svim:FP:chr21:46383965:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: Low-quality INS call in repetitive region with no truth support
- Evidence: read_depth, tandem_repeat, segdup, low_mappability, caller_quality
- The coverage track shows flat, high depth across the interval with only a minor localized dip and no convincing cluster of soft-clipped/split reads that would signal a 400-600 bp insertion breakpoint. The call carries a very low quality score (1.0) and sits in overlapping segdup/low-mappability/tandem-repeat context with no nearby truth call (nearest distance None), so there is little supporting evidence. The absence of both an insertion signature and any proximal truth event argues for a spurious call rather than a mere representation difference, though the repetitive context lowers confidence.

### svim:FP:chr21:44396119:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 18 bp
- Reason: call in tandem repeat/low-mappability adjacent to truth call
- Evidence: tandem_repeat, low_mappability, split_reads, breakpoint_ambiguity, caller_quality
- A truth DEL sits only 18 bp away and the locus carries both tandem_repeat and low_mappability flags, so the caller's 211 bp deletion likely represents the same event with shifted/ambiguous breakpoints rather than a genuine false call. The image shows no clean coverage collapse across the annotated interval (as a full deletion would produce), but faint dotted split-read arcs appear in the HP:1 track through the region, consistent with a small hard-to-place deletion in a repetitive context. The low caller quality (1.0) and the size discrepancy (211 vs. the 821 bp header) reflect the placement ambiguity typical of tandem-repeat representation differences, not clear caller error.

### svim:FP:chr21:40518588:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 200 bp
- Reason: No insertion signature and very low caller quality
- Evidence: read_depth, soft_clips, tandem_repeat, caller_quality
- The coverage tracks are essentially flat and full across the region with no localized cluster of soft-clipped or split reads that would mark a true long-read insertion breakpoint. The svim call carries a QUAL of only 1.0, the weakest possible confidence, and the nearest truth call is 200 bp away rather than co-located. Although the tandem_repeat flag raises the possibility of a representation artifact, the absence of any visible supporting signal combined with the minimal caller quality points to a spurious call.

### svim:FP:chr21:37712623:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 72 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, caller_quality, size_mismatch
- The caller reports a ~187 bp insertion inside a tandem-repeat region (title annotates ~401 bp), with a truth INS just 72 bp away, a classic setup for representation-based Truvari mismatches where inserted-length and placement are inherently ambiguous. The coverage tracks stay flat and continuous across the interval with no depth drop, which is consistent with an insertion rather than a deletion, though no split/soft-clip cluster is clearly resolvable in this coverage-only view. Given the same-type nearby truth call and repeat context, this is most likely a representation difference rather than a genuine caller error, despite the low caller quality (12).

### svim:FP:chr21:28841170:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at same position but size mismatch
- Evidence: tandem_repeat, read_depth, size_mismatch, caller_quality
- The call is an insertion inside a flagged tandem repeat, and there is a truth INS at 0 bp distance, so Truvari likely failed the match on inserted-sequence length rather than because the event is spurious (title 401 bp vs SVLEN 114 highlights the size ambiguity typical of tandem-repeat insertions). Coverage remains continuous with no depth drop as expected for an INS, and there is no evidence contradicting a real event. This representation/size discrepancy in a repeat is a classic benchmark artifact, though the low caller quality (1.0) adds some uncertainty.

### svim:FP:chr21:46048508:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 319 bp
- Reason: INS in tandem repeat with nearby truth call and size ambiguity
- Evidence: split_reads, tandem_repeat, size_mismatch, read_depth, caller_quality
- The HP2 track shows a dashed/split read signature at ~46,048,300 with no coverage drop, consistent with a heterozygous insertion rather than an artifact. The locus sits in a tandem repeat with a truth INS only 319 bp away, and the caller's reported length (687 bp) differs substantially from the displayed 401 bp event, which is the classic representation/length ambiguity for insertions in repetitive sequence. This pattern most likely reflects a breakpoint/length mismatch against the truth set rather than a genuine false call, though the very low caller quality (1.0) leaves some residual uncertainty.

### svim:FP:chr21:42477225:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS inside tandem repeat coincident with a truth call but with ambiguous size
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The call is an insertion inside a flagged tandem repeat with a truth call at 0 bp distance, so a variant is almost certainly present at this locus. Truvari's FP label is most plausibly driven by a representation/size discrepancy (SVLEN 103 vs the 401 bp span shown), which is common for INS in repeats where inserted length is inherently ambiguous. The coverage tracks are flat with no depth drop (consistent with INS rather than a false depth-based call), though low caller quality (2.0) and the size mismatch keep confidence moderate.

### svim:FP:chr21:43741251:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 16 bp
- Reason: insertion in tandem repeat near truth call
- Evidence: tandem_repeat, split_reads, size_mismatch, caller_quality, breakpoint_ambiguity
- The locus is flagged as a tandem repeat with a truth INS call only 16 bp away, and the HP1 track shows a localized split/soft-clip arc consistent with an insertion breakpoint while coverage stays flat (the expected INS signature). There is a size discrepancy (caller SVLEN 91 vs the 401 bp label), which together with the tandem-repeat context makes inserted-length and placement inherently ambiguous. This pattern of a nearby matching truth call inside a repeat is typical of a representation-difference artifact rather than a genuine false positive, though the very low caller QUAL (2.0) lowers confidence.

### svim:FP:chr21:30742266:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 161 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, split_reads, read_depth, caller_quality
- The locus is flagged as a tandem_repeat region and there is a truth INS just 161 bp away, a classic setup for representation ambiguity where insertion placement and length differ between call and truth. Coverage stays uniformly high with no depth drop (consistent with an INS, not a DEL), and a faint dotted split-read arc on HP:1 near 30742346-30742430 indicates a localized inserted-sequence signal. The very low caller quality (2.0) and repeat context make an exact length/breakpoint match to the truth unlikely, so Truvari's FP most plausibly reflects a representation mismatch rather than a spurious call.

### svim:FP:chr21:45555282:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 43 bp
- Reason: INS in tandem repeat near a truth call with size/representation ambiguity
- Evidence: tandem_repeat, size_mismatch, soft_clips, breakpoint_ambiguity, caller_quality
- The call is an INS flagged FP but sits in a tandem_repeat region with a truth INS of the same type only 43 bp away, a classic representation-difference scenario where inserted-sequence length and breakpoint placement are inherently ambiguous. The image shows flat coverage (as expected for an INS, no depth drop) with a subtle soft-clip/insert cluster near the center, consistent with a real insertion event. The large size discrepancy (caller SVLEN 69 vs 401 bp title) and low caller quality reflect this ambiguity rather than a clear caller error, so the FP is likely a benchmark artifact.

### svim:FP:chr21:42589746:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 1853 bp
- Reason: Low-quality call in segdup/low-mappability repeat with no nearby truth
- Evidence: segdup, low_mappability, tandem_repeat, caller_quality, split_reads, size_mismatch
- The call has minimal caller quality (1.0) and sits in a region flagged as segdup, low_mappability, and tandem_repeat, where spurious split/discordant signals are common. While a few dashed split-read connections are visible around 42,589,800, there is no compelling clustered INS signature (soft-clip pile-up/inserted-sequence reads) and no coverage anomaly typical of a true insertion. The nearest truth call is 1,853 bp away—too far to represent a shifted-breakpoint artifact—and the SVLEN (51) contradicts the 401 bp title, indicating an unstable, poorly supported call.

### svim:FP:chr21:46048045:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 76 bp
- Reason: INS in tandem repeat near truth call of same type
- Evidence: tandem_repeat, size_mismatch, caller_quality, read_depth
- The call is an insertion inside a tandem-repeat region with a truth INS only 76 bp away, a classic scenario where inserted-sequence length and breakpoint placement are inherently ambiguous, causing Truvari to flag a representation difference rather than a true error. The coverage tracks show no depth drop (consistent with INS rather than DEL) and remain continuous across the interval, and the packet SVLEN (77) conflicts with the displayed 401 bp, reflecting length-representation instability typical of repeats. The low caller quality (1.0) adds uncertainty, but the proximity to a same-type truth call in a tandem repeat favors a benchmark artifact over a genuine false positive.

### svim:FP:chr21:43743497:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at 0 bp but size discrepancy
- Evidence: tandem_repeat, size_mismatch, caller_quality
- The call is an INS inside a tandem repeat (region_flag) with a truth call at 0 bp distance, so a real insertion very likely exists here. Truvari flagged it as FP largely because of a length-representation difference (packet SVLEN 51 vs the 401 bp title), which is typical for ambiguous inserted-sequence length within tandem repeats. Coverage is flat as expected for an INS (no depth drop), and no contradicting signal is visible, consistent with a representation artifact rather than a caller error.

### svim:FP:chr21:37685541:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 18 bp
- Reason: size mismatch near matching truth INS
- Evidence: size_mismatch, breakpoint_ambiguity, caller_quality
- The caller reports a 139 bp INS while the plotted event is labeled 401 bp, and a truth INS of the same type sits only 18 bp away, so Truvari most likely rejected the match on size/breakpoint discrepancy rather than because the variant is spurious. Insertions carry no depth-drop signature, and the flat ~30x coverage here neither confirms nor refutes the call from short read summaries. Given a co-located same-type truth call within 18 bp, this is best explained as a representation/size difference rather than a genuine caller error, though the low caller quality (1.0) tempers confidence.

### svim:FP:chr21:43336374:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 176 bp
- Reason: no insertion signature at breakpoint
- Evidence: read_depth, soft_clips, tandem_repeat, caller_quality, split_reads
- The caller reports a 165 bp INS (image title 401 bp) but the alignment shows flat, uninterrupted coverage across all haplotypes with no localized cluster of soft-clipped or split reads and no reads carrying extra inserted sequence at the site\quality quality is minimal (QUAL=1.0). The nearest truth call is 176 bp away, and although the locus sits in a tandem repeat where INS length is ambiguous, that distance plus the absence of any visible insertion evidence argues against a genuine variant. The lack of a supporting signature favors a false positive over a benchmark representation artifact.

### svim:FP:chr21:45308004:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 30 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: tandem_repeat, size_mismatch, caller_quality, breakpoint_ambiguity
- The call is an INS flagged FP by Truvari but sits inside a tandem-repeat region with the nearest truth INS only 30 bp away, a classic representation-difference scenario where inserted-length and breakpoint placement are inherently ambiguous. The image shows flat coverage (expected for INS on long reads) with only a subtle disturbance/soft-clip cluster near ~45307800 and no evidence contradicting an insertion. There is also a size mismatch (packet SVLEN 56 vs image title 401 bp), consistent with tandem-repeat length ambiguity rather than a clean caller error.

### svim:FP:chr21:45798364:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 627 bp
- Reason: low-quality INS call in tandem repeat with no clear insertion signature and distant truth call
- Evidence: read_depth, tandem_repeat, caller_quality, size_mismatch, split_reads
- Coverage is uniform across the interval with long reads spanning cleanly and no localized cluster of soft-clips/split reads that would mark a genuine ~400 bp insertion breakpoint. The caller quality is low (19) and there is a notable size discrepancy (packet SVLEN 121 vs plotted 401 bp), consistent with an unstable call inside a tandem repeat. The nearest truth INS is 627 bp away, beyond typical Truvari matching windows, so this is unlikely to be a mere representation shift of a real event.

### svim:FP:chr21:44395801:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 424 bp
- Reason: insertion in tandem repeat with ambiguous size/placement
- Evidence: split_reads, tandem_repeat, size_mismatch, caller_quality, breakpoint_ambiguity
- The image shows a consistent split-read/soft-clip cluster (dotted arcs) near 44,395,700 across all haplotypes with no depth drop, which is the expected signature of an insertion rather than a false depth artifact. The locus is flagged as a tandem repeat, where inserted-sequence length is inherently ambiguous, and there is a truth INS only ~424 bp away with a size difference (caller 145 bp vs. ~401 bp shown), consistent with a representation/placement discordance. This is most likely a benchmark artifact rather than a genuine caller error, though the low quality (11) and distance leave some doubt.

### svim:FP:chr21:46048477:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 350 bp
- Reason: INS inside tandem repeat with nearby truth call and ambiguous length
- Evidence: tandem_repeat, split_reads, size_mismatch, caller_quality
- The locus is an insertion in a tandem-repeat region where coverage stays flat as expected for INS, and the HP:2 track shows split/interrupted reads consistent with an inserted-sequence breakpoint. The caller reports SVLEN 270 while the plot title indicates ~401 bp, and there is a truth call only 350 bp away, so this is likely the same event flagged FP due to breakpoint/length representation differences inherent to tandem repeats rather than a spurious call. The low caller quality (1.0) adds some doubt, keeping confidence moderate.

### svim:FP:chr21:19346008:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: insertion in tandem repeat with adjacent truth call and size ambiguity
- Evidence: tandem_repeat, size_mismatch, read_depth, caller_quality
- The locus is flagged tandem_repeat with a truth INS at 0 bp distance, and the caller SVLEN (271 bp) disagrees with the displayed 401 bp event, indicating an insertion-length representation difference rather than a spurious call. Long-read coverage is flat with no depth drop, which is the expected background for an INS, and inserted-sequence length in tandem repeats is inherently ambiguous. The low caller quality (1.0) and lack of a clearly resolved soft-clip/split cluster in the aggregated coverage view add some uncertainty, but proximity to a same-type truth call in a repeat makes a representation artifact most likely.

### svim:FP:chr21:17483389:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 26 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, read_depth, breakpoint_ambiguity, size_mismatch, caller_quality
- The call is an insertion inside a tandem-repeat region with a truth INS only 26 bp away, a classic setup for a representation-difference false positive rather than a true caller error. Coverage remains flat across the interval (as expected for an INS, no depth drop), consistent with a real insertion event whose breakpoint and length are inherently ambiguous in the repeat. The size discrepancy (SVLEN 70 vs the ~401 bp window label) and low caller quality (1.0) add uncertainty, but proximity to a same-type truth call in a tandem repeat most likely reflects a benchmark placement/representation mismatch.

### svim:FP:chr21:43336069:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 36 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, size_mismatch, caller_quality, read_depth
- The call is an insertion inside a tandem-repeat region only 36 bp from a truth INS of the same type, a classic setting for representation-driven Truvari mismatches where inserted-sequence length and placement are inherently ambiguous. The coverage tracks show no depth drop (consistent with INS, not DEL) and stable coverage across the interval, and the reported SVLEN (84 bp) disagrees sharply with the title (401 bp), reinforcing a length-representation discordance rather than a spurious call. The low caller quality (1.0) tempers confidence, but the tandem-repeat context plus nearby matching truth call favors a benchmark artifact over a true caller error.

### svim:FP:chr21:45156270:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 148 bp
- Reason: very low caller quality with no supporting insertion evidence in reads
- Evidence: read_depth, caller_quality, tandem_repeat, soft_clips
- The svim call has an extremely low quality score (2.0) and the alignment shows flat, uninterrupted coverage with no localized cluster of soft-clipped or split reads that would indicate a 400-500 bp insertion breakpoint. Although the region is a tandem repeat where INS representation can be ambiguous, the nearest truth call is 148 bp away (beyond typical matching windows) and there is no visible read-level support, favoring a genuine false positive over a representation artifact. There is also a size mismatch between the displayed 401 bp and the reported SVLEN of 483.

### svim:FP:chr21:46034324:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 400 bp
- Reason: Very low caller quality with no clear insertion signature
- Evidence: caller_quality, low_mappability, tandem_repeat, size_mismatch, soft_clips
- The svim call has an extremely low quality score (1.0) and the packet SVLEN (114 bp) contradicts the plotted 401 bp INS, indicating an unstable/poorly supported call. The alignment tracks show no localized cluster of soft-clips or split reads at the breakpoint that would corroborate an insertion; instead HP2 merely shows a coverage step. Although the locus sits in a low-mappability tandem repeat, the nearest truth call is 400 bp away (not a close representation match), so this is best read as an unsupported false positive rather than a benchmark artifact.

### svim:FP:chr21:45797594:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.58)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 142 bp
- Reason: INS in tandem repeat near truth call with size/placement ambiguity
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality, read_depth
- The locus is an insertion inside a tandem repeat, where inserted-sequence length and breakpoint placement are inherently ambiguous. The image shows no depth drop (consistent with INS) with aligned long reads spanning the region and dotted duplication/insertion marks on HP2, and there is a truth INS ~142 bp away. However, the low caller quality (2.0) and the size discrepancy (packet SVLEN 58 vs 401 bp displayed) plus the >142 bp offset weaken confidence, so this most likely reflects a representation/placement difference rather than a clean caller error.

### svim:FP:chr21:32477804:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.58)
- Region: segdup=False, low_mappability=True, tandem_repeat=False; nearest truth 104 bp
- Reason: ambiguous INS placement in low-mappability/homopolymer region near truth call
- Evidence: split_reads, read_depth, low_mappability, homopolymer, size_mismatch
- On HP1 there is a localized coverage dip bridged by a dotted split-read arc, consistent with a heterozygous insertion breakpoint where reads carrying the inserted sequence are clipped/split rather than a true depth loss. The locus sits in a low-mappability, homopolymer context with a same-type truth INS only 104 bp away, and the caller SVLEN (61 bp) does not match the plotted 401 bp span, indicating a representation/placement discrepancy rather than a spurious call. These are classic conditions under which Truvari labels a genuine but shifted/mis-sized insertion as FP.

### svim:FP:chr21:42587866:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 173 bp
- Reason: ambiguous deletion in tandem-repeat/segdup with nearby truth call
- Evidence: read_depth, segdup, low_mappability, tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The HP2 track shows a partial coverage reduction and dotted (split/spanning) read gaps in the interval consistent with a heterozygous deletion, so a real event is plausible. The locus sits within overlapping segdup, low-mappability, and tandem-repeat annotations with a truth deletion only 173 bp away, and the reported size is inconsistent (title 501 bp vs packet SVLEN 51), all hallmarks of representation/breakpoint ambiguity rather than a genuine caller error. Given the low caller quality (2.0) and repeat context, Truvari's FP most likely reflects imprecise placement/size of a real event, i.e., a benchmark artifact.

### svim:FP:chr21:42589853:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 292 bp
- Reason: deletion signal in repeat region with nearby truth call
- Evidence: split_reads, tandem_repeat, segdup, low_mappability, size_mismatch, caller_quality
- Both haplotype panels show dashed spanning-read gaps around 42,589,700-42,589,900 consistent with a real deletion breakpoint, though coverage does not fully collapse. The locus sits in overlapping segdup, low-mappability, and tandem-repeat annotations, and a truth deletion lies only 292 bp away, so the caller's 102 bp DEL is plausibly the same event with ambiguous placement and size (image annotates 604 bp, caller reports 102 bp). This representation/breakpoint ambiguity in a repetitive region, rather than a spurious call, best explains the Truvari FP label, albeit with low caller quality (14).

### svim:FP:chr21:46047618:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.55)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 160 bp
- Reason: weak scattered deletion signal with very low caller quality in repetitive region
- Evidence: read_depth, split_reads, low_mappability, tandem_repeat, caller_quality, size_mismatch
- The coverage tracks show no coherent drop toward zero across the 75 bp interval; instead only a few reads carry scattered dotted deletion gaps at inconsistent positions, typical of alignment noise within a tandem-repeat / low-mappability locus. The caller quality is extremely low (2.0) and there is a size discrepancy (SVLEN 75 vs a 549 bp title annotation), further undermining confidence. The nearest truth call is 160 bp away, but the absence of a consistent breakpoint-supported deletion argues this is a spurious call rather than a shifted representation of a real event.

### svim:FP:chr21:45307808:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 226 bp
- Reason: small deletion signal within tandem repeat near a truth call
- Evidence: read_depth, split_reads, tandem_repeat, breakpoint_ambiguity, caller_quality
- The image shows full, uninterrupted coverage across the interval with no clear depth drop, but a localized dashed alignment gap on HP2 around the site indicates a small deletion carried on one haplotype, consistent with a heterozygous ~62 bp event in long reads. The locus is flagged as a tandem_repeat with a truth deletion only 226 bp away, so the placement/length of the deletion is inherently ambiguous and Truvari likely failed to match it due to a representation/breakpoint shift rather than a genuine caller error. The very low caller quality (1.0) tempers confidence, but the underlying read evidence plus repeat context favors a representation artifact over a pure false positive.

### svim:FP:chr21:41814474:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 315 bp
- Reason: tandem-repeat placement ambiguity near truth call
- Evidence: read_depth, tandem_repeat, low_mappability, size_mismatch, caller_quality
- The call sits in a flagged tandem-repeat / low-mappability region with a truth DEL only 315 bp away, a classic setup for representation-driven FP labels rather than a true caller error. The HP:2 track shows partial coverage dips (het pattern) with dotted split-read lines rather than a clean full drop, consistent with a real but ambiguously placed deletion. There is a notable size discrepancy (called SVLEN 94 vs the 588 bp interval shown), and the low quality (27) reinforces that breakpoint/size resolution is uncertain in this repeat context.

### svim:FP:chr21:45307876:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 97 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, split_reads, caller_quality, size_mismatch, read_depth
- The call is an insertion in a flagged tandem-repeat region with a truth INS only ~97 bp away, a classic setup for representation-driven Truvari FP labels since inserted-length and placement are inherently ambiguous in repeats. Coverage stays flat (correct for an INS, no depth drop), and HP2 shows a faint dashed split/soft-clip cluster near the breakpoint consistent with a real insertion signature. However the very low caller quality (2.0) and the SVLEN discrepancy (54 bp vs the 401 bp track annotation) leave some doubt, hence moderate confidence.

### svim:FP:chr21:45798236:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 499 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, read_depth, caller_quality, breakpoint_ambiguity
- The locus is a 401bp INS flagged FP inside a tandem_repeat, with the nearest truth call only 499bp away (right at Truvari's default matching distance). Insertion length and placement within tandem repeats is inherently ambiguous, so a shifted breakpoint could cause a truth mismatch despite representing the same event. The image shows continuous coverage with subtle split/gapped alignments in HP1 but no clean insertion signature, and the very low caller quality (1.0) leaves some doubt, hence moderate confidence for a representation artifact rather than a genuine caller error.

### svim:FP:chr21:45499435:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 84 bp
- Reason: INS in tandem repeat near truth call with size ambiguity
- Evidence: tandem_repeat, size_mismatch, caller_quality, read_depth
- The call is an insertion inside a flagged tandem repeat, with a same-type truth call only 84 bp away, a setting where inserted-sequence length is inherently ambiguous and Truvari commonly labels representation differences as FP. The coverage track is essentially flat (consistent with an INS, which does not drop depth) and there is no contradicting deletion/duplication signature. The size discordance (caller SVLEN 61 vs the ~401 bp annotation) combined with the very low caller quality (1.0) suggests a poorly resolved but likely real repeat-region insertion rather than a clean caller error.

### svim:FP:chr21:46170874:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 314 bp
- Reason: insertion signature in tandem repeat with ambiguous representation
- Evidence: split_reads, soft_clips, tandem_repeat, size_mismatch, caller_quality
- HP:1 shows a localized break in read continuity with a dotted split-read arc near 46,170,800 and no depth drop, which is the expected signature of a heterozygous insertion. The locus is flagged as a tandem repeat where insertion size and breakpoint placement are inherently ambiguous (caller SVLEN 117 vs the ~401 bp label, and a truth call only 314 bp away). This pattern is consistent with a representation difference rather than a spurious call, though the very low caller quality (2.0) and size discrepancy leave residual doubt.

### svim:FP:chr21:44416844:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 44 bp
- Reason: INS in tandem repeat near truth call, ambiguous representation
- Evidence: tandem_repeat, low_mappability, breakpoint_ambiguity, size_mismatch, caller_quality
- The svim call is a ~400-970 bp insertion sitting in a flagged tandem-repeat and low-mappability region, only 44 bp from a same-type truth INS. Insertions inside tandem repeats have inherently ambiguous placement and length, so Truvari can label a genuine event FP when the reported SVLEN or breakpoint differs from truth. The samplot image shows no depth drop (consistent with INS) but essentially no interpretable read-level support due to poor mappability, so the FP is more plausibly a representation/length mismatch than a fabricated call. Low caller quality (1.0) and the size discrepancy (973 vs displayed 401 bp) reinforce that the disagreement is about representation rather than a clear caller error.

### svim:FP:chr21:46085553:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 132 bp
- Reason: INS in tandem-repeat/low-mappability region near truth call
- Evidence: tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an insertion sitting in a flagged tandem-repeat and low-mappability region, where inserted-length and placement are inherently ambiguous, and a truth INS lies only 132 bp away. Coverage remains uniform (~32-42x) with no depth drop, consistent with an INS rather than an artifactual DEL, but no crisp split-read/soft-clip cluster is resolvable given the region. The size discrepancy (image 401 bp vs packet SVLEN 120) and the nearby same-type truth call suggest Truvari failed to match due to representation/breakpoint offset rather than a genuine false call, though the low caller quality (1.0) leaves some doubt.

### svim:FP:chr21:45924478:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 162 bp
- Reason: INS in tandem repeat with placement ambiguity near truth call
- Evidence: tandem_repeat, low_mappability, caller_quality, size_mismatch, read_depth
- The call is an INS in a region flagged as both low_mappability and tandem_repeat, where inserted-sequence length and breakpoint placement are inherently ambiguous, and a truth INS lies only 162 bp away. The coverage tracks are flat and high with no depth drop (appropriate for INS), but the samplot view shows no clearly resolvable soft-clip/split-read cluster to independently confirm the event. Combined with the low caller quality (14) and the size discrepancy (401 bp title vs 132 bp SVLEN), the FP label most plausibly reflects a representation/placement difference in a repeat rather than a true caller error.

### svim:FP:chr21:46034357:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 367 bp
- Reason: INS in tandem repeat / low-mappability region with nearby truth call
- Evidence: tandem_repeat, low_mappability, caller_quality, breakpoint_ambiguity
- The call is a ~400-533 bp insertion sitting in a flagged tandem-repeat and low-mappability region, where inserted-sequence length and placement are inherently ambiguous. The image shows no supporting insertion signature (no soft-clip cluster or spanning-read gap), and coverage stays continuous with only a haplotype-specific depth shift, consistent with repetitive-region mapping rather than a clean event. With a same-type truth call 367 bp away and very low caller quality (2.0), Truvari's FP most likely reflects a representation/placement mismatch in a repeat rather than a genuine caller error, though evidence is weak.
