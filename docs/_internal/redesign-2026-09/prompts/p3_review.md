# te-tracks phase 3 review (codex, read-only)

You are an independent reviewer of phase 3 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p3_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md`
2. The decisions: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md`
3. The wording and comment rules: `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments"
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD --stat` and the full
   diff, plus untracked files from `git status --short`.
5. The implementer's own report, pasted below under "Implementer report".

## Judge, with evidence
- **Contract conformance**: every deliverable in the phase file present at the stated path with the stated
  content; every acceptance command re-run by you with its output quoted; any number that differs from the
  contract named.
- **Fixture adequacy**: do the fixtures and checks fail when they should? Try to break one (read-only: reason
  from the code, or run it against a modified copy under /tmp).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase 4.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 3 review (codex gpt-6-astra)
Verdict: PASS | PASS WITH ADVISORIES | BLOCKING
## Blocking
- [B1] <file:line> <finding> — <evidence> — <what fixes it>
## Advisory
- [A1] ...
## Acceptance re-run
<commands and outputs, verbatim>
## Scope check
<git status / diff --stat summary>
```
BLOCKING means a contract deliverable is missing or wrong, an acceptance number differs, or a check cannot fail.
Keep the file under 200 lines. Facts over opinions; every finding cites a path and, where possible, a line.

## Orchestrator notes (check these in addition)
- Run the taxonomy stage yourself into your own directory: create
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p3/build/tables/` holding symlinks to the orchestrator's
  `tables/rmsk_taxonomy.tsv` and `tables/rmsk_records.parquet` under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/` (read them, leave them untouched), run
  `bash src/20_build_taxonomy.sh <your build dir> config/mm39.env`, and compare the sha256 of
  `taxonomy_canonical.tsv` and `taxonomy_resolution_report.tsv` with the orchestrator's. Remove your directory when done.
- The implementer's prompt is `docs/_internal/redesign-2026-09/prompts/p3_impl.md`; the milestone 2 rulings that
  bind this phase are in `docs/_internal/redesign-2026-09/reviews/m2_rulings.md` under "Phase 3" (unresolved
  spelling `unresolved/<rmsk_name>`, one bucket per name; rule stays `taxonomy_rule_v1`; `MER53` shape fixture).
- The rule must be one pure function `resolve(labels) -> dict` with `TAXONOMY_RULE_VERSION = "taxonomy_rule_v1"`;
  judge whether any second copy of the rule lives in a check or a doc, and whether the precedence "majority over
  unspecified over uncertainty suffix over concordant" is applied per rank as the phase file states.
- Recompute from `tables/rmsk_taxonomy.tsv` with your own code: 18,484 names; 20 with more than one label; the
  status census 7 `resolved_majority`, 5 `resolved_unspecified`, 5 `resolved_uncertainty_suffix`, 3 `unspecified`;
  every multi-label name `canonical_class = DNA`; min `family_majority_share` 0.734 (`MER63C`); `Eulor5B`
  class `resolved_uncertainty_suffix` and family `resolved_unspecified`; `MER124` canonical `DNA/DNA`.
- `median_divergence_pct` per name over `divergence_pct` of `rmsk_records.parquet`: recompute for five names of
  your choice, including one multi-label name, and compare with the table.
- Fixture adequacy: on a scratch copy break the tie handling, the `?` stripping, the class-only abstention and the
  Dfam join one at a time; name the check that fails each time and quote its message. Confirm check 31 fails when
  one snapshot name is removed (set equality) and when one `dfam_repeat_subtype` is altered.
- The build reads no Dfam data and no network: confirm by reading `src/lib/build_taxonomy.py` imports and file opens.
- Wording: every sentence and comment in `src/lib/build_taxonomy.py`, `src/20_build_taxonomy.sh`, the three checks,
  the `docs/OUTPUTS.md` diff and the README diff.

## Implementer report
__REPORT__
