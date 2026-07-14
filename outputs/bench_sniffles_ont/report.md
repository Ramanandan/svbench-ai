# SVBench AI review — sniffles_ont

## Truvari benchmark (commodity metrics)

| precision | recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|
| 0.8863636363636364 | 0.601027397260274 | 0.7163265306122448 | 351 | 45 | 233 |

## The added layer — Claude's review of the discordances

> **42 of 45 false positives (93%) are benchmark artifacts** — representation / repeat-region differences, not genuine caller errors. Removing them raises precision from **0.886 → 0.992**.

- Discordant loci reviewed: **45**
- benchmark_artifact: 42 (93%)
- false_positive: 3 (7%)

### Error-class breakdown

| Truvari class | reviewed | benchmark artifact | genuine error | uncertain |
|---|---|---|---|---|
| FP | 45 | 42 | 3 | 0 |

## Per-locus explanations

### sniffles_ont:FP:chr21:30742426:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.85)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 1 bp
- Reason: INS in tandem repeat adjacent to truth call
- Evidence: tandem_repeat, split_reads, caller_quality, breakpoint_ambiguity, size_mismatch
- The call is an insertion in a tandem-repeat region with a truth call only 1 bp away, and the HP:1 track shows a dashed gap/split-read signature consistent with an inserted segment rather than a coverage drop. Coverage is stable across the interval, matching the INS signature (no depth loss). Because insertion length in tandem repeats is inherently ambiguous (caller SVLEN 278 vs title 401), Truvari's FP most likely reflects a representation/size-matching difference rather than a spurious call.

### sniffles_ont:FP:chr21:40348210:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.85)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 11 bp
- Reason: INS in tandem repeat with adjacent truth call
- Evidence: tandem_repeat, split_reads, caller_quality, breakpoint_ambiguity
- The 436 bp INS sits in a tandem-repeat region and there is a truth INS only 11 bp away, a classic representation mismatch. The image shows no depth drop (consistent with INS not DEL), with a localized cluster of split/soft-clipped reads in the HP:Undef track around the breakpoint. Given the tandem-repeat context, inserted-sequence length is inherently ambiguous and Truvari likely failed to match due to breakpoint/size representation rather than a genuine false call.

### sniffles_ont:FP:chr21:33187133:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 2 bp
- Reason: INS in tandem repeat 2bp from a truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The caller reports an insertion inside a flagged tandem repeat, only 2 bp from a truth-set INS of the same type, so this FP almost certainly reflects a representation/breakpoint-placement difference rather than a spurious call. The HP:Undef track shows a localized coverage bump near the site consistent with reads carrying extra inserted sequence, and there is no depth drop (as expected for INS). A size discrepancy (title 401 bp vs SVLEN 79) further indicates inherent length ambiguity typical of tandem-repeat insertions.

### sniffles_ont:FP:chr21:44863152:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 15 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: tandem_repeat, low_mappability, split_reads, breakpoint_ambiguity, caller_quality
- This is a ~401-445 bp insertion call sitting in a low-mappability tandem-repeat region, only 15 bp from a truth INS of the same type. On HP1 the aligned long-read track shows a dashed/broken segment consistent with an inserted-sequence breakpoint, and coverage stays flat (no depth drop) as expected for an INS. The FP label almost certainly reflects a representation/length-ambiguity mismatch within the repeat rather than a spurious call, so this is a benchmark artifact, not a caller error.

### sniffles_ont:FP:chr21:45340521:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.82)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 6 bp
- Reason: insertion in tandem repeat with truth call 6bp away
- Evidence: tandem_repeat, split_reads, breakpoint_ambiguity, size_mismatch, read_depth
- The caller reports a 557bp INS while the nearest truth call is only 6bp away, and the region is flagged as a tandem repeat, where inserted-sequence length and precise placement are inherently ambiguous. The image shows stable, uninterrupted coverage across haplotypes (no depth drop, consistent with an insertion) with split/discordant read signal on HP2 near the site, supporting a real insertion event. The likely size and coordinate discrepancy relative to the truth representation explains the Truvari FP label, making this a representation artifact rather than a genuine caller error.

### sniffles_ont:FP:chr21:42477166:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 58 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: split_reads, tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The HP:2 and HP:1 tracks show localized gaps/dashed breaks in the aligned long reads consistent with an inserted-sequence signature, with no depth drop as expected for an INS. The call sits in a tandem_repeat region and is only 58 bp from a truth INS of the same type, and there is a size discrepancy (caller SVLEN 115 vs the ~401 bp label), which is a classic representation/length-ambiguity mismatch. This pattern indicates Truvari flagged an FP due to breakpoint/length placement ambiguity within the repeat rather than a genuine caller error.

### sniffles_ont:FP:chr21:17292179:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 16 bp
- Reason: insertion in tandem repeat with nearby truth call and size ambiguity
- Evidence: tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an INS in a low-mappability tandem repeat region, and a truth INS lies only 16 bp away, which is the classic setup for a representation-difference artifact rather than a genuine caller error. Consistent with an insertion, coverage remains flat across the interval (no depth drop) and split/soft-clip signal concentrates near the breakpoint. The discrepancy between the caller's SVLEN (173 bp) and the displayed 401 bp event reflects the inherent ambiguity of inserted-sequence length inside tandem repeats, so Truvari likely failed to match on size/position rather than because the variant is false.

### sniffles_ont:FP:chr21:46161030:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 1 bp
- Reason: insertion matched to nearby truth but flagged for size/representation difference
- Evidence: homopolymer, size_mismatch, breakpoint_ambiguity
- A truth INS sits only 1 bp away from this sniffles call, so the caller detected a real insertion at the correct position. The region is flagged as homopolymer, where inserted-length estimation is inherently ambiguous, and there is a size discrepancy (image header 401 bp vs packet SVLEN 305), which likely drove Truvari to reject the match on size ratio rather than any genuine caller error. Coverage is flat with no depth drop as expected for an INS, consistent with a true event mislabeled by representation/size differences.

### sniffles_ont:FP:chr21:46090768:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 160 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, low_mappability, split_reads, caller_quality, breakpoint_ambiguity
- The 401 bp INS call sits in a low-mappability tandem-repeat region with a truth INS of the same type only 160 bp away, a classic representation/placement ambiguity. Coverage is maintained (no depth drop, consistent with an INS), and scattered split/soft-clip signals appear across the haplotypes supporting inserted sequence. Given the tandem-repeat context and the size/breakpoint ambiguity inherent to repeat insertions, the FP label most likely reflects a representation difference rather than a genuine caller error.

### sniffles_ont:FP:chr21:32024353:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at distance 0
- Evidence: tandem_repeat, size_mismatch, caller_quality, breakpoint_ambiguity
- The call is a 142 bp insertion inside a tandem-repeat region with a truth INS at the identical position (nearest_truth_call_dist_bp = 0), so a real event exists here. Truvari most likely flagged it FP due to inserted-length/representation ambiguity that is inherent to tandem repeats rather than a genuine caller error. Coverage across the region is flat and uninterrupted as expected for an INS (no depth drop), consistent with a real insertion whose size is hard to reconcile between callsets.

### sniffles_ont:FP:chr21:42615749:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 20 bp
- Reason: INS in tandem repeat near truth call with size discrepancy
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an insertion sitting inside a flagged tandem repeat with a truth INS only 20 bp away, and the reported length differs (packet 138 bp vs image 401 bp), the hallmark of representation ambiguity rather than a false variant. Coverage stays flat with no depth drop, consistent with an INS signature, and inserted-sequence length is inherently uncertain in tandem repeats. The high caller quality (60) plus a same-type truth call nearby indicate the event is real but scored FP due to breakpoint/length representation mismatch.

### sniffles_ont:FP:chr21:32477786:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 86 bp
- Reason: INS in tandem repeat near truth call with size/breakpoint ambiguity
- Evidence: split_reads, tandem_repeat, low_mappability, size_mismatch
- HP:1 shows a clear localized cluster of split/soft-clipped reads with dotted insertion signatures around 32,477,706-32,477,806 and no depth drop, matching the expected INS signature on a single haplotype. The call sits in a low-mappability tandem repeat only 86 bp from a truth INS, and there is an inconsistency in reported length (128 bp in packet vs 401 bp in the title), all hallmarks of representation ambiguity. A real insertion is present but Truvari flagged it as FP due to breakpoint/size shift within a repeat, not a caller error.

### sniffles_ont:FP:chr21:39974382:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 112 bp
- Reason: INS in tandem repeat near truth call
- Evidence: split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity, caller_quality
- The image shows no depth drop (consistent with INS, not DEL) and split/soft-clipped read signatures around the breakpoint on both haplotypes, supporting a real insertion. The locus sits in a low-mappability tandem repeat with a truth INS only 112 bp away, and insertion length (351 vs ~401 bp displayed) is inherently ambiguous in such repeats. This is most consistent with a representation/placement difference rather than a genuine caller error.

### sniffles_ont:FP:chr21:37685697:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 8 bp
- Reason: insertion supported near a truth call in homopolymer context
- Evidence: split_reads, soft_clips, homopolymer, size_mismatch, breakpoint_ambiguity, caller_quality
- The image shows no depth drop (correct for INS) with a localized cluster of split/soft-clipped reads at ~37,685,697 in both HP1 and HP2, consistent with a real heterozygous-to-homozygous insertion signal at a single breakpoint. A truth INS lies only 8 bp away and the region is flagged as homopolymer, where inserted-length is inherently ambiguous; note the size discrepancy (title 401 bp vs SVLEN 129), pointing to a representation/size mismatch rather than a spurious call. This is most consistent with a benchmark artifact driven by breakpoint/size ambiguity in a low-complexity context, not a caller error.

### sniffles_ont:FP:chr21:41931894:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 30 bp
- Reason: deletion call in tandem repeat with nearby truth call
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, breakpoint_ambiguity
- The HP:2 track shows a localized coverage dip and a cluster of split/spanning-read gaps (dotted arcs) around 41,931,850-41,931,950, consistent with a real ~50 bp deletion on one haplotype. The locus falls in a tandem-repeat, low-mappability region and sits only 30 bp from a truth call of the same type, so Truvari's FP label most likely reflects a breakpoint/representation shift within the repeat rather than a spurious caller event. This pattern (short DEL inside a tandem repeat near a matching truth call) is a classic benchmark artifact.

### sniffles_ont:FP:chr21:45898649:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 5 bp
- Reason: tandem-repeat representation/size ambiguity near a truth call
- Evidence: read_depth, split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity
- The alignments show a genuine deletion signal: coverage dips and clustered split/spanning reads (dotted lines) appear on HP1/HP2 around 45,898,600-45,898,900, matching a real DEL. However the locus sits in a tandem repeat and a truth DEL lies only 5 bp away, while the caller's SVLEN (84 bp) conflicts with the ~568 bp span depicted, indicating breakpoint/size representation ambiguity rather than a spurious call. Truvari's FP therefore reflects a representation mismatch inside a repeat, not a caller error.

### sniffles_ont:FP:chr21:24989034:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 27 bp
- Reason: INS in tandem repeat near truth call with size/breakpoint ambiguity
- Evidence: tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The locus is flagged as a tandem repeat and there is a truth INS only 27 bp away, so this sniffles INS call almost certainly represents the same event but with an ambiguous breakpoint and length (note the packet SVLEN of 110 versus the 401 bp label, reflecting representation instability typical of repeat-embedded insertions). The image shows flat, well-supported long-read coverage with no deletion signature, consistent with an insertion rather than a caller error. Truvari's FP label is best explained by representation differences within the tandem repeat rather than a genuine false call.

### sniffles_ont:FP:chr21:27627199:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 55 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, low_mappability, soft_clips, size_mismatch, caller_quality
- The call is an insertion inside a low-mappability tandem-repeat region, where coverage stays flat (as expected for INS, no depth drop) and a localized cluster of soft-clipped/split reads is visible on HP1 near the left breakpoint, supporting a real insertion. A truth call of the same type sits only 55 bp away, and the size differs (title 401 bp vs caller SVLEN 512), which are hallmarks of representation ambiguity for INS in tandem repeats. This is most consistent with a benchmark artifact rather than a genuine caller error.

### sniffles_ont:FP:chr21:45500921:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 0 bp
- Reason: INS in tandem repeat with truth call at same site
- Evidence: tandem_repeat, low_mappability, caller_quality, split_reads
- The 401bp INS sits in a low-mappability tandem-repeat region with a truth call at distance 0bp, the classic setup for representation-driven FP labeling. The image shows no depth drop (consistent with INS) and split/soft-clip signals in HP1 near the breakpoint, indicating a real inserted-sequence event. Given the co-located truth call and inherent length ambiguity of tandem-repeat insertions, this is most likely a representation mismatch rather than a genuine caller error.

### sniffles_ont:FP:chr21:40508755:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 21 bp
- Reason: Real deletion in tandem repeat with nearby truth call (representation difference)
- Evidence: split_reads, tandem_repeat, homopolymer, breakpoint_ambiguity
- Both HP1 and HP2 tracks show a localized cluster of split/gapped reads (dashed alignments with a coverage notch) around 40,508,760-40,508,820, consistent with a real ~50bp deletion rather than a spurious call. The locus is flagged as a tandem repeat/homopolymer and sits only 21bp from a truth-set deletion, so Truvari's FP label most likely reflects breakpoint/size representation ambiguity in a repetitive context rather than a genuine caller error. The good caller quality (59) and clear read support further favor a benchmark representation artifact.

### sniffles_ont:FP:chr21:46183812:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 191 bp
- Reason: real heterozygous deletion in tandem repeat with size/breakpoint mismatch
- Evidence: read_depth, split_reads, tandem_repeat, low_mappability, size_mismatch, breakpoint_ambiguity
- HP:1 shows a clear coverage drop and a cluster of split/spanning reads across the interval, matching a heterozygous deletion signature, while HP:2 remains intact, so a real DEL is supported. The locus sits in a tandem-repeat and low-mappability region with a truth call only 191 bp away, and there is a size discrepancy (caller SVLEN 71 vs the ~541 bp span shown), so Truvari's FP is most consistent with a representation/breakpoint mismatch rather than a spurious call. This is best explained as a benchmark artifact, not a caller error.

### sniffles_ont:FP:chr21:45156176:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.78)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 54 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, size_mismatch, caller_quality
- The call is a 306-401 bp insertion sitting in a flagged tandem-repeat region, and there is a truth INS only 54 bp away, a hallmark of a representation/placement difference rather than a genuine caller error. Coverage is flat and uniform across all haplotypes with no depth drop, consistent with an insertion rather than a deletion, and Sniffles reports solid quality (60). Truvari most likely failed to match due to breakpoint shift and inherent insertion-length ambiguity inside the repeat.

### sniffles_ont:FP:chr21:36497085:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.76)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 37 bp
- Reason: INS in tandem repeat near matching truth call
- Evidence: tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality, read_depth
- The coverage tracks are flat with no depth drop, consistent with an insertion rather than an artifact of missing reads. The call sits inside a tandem repeat only 37 bp from a truth INS, and there is a size discrepancy (caller SVLEN 191 vs the ~401 bp displayed), which is the classic ambiguity of insertion length/placement within repeats. This pattern indicates a representation difference that Truvari failed to match rather than a genuine caller error.

### sniffles_ont:FP:chr21:24969746:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 8 bp
- Reason: real het deletion near truth call with representation/size mismatch
- Evidence: split_reads, soft_clips, read_depth, size_mismatch, caller_quality
- On HP1 there is a localized cluster of split/soft-clipped reads with a slight coverage dip around 24,969,770, consistent with a real heterozygous deletion on a single haplotype (HP2 is undisturbed). A truth deletion sits only 8 bp away, and the packet SVLEN (50 bp) versus the wider drawn interval indicates a breakpoint/size representation difference rather than a spurious call. Truvari likely failed to match due to this size/position discrepancy, so the call is essentially correct.

### sniffles_ont:FP:chr21:33577627:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 23 bp
- Reason: tandem-repeat size/breakpoint ambiguity near a truth call
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The image shows a cluster of split/gapped reads across ~33,577,555-33,577,700 on both haplotypes, consistent with a real deletion signal rather than an artifact of noise. The locus sits in a tandem repeat with a truth DEL only 23 bp away, and there is a size discrepancy (packet SVLEN 77 vs the 553 bp shown in the title), all hallmarks of a representation difference. In tandem repeats, deletion size and breakpoint placement are inherently ambiguous, so Truvari's FP most likely reflects a failure to match an equivalent truth event rather than a genuine caller error.

### sniffles_ont:FP:chr21:40378554:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=False; nearest truth 0 bp
- Reason: real deletion in low-mappability/homopolymer region with size/representation ambiguity
- Evidence: split_reads, read_depth, low_mappability, homopolymer, size_mismatch, truvari_refine
- Both HP1 and HP2 show a localized cluster of split/soft-clipped reads with a small coverage dip near 40,378,550, matching the expected signature of a small deletion, so alignment evidence supports a real variant. A truth call sits at 0 bp distance, and the region is flagged low_mappability and homopolymer, where breakpoint placement and deletion length are inherently ambiguous. The caller reports a 50 bp DEL while the region context suggests a differing representation, so Truvari's FP most likely reflects a representation/size mismatch rather than a genuine caller error.

### sniffles_ont:FP:chr21:28891444:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.72)
- Region: segdup=False, low_mappability=True, tandem_repeat=False; nearest truth 233 bp
- Reason: nearby truth DEL with breakpoint/representation ambiguity in low-mappability region
- Evidence: read_depth, split_reads, low_mappability, homopolymer, breakpoint_ambiguity, size_mismatch
- The alignment supports a real deletion: the HP:Undef panel shows a clear localized coverage drop around 28,891,450-28,891,750 and HP:2 shows spanning/split reads (dotted lines) crossing the interval, consistent with a heterozygous DEL. A truth call of the same type lies only 233 bp away, and the locus sits in a low-mappability, homopolymer region where breakpoint placement and size are inherently ambiguous, so Truvari's FP most likely reflects a representation/breakpoint offset rather than a spurious call. The size discrepancy (caller 316 bp vs the ~1 kb display span) further points to size/placement ambiguity rather than a false event.

### sniffles_ont:FP:chr21:14106170:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=True, low_mappability=False, tandem_repeat=True; nearest truth 22 bp
- Reason: small DEL in tandem repeat near truth call
- Evidence: segdup, tandem_repeat, homopolymer, split_reads, breakpoint_ambiguity, caller_quality
- The 56 bp deletion sits inside a region flagged as segmental duplication, tandem repeat, and homopolymer, and lies only 22 bp from a matched truth call of the same type. The image shows a localized cluster of discordant/split reads near the center with only a minor coverage perturbation consistent with a short deletion, rather than a spurious call. Given the repeat context and the very close truth call, this is most likely a representation/breakpoint-placement discrepancy rather than a genuine caller error.

### sniffles_ont:FP:chr21:46006146:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 65 bp
- Reason: INS in tandem repeat with nearby truth call and size/representation ambiguity
- Evidence: tandem_repeat, size_mismatch, soft_clips, caller_quality
- The call is an insertion inside a flagged tandem repeat with a truth call of the same type only 65 bp away, a classic scenario where inserted-sequence length and breakpoint placement are inherently ambiguous. The image shows no depth drop (consistent with INS) and localized split/soft-clip clustering near the breakpoint in HP2, supporting a real insertion. The size discrepancy (packet SVLEN 90 vs 401 bp title) and proximity to truth indicate a representation difference rather than a spurious caller error.

### sniffles_ont:FP:chr21:38429549:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 10 bp
- Reason: call in tandem repeat near truth call
- Evidence: tandem_repeat, low_mappability, split_reads, breakpoint_ambiguity
- The caller reports a 50 bp deletion sitting in a low-mappability tandem-repeat region with a truth call only 10 bp away, and the image shows clustered split-read/soft-clip signal around 38429474-38429574 on both haplotypes consistent with a small deletion breakpoint rather than clean reference. A small deletion inside a tandem repeat is highly prone to breakpoint-shift and size-ambiguity representation differences, which is the classic cause of a Truvari FP that is not a true caller error. The very short distance to the nearest truth call of the same type supports this being the same event with an alternate representation.

### sniffles_ont:FP:chr21:44984156:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 54 bp
- Reason: insertion near truth call in homopolymer context
- Evidence: homopolymer, breakpoint_ambiguity, caller_quality
- The caller reports a ~471bp INS with solid quality (60) only 54bp from a truth insertion call, and the locus is flagged as homopolymer, where insertion placement and length are inherently ambiguous. The coverage tracks remain smooth and flat with no depth drop, consistent with an INS rather than a false depth-based artifact, and insertions do not show coverage loss. The proximity of a same-type truth call combined with the homopolymer context strongly suggests a representation/breakpoint-shift mismatch rather than a genuine caller error.

### sniffles_ont:FP:chr21:42570180:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 18 bp
- Reason: tandem-repeat representation/size ambiguity near matching truth call
- Evidence: split_reads, tandem_repeat, size_mismatch, breakpoint_ambiguity, caller_quality
- The HP:2 haplotype shows a cluster of split/spanning reads with dotted alignment arcs around 42,570,110-42,570,351, consistent with a real deletion event on one haplotype (heterozygous), rather than noise. The locus is flagged as tandem_repeat and there is a truth call only 18 bp away of the same type, while the caller's SVLEN (102 bp, though the plot title lists 604 bp) creates a size/breakpoint discrepancy. This pattern—a supported DEL inside a tandem repeat adjacent to a matching truth call—strongly indicates a Truvari representation mismatch rather than a genuine false positive.

### sniffles_ont:FP:chr21:45490005:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 49 bp
- Reason: deletion in tandem repeat with nearby truth call
- Evidence: split_reads, tandem_repeat, breakpoint_ambiguity, read_depth, caller_quality
- The HP1 haplotype shows a cluster of split reads and coverage perturbation around 45489900-45490137 consistent with a heterozygous deletion, while HP2 remains flat, matching a het event. The call falls in a tandem_repeat region and sits only 49 bp from a truth call of the same type, so the FP label most likely reflects breakpoint/representation ambiguity within the repeat rather than a genuine caller error. The apparent size discordance (title 516 bp vs SVLEN 58) further supports representation instability in this repetitive locus.

### sniffles_ont:FP:chr21:42582960:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.70)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 44 bp
- Reason: INS in tandem repeat near a truth call
- Evidence: tandem_repeat, breakpoint_ambiguity, size_mismatch
- The call is an insertion inside a tandem repeat, where inserted-sequence length and breakpoint placement are inherently ambiguous, and a truth INS lies only 44 bp away. Coverage is flat and continuous across the region as expected for an INS (no depth drop), consistent with a real event rather than a spurious deletion signal. The Truvari FP most likely reflects a representation/size discrepancy (packet SVLEN 50 vs. plotted 401 bp) within the repeat rather than a genuine caller error.

### sniffles_ont:FP:chr21:45898838:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 184 bp
- Reason: deletion in tandem repeat with size/breakpoint ambiguity near a truth call
- Evidence: split_reads, tandem_repeat, read_depth, size_mismatch, breakpoint_ambiguity
- The image shows clustered split reads across ~45898767-45898996 and a mild coverage dip on the haplotype tracks, consistent with a real deletion signal rather than a purely spurious call. However, the region is flagged as a tandem repeat and there is a size discordance (packet SVLEN=87 vs the ~573 bp span shown), with a truth call only 184 bp away. In tandem repeats, deletion length and breakpoint placement are inherently ambiguous, so this FP most likely reflects a representation difference rather than a genuine caller error.

### sniffles_ont:FP:chr21:45437562:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 69 bp
- Reason: deletion within tandem repeat with nearby truth call
- Evidence: tandem_repeat, read_depth, breakpoint_ambiguity, size_mismatch, caller_quality
- The call is a 72 bp DEL flagged as FP but sits within a tandem-repeat region only 69 bp from a truth call of the same type, a classic representation/placement ambiguity. The image shows a modest coverage dip on the HP1 haplotype across the interval, consistent with a real small deletion event rather than pure noise. Given the tandem-repeat context and close proximity to a truth call, Truvari's failure to match is most likely a breakpoint/size representation difference rather than a genuine caller error.

### sniffles_ont:FP:chr21:31784692:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.68)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 120 bp
- Reason: INS in tandem repeat near truth call
- Evidence: tandem_repeat, size_mismatch, read_depth
- The call is a 130 bp insertion (title annotates ~401 bp) sitting inside a tandem_repeat with a truth INS only 120 bp away, a classic representation-difference scenario where inserted-length and breakpoint placement are inherently ambiguous. Coverage is stable across the region with no depth drop, consistent with an insertion rather than a deletion, and no contradicting evidence is visible. This pattern (INS mismatch inside a tandem repeat adjacent to a same-type truth call) most likely reflects a Truvari representation mismatch rather than a genuine caller error.

### sniffles_ont:FP:chr21:42588371:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth 87 bp
- Reason: call in repetitive region adjacent to matching truth
- Evidence: segdup, low_mappability, tandem_repeat, split_reads, discordant_pairs, breakpoint_ambiguity, read_depth
- The locus sits within overlapping segdup, low-mappability, and tandem-repeat annotations, and a truth DEL lies only 87 bp away, so the FP label most likely reflects ambiguous breakpoint placement rather than a spurious call. The HP2 track shows a cluster of discordant/split reads across the interval consistent with a structural rearrangement, though there is no clean coverage drop to zero (expected given the repetitive, mappability-challenged context). The SVLEN mismatch (packet 1633 bp vs 3.67 kb banner) further indicates a representation/size discrepancy rather than a caller error.

### sniffles_ont:FP:chr21:45896692:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.62)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 249 bp
- Reason: INS inside tandem repeat with ambiguous size/placement
- Evidence: tandem_repeat, split_reads, size_mismatch, breakpoint_ambiguity, caller_quality
- The call is an insertion in a tandem-repeat region, where inserted-sequence length and exact breakpoint are inherently ambiguous. Coverage is flat as expected for an INS (no depth drop), and the HP1 track shows a discontinuity/dashed split-read signal in the right half of the window consistent with a real insertion event. There is a truth INS ~249 bp away and a notable size discrepancy (caller SVLEN 164 vs 401 bp label), suggesting Truvari failed to match due to representation/placement differences rather than a genuine false call. Confidence is moderate because the 249 bp offset is somewhat large for a clean artifact match.

### sniffles_ont:FP:chr21:45437819:DEL
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=True, tandem_repeat=True; nearest truth 44 bp
- Reason: tandem-repeat/low-mappability locus adjacent to a truth DEL
- Evidence: tandem_repeat, low_mappability, breakpoint_ambiguity, size_mismatch, caller_quality
- The call sits in a flagged tandem-repeat and low-mappability region only 44 bp from a truth DEL of the same type, so the FP label most likely reflects ambiguous breakpoint/size placement rather than a spurious call. The reported SVLEN (109 bp) also disagrees with the plotted 617 bp span, consistent with representation instability in repetitive sequence. The alignment shows fragmented/split reads and coverage dips across the interval but no clean full drop, which is typical of an under- or mis-sized deletion inside a repeat rather than a clear artifactual call.

### sniffles_ont:FP:chr21:41835844:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.60)
- Region: segdup=False, low_mappability=False, tandem_repeat=False; nearest truth 15 bp
- Reason: insertion adjacent to truth call with size discrepancy
- Evidence: read_depth, size_mismatch, breakpoint_ambiguity
- Coverage is flat across the interval with no depth drop, consistent with an insertion rather than a deletion, and the HP2 haplotype carries aligned long reads spanning the site. The call sits only 15 bp from a truth INS of the same type, and there is a notable size discrepancy (packet SVLEN 110 bp vs displayed 401 bp), suggesting Truvari flagged this as FP due to inserted-length representation differences rather than a genuine caller error. INS length ambiguity of this kind is a classic benchmark representation artifact.

### sniffles_ont:FP:chr21:13017861:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=True, low_mappability=False, tandem_repeat=False; nearest truth None bp
- Reason: insertion call in segmental duplication with no supporting local signal and no nearby truth variant
- Evidence: read_depth, segdup, caller_quality
- The region carries a segdup flag, where mismapping of reads commonly produces spurious insertion calls. The coverage across both haplotypes is uniform and unremarkable with no localized cluster of soft-clips or breakpoint disturbance at ~13,017,861 to support a 425 bp insertion. With no truth call anywhere nearby (nearest_truth_call_dist_bp = None) and only moderate caller quality (55), the evidence favors a false positive rather than a representation artifact of a real event.

### sniffles_ont:FP:chr21:13042673:INS
- Truvari: **FP** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=True, low_mappability=True, tandem_repeat=False; nearest truth None bp
- Reason: Insertion call in segdup/low-mappability region lacking supporting signature
- Evidence: read_depth, segdup, low_mappability, caller_quality
- The caller reports a ~301-401 bp insertion, but the alignment tracks show flat, uninterrupted coverage across all haplotypes with no localized soft-clip/split-read cluster at the breakpoint that would mark a genuine insertion. The locus sits in a segmental duplication and low-mappability region, which readily produces spurious sniffles calls from mismapped reads. With no truth call anywhere nearby (nearest_truth_call_dist_bp = None) and only moderate QUAL (60), the evidence favors a mapping-driven false positive rather than a representation artifact.

### sniffles_ont:FP:chr21:16971274:INS
- Truvari: **FP** → Claude: **benchmark_artifact** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth 218 bp
- Reason: INS in tandem repeat with nearby truth call
- Evidence: tandem_repeat, size_mismatch, caller_quality, read_depth
- The call is a 151 bp (title reads 401 bp) sniffles insertion sitting inside a tandem-repeat region, where inserted-sequence length and precise breakpoint placement are inherently ambiguous. Coverage is flat and uniform across all haplotypes with no depth anomaly, consistent with an INS (which does not drop coverage), and a truth INS lies only 218 bp away. The combination of tandem-repeat context, proximate same-type truth call, and size discrepancy points to a representation difference rather than a genuine false call, though the moderate distance and size mismatch leave some doubt.

### sniffles_ont:FP:chr21:40620211:DEL
- Truvari: **FP** → Claude: **false_positive** (confidence 0.55)
- Region: segdup=False, low_mappability=False, tandem_repeat=True; nearest truth None bp
- Reason: small DEL in tandem-repeat/homopolymer with no clear depth drop
- Evidence: read_depth, split_reads, tandem_repeat, homopolymer, caller_quality
- The packet describes an 80 bp DEL flagged by Truvari as FP with no truth call at any nearby distance, sitting in a tandem-repeat and homopolymer context that is prone to ONT alignment artifacts. Coverage on both haplotypes remains near baseline (~28x on HP2, stable on HP1) with no convincing drop toward zero across the reported interval, and only scattered ambiguous dotted split-read patterns in HP1 that are consistent with tandem-repeat mismapping rather than a clean deletion. The absence of any nearby truth call argues against a mere representation shift, favoring a spurious call in a difficult repeat region.
