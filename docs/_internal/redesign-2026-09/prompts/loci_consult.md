# te-tracks loci consult: how Stellarscope, IRescue, STARsolo and cellranger define a locus, and the `record_starsolo.gtf` specification (codex, read-only)

You are consulted on design; you read source and recommend, you implement nothing. Working directory
`/workspaces/Meta-Aging/01_modules/te-tracks`, branch `redesign-2026-09`, commit `9c27b14`. You write exactly one
file: `docs/_internal/redesign-2026-09/consults/loci_gtf_consult.md`. You change nothing else. No git writes anywhere
(the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too; `14839-DM-cGAS` and `sene/`
are the owner's directories, read the first, leave both alone), no installs, no network. Export
`PYTHONDONTWRITEBYTECODE=1`. Scratch only under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/loci-consult/`,
removed when you finish (Python `shutil`; `/tmp` is noexec).

Read-only inputs: the core build `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` (its
`exports/<namespace>/interspersed/full/record.gtf`, `record.bed`, `subfamily.gtf`, `subfamily.bed`, the registration
`tables/export_feature_members.tsv.gz`, `tables/contig_aliases.tsv`); the 10x reference contig list at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refs/refdata-gex-GRCm39-2024-A/star/chrNameLength.txt` and its
`genes/genes.gtf.gz` (if absent when you start, say so); the checkouts `stellarscope`, `irescue`, `TEsingle`, `TElocal`,
`TEtranscripts`, `TEsingle_benchmarking_scripts`, `TEsingle_Martirosyan_analysis_code`, `Thesis_2023` under
`/workspaces/Meta-Aging/01_modules/.ref/`.

## Read first, in order
1. `docs/_internal/redesign-2026-09/consults/adr_rulings_2026-09-17.md` (the owner's rulings; C7 and C8 are your
   subject: STARsolo re-alignment, IRescue conservative, TEsingle modern, Stellarscope evaluated for loci).
2. `consults/field_practice_consult.md` Q2, Q4 and Q7; `consults/field_practice_synthesis.md` sections 4 and 5;
   `consults/gene_context_adr_brief.md` C8; `consults/tesingle_notes.md` (corrections section included).
3. `docs/OUTPUTS.md` (exports, registration, consumer table with the Stellarscope boundary defect at lines 504–506),
   `src/lib/build_exports.py` (the export contracts and jobs), `tests/checks/consumers/10_irescue_parser.required.py`,
   `11_stellarscope_parser.py`, `12_tesingle_parser.required.py`, `tests/lib/consumers.py`.

## The owner's words (verbatim, 2026-09-17)
> a second loci GTF would be necessary it seems, but it would be wise to understand on how stellarscope and irescue
> work loci-wise and what annotation they expect

## Questions
1. **Stellarscope.** From `stellarscope/stellarscope/annotation/` and `cmdopts/`: how GTF rows become features; what
   `--attribute` groups (default `locus`); whether rows sharing an attribute value merge into one feature and how
   overlapping or discontiguous rows are treated; how a read overlapping two features is assigned (overlap
   threshold, `--overlap_mode`); the right-boundary defect the fixture observes (`0,1,1,1` against `0,1,1,0`) with
   the source lines that cause it and its practical effect on record-level counts; what the tool expects for locus
   versus instance counting and which te-tracks export serves each (`record.gtf` with `locus` and `instance_id`;
   `subfamily.gtf`). State the STAR parameters its documentation recommends.
2. **IRescue.** From `irescue/irescue/map.py`, `count.py`, `em.py`, `README.md`: the BED name grammar it writes for its
   own RepeatMasker conversion (`subfamily#class/family~index`, instance mode `...~instance`), how a custom BED's
   column 4 is parsed in `count.py` and whether family and class survive into the output when the name carries no
   `#` (te-tracks' `record.bed` names are `name|chrom:start-end|strand`, `subfamily.bed` names are `rmsk_name`); the
   `--locus` modes; chromosome-name matching (`map.py:244-247`) against te-tracks' namespaces; the STAR parameters
   its README recommends; whether a te-tracks BED variant spelled in IRescue's own grammar would let its parsers
   emit class and family, and what that variant's registration grammar would be.
3. **STARsolo GeneFull on a combined gene and TE GTF.** Which GTF fields STARsolo needs (exon rows, `gene_id`,
   `transcript_id`, `gene_name`, `gene_type`/`gene_biotype`), how `features.tsv` is written, what `--soloMultiMappers
   EM` outputs and how those matrices join back to te-tracks' registration `(record, record_alias)`. From
   `TEsingle_benchmarking_scripts/index_generation/T2T_STAR_index_generation.sh` and `T2T_CellRangerTE_mkref.sh`, the
   attribute grammar the paper's combined GTFs used and the `cellranger mkgtf`/`mkref` requirements. State the
   collision rules between TE record aliases and gene ids, and which te-tracks namespace matches the 10x
   reference's contig names exactly (compare `chrNameLength.txt` with `contig_aliases.tsv`).
4. **Instances as one feature.** For each tool, whether fragments of one instance can be one competitor: Stellarscope
   through a shared attribute value; IRescue through instance mode; STARsolo through a multi-exon transcript (one
   gene, one transcript, one exon row per fragment; `Gene` counts exon overlap, `GeneFull` counts the span
   including gaps); TEsingle and TElocal, whose parsers append each row as its own entry. State the consequence for
   EM competition and for gap reads.
5. **Specification of `record_starsolo.gtf`.** Propose: rows (one exon per record; the `full` variant only), `gene_id`
   = `transcript_id` = record alias, `gene_name`, `gene_type "transposable_element"` or the value STARsolo and
   cellranger accept, `locus`, `rmsk_name`, `family_id`, `class_id` attributes; namespaces (ucsc, ensembl, gencode);
   the export contract fields (`docs/OUTPUTS.md` export table, `build_exports.py`); the registration pair it binds to;
   size estimate per namespace from `record.gtf`'s size; the fixture (two records of one name become two genes; a
   gene–TE overlap; a read in a gap between two fragments; a record alias colliding with no gene id); acceptance
   numbers (rows per namespace equal the universe's record count); and the phase 9 scope-amendment cost (inventory,
   identity, host disk 10.5 GB per build). Say whether an instance-transcript variant (`instance_starsolo.gtf`) should
   accompany it or wait.
6. **Recommendation.** For the 14761-first pilot the owner ordered: which te-tracks exports each tool consumes as
   shipped, which need the new profile, and what the consumer must supply itself (gene GTF, index, STAR parameters,
   barcode roster). Each recommendation states what it prevents and its settling measurement.

## Output format
```
# Loci consult: Stellarscope, IRescue, STARsolo, cellranger and record_starsolo.gtf (codex gpt-6-astra)
## Summary
## Q1 .. Q6
## Measurements and source facts (paths and lines)
## Open for the owner
```
Under 250 lines. Facts over opinions; every tool claim cites a path and line; where you rely on knowledge beyond
the checkouts (STAR or cellranger documentation you cannot read here), say so in the sentence. Recommend; do not
implement.
