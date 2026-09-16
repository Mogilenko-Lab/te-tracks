Re-review phase __N__ of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/__PHASEFILE__ (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p__N___codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.

__EXTRA__

Report as:
# Phase __N__ re-review (Opus)
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
