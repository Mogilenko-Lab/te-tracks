# Consult: the unified TE schema, the interactive genome projection and reconstruction as a consumer (codex, read-only)

You are consulted on design. Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks`, branch
`redesign-2026-09`, tree clean at the commit that carries this prompt. You write exactly one file:
`docs/_internal/redesign-2026-09/consults/unified_te_schema_consult.md`. You change nothing else. No git writes
anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too; `14839-DM-cGAS`
there is the owner's copy, read it and leave it alone; `sene/` you leave alone), no installs, no network. Export
`PYTHONDONTWRITEBYTECODE=1`. Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/schema-consult/`,
removed with Python `shutil` when you finish (`/tmp` is noexec). Read-only inputs: the core build at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` (`BUILD_ID` `9ddf3622…`), the Dfam census
and classification tree under `docs/_internal/redesign-2026-09/taxonomy/`, and the datasets' documents named below.
Another unit implements phase 8 in this tree while you work; read package files as they are and write only your
consult file.

## The owner's words (verbatim, the brief you answer)

> "Reconstruction waits for a consumer" well I could imagine a consumer to be some interactive tool projecting
> onto the genomic coordinates where the remnants of that or this virus are scattered around a genome, and then
> asking specific focused interactive questions about scattered fragments by filtering of the unified schema. e.g.
> highlight L1 remnants in the full genome - and it lights up where in the current dataset we see TEs to project to
> align to derived from snRNAseq for example, and then ask a different question, show me where those fragments map
> to regions of the open chromatin, and then we could funnel down, which TF families/TFs/motif patterns do we see
> within TE-derived regions of open chromatin that have confirmed transcription (picked up by RNA transcripts), and
> thus kind of pinning down to biologically defined subset that needs validation of importance in the conditions we
> study. [...] This largely overlaps with the problem on how do we design the unified schema that is conveniently
> queriable either via plain SQL, or interactively or for dedicated statistical modelling of specific questions.
> Would have to take into account what is self multiome sustained, and what would require unpaired splenic run.

> We would need to have an understanding on what is the evolutionary origins of TE-driven aging so to speak.

The downstream structure the schema must fit (14761-DM D2 outline, `02_analysis/scripts/`):
`00_foundation_peak_atlas/`, `10_requantify_embed/`, `20_chromatin_readouts/`, `30_grn/`,
`40_transposable_elements/`, `90_integration_exports/`. The owner's D1 layer statement:

> LAYER 1 (parallel quantification, feeds off RAW): TE expression (snRNA) and TE accessibility (snATAC) need the
> BAMs, not the fragment file — cellranger-arc fragments keep MAPQ>=30 uniques, which structurally underrepresents
> young TE families. Locus-level claims are biased toward old/diverged copies; family-level claims need
> multimapper-aware realignment (EM for RNA; custom for ATAC). Declare this bias in the namespace README from day one.
> LAYER 2 (intersection, feeds off the v2 atlas): RepeatMasker mm39 (class/family/subfamily/locus) becomes another
> annotation registry — same NEVER-GATE law as ImmGen/SCREEN/EasySci. Peak coordinates are the join surface:
> TE-derived open chromatin = rmsk ∩ admitted peaks; "is this TE-peak open in celltype X" is answered by the
> EXISTING counts (no new counting); motif scanning inside TE-overlapping peaks connects TE families to TF families
> (ERV/LTR motif donation); GRN eRegulon regions intersect TE-peaks -> TE-to-GRN linkage with peak-coordinate
> accuracy. Feature annotation (gene models + rmsk + registry classes) supplies the dimension tables that make those
> joins readable.

## Read, in order
1. `docs/DECISIONS.md` (all sections, in particular 4, 9, 10, 11, 12, 13, 14, 15) and `docs/OUTPUTS.md` (records,
   instances, taxonomy, registration and its binding key, exports, namespaces).
2. `docs/_internal/redesign-2026-09/consults/adr_rulings_2026-09-17.md` (all rounds; the third round carries the
   owner's rulings on windows, structural views, Dfam, the consumer boundary and the packaging direction) and
   `consults/open_questions_premises_2026-09-17.md` (the biology and premises).
3. `consults/structural_views_consult.md`, `consults/loci_gtf_consult.md`, `consults/field_practice_synthesis.md`,
   `consults/gene_child_consult.md` Q5 and Q6 (the context relation's geometry), `consults/mask_policy_consult.md`
   Q5 (intron-retention views).
4. `docs/_internal/redesign-2026-09/taxonomy/dfam_census_1220_20260917.tsv` and
   `taxonomy/dfam_classes_20260917.json` (each node carries `wicker_equiv`, `repeatmasker_type` and
   `repeatmasker_subtype`); the owner ruled a Dfam view with Wicker's rank names, per-rank status and the clade per
   model as the age-tier evidence, admitted now.
5. `/workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology/02_next_session_agenda.md`
   and its siblings in that directory (the D2 outline and the D1 consult), `/workspaces/Meta-Aging/AGENTS.md` (the
   cohort design: `condition_key`, `MouseID`, the three datasets' replication structure).
6. The counting tools' feature identities as te-tracks registers them (`docs/OUTPUTS.md` consumer table) and the
   dataset facts in `consults/field_practice_synthesis.md` section 5 (chemistries, references, BAM layouts).
7. The project's exploration conventions: `/workspaces/Meta-Aging/AGENTS.md` "Craft standards" (marimo notebooks
   over parquet exported to `03_results/interactive/`, jscatter panels, `notebook-exploration` skill) and the
   standing marimo ports table.

## Questions, each with options, consequences, a recommendation and the settling measurement
1. **The unified schema.** Entities and their identities: record, instance, subfamily, Dfam model and lineage
   node, gene and transcript per annotation pin, gene child snapshot, peak (v2 atlas), cell, cluster or cell type,
   condition and animal, estimator run, molecule counts per feature per cell group, ATAC cut counts per record and
   per peak, motif hits, eRegulon regions. Which are reference dimensions te-tracks publishes, which are dataset
   facts, which are integration facts across datasets. Keys (`te_catalog_id`, `te_build_id`, `rmsk_record_id`,
   record and instance aliases, child snapshot ids, annotation digests, run ids, `condition_key`, `MouseID`). Fact
   and dimension tables, grain of each, provenance columns, and a storage recommendation for plain SQL (parquet plus
   DuckDB is the working assumption; say where it fails). Give the schema as a table list with keys, and five
   example SQL queries, one of them the owner's funnel.
2. **The interactive genome projection.** What the tool needs from the schema: an interval index over genome
   coordinates, layered tracks (records coloured by lineage, clade or divergence; dataset signals by cell group;
   accessibility; motif hits; GRN links), and the query grammar the owner describes as a funnel (all L1 remnants;
   those with RNA support in the nuclei; those in open chromatin; the TF motifs inside them; the subset under the
   studied conditions). Options for the tool itself within the project's conventions (marimo with jscatter panels
   over parquet; an embedded genome browser such as igv.js or JBrowse; HiGlass; a DuckDB-backed track server),
   with consequences for scale (3.8 million records, 30 million context pairs, millions of cells). What te-tracks
   must publish for it to work, and in which order: the instance block union, record 5′ windows, LTR–internal
   candidate pairs, divergence bins, the Dfam rank and clade view, the context relation, `record_starsolo.gtf`.
3. **Reconstruction as a consumer.** Define the first reconstruction questions this tool asks (full-length L1
   copies by subfamily with the model prefix present; provirus candidates from LTR, internal and LTR records; solo
   LTR candidates) and the parameters each needs; how the schema stores candidate status and evidence so that
   verdicts stay the analysis's; which te-tracks views come first and what evidence gate each passes.
4. **The evolutionary-origin question.** How the schema lets the analysis ask whether age-associated TE signal comes
   from young lineages (clade Mus or Mus musculus, low divergence) or old ones (Muroidea, Rodentia, Mammalia): the
   aggregation levels (Wicker order and superfamily, Dfam node, subfamily, clade tier, divergence bin), what is
   testable at each with four animals per condition, and what stays descriptive.
5. **Self-sustained Multiome against unpaired runs.** Which questions the 14761 Multiome answers within one nucleus
   (paired RNA and ATAC: a TE-derived open region with a transcript in the same nuclei), which need the whole-cell
   arms (replication across animals, tissue pairing), and how the schema flags evidence tier per row so a paired
   claim and a condition-level claim never read alike. What "confirmed transcription" means operationally for a
   TE-derived open chromatin region in paired data, given multimapping and host read-through.
6. **Statistical modelling entry points.** How the schema serves per-subfamily and per-lineage aggregation, per-locus
   drill-down, and the cohort design (`condition_key`, `MouseID`, tissue pairing) so a model reads one tidy table
   per question; the reporting tiers; what must never be aggregated silently (multi-universe registration rows,
   overlapping records, fractional EM counts).
7. **Staging.** What to build first in `40_transposable_elements/` and what te-tracks adds in phase 9 for it; what
   waits for the ATAC schema; the smallest end-to-end slice that exercises the funnel on real data (name the
   dataset, the tables and the query).

## Output format (the consult file)
```
# Unified TE schema consult (codex gpt-6-astra)
## Summary of recommendations
<one line per question>
## Q1 .. Q7
<question; evidence with file:line; options and consequences; recommendation; settling measurement>
## Schema sketch
<tables with grain, keys and owner (te-tracks, dataset, integration); the five SQL examples>
## What te-tracks publishes next, in order
<numbered; each with the consumer question it serves and the evidence gate>
## Measurements performed
<commands and outputs, verbatim; read-only>
## Open for the owner
<what only the owner can decide>
```
Under 350 lines. Facts over opinions; every claim about a tool, a table or a document cites a path and, where
possible, a line. Mark general knowledge beyond the local inputs as such. Recommend; do not implement.
