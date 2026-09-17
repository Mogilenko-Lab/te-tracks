# TEsingle 1.0: the dissertation's method in production (orchestrator notes, 2026-09-16)

Owner context: Cole Wunderlich, author of the 2023 dissertation excerpted in `thesis_2023_excerpts.md`, is a
co-author of TEsingle (Forcier, Wunderlich, Tam, Hammell; checkout `/workspaces/Meta-Aging/01_modules/.ref/TEsingle`,
HEAD `655f127`, version 1.0; the paper is a March 2026 preprint). TEsingle is therefore the field's production form
of the design the dissertation argues for, and te-tracks already tests its parser (consumer check 12). Facts cite
file:line in the checkout.

- **Input and alignment.** A STARsolo BAM (`TEsingle:77-78`); multimappers are read as alternative alignments per
  read (`TEtools/AlignmentIO.py`), so full genome alignment with multimappers retained is assumed.
- **Gene model.** `GeneFeatures(args.gtffile, args.stranded, "transcript", "gene_id")` (`TEsingle:112`): gene support
  is the full transcript span, so intronic reads count to their gene. This is the GeneFull behaviour the dissertation
  chose, built into the tool.
- **TE model.** `TEindex.build` requires `gene_id`, `transcript_id`, `family_id` and `class_id` on every TE row and
  refuses rows lacking any (`TEtools/TEindex.py:302-329`); the feature name is
  `transcript_id:gene_id:family_id:class_id[:strand]`. Because `transcript_id` (the locus) is part of the key, TEsingle
  counts at the **locus** level with the subfamily, family and class carried along. This is the dissertation's
  "subfamily GTF" grammar, and te-tracks' `record.gtf` writes exactly these four attributes (`docs/OUTPUTS.md`,
  consumer check 12).
- **UMI handling.** Per barcode, `cell_graph` links UMIs at Hamming distance 1 through a wildcard index and takes
  connected components as molecules (`TEtools/CellGrapher.py:4-39`). Within a component, reads with a single alignment
  that overlaps an annotation are "anchored" and fix the molecule's annotation set; a component with no anchored
  read is "unmoored" and is split equally across its alignments and annotations (`TEtools/Counters.py:62-183`). This
  is a connected-components simplification of Alevin's parsimonious UMI graph, pooling multi-mapping alignments per
  molecule.
- **EM.** Unmoored molecule vectors go through an accelerated EM (SQUAREM-style step control, tolerance 1e-4, at
  most 100 iterations) over all gene and TE features of the cell (`TEtools/EM.py`, `Counters.py:201`).
- **Gene versus TE ambiguity.** An anchored molecule with both gene and TE annotations is category 4 and is counted
  to both sides with a per-cell prior `te_frac` = share of TE-only anchored molecules among anchored molecules
  (`Counters.py:36-45,137`); an unmoored molecule with both gene and TE alignments is split 0.5/0.5 (category 1).
  This is a heuristic, and the dissertation's own benchmark reports that no method resolves gene-overlapping TEs.
- **Cells.** `--cutoff 1000` uncorrected UMIs per barcode (`TEsingle:92-93`); strandedness defaults to `forward`
  (10x second-strand libraries).
- **What it does not do.** No genic-context output: an intronic TE molecule and an intergenic one leave the tool
  alike, and the gene-TE split above is the only place gene overlap enters. Sparsity rounding, cluster pooling and
  annotation pruning (promoter-intact filtering) are outside the tool.

Consequences for te-tracks: `record.gtf` is TEsingle's native input and its four-attribute grammar is the contract to
protect; a `gene_id = locus` variant is unnecessary for TEsingle since the locus is already in its key, and matters
only for STARsolo GeneFull counting where `gene_id` is the counted unit; the context relation is what lets a
consumer stratify TEsingle's locus counts by exon, intron, intergenic and promoter geometry, which the tool itself
cannot supply.

## Paper excerpts supplied by the owner (TEsingle preprint, March 2026)

> Accurate handling of TE reads becomes especially important when trying to analyze data from single-nucleus RNA
> sequencing (snRNA-seq) assays where unprocessed intron sequences constitute up to 40% of the transcripts captured –
> and these intronic sequences are packed with both functional and fragmentary TEs. Given these challenges, accurate
> quantification of TE-derived transcripts for scRNA-seq data requires computational tools that can accurately align
> multi-mapping reads, perform UMI correction while accounting for ambiguity in alignment and annotation, properly
> handle intron inclusion, and accurately assign ambiguous reads to their locus of origin.
>
> We show that TEsingle simultaneously assesses both gene and TE expression and optimizes for TE analysis without
> compromising its accuracy on gene abundance estimation. In fact, TEsingle outperforms other standard single-cell
> analysis software by also returning better estimates for gene expression
>
> TEsingle focuses on accurate assignment of aligned reads to the most likely gene or TE locus of origin. The basic
> design of TEsingle follows our popular software package for bulk gene expression analysis, TEtranscripts. More
> specifically, the heart of the TEsingle algorithm involves an expectation-maximization algorithm for resolving any
> ambiguous alignments of TE-derived RNA-seq reads
>
> To adapt TEtranscripts for single-cell and single-nucleus RNA-seq data, we added several steps to properly handle
> Unique Molecular Identifier (UMI) barcodes that label individual captured transcripts and enable resolution of PCR
> duplicates in snRNA-seq data
>
> TEsingle requires an alignment file, in either SAM or BAM format, and two annotation files, in GTF format, to
> identify all annotated genes and TEs, respectively. The alignment file generated by STARsolo provides the
> algorithm with a whitelist-corrected set of cell barcodes and UMIs for each read alignment. With these input files,
> TEsingle first builds one index tree structure for gene annotations and locations, and a separate index for TE
> annotations and locations. Gene annotations are modeled as full-length transcripts, rather than excluding reads
> that align to intronic regions, which we find improves disambiguation of intron retention events from intronic TE
> expression.
>
> TEsingle uses the whitelist-corrected cell barcode and uncorrected UMI flags to group reads by transcript. It then
> uses the searchable index structures to enumerate all possible annotations to which each read could have aligned.
> At this point, TEsingle then divides the sequencing data by individual cell barcode for further processing on a
> cell-by-cell basis. For each cell, TEsingle builds a UMI graph network, where each UMI is represented by a single
> node and edges connect any two nodes whose sequence differs by one Hamming distance. This enables TEsingle to group
> together any reads that likely derived from the same originating transcript, but which contain up to 1 PCR or
> sequencing error within the UMI sequence. Every independent subgraph is taken as one transcript, and the associated
> reads, for all the interconnected UMIs that make up that subgraph, are pooled to determine annotation of origin.
> From this point forward, TEsingle works at the UMI/transcript level, where each pooled UMI subgraph is assumed to
> represent a single originating transcript.
>
> With the initial estimated genomic origins established, each UMI with a nonzero value for any TE annotation is
> further processed using an expectation-maximization (EM) algorithm to determine the most likely annotation for
> each transcript. Transcripts with at least one uniquely mapping read assigned exclusively to a gene annotation are
> excluded from the EM algorithm to prevent potential biasing of TE-originating transcript counts towards abundantly
> expressed genes. During development of TEtranscripts and TEsingle, we noted that inclusion of uniquely mapping
> gene and TE reads within the EM algorithm tends to incorrectly bias the outcome toward assignment of reads to genes
> (which tend to be more abundantly expressed) and older TE copies (which tend to contain more unique sequences).
> Thus, only ambiguous reads with potential TE annotations are included in the EM algorithm, a strategy that mirrors
> TEtranscripts. Once the EM algorithm finishes determining the transcript of origin for the pool of ambiguously
> mapped and annotated UMIs, the total counts for all UMIs are summed for each cell and arranged as an output table
> in cell by gene format, where "gene" includes all expressed genes and TEs detected.
>
> Our benchmarking results demonstrate that TEsingle outperforms both gene-focused and TE-focused software packages
> in accurately evaluating expression of transposable element loci, whether the results are locus-specific or
> aggregated by subfamily. STARsolo-TE, a slight modification of the STARsolo package (see methods), had the
> second-best performance on both gene and TE estimation
>
> When comparing across neuronal subtypes, we found that most of the PD-elevated TEs were unique to a neuronal
> subpopulation, with only a handful of shared PD-elevated TEs found in more than one neuronal population (see upset
> plot in Figure 5D). We found the largest set of elevated TE loci in excitatory neurons (Figure 5C, E), which showed
> elevated expression of hundreds of LINE, SINE, and ERV type TEs. Many of these elevated TEs belonged to relatively
> young, intact and/or human-specific TE subfamilies (Figure 5F), such as a young LINE element (L1PA2-dup4380),
> sequences from endogenous retrovirus families (HERV9-dup294, LTR12B-dup142), and from human-specific SVA elements
> (SVA-E-dup596, SVA-F-dup252). In particular, several of these young and intact PD-elevated TEs were specific to DA
> neurons, such as SVA-F-dup252, which is both PD-elevated and expressed nearly exclusively in DA neurons (Figure 5G).
> [...] Altogether, this demonstrates that relatively young and intact TEs are elevated in specific neuronal
> subpopulations of PD patient tissues, and that some of the more interesting TE candidates are specific to DA
> midbrain neurons, the cell type most vulnerable in PD.
>
> The GTF annotation file for the gene annotations found in the T2T human genome was obtained from RefSeq and the GTF
> file for transposable element annotations was generated from the RepeatMasker table obtained from the UCSC genome
> database. The TE annotation table was then filtered to remove regions of low complexity, simple repeats, rRNA,
> scRNA, snRNA, srpRNA, and tRNA. Annotation files prepared in this fashion have been provided for several genomes as
> indicated at the TEsingle GitHub repository, but TEsingle can also use custom annotations that conform to the
> specified GTF format.

The paper's benchmark used the T2T CHM13v2 human assembly; the programme's data are mouse, and human is out of
scope for now (owner).

## The paper's filter against te-tracks universes (measured on the mm39 build)

Removing the RepeatMasker classes `Low_complexity`, `Simple_repeat`, `rRNA`, `scRNA`, `snRNA`, `srpRNA` and `tRNA`
keeps **3,802,177** records with classes DNA, DNA?, LINE, LTR, RC, Retroposon, SINE, Satellite, Unknown and
Unspecified: exactly te-tracks' `interspersed_plus_satellites` universe (`universes.json`, 3,802,177 records in
`universe_summary.tsv`). The `compat_tetranscripts_mm39` universe (3,799,629) differs from it only by excluding the
2,548 SINE records whose family name begins with `tRNA`, the packaged TEtranscripts GTF's rule; the paper's class
filter keeps them since their class is SINE. `interspersed` (3,764,949) additionally excludes the 37,228 satellites.
So the TEsingle paper's universe already exists in te-tracks under its own name, and `interspersed` is the stricter
choice the design made for counting.

## The benchmarking and analysis checkouts

- `/workspaces/Meta-Aging/01_modules/.ref/TEsingle_benchmarking_scripts` (HEAD `6e85f5d`): `index_generation/`
  shows the annotation routes per tool. TEsingle and STARsolo-TE and CellRanger-TE take one combined gene-and-TE GTF
  for the STAR or `cellranger mkref` index (`T2T_geneTE_forSTAR.gtf`, `T2T_geneTE_forCellRangerTE.gtf`); scTE is built
  with `-m nointron` for the benchmark (`T2T_scTE_build.sh`); IRescue's subfamily BED takes `gene_id` and its locus
  BED takes `transcript_id` from the TEsingle TE GTF (`T2T_iRescue_BED_generation.sh`), which is the pair te-tracks
  emits as `subfamily.bed` and `record.bed`. `software_running/` holds the per-tool commands; `accuracy_calculations/`
  the comparison to simulated truth (an F1 with a within-15-percent accuracy call, as in the dissertation).
- `/workspaces/Meta-Aging/01_modules/.ref/TEsingle_Martirosyan_analysis_code` (HEAD `f147250`): STAR plus TEsingle on
  the T2T index, emptyDrops and DoubletFinder on TEsingle output, aggregation to one matrix, Seurat downstream. The
  "young, intact and/or human-specific" statements about elevated TE loci are narrative knowledge of subfamily
  identity (L1PA2, SVA-E, SVA-F, HERV9); no script computes an age or intactness field, and the only `age` variable is
  donor age (`Seurat/scripts/Martirosyan_integration.R:22`). A published, versioned age or intactness annotation is
  therefore absent from the reference practice, which is the gap te-tracks' divergence and consensus-coordinate
  columns can fill.

## Corrections from source, after the field consult (orchestrator, 2026-09-16, later the same day)

The codex field consult (`field_practice_consult.md` Q7, M5) probed the TEsingle source; the orchestrator read the
same lines and confirms the following, which supersede the bullets above where they differ.

- **UMI graph.** `cell_graph.grapher` links every pair of a cell's UMIs at Hamming distance 1 through the wildcard
  index and `subgrapher` takes connected components, with no annotation-compatibility or abundance condition
  (`TEtools/CellGrapher.py:4-39`). A chain `AAAA, AAAT, AATT` is one molecule although its ends differ at two bases,
  and one UMI shared by molecules of unrelated genes is one node.
- **EM scope.** `rearranger` routes gene-only molecules (unmoored gene-only, category 2; anchored gene-only,
  category 5) past the EM as fixed counts; every TE-containing molecule enters it: unmoored TE-only (category 0),
  unmoored gene+TE split 0.5/0.5 (category 1), anchored TE-only (category 3) and anchored gene+TE after the
  `te_frac` weighting (category 4) (`TEtools/Counters.py:19-33,195-201`). The earlier bullet's "unmoored molecule
  vectors go through the EM" is therefore too narrow.
- **`te_frac`.** `resolver` computes `te_frac = category[3] / (category[3] + category[5])`: anchored TE-only over
  anchored TE-only plus anchored gene-only; anchored gene+TE molecules are outside the denominator, and a zero
  denominator gives zero TE weight (`Counters.py:36-41`).
- **Final allocation.** After convergence `compute_likeliest` adds one count to the `argmax` feature of each
  molecule's masked weight vector, ties resolving to the first index in feature order (`TEtools/EM.py:30-36,114`).
  TE-containing molecules therefore yield hard integer allocations; only the gene-only path can leave fractional
  gene counts. `preprocess` builds Boolean candidate masks from `count != 0`, so a zero initial weight removes a
  candidate (`EM.py:55-61`). There is no effective-length weighting; the dissertation prototype had one
  (`Thesis_2023/quantification_method/EM/multiprocess_wrapper_cole.py`).
- **Paired mates.** `read_in_alignment` groups records by `(CB, UR, query_name)` and appends every record as an
  alternative alignment with its own `is_reverse`, without `is_read1`, `is_read2`, `is_proper_pair` or `HI`
  handling (`TEtools/AlignmentIO.py:60-76`). A uniquely aligned proper pair becomes two entries with opposite
  annotation strands, and `count_reads` treats a read as anchored only with exactly one entry (`Counters.py:71-72`).
  The two whole-cell datasets' cellranger BAMs are fully paired (both cDNA mates aligned), so a TEsingle run on a
  paired STARsolo BAM needs a fragment-aware fix or a declared single-mate route before it counts anything.
- **Index recipes differ between the two paper checkouts.** The benchmarking scripts build a combined gene-and-TE
  STAR index (`TEsingle_benchmarking_scripts/index_generation/T2T_STAR_index_generation.sh`); the Martirosyan
  analysis builds the STAR index from the gene GTF alone (`TEsingle_Martirosyan_analysis_code/TEsingle/
  setup_STAR_index.sh:92-96`) and passes the TE GTF to TEsingle at count time (`run_STAR_TEsingle.sh:96`, with
  `--stranded`, `--cutoff` 100 and STAR `--outFilterMultimapNmax`/`--winAnchorMultimapNmax` from the script's
  variables). The "combined index" sentence in the benchmarking paragraph above describes the benchmark only.
- **Identical four-tuples collapse before counting.** `TEindex.TE_annotation` translates every overlapping GTF row to
  `fullShortIdxDict[idx]`, the index of its `transcript_id:gene_id:family_id:class_id` tuple, so two rows carrying the
  same four attributes are one competitor and one count column; `subfLengthDict` sums their lengths rather than
  taking a block union (`TEtools/TEindex.py:252-275,329-364`; loci consult M6, 2026-09-17). TElocal keeps each row a
  separate entry until reporting. The Martirosyan STAR recipe sets `outFilterMultimapNmax 100` and
  `winAnchorMultimapNmax 200` (`run_STAR_TEsingle.sh:12-13`); the dissertation text's 100/150 describes its own runs.
