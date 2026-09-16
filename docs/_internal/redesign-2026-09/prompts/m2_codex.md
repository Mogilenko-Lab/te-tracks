# te-tracks milestone review after phase 2: schema and identity seam (codex, read-only)

You review the committed state of the te-tracks redesign after phases 0, 1 and 2. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, commit `__P2_COMMIT__`. You
write exactly one file: `docs/_internal/redesign-2026-09/reviews/m2_codex.md`. You change nothing else. No
git writes, no installs, no network. Scratch work goes under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m2-codex/`
and is removed when you finish; the orchestrator's build at
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` is read-only for you.

Your question is the identity seam: do the published schema, keys and universes carry phases 3 to 9 and the
consuming project without a later rename or re-keying? Two other reviewers cover numbers and fixtures (Opus)
and unstated assumptions (divergent); leave those to them.

## Read
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md`, `01_decisions.md`,
   `12_phase2_canonical.md`, then the downstream phase files `13_phase3_taxonomy.md`, `14_phase4_exports.md`,
   `16_phase6_ensembl_preflight.md`, `17_phase7_publication.md`, `18_phase8_gene_child_seam.md`.
2. `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` (schema, ledger relations, conservation rule).
3. Public contract: `README.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `AGENTS.md`.
4. Code: `src/lib/rmsk_out.py`, `src/lib/records_io.py`, `src/lib/build_records.py`,
   `src/lib/build_universes.py`, `tests/lib/records.py`, `tests/checks/core/*`.
5. The phase reviews: `docs/_internal/redesign-2026-09/reviews/p{0,1,2}_{codex,opus}.md`.

## Judge, with evidence
- **Record key.** `rmsk_record_id = <rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`: does every downstream
  consumer named in the plan (GTF attributes, SAF GeneID, BED name, `export_feature_members`, the ledger's
  `peak_record_overlaps` and `te_feature_registration`) parse or carry it without escaping? Which characters in
  the measured mm39 name set (`tables/rmsk_taxonomy.tsv`) sit outside the phase 4 safe alphabet
  `[A-Za-z0-9_.+/?()|:-]+`, and which GTF or SAF readers named in phase 5 treat any of them specially?
- **Instance key.** `rmsk_instance_id` is the `.out` ID as text, valid within one source-wide run. What in the
  schema or the manifest states that scope, and what breaks when a future assembly ships per-contig `.out`
  files with restarting IDs (hg38 deferral)? Is the text type compatible with the phase 4 `instance_id`
  attribute `I|mm39|<id>` and the phase 7 identity hash?
- **Taxonomy seam.** `rmsk_taxonomy` (raw triples) feeds phase 3's `taxonomy_canonical` (one row per name).
  Does `rmsk_taxonomy` carry what `taxonomy_rule_v1` needs (record counts per raw label, the `?` suffix
  intact, class-only tokens distinguishable)? Name any input the rule needs that the table lacks.
- **Universe grammar.** `universes.json` predicates use `class_in`, `family_prefix_excluded`, `or`. Can the
  phase 4 exports, the phase 6 namespace copies and the phase 8 child build reference a universe by name
  alone, and can a future universe (for example an ERV unit set) be expressed without a new grammar? Judge
  the decision to author the definitions as a Python dict serialized into the build.
- **Contig namespaces.** Phase 6 renames `chrom` in exports while record ids keep UCSC names. Does anything in
  the phase 2 schema or checks assume `chrom` equals the id's contig component?
- **Identity hash inputs.** Phase 7 hashes `universes` and `export_contracts` into `BUILD_ID`. Is
  `universes.json` byte-stable across Python versions (key order, `ensure_ascii`, indentation) and does its
  `schema_version` cover the predicate grammar?
- **Serialization contract.** TSV and parquet: are the stated guarantees (LF, `true`/`false`, no nulls,
  `\N` reserved) sufficient for DuckDB, R `arrow`/`data.table` and pandas readers named in the consults? Any
  column whose type will surprise a reader (`rmsk_instance_id` as text, signed `consensus_left_bp`)?
- **Legacy compatibility.** `compat_tetranscripts_mm39` reproduces the legacy TEtranscripts class set with the
  `tRNA` family-prefix exclusion. Compare its predicate to the legacy rule in `docs/PROVENANCE.md` and the
  legacy `config` at `git show 6ff3ee9:config/mm39.env`; name any difference.

## Output format (the review file)
```
# Milestone 2 review: schema and identity (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it, and in which phase>
## Advisory
- [A1] ...
## Evidence
<commands and outputs, verbatim, for every measured claim>
## Scope check
<git status before and after; files you wrote>
```
BLOCKING means a later phase cannot proceed without changing a published key, column or file name. Keep the
file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.
