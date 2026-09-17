# Owner-supplied excerpts: a 2023 dissertation on single-cell TE quantification (recorded 2026-09-16)

The owner handed these excerpts verbatim as input for the te-tracks design and the single-cell TE
programme; the full method parameters and code sit in `/workspaces/Meta-Aging/01_modules/.ref/Thesis_2023`.
The owner's framing: keep the ideal in mind even where it is unattainable, for accurate TE
quantification and locus resolution in scRNA-seq, snRNA-seq and ATAC-seq.

## The datasets this programme serves (owner's table)

| dataset | chemistry | pipeline | compartment | matching | conditions | n per condition |
|---|---|---|---|---|---|---|
| 14616-DM spleen | 5′ PE OCM v3 | cellranger 9.0.1 | whole cells | same 20 animals as lung (per-mouse pairs, join on MouseID) | young, old, old+A, old+B, old+A+B | 4 mice (true biological replicates) |
| 14782-DM lung | 5′ PE OCM v3 | cellranger 10.0.0 | whole cells | same 20 animals as spleen, tissue pair per animal | young, old, old+A, old+B, old+A+B | 4 mice (true biological replicates) |
| 14761-DM spleen | Multiome ATAC+GEX v1 (ARC) | cellranger-arc 2.1.0 | nuclei | different animals (12 mice); matched to the others at condition level only | young, old, old+A, old+B; no old+A+B arm | 1 pooled library (3 mice pooled inside; condition ≡ library, no replicates) |

## Classification

> In general, each copy of a TE that exists in the genome can be described by its: class, subclass,
> superfamily, family, subfamily, and genomic coordinates. This classification system allows for the
> naming of newly discovered TE copies in ways that allow for easy recognition of characteristics that
> might be shared across related types of TEs [34,35]. This is especially important, given that many
> individual active TEs are species specific, but can be related to TEs found across the plant and animal
> kingdom. Examples of retrotransposon superfamilies include the aforementioned LINEs, SINEs, and
> ERVs. Finally, these superfamilies are then broken down into families and subfamilies which are a
> closely related group of elements based on sequence similarity and inferred common ancestry. This
> area of classification is often the most subjective with families and subfamilies varying widely in their
> size and specificity. By applying this classification system, each individual TE locus has a class,
> subclass, superfamily, family, and subfamily (if defined). For example, the HERVK9-int_dup720
> locus belongs to the HERVK9 subfamily, the ERVK family, the ERV superfamily, the LTR subclass,
> and the retrotransposons class (Class I)
>
> These facets of TE biology can be important to take into account when attempting to measure TE
> RNA expression, protein production, or transpositional activity. For example, attempting to assess
> the accumulation of RNA transcripts from a given TE can be difficult if only a portion of the TE is
> sequenced in a particular genomic profiling study
>
> many TE copies are located within the exons and introns of transcribed host genes, and might be
> transcribed as part of that gene in what's been termed "passive transcription". Thus, without
> additional information, it can be difficult to tell whether a TE sequence in a transcriptome study is
> derived from: passive transcription as part of another transcript; non-functional fragments that exist
> within other host genes or lncRNAs; or fully intact TE transcripts driven from that TE's promoter.

## The ideal single-cell TE method

> An ideal single-cell TE method should have the following properties with respect to TEs: accurate
> alignment, UMI correction that accounts for multi-mapping and multi-annotating reads, the ability to
> handle intron inclusion, and accurate assignment of ambiguous (i.e. multi-annotating) reads. Based on
> previous knowledge from bulk data, full alignment to the genome has been shown to produce the most
> accurate TE alignments, with the most accurate aligner overall being STAR [81], and EM-based
> approaches have been shown to perform best for resolution of multi-annotating reads. With respect to
> robust UMI correction, only one published method currently exists capable of correcting UMIs that
> accounts for multi-mapping and multi-annotating reads, the parsimonious UMI graph algorithm (PUG)
> introduced as part of the scRNA-Seq quantification method Alevin
>
> Since at the inception of this project no single-cell TE methods existed and all standard
> quantification pipelines lacked at least one of the essential aspects listed above, we sought to fill this
> gap in the field by developing our own method that sufficiently addressed each of these critical
> requirements. This involves using STARsolo for initial mapping, a stand-alone executable for UMI
> handling utilizing Alevin's parsimonious UMI graph method, and an EM algorithm adapted from our
> bulk TE tool, TEcount [82], for final processing of UMIs that remain ambiguous after UMI correction.
> Over the lifetime of this project, however, several developments have occurred that allow standard
> analysis pipelines to better address some of these critical issues as well as the release of TE centric
> scRNA-Seq quantification methods.

## Issues with scTE and SoloTE

> scTE does not specify how it handles gene-gene or TE-TE multi-annotating conflicts. scTE also works
> exclusively at the subfamily level by aggregating the individual loci of each TE subfamily together into
> what they dub a "metagene". This aggregation occurs at the read level, such that even if a read
> multi-maps to only the loci within a subfamily, it is considered as being uniquely annotated to that
> subfamily. After determining the potential annotations for each read, scTE follows a fairly simple
> prioritization scheme for annotation assignment. By default, it first assigns reads to gene exons if
> possible and then TEs if no gene exon can be found. This is known as "exclusive" mode. scTE also
> includes two other modes: "nointron mode" which is identical to exclusive mode except that all reads
> mapping to intronic TE loci are discarded, and "inclusive mode" where reads are assigned to both genes
> and TEs in the case where a TE overlaps a gene exon instead of giving the read exclusively to the gene.
> This prioritization scheme, however, leaves out two critical details: how intronic reads that do not
> overlap a TE are handled and how reads that either gene-gene or TE-TE multi-annotate are handled.
> This oversight is not addressed in either the paper or the online documentation for scTE
>
> SoloTE shares many of the same issues as scTE, however, including random selection of a single
> alignment for multi-mappers, blindly prioritizing gene assignments over TE assignments, and having no
> mechanism for addressing reads that remain ambiguous (gene-gene multi-annotators or TE-TE
> multi-annotators). Similar to scTE, however, SoloTE does not specify how gene-gene or TE-TE
> multi-annotators are handled. In summary, this prioritization scheme results in reads being assigned
> exclusively to genes whenever possible with the left-over reads assigned to either TE loci or subfamilies
> depending on whether or not they uniquely map.

## STARsolo

> STARsolo has continued to maintain feature parity with Cell Ranger while also developing its own set
> of advanced features. Its primary selling points include implementations of several top-performing
> single-cell algorithms from the literature, full control over all STAR parameters due to its direct
> integration with STAR (something not supported by Cell Ranger), and an EM algorithm for handling
> multi-mapping and multi-annotating reads. The EM algorithm in particular is one of STARsolo's
> defining features, making it the only single-cell quantification method available that uses full genomic
> alignment while also being capable of handling multi-mapping and multi-annotating reads.
> ... attractive candidate for single-cell TE quantification. Some of these important features include
> full genomic alignment using a custom set of TE-tuned parameters and appropriate handling of
> multi-mapping and multi-annotating reads (usually done via an EM)
>
> No unique modifications were necessary to quantify TEs with STARsolo. Our loci TE gtf was combined
> with the gene gtf during index generation. This results in each TE locus being annotated as its own
> "gene" with a single-exon transcript marking the loci's location. Alignment was performed using a
> combination of the GENCODE-recommended parameters and TE-optimized parameters that have been
> shown to produce the best results for bulk TE quantification [citing TEtranscripts]
>
> Since TEs often reside in the introns of genes, there are likely to be a substantial number of reads that
> multi-annotate between a TE locus and a gene intron

## Single-cell counting caveats

> In order to be able to quantify reads originating from retained introns, fully unspliced transcripts were
> used to construct the transcriptome index. While this allows for the handling of intronic reads, it will
> likely cause splice-junction spanning reads to not align. An additional caveat is that Alevin performs
> quantification at the transcript level. What this practically entails is that if two sets of reads map to
> the same gene but to different transcripts of that gene, they are counted as being distinct, even if they
> have the same UMI, resulting in that UMI being counted twice. Given that most scRNA-Seq data is
> highly sparse, both at the read and at the UMI-count level, gene-level quantification may be more
> robust than transcript-level quantification as there is often little evidence to support splitting a single
> observed UMI sequence over multiple transcripts.

## Annotations used

> Gene Annotations. The primary assembly annotation GTF from GENCODE release 40 (GRCh38.p13)
> was downloaded and then filtered using CellRanger mkgtf so that only annotations with the following
> biotypes were retained: protein_coding, lncRNA, IG_V_gene, TR_V_gene, IG_V_pseudogene, TR_J_gene,
> IG_D_gene, TR_V_pseudogene, IG_J_gene, TR_C_gene, IG_C_pseudogene, TR_D_gene, TR_J_pseudogene,
> and IG_J_pseudogene. The resulting GTF file was used to supply gene annotations to all methods and
> will be referred to as the "gene GTF". For the Alevin and Minnow transcriptomes, BEDtools [91] was
> used in conjunction with the gene GTF to extract all transcript sequences in their fully unprocessed
> form from the reference genome.
>
> TE Annotations. RepeatMasker [92] tables were downloaded from the UCSC genome database for
> GRCh38.p13 and converted into GTF format after removal of all annotations marked as
> "Low_complexity" or "Simple_repeat". When converting to GTF format, for each TE locus the
> subfamily name was used as the gene ID, the locus name was used as the transcript ID, and two
> additional fields were added for the family (family_ID) and class (class_ID) information. This
> annotation scheme results in each TE locus being annotated as a single-exon transcript belonging to
> its subfamily as a "gene" (Fig. 5). This GTF file was use to supply TE annotations to all subfamily-level
> methods and will be referred to as the "subfamily GTF". The subfamily GTF was then modified to create
> the "loci GTF" by altering the gene ID of each annotation so that it contained the locus name rather
> than the subfamily name. This results in an annotation scheme where each TE locus is annotated as a
> single-exon transcript of its own unique "gene" of the same name. This loci GTF was used to provide TE
> annotations to all locus-specific methods.

Parameters (STARsolo and STARsolo-EM): `outFilterMultimapNmax 100`, `winAnchorMultimapNmax 150`,
`soloType CB_UMI_Simple`, `soloFeatures GeneFull`, `soloUMIdedup 1MM_All`, `soloMultiMappers EM`,
`soloCellFilter EmptyDrops_CR`, plus the ENCODE recommended parameters.

> STARsolo was run in GeneFull mode to ensure that intronic sequences were counted. We opted to not
> use any of STARsolo's exon prioritization modes in order to avoid preferentially giving reads to
> intronic TEs. To ensure high-quality alignments, we used the ENCODE recommended mapping
> parameters along with modifications for preserving multi-mapping reads that have been shown to work
> best for TEs [citing TEtranscripts]

## Benchmark against synthetic data

> All entries that were zero in both the ground truth and the given count matrix were dropped. For
> EM-based methods, which report fractional counts, all counts were rounded half-to-even. For
> subfamily-level summaries of instance-level methods, counts were aggregated by subfamily before
> rounding. In the case of SoloTE, which reports a mix of locus and subfamily level results,
> locus-specific counts were aggregated with their corresponding subfamilies. Finally, each method was
> then profiled for accuracy, where we define an accurate call to be within 15% of the true value
>
> In terms of overall accuracy, EM-based methods strike the best balance of gene and TE accuracy. For
> TE accuracy alone, however, STARsolo has the highest TE accuracy rate largely due to its low TE false
> positive rate (Fig. 10). Locus-specific methods out-perform subfamily-level methods across the board,
> including both subfamily only methods and subfamily-level aggregation of locus-specific results. The
> TE-specific methods SoloTE and scTE are the two worst performers in terms of TE accuracy, with
> SoloTE largely suffering from over counting and scTE from a high false-negative rate
>
> Across both datasets accuracy on young (and thus harder to map) TEs is excellent for locus specific
> methods, often being just as high and in some cases higher than overall TE accuracy. The same cannot
> be said for subfamily-level methods, however. On the Minnow dataset subfamily-level methods tend to
> have worse young TE accuracy compared to overall TE accuracy (Fig. 13). Whereas on the Flux
> Simulator dataset they tend to have notably better accuracy on young TEs, especially for the
> subfamily-level only methods (Fig 14).
>
> The picture is much bleaker for gene-overlapping TEs, where all methods completely fail to handle
> them with even a modest degree of accuracy. Accuracy on intergenic TEs is excellent, however,
> routinely exceeding that of overall TE accuracy across all methods and on both datasets
>
> STARsolo performs fairly well on both datasets, having the top TE accuracy overall. This comes at a
> cost, however, as STARsolo has markedly lower gene accuracy when compared to methods with similar
> TE accuracy (Figs. 9 and 11). This result is somewhat surprising, as one would not expect discarding all
> multi-annotating reads to be such an effective strategy for TE quantification. This strategy achieves
> such high TE accuracy by having a very low TE false positive rate at the cost of high gene false
> negative and undercounting rates
>
> In terms of performance across datasets, STARsolo performs best on the Minnow dataset, having the
> top TE accuracy and tying for top TE recall with the Alevin family of methods (Fig. 9). Gene accuracy
> is markedly lower than other top TE performers, however, due to a high gene false negative rate
> (Fig. 29). Taken together, this indicates that discarding multi-annotators has a significantly more
> detrimental effect on genes than TEs in the Minnow dataset. Performance is more mixed when it comes
> to the Flux Simulator dataset, with both gene and TE accuracy rates significantly lower than in the
> Minnow data (Figs. 9 and 11). Genes and TEs seem to suffer more equally from discarding
> multi-annotators, with both being affected by elevated rates of undercounting and false negatives.
> STARsolo has nearly identical TE accuracy rates to the other three locus specific methods, but has
> noticeably lower TE recall due to its abnormally high TE false negative rate. (Fig. 28) This decreased
> performance is likely due to the greater prevalence of gene-TE overlap in the Flux Simulator dataset,
> causing the discarding of multi-annotating reads to more heavily impact genes and TEs alike.
>
> In terms of overall accuracy, we find that the EM-based methods, Alevin, Alevin-Fry, and STARsolo-EM,
> produce the best balance between gene and TE accuracy on both datasets. In terms of TE accuracy
> alone, however, we find that STARsolo has the top accuracy on the Minnow dataset and nearly identical
> accuracy to the EM-based methods on the Flux Simulator dataset. This is fairly surprising given that,
> rather than attempting to handle multi-annotating reads, as the more sophisticated methods do, it
> simply discards them instead. This TE accuracy comes at a cost, however, as STARsolo has markedly
> lower gene accuracy when compared to methods with similar TE accuracy
>
> Parsimonious UMI Graph Algorithm Resolution. Given that Alevin and Alevin-Fry had near-identical
> performance across both datasets, we do not find any evidence to suggest that there is a benefit to
> choosing either the gene or the transcript level of resolution when implementing the parsimonious
> UMI graph algorithm.
>
> Gene-TE disambiguation. We find that none of the methods tested were able to successfully resolve
> TEs that significantly overlap genes. This can be seen by the near-zero accuracy on intronic TEs across
> all methods on both datasets (Figs. 15 and 16). It appears the EM-based methods attempt but fail to
> redistribute these UMIs, resulting in nearly all false-positive calls due to fractional counts, while
> STARsolo discards these reads, resulting in nearly all false-negative calls.
>
> Final conclusions. Overall, we find that all methods struggle to handle ambiguous reads well, with most
> methods producing a high degree of TE false-positives or false-negatives (due to rounding fractional
> counts to zero) (Figs. 28 and 29). This problem is so significant, in fact, that it appears the best way to
> achieve high TE accuracy is to simply discard all ambiguous reads, significantly reducing TE
> false-positives while substantially increasing gene false-negatives, as is done with STARsolo. If one
> desires to strike a more even balance between gene and TE accuracy, however, it appears that using an
> EM-based method is best. In particular, we recommend Alevin-Fry, as it can handle alternative
> splicing, unlike Alevin, and it performed the most consistently across datasets. This is likely due to its
> ability to handle UMI errors in multi-annotating reads, the absence of which seemed to hurt
> STARsolo-EM on the Minnow dataset.
>
> Overall Recommendations. For general TE analysis we recommend the use of a locus-specific, EM-based
> method such as Alevin-Fry or STARsolo-EM. We recommend Alevin-Fry as it had the most consistent
> performance across datasets and was the top performer out of the EM-based methods on the Minnow
> dataset (Figs. 9, 11, 28, and 29). The one limitation of Alevin-Fry, however, is that it requires selective
> alignment to the transcriptome. While this shows excellent performance on our simulated datasets,
> real-world performance may be lower, especially in datasets with novel isoforms or expression of
> unannotated genomic features. While full alignment to the genome, as is used by STARsolo, has been
> shown to handle these issues well, selective or pseudo alignment to the transcriptome will often force
> reads derived from these features to align to the transcriptome and known transcripts, causing
> artificially elevated expression estimates [84]. We also recommend STARsolo-EM as it provides full
> alignment to the genome and was the top performing standard EM-based method on the Flux
> Simulator dataset

## Future directions (the owner notes these still hold)

> Improving EM Estimation. As discussed in section 2.5, while EM-based methods generally provide the
> best overall performance, they still struggle to disambiguate fully overlapping annotations, especially
> when it comes to TEs that overlap genes (Figs. 13 and 14). Compared to their performance on bulk
> RNA-Seq data [82,83,97,98], EM algorithms seem to struggle when faced with the unique properties of
> single-cell data, especially its high degree of sparsity and low-count nature, with the majority of
> expressing genes having only a handful of UMI counts (Figs. 17-20). It may be possible to improve the
> accuracy of EM approaches by taking into account the unique nature of single-cell data.
> One potential approach would be to develop an EM method that accounts for the sparsity of single-cell
> data by biasing counts towards zero. This could be achieved by introducing an additional weight that
> promotes the reassignment of reads toward annotations that have an estimated expression level above
> a certain threshold. Every EM iteration, each annotation's currently estimated expression level could
> be considered and this additional biasing weight added or removed from each annotation accordingly.
> We have already seen hints that accounting for sparsity is important in our simulation results. By
> rounding-to-even the output of all EM-based methods, all instances of 0.5 counts were rounded down
> to zero. This had a striking effect on TE accuracy, dramatically reducing false positives and increasing
> overall accuracy in some cases by as much as 20 percent. This underscores the importance of
> considering the sparsity of the data, where it is overwhelmingly beneficial to bias fractional count
> estimates toward zero instead of retaining them.
> Another potential approach is to try to leverage expression information across similar cells to improve
> EM estimates. The main idea behind this approach is that while individual cells represent a stochastic
> sampling of the top ~5k expressed genes [99], pooling similar cells together may provide a deeper and
> more robust estimate of true expression levels. This could be accomplished by either running a
> standard EM or skipping EM and performing cell clustering on the results of a standard pipeline. The
> cell cluster identities could then be used by the EM in one of two ways. One, cells of the same cluster
> could be pooled and undergo EM together as a sort of "pseudo-bulk" sample. Or two, normalized
> expression estimates for each cluster could be computed and used as weights in the EM, running each
> cell individually while incorporating its cluster-specific weights. A similar approach has been tried
> with some success in [100] where Shao and Wang used a cell anchoring approach to determine related
> cells and used that information to set the priors in a variational Bayesian optimization algorithm
> (rather than a standard EM). The main caveat to these types of clustering approaches is that they have
> a tendency to mask heterogeneity within clusters/cell-types or to overlook rare cell populations. As a
> result, these kinds of approaches are likely to be a valuable supplement to, but not replacement for,
> standard individual-cell analysis.
>
> Improving TE annotations. Another potential avenue for improvement lies in the choice of TE
> annotations. As discussed in section 2.2, we are currently taking all TE annotations from the UCSC
> RepeatMasker track as part of our analysis. While this casts an appropriately broad net, there may be
> some room for refinement in what annotations we keep. By further restricting our annotation set to
> the TEs most likely to be expressed, we can reduce the number of potential mapping locations we
> consider, enriching for valid locations which will boost accuracy. One potential strategy is to remove
> all TE annotations that do not have an intact promoter. This phenomenon is especially common with
> LINE elements that often become 5' truncated when inserting, losing their promoter [36–38]. For
> example, of the ~500,000 LINE-1 elements annotated in the human genome, only 5,000 are full length,
> containing an intact promoter [101,102]. This process, however, is not always trivial, as it can be
> difficult to associate some TE loci with their promoter sequences, often leading to them having
> separate annotations in the RepeatMasker output. It also raises the question of how to handle
> solo-LTRs which occur when LTR-retrotransposons undergo homologous recombination between their
> two LTRs, removing the internal sequence and leaving nothing but the promoter-containing LTR behind
> [39–41]. This pruning of annotations also comes with some important caveats. First, while TE
> expression driven by their own promoters is of primary interest, there are other forms of TE expression
> that are potentially biologically relevant and worth measuring including TE-containing chimeric
> transcripts driven by upstream promoters (as is known to happen with LINEs [51,103] and SVAs [104])
> as well as TE promoters driving transcription of long non-coding RNAs [105–107] and nearby genes
> [39,108]. As a result, some TE annotations that do not contain promoters (or are "only" promoters in
> the case of solo-LTRs) may still be valuable to retain. Second, if any of the aforementioned
> "non-standard" TE transcription does occur involving pruned annotations, there is a risk that those
> annotations will also map to the retained annotations, leading to overestimation.
> Another intriguing possibility is to follow the approach taken in [109] where Srivastava et al. attempt
> to assemble a TE transcriptome from a paired bulk RNA-Seq sample and use that as part of the
> reference they align against rather than a standard annotation set. This has the same promise as the
> previous approach, biasing the annotations toward things known or likely to be expressed, but also
> comes with two important caveats. One, TE transcripts are difficult to accurately assemble due to their
> repetitive nature. Two, this approach risks overlooking transcripts expressed at a low level or in rare
> cell populations which could lead to bias in the resulting quantification. Another potentially
> interesting variant of this idea would be to use long-read data from a matched sample to provide the
> TE reference transcriptome instead relying on transcript assembly from bulk RNA-Seq data.
>
> Incorporating Emerging Technologies. There are several emerging and existing technologies that could
> be leveraged to increase TE quantification in single-cell data. One of the most obvious technologies is
> 5' rather than 3' capture assays for droplet-based single-cell sequencing. The main advantage of 5'
> capture is that the resulting reads lie close to the promoter of the originating transcript. This would
> allow for easy disambiguation between TEs that are passively transcribed as part of gene introns from
> TEs that are driven by their own promoters, as well as identification of the source promoter for
> chimeric transcripts. However, our experience with the v2 5' capture kit from 10x Genomics was quite
> poor, with the resulting libraries having extremely low coverage, truncated reads, and a high degree of
> RT primer inclusion. If the quality of the 5' capture kit is brought up to par with 10x's current 3'
> capture offering, however, then it would definitely be worth revisiting.
> Another promising avenue is the use of long-read technology at either the bulk or single-cell level.
> Full-length transcripts would be highly useful as they would vastly reduce the issue with multimapping
> reads, allow for disambiguation between passive and active TE transcription, and give a complete view
> of chimeric transcripts [110]. Long-read technology could also be useful in developing a TE
> transcriptome, as mentioned earlier. The primary barrier to adopting long-read technology for TE
> quantification, however, are the high (and in the case of Oxford Nanopore, non-random) error rates.
> This is especially relevant with regard to TEs as many loci only differ by a few polymorphisms. A final
> promising direction is the emerging field of single-cell multi-omics. Often the use of transcriptome
> data alone is insufficient to pinpoint the exact locus a TE transcript originated from. Incorporating
> information such as methylation, histone acetylation, chromatin accessibility, and promoter occupancy
> can help significantly narrow down the potential loci that a TE transcript originated from. The
> simultaneous incorporation of several of these assays with scRNA-Seq technology represents an
> exciting opportunity to further explore TE expression at single-cell resolution, although these assays
> share many of the same difficulties in including TEs in their analysis as their bulk counterparts do
> [24,90].

## Owner note on provenance (added the same day)

The dissertation's author, Cole Wunderlich, is a co-author of TEsingle, the tool vendored at
`/workspaces/Meta-Aging/01_modules/.ref/TEsingle`; its paper is a March 2026 preprint. TEsingle is therefore the
production form of the method the excerpts describe; `tesingle_notes.md` records what it implements.

## The owner's questions to the programme

How does the field treat TE annotation: where it maps TEs, where it separates them into classes,
families and subfamilies, and what genic context metadata it uses (exon, intron, intergenic, 5' and 3'
UTR, or else). te-tracks should cover the rungs of questions one asks when counting TE features as
aggregates of classes, families, subfamilies or loci, and should know which counting the field primarily
uses. The ideal above is the reference point for accurate TE quantification and locus resolution in the
three datasets.
