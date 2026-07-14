# SVBench AI review — sniffles_hg005

## Truvari benchmark (commodity metrics)

| precision | recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|
| None | None | None | None | None | None |

## The added layer — Claude's review of the discordances

> Claude attached an evidence-grounded reason to every reviewed discordance — the judgment a metrics-only benchmark cannot make.

- Discordant loci reviewed: **8**
- uncertain: 5 (62%)
- true_positive: 2 (25%)
- false_positive: 1 (12%)

## Per-locus explanations

### sniffles_hg005:QC:chr21:5227394:DEL
- Truvari: **QC** → Claude: **true_positive** (confidence 0.72)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: clear haplotype-specific split-read deletion signature
- Evidence: split_reads, read_depth, tandem_repeat, segdup, size_mismatch
- HP1 reads show a distinct gap bridged by split/spanning alignments (dashed connectors) around 5,227,400-5,227,560, consistent with a heterozygous deletion, while HP2 shows continuous coverage. Although the locus is flagged as segdup/low-mappability/tandem-repeat, the deletion signature is confined to a single haplotype and is well-supported. Note a size discrepancy between the plotted 649 bp title and the packet SVLEN of 125 bp, indicating some breakpoint/size ambiguity, but the underlying deletion appears real.

### sniffles_hg005:QC:chr21:5290633:INS
- Truvari: **QC** → Claude: **false_positive** (confidence 0.60)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: No insertion breakpoint signature in repeat-rich region
- Evidence: read_depth, tandem_repeat, segdup, low_mappability, size_mismatch
- The single haplotype track shows uniform ~45x coverage with no localized soft-clip, split-read, or insert-carrying read cluster at the stated breakpoint (5290633), which is what an INS should produce. The locus sits in overlapping segdup, low-mappability, and tandem-repeat context that commonly generates spurious INS calls. A size discrepancy also exists (title 401 bp vs packet SVLEN 171), and no supporting evidence is visible, so the call appears to be an alignment/repeat artifact.

### sniffles_hg005:QC:chr21:5292227:INS
- Truvari: **QC** → Claude: **true_positive** (confidence 0.60)
- Region: segdup=True, low_mappability=False, tandem_repeat=True; nearest truth None bp
- Reason: insertion split-read signature without depth drop
- Evidence: split_reads, read_depth, tandem_repeat, segdup, caller_quality
- Coverage remains flat across the interval with no depth drop, consistent with an insertion rather than a deletion. The HP:2 track shows dotted split-read/gapped signatures near the breakpoint (~5292147-5292307) indicating reads carrying inserted sequence at a single haplotype. The call sits in a segdup/tandem-repeat region which raises artifact risk, but the presence of a haplotype-restricted split signal plus reasonable caller quality (54) supports a real insertion, hence moderate confidence.

### sniffles_hg005:QC:chr21:5114310:INS
- Truvari: **QC** → Claude: **uncertain** (confidence 0.55)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: No visible insertion signature in a difficult region
- Evidence: read_depth, segdup, low_mappability, tandem_repeat, size_mismatch
- The samplot shows only coverage tracks with no discernible soft-clip, split-read, or insert-carrying read evidence at a single breakpoint, which is what an INS should produce. Coverage remains continuous (no depth drop, consistent with not being a deletion), but there is no positive support for the inserted sequence. The locus sits in segdup/low-mappability/tandem-repeat context, and there is a notable size discrepancy (title 401 bp vs packet SVLEN 120), so evidence is insufficient to confirm or reject the call.

### sniffles_hg005:QC:chr21:5285189:INS
- Truvari: **QC** → Claude: **uncertain** (confidence 0.55)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: repetitive region with no clear insertion signature and size mismatch
- Evidence: read_depth, size_mismatch, segdup, low_mappability, tandem_repeat, caller_quality
- The locus sits in a segdup / low-mappability / tandem-repeat region, and the coverage tracks show continuous depth without any clearly visible split reads, soft-clips, or insert-carrying long reads at the breakpoint that would confirm an insertion. There is also a size discrepancy (image title 401 bp vs packet SVLEN 171 bp), which raises breakpoint/size ambiguity. With only moderate caller quality (30) and no unambiguous insertion signature displayed, the evidence is insufficient to confirm or reject the call.

### sniffles_hg005:QC:chr21:5291200:INS
- Truvari: **QC** → Claude: **uncertain** (confidence 0.55)
- Region: segdup=True, low_mappability=False, tandem_repeat=True; nearest truth None bp
- Reason: weak/ambiguous insertion signal in repeat region with size mismatch
- Evidence: tandem_repeat, segdup, size_mismatch, breakpoint_ambiguity, read_depth
- Coverage is flat with no depth change, which is consistent with an INS, but the only supporting feature is a faint dotted arc near ~5290970 rather than a clear cluster of soft-clips or split reads at a defined breakpoint. The locus falls in both segdup and tandem-repeat context, and there is a notable size discrepancy (packet SVLEN 172 vs. displayed 401 bp), undermining confidence. The evidence is too ambiguous to confirm or reject a real insertion.

### sniffles_hg005:QC:chr21:5291569:INS
- Truvari: **QC** → Claude: **uncertain** (confidence 0.55)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: no visible insertion signature in repeat region
- Evidence: read_depth, tandem_repeat, segdup, low_mappability, size_mismatch
- Coverage is flat and uniform (~52x) across the entire window on HP2 with no discernible split reads, soft-clips, or insert-carrying evidence at the putative breakpoint. The call sits in overlapping segdup, low-mappability, and tandem-repeat context, which frequently produces spurious INS calls, and there is a size discordance (title 401 bp vs SVLEN 302). Without any clearly resolvable read-level insertion signature in this collapsed depth view, the evidence is insufficient to confirm a real event.

### sniffles_hg005:QC:chr21:5291745:INS
- Truvari: **QC** → Claude: **uncertain** (confidence 0.55)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: no visible insertion signature in repeat context
- Evidence: read_depth, tandem_repeat, segdup, low_mappability, size_mismatch
- The samplot shows only a smooth, uniform coverage envelope (~52x) on the HP:2 track with no visible soft-clips, split reads, or insert-carrying reads at the expected breakpoint that would confirm a 170 bp insertion. The call sits in overlapping segdup/low-mappability/tandem-repeat regions where such calls are prone to alignment artifacts, and there is a size discrepancy between the plotted title (401 bp) and the packet SVLEN (170 bp). Because long-read insertion evidence is not rendered as individual reads here, the coverage-only view is insufficient to either confirm or refute the variant.
