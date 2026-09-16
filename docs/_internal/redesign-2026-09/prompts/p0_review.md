# te-tracks phase 0 review (codex, read-only)

You are an independent reviewer of phase 0 of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p0_codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/10_phase0_decisions_scaffold.md`
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
  bite phase 1.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Output format (the review file)
```
# Phase 0 review (codex gpt-6-astra)
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


Phase-0 specific questions: (a) does `tests/run.sh` really exit 1 on a failing check and on an unsupported
`.required.*` check, and 0 on plain unsupported? Test it on a throwaway copy under
/workspaces/Meta-Aging/_scratch/ (the /tmp filesystem is noexec, so copies there cannot run). (b) Does the
README truth table name every artifact the phase files promise, and nothing more? (c) Is any sentence in
the public files a promise phase 9 cannot deliver? (d) `docs/DECISIONS.md` lacks a title line; say whether
that matters.

## Implementer report
Phase 0 is complete. All acceptance results match expectations.

- [README.md](/workspaces/Meta-Aging/01_modules/te-tracks/README.md): rewrote purpose, sources, build guidance, artifact truth table and guarantees.
- [AGENTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/AGENTS.md): created package rules and test guidance; 33 lines.
- [CLAUDE.md](/workspaces/Meta-Aging/01_modules/te-tracks/CLAUDE.md): created the exact import line.
- [.gitignore](/workspaces/Meta-Aging/01_modules/te-tracks/.gitignore): preserved existing rules and added recursive tracking exceptions.
- [docs/DECISIONS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/DECISIONS.md): added eight ADRs and recorded deferrals.
- [docs/OUTPUTS.md](/workspaces/Meta-Aging/01_modules/te-tracks/docs/OUTPUTS.md): corrected legacy `rmsk_id` and documented deferred artifacts by phase.
- [tests/run.sh](/workspaces/Meta-Aging/01_modules/te-tracks/tests/run.sh): created executable runner with required exit handling.
- [tests/checks/core/.gitkeep](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/core/.gitkeep): created mode placeholder.
- [tests/checks/consumers/.gitkeep](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/consumers/.gitkeep): created mode placeholder.
- [tests/checks/acceptance/.gitkeep](/workspaces/Meta-Aging/01_modules/te-tracks/tests/checks/acceptance/.gitkeep): created mode placeholder.

Temporary runner checks also passed and were removed.

Acceptance output, verbatim:

```text
syntax ok build.sh
syntax ok lib/common.sh
syntax ok src/00_fetch_sources.sh
syntax ok src/10_build_master.sh
syntax ok src/90_manifest.sh
syntax ok src/99_verify.sh
syntax ok src/release.sh
syntax ok tests/run.sh
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode core
exit=0
checks=0 pass=0 fail=0 unsupported=0
no checks registered for mode consumers
exit=0
usage: tests/run.sh <core|consumers|acceptance> [--refroot DIR]
exit=2
CLAUDE.md ok
 M .gitignore
 M README.md
 M docs/DECISIONS.md
 M docs/OUTPUTS.md
?? AGENTS.md
?? CLAUDE.md
?? tests/checks/
?? tests/run.sh
```

Grep hits: none. Phase-file deviations: none. No git writes, installs or network access.
