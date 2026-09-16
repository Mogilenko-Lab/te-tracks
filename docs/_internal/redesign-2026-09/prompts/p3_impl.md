# te-tracks phase 3: canonical taxonomy by rule

You are the implementer for phase 3 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 2 have landed:
read `AGENTS.md`, `tests/run.sh` (checks are `tests/checks/<mode>/*.sh` and `*.py`, run by name order through
`bash` or `python3`; exit 0 pass, 3 unsupported, other fail; build dir `$TE_TRACKS_REFROOT/te_mm39/build`,
with `tests/lib/records.py` supplying `BUILD`, `require` and a typed TSV reader), `src/lib/build_records.py`,
`src/lib/build_universes.py`, `src/lib/records_io.py` (`tsv_stream`, `write_tsv` for deterministic output)
and `docs/OUTPUTS.md` for the table contracts you build on. `tables/rmsk_taxonomy.tsv` has the columns
`rmsk_name, rmsk_family, rmsk_class, record_count, record_length_sum_bp`, one row per raw triple; class-only
`.out` tokens appear with `rmsk_family` equal to `rmsk_class`, and uncertain labels keep their trailing `?`.
The reviewed class set lives in `config/mm39.classes.tsv`.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md` (your phase: the rule
   `taxonomy_rule_v1`, statuses, precedence, deliverables, acceptance numbers). Follow it exactly.
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 1 and 5
3. `docs/_internal/redesign-2026-09/taxonomy/README.md`, `dfam_lookup_20names.tsv`,
   `out_token_census_20names.tsv` (the evidence and the fixture source)
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Deliverables (exact paths; details in the phase file)
1. `src/20_build_taxonomy.sh <build-dir> <config.env>` calling `src/lib/build_taxonomy.py`, which reads
   `<build-dir>/tables/rmsk_taxonomy.tsv` and `tables/rmsk_records.parquet` (for `median_divergence_pct`
   per name over `divergence_pct`) and writes `tables/taxonomy_canonical.tsv` (13 columns in the phase
   file's order, one row per name, sorted by name) and `tables/taxonomy_resolution_report.tsv` (names with
   `label_count > 1`). The rule lives in one pure function `resolve(labels: list[tuple[cls, fam, count]])
   -> dict` with the module constant `TAXONOMY_RULE_VERSION = "taxonomy_rule_v1"`, importable by tests.
   Ties publish `unresolved` at that rank and below, with empty canonical fields at unresolved ranks.
2. `tests/fixtures/taxonomy/dfam_snapshot.tsv`: the 20-name Dfam lookup copied from
   `docs/_internal/redesign-2026-09/taxonomy/dfam_lookup_20names.tsv` with an added `fetched_on` column
   (`2026-09-16`), plus `dfam_snapshot.provenance.json` stating the API endpoint pattern
   (`https://dfam.org/api/families?name=<name>&format=summary`), the fetch date, and that the snapshot is
   test evidence the build never reads.
3. Checks under `tests/checks/core/`:
   - `30_taxonomy_canonical.py`: exit 3 when the table is absent; asserts the acceptance numbers in the
     phase file (18,484 rows; 20 `has_multiple_labels`; 0 unresolved at either rank; family statuses 7
     resolved_majority, 5 resolved_unspecified, 5 resolved_uncertainty_suffix, 3 unspecified; all 20
     multi-label names `canonical_class = DNA`; min `family_majority_share` among resolved_majority rows
     0.734; the resolution report has exactly the 20 names).
   - `31_taxonomy_dfam_agreement.py`: joins the resolution report with the snapshot; asserts
     `canonical_class == dfam_repeat_type` for every name and `canonical_family == dfam_repeat_subtype`
     where the subtype is non-empty; asserts the two name sets are equal; prints each disagreement with
     both labels before failing.
   - `32_taxonomy_rule_fixtures.py`: imports `resolve` and runs it on hand-authored inputs under
     `tests/fixtures/taxonomy/rule_cases.tsv` (columns: case, labels as `class/family=count;...`, expected
     canonical_class, canonical_family, class_status, family_status): one case per status; a class-level
     competition; a two-way family tie (expects `unresolved`); a two-way class tie; a name mixing `?` and an
     unspecified family (Eulor5B shape); a name whose only labels are class-only with and without `?`
     (MER124 shape, expects `DNA/DNA`, family `unspecified`); a parent/child family competition where the
     specific token holds the majority (MER53 shape: hAT 7, hAT-Blackjack 1633; expects `hAT-Blackjack`,
     `resolved_majority`); a rollup case where a name with two labels and one record count contributes
     once to its family total.
4. `docs/OUTPUTS.md`: sections for `taxonomy_canonical` and `taxonomy_resolution_report` (columns, one-line
   contracts), the rule stated in four numbered sentences with its version, and the rollup rule (family and
   class rollups join through `taxonomy_canonical`; a name unresolved at a rank carries an empty canonical
   label there, and every rollup at that rank names it `unresolved/<rmsk_name>`, one bucket per name,
   distinct from RepeatMasker's literal `Unknown`). README truth table rows to `tested`, phase 3.

## Rules
- Touch only: `src/20_build_taxonomy.sh`, `src/lib/build_taxonomy.py`, `tests/fixtures/taxonomy/**`,
  `tests/checks/core/3*`, `docs/OUTPUTS.md`, `README.md` (truth table rows). Nothing else.
- No git writes. No installs. No network: the Dfam snapshot is copied from the file named above.
- The build reads no Dfam data and no network. The rule is total: any input list yields a result.
- Report a deviation instead of editing a number, an expectation, or a plan file to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
bash src/20_build_taxonomy.sh "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env; echo "exit=$?"
wc -l "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_canonical.tsv" "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_resolution_report.tsv"
cut -f5 "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_canonical.tsv" | sort | uniq -c
cut -f4 "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_canonical.tsv" | sort | uniq -c
cat "$TE_TRACKS_REFROOT/te_mm39/build/tables/taxonomy_resolution_report.tsv"
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim; any deviation.
