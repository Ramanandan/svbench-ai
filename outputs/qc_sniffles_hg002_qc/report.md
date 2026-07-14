# SVBench AI review — sniffles_hg002_qc

## Truvari benchmark (commodity metrics)

| precision | recall | F1 | TP | FP | FN |
|---|---|---|---|---|---|
| None | None | None | None | None | None |

## The added layer — Claude's review of the discordances

> Claude attached an evidence-grounded reason to every reviewed discordance — the judgment a metrics-only benchmark cannot make.

- Discordant loci reviewed: **3**
- true_positive: 3 (100%)

## Per-locus explanations

### sniffles_hg002_qc:QC:chr21:5271424:DEL
- Truvari: **QC** → Claude: **true_positive** (confidence 0.90)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: Clear haplotype-specific coverage drop with spanning split read
- Evidence: read_depth, split_reads, population_support
- On HP:1 there is a distinct localized coverage drop toward zero across roughly 5,271,430-5,271,600 with a dotted arc indicating reads spanning the deleted segment, the canonical long-read deletion signature. The drop is haplotype-specific (absent on the other haplotype), consistent with a heterozygous DEL. A structurally matching SV is catalogued in dbVar and HGSVC, corroborating a recurrent real deletion here despite the segdup/tandem-repeat/low-mappability flags.

### sniffles_hg002_qc:QC:chr21:5227406:DEL
- Truvari: **QC** → Claude: **true_positive** (confidence 0.85)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: split-read deletion signature with strong population match
- Evidence: split_reads, read_depth, population_support, caller_quality
- The HP:2 haplotype track shows a clear cluster of split/gapped long-read alignments (dashed arcs) spanning the deletion interval around 5,227,400-5,227,550, consistent with a heterozygous deletion carried on one haplotype while HP:1 remains largely intact. Although the region is flagged segdup/low_mappability/tandem_repeat, the localized split-read signature is coherent and the locus matches a common gnomAD-SV/dbVar deletion (max_pop_AF=0.636), strongly corroborating a recurrent real SV. The reasonable caller quality (54) further supports the call despite minor breakpoint/size ambiguity between the 150 bp packet size and larger title annotation.

### sniffles_hg002_qc:QC:chr21:5253685:DEL
- Truvari: **QC** → Claude: **true_positive** (confidence 0.82)
- Region: segdup=True, low_mappability=True, tandem_repeat=True; nearest truth None bp
- Reason: split-read signature spanning deletion on one haplotype with population recurrence
- Evidence: split_reads, read_depth, population_support, segdup, low_mappability
- HP1 shows a clear split/spanning long-read alignment (black dotted arc) bridging the ~5,257kb-5,285kb interval, accompanied by a coverage reduction across the middle of the region consistent with a heterozygous deletion, while HP2 remains largely reference-like. Although the locus is flagged segdup/low_mappability/tandem_repeat, the split-read evidence is a genuine breakpoint signature rather than diffuse noise. A structurally matching, common SV in gnomAD-SV/dbVar (max_pop_AF=0.267) strongly corroborates that a real deletion recurs here, raising confidence. The exact size differs somewhat from the annotated coordinates, but the deletion signal itself is well supported.
