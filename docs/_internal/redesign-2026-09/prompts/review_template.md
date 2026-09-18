# te-tracks phase __N__ review (codex, read-only)

You are an independent reviewer of phase __N__ of the te-tracks redesign. Working directory:
`/workspaces/Meta-Aging/01_modules/te-tracks` (git branch `redesign-2026-09`). The implementer has finished;
you judge the result against the contract. You write exactly one file:
`docs/_internal/redesign-2026-09/reviews/p__N___codex.md`. You change nothing else. No git writes, no
installs, no network.

## Read
1. The phase contract: `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/__PHASEFILE__`
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
  from the code, or run it against a real copy under the scratch directory the specifics name).
- **Silent assumptions**: anything the code or docs assume that the contract leaves open; anything that will
  bite phase __N+1__.
- **Wording rule**: contrastive negation, history, or provenance chatter in public files or comments.
- **Scope**: files touched outside the phase's allowed set.

## Mutation safety (applies to every review in this series)

When a finding needs a mutation, copy the target and mutate the copy, and make the copy a real one. A
hardlinked copy shares its inode, so writing to it writes through to the artifact under review and a
concurrent reader sees a corrupted payload. Never use `cp -al`, `cp -l`, or `shutil.copytree` with a linking
copy function on a build, an archive or a fixture. As your last step, verify that nothing you did persisted:
run the build verifier on the build directory and on every archive under the published root, and
`release.py verify-current` for both families, and report those exits.

## Output format (the review file)
```
# Phase __N__ review (codex gpt-6-astra)
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

## Implementer report
__REPORT__
