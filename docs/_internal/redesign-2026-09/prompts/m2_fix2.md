# te-tracks milestone 2 fix, round 2: two corrections to `m2_fix.md`

You are the implementer for the second round of the milestone 2 fix unit. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, uncommitted tree from round 1
(`docs/_internal/redesign-2026-09/prompts/m2_fix.md`). Round 1 reported two deviations, both caused by the
prompt; this round corrects the specification. Read `tests/run.sh`, `tests/checks/core/01_runner_selftest.sh`,
`src/lib/build_universes.py` (`check_class_set`), `tests/checks/core/22_universes.py`,
`tests/checks/core/23_records_fixtures.py`, `config/mm39.classes.tsv` and `tests/fixtures/records/classes.tsv`.

Binding prose rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Corrections

1. **Runner self-test uses a mode the runner accepts.** `tests/run.sh` takes `core`, `consumers` or `acceptance`.
   In `01_runner_selftest.sh`, create the probe checks under `<scratch>/tests/checks/core/` and invoke the copied
   runner with `core --refroot <scratch>`. Keep every assertion (five status lines, the counts line, the stderr
   diagnostic, the two removals, the missing-directory exit 2 with `acceptance`, the usage exit 2). The check
   passes on this tree.
2. **Disposition gate as a per-class biconditional.** A fixture's reviewed file lists only the classes the fixture
   observes, so an exact-set comparison with `INTERSPERSED_CLASSES` fails there. Replace the two exact-set
   assertions in `check_class_set` with, for every reviewed class `c`:
   `(disposition[c] == "interspersed") == (c in INTERSPERSED_CLASSES)` and
   `(disposition[c] == "satellite") == (c == "Satellite")`; a violation names the offending classes on each side
   (`disposition_without_predicate`, `predicate_without_disposition`). Keep the column, duplicate, vocabulary and
   observed-equals-reviewed checks and the provisional check (every provisional class present in the reviewed file
   is dispositioned `interspersed`). `22_universes.py` asserts the same biconditionals over `config/mm39.classes.tsv`
   and, for mm39, that every class in `INTERSPERSED_CLASSES` is reviewed. `23_records_fixtures.py` keeps its two
   failing cases and adds a third: a predicate class present in the fixture dispositioned `structural_rna` (LINE)
   fails with `predicate_without_disposition=['LINE']`. Fixture records and expectations stay as they are.
3. **Contract sentence.** In `docs/OUTPUTS.md`, the universes paragraph sentence beginning "The build requires the
   observed class set to equal the reviewed set" states the relations as: observed class set equals the reviewed
   set; the disposition `interspersed` agrees with the authored predicate class by class; the disposition
   `satellite` marks exactly `Satellite`; every provisional class is dispositioned `interspersed`.

## Rules
- Touch only: `tests/checks/core/01_runner_selftest.sh`, `src/lib/build_universes.py`,
  `tests/checks/core/22_universes.py`, `tests/checks/core/23_records_fixtures.py`, `docs/OUTPUTS.md` (that one
  sentence). Nothing else.
- No git writes. No installs. No network. Re-run only stage 15 on `$TE_TRACKS_REFROOT/te_mm39/build`; every table
  digest and `universes.json` must verify against `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m2fix_before.sha`.
- Report a deviation instead of editing a number, an expectation or a fixture to fit. Tests are strengthened only.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
B="$TE_TRACKS_REFROOT/te_mm39/build"
bash -n tests/checks/core/01_runner_selftest.sh && echo syntax ok
bash src/15_build_universes.sh "$B" config/mm39.env; echo "exit=$?"
sha256sum -c /workspaces/Meta-Aging/_scratch/te-tracks-audit/m2fix_before.sha
tests/run.sh core; echo "exit=$?"
git status --short | grep -v docs/_internal
```
Expected: stage 15 exits 0; every digest `OK`; `core` exits 0 with `checks=7 pass=7 fail=0 unsupported=0`; the
status list equals round 1's package files with no additions.

## Final message
Every file changed; acceptance outputs verbatim; the three disposition mutation messages; any deviation.
