# te-tracks phase 2: fix loop after review

You are the implementer for phase 2 of the te-tracks redesign, returning to fix review findings. Working
directory (absolute): `/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Your
phase 2 work is in the working tree (uncommitted).

Read both reviews first: `docs/_internal/redesign-2026-09/reviews/p2_codex.md` and
`docs/_internal/redesign-2026-09/reviews/p2_opus.md`. Both pass with advisories; the orchestrator rules that the
items below are fixed now, before the phase commits. Then re-read the phase contract
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/12_phase2_canonical.md` and your prompt
`docs/_internal/redesign-2026-09/prompts/p2_impl.md`. Wording rules: `/workspaces/Meta-Aging/AGENTS.md`
sections "Prose" and "Comments".

## Resolutions (the orchestrator's rulings; implement exactly)
- **F1, README (codex A1, Opus A1).** Rewrite the Build section (lines 21 to 36) and the Outputs paragraph
  (lines 38 to 42) in one pass so every sentence is true of the current build: `build.sh` writes the pinned
  sources with `source/SOURCES.json` and `source/qualification.md`, the canonical tables under `tables/` and
  `universes.json`; core checks cover the parser fixtures, the qualification report, the record schema,
  instances, universes and the record fixtures. The Outputs paragraph reads: "Published legacy releases in the
  reference cache carry `te_loci.tsv.gz`, `te_dim.tsv`, `MANIFEST.json` and `BUILD_ID`; the current build
  produces `source/`, `tables/` and `universes.json`, and phases 3 to 9 supply the remaining artifacts." The
  sentence after the truth table (line 106) then reads: "[docs/OUTPUTS.md](docs/OUTPUTS.md) specifies the
  schemas, serialization and deferred export contracts." Add the truth table row
  `tests/lib/records.py | delivered, tested | 2` beside `tests/lib/consumers.py`.
- **F2, legacy schema (codex A2, Opus A2).** In `docs/OUTPUTS.md`, add a section `## Published legacy release`
  between the phase 2 sections and `## Deferred`, restoring from `git show HEAD:docs/OUTPUTS.md` (lines 6 to
  37) the one-sentence description, the 15-column `te_loci.tsv.gz` table (with the UCSC `rmsk_id` meaning)
  and the `te_dim.tsv` column sentence. Add disposition rows to "Legacy names and their disposition":
  `te_loci.tsv.gz` → `tables/rmsk_records.tsv.gz` (phase 2); `te_dim.tsv` → `tables/rmsk_taxonomy.tsv` and
  `tables/universe_summary.tsv` (phase 2); legacy `MANIFEST.json` and `BUILD_ID` → their phase 7 forms.
- **F3, reviewed class set as configuration (codex A3, Opus A3).** Create `config/mm39.classes.tsv`: header
  `rmsk_class`, one reviewed class per row, C-locale sorted (the 17 mm39 classes). Add `!config/*.tsv` to
  `.gitignore` under a one-line intent comment. `src/15_build_universes.sh` passes
  `--class-set "$REPO_ROOT/config/${GENOME}.classes.tsv"`; `build_universes.py` gates on set equality with
  that file (validate header and uniqueness; name unreviewed and absent classes in the failure).
  `tests/expectations/mm39/class_census.tsv` keeps the counts; `tests/checks/core/22_universes.py` asserts the
  counts against it and asserts that its class set equals the config set. Rename the fixture
  `tests/fixtures/records/class_census.tsv` to `classes.tsv` with the single column and use it in check 23.
  `docs/OUTPUTS.md` universes paragraph: publication requires the observed class set to equal
  `config/<genome>.classes.tsv`; core checks compare measured counts with
  `tests/expectations/<genome>/class_census.tsv`.
- **F4, join disagreement fixture (Opus A4).** Add `tests/fixtures/records/disagree.tsv` (the `rmsk.tsv` rows
  with `Split`'s family changed to `hAT2`) to the check 23 join loop, expecting `UCSC rmsk_family disagreement`
  naming `Split`.
- **F5, one class list (Opus A5).** In `build_universes.py`, author the nine interspersed classes once as a
  module constant and build every predicate from it; spell `interspersed_plus_satellites` as a single
  `class_in` list (the constant plus `Satellite`) and `compat_tetranscripts_mm39` likewise plus the family
  exclusion. Remove the `or` key from the grammar (evaluator, check 22's `declared_mask`, the `docs/OUTPUTS.md`
  grammar paragraph and table). The published `universes.json` changes accordingly; the summaries stay equal.
- **F6, redundant sample (Opus A6).** In check 20, delete the 10,000-index sample comparison; the full-table
  equality stays. Adjust the pass message.
- **F7, census read (Opus A7).** Check 22 reads the census with `keep_default_na=False` and explicit dtypes.
- **F8, instance statistics by token (Opus A8).** `RecordStats.add` in `src/lib/rmsk_out.py` keys instances by
  the text token; `tools/qualify_source.py` converts to `int` only for `id_min`, `id_max` and `ids_contiguous`.
  The mm39 qualification report must stay byte-identical to the tracked copy.

## Rules
Touch only: `README.md`, `docs/OUTPUTS.md`, `.gitignore`, `config/mm39.classes.tsv` (new),
`src/15_build_universes.sh`, `src/lib/build_universes.py`, `src/lib/rmsk_out.py`, `tools/qualify_source.py`,
`tests/checks/core/20_records_schema.py`, `tests/checks/core/22_universes.py`,
`tests/checks/core/23_records_fixtures.py`, `tests/fixtures/records/classes.tsv` (renamed from
`class_census.tsv`), `tests/fixtures/records/disagree.tsv` (new). No git writes (rename with `mv`), installs or
network. Report a deviation instead of editing a number, an expectation, a fixture value or a plan file to fit.

## Acceptance (run and paste verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
python3 - <<'PY'
import shutil, pathlib
p = pathlib.Path('/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build')
shutil.rmtree(p, ignore_errors=True); print('clean:', not p.exists())
PY
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
time ./build.sh --genome mm39 --build-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
cmp "$TE_TRACKS_REFROOT/te_mm39/build/source/qualification.md" docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md && echo "report identical"
cat "$TE_TRACKS_REFROOT/te_mm39/build/universes.json"
sha256sum "$TE_TRACKS_REFROOT/te_mm39/build/tables/"* "$TE_TRACKS_REFROOT/te_mm39/build/universes.json"
tests/run.sh core; echo "exit=$?"
grep -rn "tests/expectations" src || echo "no test path in src"
grep -n '"or"' src/lib/build_universes.py tests/checks/core/22_universes.py docs/OUTPUTS.md || echo "no or clause"
grep -n -E "source layer under|Core checks cover parser fixtures" README.md || echo "README paragraphs rewritten"
grep -n "tests/lib/records.py" README.md
git check-ignore -v config/mm39.classes.tsv || echo "config class set trackable"
git status --short
```
Mutation probes (scratch copies under `/workspaces/Meta-Aging/_scratch/`, removed afterwards; paste outputs):
1. A copy of `config/mm39.classes.tsv` without `DNA?` given to `build_universes.py` on a scratch build dir that
   holds a symlink to the built `tables/rmsk_records.parquet` → exit 1 naming `DNA?`.
2. A scratch repo copy whose `tests/expectations/mm39/class_census.tsv` lacks `DNA?` → check 22 exit 1.
3. Fixture `disagree.tsv` fed directly to `build_records` → `ValueError` naming `Split`.

## Final message
Each finding with what changed (file and line range); acceptance and probe outputs verbatim; the new
`universes.json` digest; any deviation.
