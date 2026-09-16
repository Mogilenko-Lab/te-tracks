Re-review phase 3 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p3_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.

Phase-3 specifics:
(a) Run the taxonomy stage into your own directory `/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p3/build`
whose `tables/` holds symlinks to the orchestrator's `rmsk_taxonomy.tsv` and `rmsk_records.parquet` under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/` (read-only; `/tmp` is noexec, so
scratch lives under `/workspaces/Meta-Aging/_scratch/`). Compare both output digests with the orchestrator's build.
Remove your directory when done.
(b) Re-derive the canonical table with your own implementation of the four rule sentences in the phase file, from
`rmsk_taxonomy.tsv` alone, importing nothing from `src/` or `tests/`: compare `canonical_class`, `canonical_family`,
`class_status`, `family_status`, `class_majority_share`, `family_majority_share`, `label_count`, `record_count`,
`record_length_sum_bp`, `has_uncertain_source`, `has_multiple_labels` on all 18,484 rows; report every mismatch with
the name and both values. Recompute `median_divergence_pct` from the parquet for all names and compare.
(c) Status census 7 / 5 / 5 / 3 over the 20 multi-label names; 0 unresolved at either rank; min majority share
0.734; the three parent/child competitions `MER53`, `UCON44`, `X4b_DNA` resolve to the specific token.
(d) The Dfam snapshot: every row of `tests/fixtures/taxonomy/dfam_snapshot.tsv` equals the corresponding row of
`docs/_internal/redesign-2026-09/taxonomy/dfam_lookup_20names.tsv` plus the `fetched_on` column; the provenance
JSON states the endpoint pattern, the date and that the build never reads it; check 31 fails on a removed name and
on an altered subtype (scratch copies; verify tracked files by md5 before and after).
(e) Rule fixtures: read `tests/fixtures/taxonomy/rule_cases.tsv`; for each case compute the expected result by hand
from the rule text and compare with the authored expectation; state any case where the authored expectation
encodes the implementation rather than the rule. Confirm the tie case publishes `unresolved` with empty canonical
fields, and that the rollup label rule (`unresolved/<rmsk_name>`, one bucket per name; milestone 2 ruling M2 in
`reviews/m2_rulings.md`) is stated in `docs/OUTPUTS.md`.
(f) Silent assumptions: count weighting by records rather than by length; `?` stripped before voting; class-only
tokens abstaining from the family vote; precedence per rank; sort order and float formatting of the shares;
determinism of the median over the parquet row order.
(g) Confirm no git write happened: `git -C /workspaces/Meta-Aging/01_modules/te-tracks reflog -3` shows the
milestone 2 commit as the latest entry and the phase 3 changes uncommitted.

Report as:
# Phase 3 re-review (Opus)
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
