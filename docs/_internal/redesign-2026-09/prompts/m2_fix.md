# te-tracks milestone 2 fix: rulings that change phase 1 and 2 artifacts

You are the implementer for the milestone 2 fix unit of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, tree at `c28caea` plus plan-file
edits. Read `AGENTS.md`, `tests/run.sh`, `src/lib/build_universes.py`, `src/lib/build_records.py`,
`src/00_fetch_sources.sh`, `tests/checks/core/{11_source_qualification.sh,22_universes.py,23_records_fixtures.py}`,
`config/mm39.classes.tsv`, `tests/fixtures/records/classes.tsv` and `docs/OUTPUTS.md` first. The rulings you
implement are items 1 to 4 under "Package changes before phase 3" in
`docs/_internal/redesign-2026-09/reviews/m2_rulings.md`; the reviews behind them are `reviews/m2_codex.md` (A4)
and `reviews/m2_divergent.md` (H1, H2, H4, L1, M3).

Binding prose rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (affirmative, intent
only, one line where one line does it).

## Changes

1. **Class disposition (H4).** `config/mm39.classes.tsv` gains a second column `disposition` with one value per
   class from the closed vocabulary `interspersed`, `satellite`, `simple_repeat`, `low_complexity`,
   `structural_rna`: DNA, DNA?, LINE, LTR, RC, Retroposon, SINE, Unknown, Unspecified are `interspersed`;
   Satellite is `satellite`; Simple_repeat is `simple_repeat`; Low_complexity is `low_complexity`; rRNA, scRNA,
   snRNA, srpRNA, tRNA are `structural_rna`. `build_universes.check_class_set` asserts, with a distinct message
   each: columns are exactly `rmsk_class, disposition`; classes unique; every disposition in the vocabulary;
   observed class set equals the reviewed set; the set dispositioned `interspersed` equals `INTERSPERSED_CLASSES`;
   the set dispositioned `satellite` equals `{"Satellite"}`; every `provisional_classes` entry in `DEFINITIONS` is
   dispositioned `interspersed`. `tests/checks/core/22_universes.py` asserts the same relations from the file.
   `tests/fixtures/records/classes.tsv` gains the column; `23_records_fixtures.py` adds failing cases: a class
   dispositioned `interspersed` that the predicate lacks, and an unknown disposition word. The predicate stays
   authored once in `build_universes.py`.
2. **Declared assembly (M3).** `src/00_fetch_sources.sh` writes `declared_assembly` into `SOURCES.json`:
   `{"genome_fa_url": $GENOME_FA_URL, "genome_fa_md5": $GENOME_FA_MD5, "status": "declared"}`, with no fetch and
   no checksum of a FASTA. Check 11 asserts both values equal the config pins. Regenerate the build's
   `SOURCES.json` by re-running `src/00_fetch_sources.sh` against the existing build dir (cache hits copy the
   retained bytes; the four md5s are unchanged).
3. **Component alphabet (L1).** `validate_records` rejects `:` in `rmsk_name` (pattern `[|:\s]`, same message
   `invalid rmsk_name for record identity`). Add `tests/fixtures/records/colon_name.out` with one row whose name
   is `Bad:Name` and register it in the failure table of check 23 with offender `Bad:Name`.
4. **Disposition rows in `docs/OUTPUTS.md` (A4, H1, H2).** In the legacy disposition table: `te_subfamily.gtf` →
   "`subfamily.gtf` (phase 4)"; `te_locus.gtf` → "`record.gtf` (phase 4)"; `te_locus.locInd` → "`.locInd` index
   built from `record.gtf` by TElocal's own indexer (fixture, phase 5)"; `rename_map.tsv` → "Superseded by
   `tables/taxonomy_canonical.tsv` (phase 3); the legacy selection is reproducible as the
   `compat_tetranscripts_mm39` membership". Rewrite the class-set paragraph (around lines 84 to 88) to state the
   two-column file, the vocabulary and the three set relations the build asserts. Add one sentence under the
   universes section: the `compat_tetranscripts_mm39` universe ships as membership, and the legacy comparison is
   a phase 9 reconciliation. Add one sentence in the phase 4 section: exports carry no provisional flag; the
   status is a class property recoverable by joining names to `rmsk_taxonomy`.

5. **Runner self-test (Opus A1).** New check `tests/checks/core/01_runner_selftest.sh`: copy `tests/run.sh` into
   a temporary tree as `<tmp>/tests/run.sh`, create `<tmp>/tests/checks/probe/` with `10_pass.sh` (exit 0),
   `20_unsupported.sh` (exit 3), `30_required.required.sh` (exit 3), `40_fail.sh` (exit 7, prints one line),
   `50_dangling.sh` (symlink to a missing target); run `<tmp>/tests/run.sh probe --refroot <tmp>` and assert
   exit 1 and the five status lines (`pass`, `unsupported`, `unsupported` for the required check, `fail`,
   `fail ... dangling symlink`); then remove `30_*`, `40_*`, `50_*` and assert exit 0. Also assert exit 2 for a
   missing check directory and for no arguments. The check needs no build and never exits 3.
6. **Gate fixtures isolate their gate (Opus A2).** For `beyond_end.out`, `missing_chrom.out`,
   `spanning_instance.out`, `invalid_name.out`, `invalid_chrom.out` and the new `colon_name.out`, author a
   matching one-row (or, for the spanning case, matching-row) UCSC table `tests/fixtures/records/<stem>.tsv`
   and pass it in check 23's failure table, so removing the named gate fails on the named message alone.
   Verify by temporarily disabling each gate locally and restoring it; report the observed message.
7. **DECISIONS.md wording (Opus A3).** Entry 2's sentence "Each new assembly passes a class census before any
   biological universe publishes" becomes a statement that the observed class set matches the reviewed
   disposition file (`config/<genome>.classes.tsv`) before any biological universe publishes.
8. **Consensus ordering (Opus A4).** Beside the signed consensus-column contract in `docs/OUTPUTS.md`, one
   sentence: consensus start and end follow the source; two mm39 records carry start above end
   (`L1MdFanc_II|chr1:9847889-9847905|-`, `L1MdF_III|chr2:116363011-116363342|-`), so a derived consensus-match
   length is signed.

## Rules
- Touch only: `config/mm39.classes.tsv`, `src/lib/build_universes.py`, `src/lib/build_records.py`,
  `src/00_fetch_sources.sh`,
  `tests/checks/core/{01_runner_selftest.sh,11_source_qualification.sh,22_universes.py,23_records_fixtures.py}`,
  `tests/fixtures/records/{classes.tsv,colon_name.out,<stem>.tsv for the six gate fixtures}`, `docs/OUTPUTS.md`,
  `docs/DECISIONS.md`. Nothing else.
- No git writes. No installs. No network. The build dir is `$TE_TRACKS_REFROOT/te_mm39/build`; re-run only stages
  00 and 15 there. Every table digest and `universes.json` must be byte-identical before and after.
- Report a deviation instead of editing a number, an expectation, a fixture expectation or a plan file to fit.
- Tests are strengthened only; report any check you cannot make pass by name.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
B="$TE_TRACKS_REFROOT/te_mm39/build"
sha256sum "$B"/tables/* "$B"/universes.json > /workspaces/Meta-Aging/_scratch/te-tracks-audit/m2fix_before.sha
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
bash src/00_fetch_sources.sh "$B" config/mm39.env; echo "exit=$?"
python3 -c "import json;d=json.load(open('$B/source/SOURCES.json'));print(d['declared_assembly'])"
bash src/15_build_universes.sh "$B" config/mm39.env; echo "exit=$?"
sha256sum -c /workspaces/Meta-Aging/_scratch/te-tracks-audit/m2fix_before.sha
tests/run.sh core; echo "exit=$?"
git status --short
```
Expected: `declared_assembly` prints the config URL and md5 with status `declared`; both stages exit 0; every digest
reports `OK` (universes.json stays `617feb99e7711f413df3e7935e532abcc12d4ecf7cfbcc4009a6cf31f2cb1b4c`); `core`
exits 0 with seven passes; `git status` lists only the files named above plus the pre-existing plan and review files.

## Final message
Every file created or changed; acceptance outputs verbatim; any deviation.
