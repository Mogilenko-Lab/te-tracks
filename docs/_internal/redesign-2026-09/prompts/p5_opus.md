Re-review phase 5 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/15_phase5_consumer_fixtures.md (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p5_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.

Phase-5 specifics:
(a) Rebuild the synthetic fixtures through `tests/lib/consumers.py` into your own refroot under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p5/` (the `/tmp` filesystem is noexec); compare every fixture
file digest with the orchestrator's under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/fixtures/consumers/`
(read-only). Remove yours when done.
(b) With your own pysam code: molecules per BAM by CB+UB, duplicates, multimappers (`NH:2`), gap-only reads and the
four boundary reads' 0-based half-open coordinates against `Edge` (GTF 101..110); compare to the builder's intent
and to the checks' assertions.
(c) With your own parsers written from the vendored sources under `/workspaces/Meta-Aging/01_modules/.ref/`
(read them; import nothing from `src/` or `tests/`): IRescue's BED name handling, Stellarscope's `locus` and
`instance_id` grouping and the boundary rule, TEsingle's four-attribute tuple from both GTFs, TEtranscripts' grain,
TElocal's index build and pickle load; compare feature counts with the roster (11 records, 8 names, 10 instances).
(d) Make each consumers check fail on a scratch copy; make each report `unsupported` with its stated reason where
the plan says so; verify tracked files by md5 before and after; verify every checkout under `.ref` is clean.
(e) Silent assumptions: fixture layouts against the real 14761 ARC and 14616 OCM libraries; the UR cutoff read
from source rather than executed; the MATES adapter as optional; what "supported" means for a tool whose
executable never ran here.
(f) Confirm no git write happened: `git -C /workspaces/Meta-Aging/01_modules/te-tracks reflog -3` shows the phase 4
commit as the latest entry and the phase 5 changes uncommitted.

Report as:
# Phase 5 re-review (Opus)
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
