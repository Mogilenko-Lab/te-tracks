# te-tracks phase 5 review (codex, read-only)

You are an independent reviewer of phase 5 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p5_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/15_phase5_consumer_fixtures.md`
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
  bite phase 6.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 5 review (codex gpt-6-astra)
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
- The plan file and `reviews/m2_rulings.md` ("Phase 5") bind: TElocal's `.locInd` built by its own indexer and
  loaded through its pickle reader; TEsingle's tuple at record grain from `record.gtf` and at subfamily grain
  from `subfamily.gtf`; the fixture roster of 11 records, 8 names, 10 instances stated in `prompts/p5_impl.md`.
- Rebuild the synthetic fixture set through `tests/lib/consumers.py` into your own refroot under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/review-p5/` and run `tests/run.sh consumers --refroot <yours>`;
  compare every fixture file's sha256 with the orchestrator's under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/fixtures/consumers/` (read-only). Remove yours when done.
- Support honesty: for each check, state which status it reports here and why; confirm an absent executable, a
  missing checkout dependency and the Stellarscope boundary defect each yield exit 3 with the stated reason, and
  that any other failure yields exit 1. Confirm `tests/run.sh consumers` exits 0 here.
- Count molecules in each fixture BAM with pysam yourself and compare to the builder's intent and to what the
  checks assert; confirm every BAM is sorted and indexed.
- Confirm no write reached any checkout under `/workspaces/Meta-Aging/01_modules/.ref/` (`git status --short` in
  each) and no bytecode was written there.
- Fixture adequacy: on scratch copies, break one thing per check (a molecule count, a boundary read, the
  Stellarscope defect message, the TElocal pickle, the TEsingle tuple) and name the check that fails.
- Wording: every sentence and comment in `tests/lib/consumers.py`, the consumers checks, the OUTPUTS.md
  "Consumer contracts" section and the README diff.

## Implementer report
__REPORT__
