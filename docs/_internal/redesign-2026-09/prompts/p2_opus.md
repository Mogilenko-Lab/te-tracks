Re-review phase 2 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/12_phase2_canonical.md (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p2_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.

Phase-2 specifics:
(a) Build into your own directory, `/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p2/build`, with
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` (about five minutes; the
`/tmp` filesystem is noexec, scratch under `/workspaces/Meta-Aging/_scratch/` executes). Leave
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` untouched; compare your digests with
it. Remove your build directory when done.
(b) Recompute with your own code from `tables/rmsk_records.parquet` (pyarrow or pandas), independent of
`src/lib/`: 5,320,771 rows; 24 columns in the ADR 5 order (`consults/ADR5_consult.md` section 2) with
int64/float64/bool/string types and zero nulls; `rmsk_record_id` unique and equal to
`<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`; 4,696,900 distinct `rmsk_instance_id`, sizes 1: 4,251,251,
2: 338,697, 3+: 106,952, each on one contig; six universes with records/names/triples/length_sum_bp equal to
`tests/expectations/mm39/universe_summary.tsv`; `universe_members.tsv.gz` rows = 14,997,840 (the five
non-`all_rmsk` universes summed) with `provisional=true` on exactly 5,893 rows in each of `interspersed` and
`interspersed_plus_satellites` (Unknown 5,786 + Unspecified 98 + DNA? 9) and none elsewhere; class census
equal to `tests/expectations/mm39/class_census.tsv`; 20 names with more than one raw label covering 6,517
records; 3 coordinate-only collision pairs; exactly 6 rows with `consensus_left_bp < 0` and none with
`query_left_bp < 0`; `length_bp = end_1 - start_1 + 1`; `source_row_number` a permutation of 1..5,320,771;
TSV and parquet equal as typed rows; the TSV gzip header bytes 4..7 zero (mtime 0).
(c) Make each check fail on a copy: a changed value in a copy of `tests/expectations/mm39/universe_summary.tsv`
fails check 22; a changed `provisional` cell in a copy of `universe_members.tsv.gz` fails check 22; a
dropped row in a copy of `rmsk_instance_members.tsv.gz` fails check 21; a swapped column value in a copy of
`rmsk_records.tsv.gz` fails check 20; a changed expected value in `tests/fixtures/records/expected_records.tsv`
fails check 23 (all on scratch copies; tracked files unchanged, verify by md5 before and after).
(d) Silent assumptions to probe: the C-locale sort claim (pandas sorts by code point; are all chrom and name
strings ASCII?); float serialization (`to_csv` repr) round-tripping through the TSV reader; `rmsk_class` and
`rmsk_family` taken from the UCSC columns after an equality gate against the parsed `.out` labels; the
build's dependence on `tests/expectations/<genome>/class_census.tsv`; the universe definitions authored as a
Python dict; `interspersed_plus_satellites` spelled as an `or` of two `class_in` lists.
(e) Wording: read every sentence and comment in the new `src/lib/*.py`, `src/1*.sh`, `tests/lib/records.py`,
the four checks, the `docs/OUTPUTS.md` diff and the README diff for contrastive negation, history or
provenance chatter; judge `README.md` line 38 against line 106.
(f) Confirm no git write happened: `git -C /workspaces/Meta-Aging/01_modules/te-tracks reflog -3` shows
`8fe7bb5` (phase 1 commit) as the latest entry and the phase 2 changes uncommitted.

Report as:
# Phase 2 re-review (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Numbers recomputed
<table: quantity | contract | observed | command>
## Agreement with codex review
<one line per codex finding: agree / disagree with evidence>
Under 150 lines. FAIL when a contract deliverable is missing or wrong, an acceptance number differs, or a
check cannot fail.
