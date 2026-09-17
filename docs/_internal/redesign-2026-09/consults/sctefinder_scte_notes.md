# scTEfinder and scTE: how they treat TE annotation (orchestrator notes, 2026-09-16)

Read from the checkouts `/workspaces/Meta-Aging/01_modules/.ref/scTEfinder` (HEAD `b896cbb`) and
`/workspaces/Meta-Aging/01_modules/.ref/scTE` (HEAD `566f6ab`, version 1.0). Facts cite file:line.

## scTEfinder

- A Snakemake wrapper with four modules: STARsolo mapping, Seurat or Scanpy cell QC, BAM subset to
  the QC barcodes, `scTE` counting (`Snakefile`, `modules/*.smk`). It does no annotation work itself.
- Default job config points at a bundled `hg38.exclusive.idx` scTE index and a Cell Ranger GRCh38 STAR
  genome (`configs/default.tsv`); only human is bundled.
- STAR keeps multimappers and writes one random alignment per read: `--outFilterMultimapNmax 100
  --winAnchorMultimapNmax 100 --outMultimapperOrder Random --runRNGseed 777 --outSAMmultNmax 1`,
  with `--soloFeatures GeneFull_Ex50pAS Velocyto --soloMultiMappers EM` for its own gene matrix
  (`modules/Mapping.smk`).
- `scTE` is called with `-CB CB -UMI UB --expect-cells 20000 --min_counts 0 --min_genes 0`
  (`modules/CallTE.smk`), so scTE's own cell filter is off and a 20,000-cell cap applies.
- Output: `3.scTE/<job>.csv.gz`, scTE's combined gene and TE matrix.

## scTE index (`bin/scTE_build`)

- Inputs: a gene GTF and a TE table. `-g mm10` downloads GENCODE vM21 and UCSC `mm10/rmsk.txt.gz`
  (`:427-428`); custom genomes take any GTF plus a six-column BED with the TE name in column 4
  (`:373-377`, `Data/TE.bed`).
- Gene side: `exon` and `UTR` rows keyed by `gene_name`, merged per gene into exon blocks (`:51-90`).
  Two gene sets: `raw` = every gene; `clean` = rows whose GTF line contains the substring
  `protein_coding` or `lincRNA` (`:83`). Current GENCODE labels those genes `lncRNA`, so with vM37 the
  `clean` set is protein-coding exons only.
- TE side from rmsk: classes DNA, LINE, LTR, SINE, Satellite, Retroposon kept (`:169`); name =
  `repName` (`:167`). Contigs limited to 1 to 49, X, Y, M with `chr` stripped, so scaffolds drop
  (`:14,69,177`).
- Modes (`:129-356`): `exclusive` removes a TE locus whole if it overlaps any `clean` exon block
  (`left < k[1] and rite > k[0]`); `nointron` uses each gene's span (min to max over exons) as the
  mask, leaving intergenic TEs only; `inclusive` keeps every TE. Removal is whole-record, never
  trimming.
- The index is one interval list: gene exon blocks labelled by `gene_name` plus surviving TE loci
  labelled by TE name (`:208`). TE counts therefore aggregate by name, the subfamily level; no locus
  identity survives.

## scTE counting (`scTE/base.py`)

- Every BAM record becomes the interval `[pos, pos+100)` from its leftmost position, ignoring read
  length, CIGAR and splicing; no flag or MAPQ filter (`:168`). Barcode and UMI come from tags;
  `awk '!x[$4$5]++'` keeps the first record per barcode plus UMI in file order, so duplicates and
  multimappers collapse to the lowest-coordinate alignment.
- Each interval counts once to every index feature it overlaps, gene or TE, with no priority
  (`:409-413`); the README's "genes first" is entirely the index-time removal above.
- Cells: the top `--expect-cells` barcodes by number of distinct features with at least
  `--min_genes` (`:426-443`). Output CSV or h5ad: barcodes as rows, every feature name as a column,
  genes and TE subfamilies sorted together (`:467-495`).
- Multimappers get no treatment in scTE; with scTEfinder's STAR settings each read lands on one
  random locus and is counted there.

## Consequences for te-tracks and the gene-context discussion

- scTE is a live "carve the annotation" implementation at whole-locus grain whose mask policy changed
  silently when GENCODE renamed `lincRNA`; te-tracks names its mask policy explicitly and ships the
  context relation rather than only a carved SAF.
- te-tracks' `subfamily.bed` matches scTE's custom `-te` input; `record.bed` would make scTE count at
  locus level, at memory and column cost; both need the alias table since scTE strips `chr` and drops
  scaffolds.
- scTE offers no genic context: intronic and intergenic TE reads both count to the subfamily and
  exon-overlapping loci vanish. Its `nointron` mode is the coarse intergenic-only stratification the
  bulk toolkit's Rung 2 asks for, obtained by deletion.
- The combined matrix's gene counts come from scTE's exon-block counting with the 100 bp window, so
  they differ from the STARsolo GeneFull matrix the same pipeline used for QC.
