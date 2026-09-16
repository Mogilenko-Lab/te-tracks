# Orchestration protocol for the implementation session

The orchestrator holds the whole picture and never implements. Per phase:

1. **Prompt.** Write a file-backed prompt from the phase file: task, exact deliverables with paths,
   working directory `/workspaces/Meta-Aging/01_modules/te-tracks`, forbidden actions (git writes,
   installs, network beyond the pinned URLs, edits outside the phase's scope), acceptance commands
   with expected numbers, and the rule to report a deviation instead of editing an artifact or a
   test to match. Run each acceptance command yourself before delegating it.
2. **Implement.** codex `gpt-6-astra`, `--effort xhigh`, via
   `.claude/skills/delegate-cli/assets/launch.sh --unit te-tracks-p<N>-impl --workdir <te-tracks> --effort xhigh --prompt <file>`
   as a harness background task. Exit 32 is the blind-run detector reacting to skill prose; codex
   exit code plus disk truth decide. One implementer at a time unless two phases are independent in
   both reads and writes.
3. **Verify.** Re-run the acceptance commands, diff the touched files, check `git status` in
   te-tracks and in every reachable repo. Numbers in the report must match numbers on disk.
4. **Review.** codex `gpt-6-astra`, `--effort xhigh`, read-only, one review file under
   `docs/_internal/redesign-2026-09/reviews/p<N>_codex.md`: contract conformance, fixture
   adequacy, silent assumptions, wording rule.
5. **Re-review.** Opus 5 through the Agent tool with `subagent_type: opus-reviewer` (installed at
   `.claude/agents/opus-reviewer.md`, read-only, recomputes numbers), writing its verdict into the
   final message; the orchestrator saves it as `reviews/p<N>_opus.md`.
6. **Fix loop.** BLOCKING findings go back to the implementer with the review attached. ADVISORY
   findings are recorded and scheduled.
7. **Commit.** Orchestrator commits in te-tracks with an affirmative message. Umbrella pin bumps at
   milestones only.

**Milestone reviews** (after phases 2, 5, 7, 9): fan out two or three independent read-only
reviewers with disjoint questions, for example codex on schema and identity, Opus on numbers and
fixtures, and a `divergent` agent on what the design still assumes. Each writes one file.

**Validation challenges** that deserve their own reviewer when reached: the Stellarscope boundary
gate; the IRescue 4/2 versus 3/3 allocation fixture; the registration conservation query; the
same-day and concurrent publication tests on the host filesystem.

**Context budget.** One phase per implementer session, roughly a third of the context. The
orchestrator reads reviews and diffs, never whole artifacts.
