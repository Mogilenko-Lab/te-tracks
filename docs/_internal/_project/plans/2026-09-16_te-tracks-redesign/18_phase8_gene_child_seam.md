# Phase 8: the gene child family, seam only

Goal: the place where gene-dependent views live exists, with one view and no interpretation.

Deliverables
- `config/mm39_gene.env`: `PARENT_FAMILY=te_mm39`, `GENE_GTF_URL` (GENCODE vM37 primary assembly),
  `GENE_GTF_MD5=702e27a8727db66cd23e9f66f5aa1d38`, `EXON_MASK_POLICY=all_exons_unstranded_union_v1`.
- Family `te_mm39_gene` built by the same `build.sh`, manifest identity pins
  `parent_core_build_id`.
- `exports/{ucsc,ensembl}/interspersed/exon_subtracted/subfamily.saf`: mask = union of every
  `exon` row of the pinned GTF, both strands; pieces registered in `export_feature_members` with
  `block_start_1`, `block_end_1`; per-record view status table `tables/exon_subtraction_status.tsv`
  (`unchanged`, `trimmed`, `split`, `fully_subtracted`, `retained_bp`, `removed_bp`).
- Zero residual exon overlap asserted; `retained_bp + removed_bp = length_bp` per record.

Acceptance: exon_subtracted rows for `compat_tetranscripts_mm39` reproduce the lab's current
no-exon SAF row count when built with that universe (3,717,740 records retain at least one
piece, from the current config's expectation, to be re-measured); central-exon fixture yields two
pieces with the parent id.

Deferred to a dedicated design session, recorded here so nothing pretends otherwise
- The record-by-transcript context relation (exon, intron, promoter, relative strand, TSS and TES
  distances, exact blocks, per-record status).
- Which gene annotation each consumer corroborates against: bulk datasets carry their own GTF on
  disk; 10x chemistries ship references whose GTF may differ from GENCODE vM37; a child build per
  gene annotation pin is the mechanism, the policy for choosing and reconciling them is the open
  question.
- Promoter window parameters, isoform selection, spliced versus genomic distance.
