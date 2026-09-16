# Phase 8: the gene child family, seam only

Goal: the place where gene-dependent views live exists, with one view and no interpretation.

Entry condition (owner, 2026-09-16): phase 8 opens with a design consult with codex on the child family's topology,
architecture and approach (one child per gene annotation pin or one child with many views; how the exon mask, the
piece registration and the transcript-context relation relate; what the consuming projects' combined-mode counting
needs from the SAF; the child exporter's explicit universe, variant and block inputs and its own inventory; a
pinned alias and length source for child preflight, since the parent's `contig_aliases.tsv` sits beside the parent
build), recorded under `redesign-2026-09/consults/` and ruled by the owner, before any implementation
prompt is written. The deliverables below are the current draft and the consult may reshape them.

Deliverables
- `config/mm39_gene.env`: `PARENT_FAMILY=te_mm39`, `GENE_GTF_URL` (GENCODE vM37 primary assembly),
  `GENE_GTF_MD5=702e27a8727db66cd23e9f66f5aa1d38`, `EXON_MASK_POLICY=all_exons_unstranded_union_v1`.
- Family `te_mm39_gene` built by the same `build.sh`, manifest identity pins `parent_build_id` and
  `parent_catalog_id` (milestone 2 ruling H5).
- `exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/{subfamily,taxonomy_triple}.saf`: mask = union of every
  `exon` row of the pinned GTF, both strands; pieces registered in `export_feature_members` with
  `block_start_1`, `block_end_1`, one row per retained block, so uniqueness holds over the registration key plus the
  block columns (milestone 5 ruling A1); the child exporter takes universe, variant and block bounds as explicit
  inputs and writes the child build's own `tables/exports.tsv` (ruling A2); per-record view status table `tables/exon_subtraction_status.tsv`
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
- `gene_context` for the 14761 ledger. `exon_subtraction_status` describes counting-support geometry
  under the exon mask, and `unchanged` covers intronic and intergenic records alike; the context relation
  supplies intron, promoter and TSS distances. D2 records `gene_context` as pending this design session
  and populates nothing from the status table (milestone 2 ruling H3).
