# te-tracks phase 8 design consult: the gene child family (codex, read-only)

You are consulted on design, before any implementation prompt exists. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, commit `__HEAD__`. You write exactly
one file: `docs/_internal/redesign-2026-09/consults/gene_child_consult.md`. You change nothing else. No git writes
anywhere (the eleven consumer checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too:
DfamTEBrowser, irescue, mascarade, MATES, mLLMCelltype, scTE, scTEfinder, stellarscope, TElocal, TEsingle, TEtranscripts; the
directory also holds `14839-DM-cGAS`, the owner's copy, read it and leave it alone, and `sene/`, which you leave alone), no installs, no network.
Export `PYTHONDONTWRITEBYTECODE=1`. Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8-consult/`,
removed when you finish (Python `shutil`; `/tmp` is noexec). Read-only inputs: the core build at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` (`BUILD_ID` `0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a`,
`CATALOG_ID` `0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4`), the published root `.../refroot/pubroot`, and the GENCODE vM37 GTF at
`/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz`
(md5 `702e27a8727db66cd23e9f66f5aa1d38`).

The owner rules on this consult; the orchestrator then holds an ADR discussion with the owner on the
transcript-context relation and `gene_context`, and only then writes the phase 8 implementation prompt. Your job is
to make that ruling well informed: options with consequences, a recommendation per question, and the measurement
that would settle each open point.

## Read, in order
1. `docs/_internal/redesign-2026-09/consults/gene_context_material.md`: the evidence pack (sources, consumer needs,
   tool gene models, the vM37 census, open questions, candidate ADR statements G1 to G6). Section 8 records which
   facts the orchestrator re-verified; section 7 lists what stays unverified.
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md` (the current draft
   the consult may reshape) and `19_phase9_acceptance_park.md`.
3. `docs/DECISIONS.md` (entries 4, 7 and the deferrals), `docs/OUTPUTS.md` (exports, registration key, preflight),
   `docs/RELEASES.md` (identity, `parent_build_id`, publication), `README.md`.
4. Rulings that bind the child: `reviews/m2_rulings.md` (H3, H5), `reviews/m5_rulings.md` (A1 block columns, A2
   explicit exporter inputs), `reviews/p6_rulings.md` (alias table for child preflight), `reviews/p7_rulings.md`
   (verifier against the archive's own declaration, `CATALOG_ID` scope, `build_sources`).
5. Earlier consults on this seam: `consults/ADR4_consult.md`, `consults/ADR38_consult.md`,
   `consults/FINAL_REPORT.md` sections on the two build families, `consults/SYNTHESIS.md`, `consults/codex_critique.md`.
6. Code the child extends: `build.sh`, `src/lib/manifest.py`, `src/release.py`, `src/lib/build_exports.py`,
   `src/lib/contigs.py`, `bin/te-tracks-preflight`, `tests/fixtures/publication/build_fixture.py`.
7. The consumers: the D2 plan under `/workspaces/Meta-Aging/14761-DM/docs/_internal/_project/plans/2026-09-11_codebase-topology/`;
   the lab's bulk recipe `/workspaces/Meta-Aging/14761-DM/01_modules/scio/skills/te-reference-saf-build/scripts/build_te_saf.sh`
   and `/workspaces/Meta-Aging/01_modules/.ref/14839-DM-cGAS/01_modules/TE-RNAseq-toolkit/docs/{METHODOLOGY,LIMITATIONS}.md`;
   the tool gene models cited in the evidence pack (TEsingle `transcript`, TEtranscripts and TElocal `exon`, MATES gene bodies).

## Questions to answer, each with options, consequences, a recommendation and the settling measurement
1. **Topology.** One child family per (parent build, gene annotation pin, policy id) holding both the
   exon-subtracted SAF and the context relation, versus separate children per product, versus one child with
   several named views. Consider identity (`BUILD_ID`, `parent_build_id`, `parent_catalog_id`, a GTF digest and a
   policy id), the GENCODE bump path, and what a consumer pins.
2. **Architecture.** How the child reuses the core: `build.sh` family dispatch and config shape (`config/mm39_gene.env`
   with `PARENT_FAMILY`), how the child locates and pins its parent (`current` may move; an archive path or a
   `BUILD_ID` under a root), the child's own `tables/exports.tsv` and inventory, the alias and length source for child
   preflight (copy by digest, pin, or symlink), and what `manifest.py` and `release.py` need to admit a family whose
   parents are non-null (the verifier accepts published versions and judges an archive against its own declaration;
   the `SPECIES` table and the family regex are the admission points).
3. **The exon mask.** All `exon` rows of all transcript types, both strands (`all_exons_unstranded_union_v1`), against
   narrower masks (`basic`, `Ensembl_canonical`, protein-coding); the evidence pack measured the genomic unions
   (160.5 / 132.6 / 112.7 / 75.9 Mb). Judge against the lab's gene pass (`-t exon` over every exon row) and the
   tools' gene models; state what a minimum retained block length would do and whether to record one.
4. **Piece registration and status.** Block columns in the registration key (ruled), one row per retained block;
   whether `exon_subtraction_status` stays a table of its own or becomes columns of a per-record status row shared
   with the context relation; how `fully_subtracted` records appear to a consumer; the acceptance anchor 3,717,740
   retained records under `compat_tetranscripts_mm39`, which the plan marks "to be re-measured" (measure it if a
   bounded computation on the build and the GTF allows; state the method and the result).
5. **The context relation.** Sparse record × transcript with a per-record status row (G3); geometry per G4 (TSS and
   TES landmarks, signed genomic distances with the closest-base rule, relative strand, promoter bases stored under a
   `promoter_policy_id` with `(U, D)`, all isoforms with ties, `Ensembl_canonical` as a flag); per-record status
   vocabulary (`evaluated`, `contig_outside_annotation`, `unsupported_structure`, `not_computed`); expected row
   counts and bytes at mm39 scale (estimate from the build's 5,320,771 records and the GTF's 278,369 transcripts,
   under the sparsity rule the evidence pack quotes); whether the relation ships in phase 8 or in a later child.
6. **Where `gene_context` is computed** (G5). te-tracks ships the relation and consumers derive labels, versus
   te-tracks ships a named, versioned convenience view, versus each consumer computes from its own GTF. State what
   D2 would put in `te_locus_dim` under each option and how the 10 kb / 20 kb bulk windows are derived.
7. **Combined-mode counting.** What the SAF must carry so the lab's driver (`featureCounts -F SAF`, TE pass with
   `-M`, gene pass unique-only, row-bind) and TEtranscripts/TEsingle/TElocal consume it without a rename; whether
   the child also emits exon-subtracted BED or GTF; contig namespace of the SAF against a consumer's BAM.
8. **Acceptance and fixtures.** The fixtures a phase 8 implementer needs (central exon splitting a record into two
   pieces with the parent id; a record fully inside an intron; a record on a contig without annotation; a GTF contig
   name mapped through the alias table; an exon on a scaffold), and the numbers a check can pin.

Critique G1 to G6 in the evidence pack directly: keep, amend or reject each, with the reason.

## Output format (the consult file)
```
# Phase 8 design consult: the gene child family (codex gpt-6-astra)
## Summary of recommendations
<one line per question>
## Q1 .. Q8
<question; evidence with file:line; options and consequences; recommendation; settling measurement>
## Candidate ADR statements for the owner
<numbered; one paragraph each; each names what it prevents; mark recommended or alternative>
## Measurements performed
<commands and outputs, verbatim>
## Open for the owner
<what only the owner can decide, and what the discussion needs from them>
```
Under 300 lines. Facts over opinions; every claim about a tool or a document cites a path and, where possible, a
line. Recommend; do not implement.
