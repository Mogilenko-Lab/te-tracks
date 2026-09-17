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
   findings are recorded and scheduled. When a phase's reviews carry design findings, the rulings land in
   `reviews/p<N>_rulings.md` and the phase file is rewritten to the corrected contract before the fix launches.
7. **Commit.** Orchestrator commits in te-tracks with an affirmative message. Umbrella pin bumps at
   milestones only.

**Milestone reviews** (after phases 2, 5, 7, 9): fan out two or three independent read-only
reviewers with disjoint questions, for example codex on schema and identity, Opus on numbers and
fixtures, and a `divergent` agent on what the design still assumes. Each writes one file. Rulings on
milestone findings land in `reviews/m<N>_rulings.md` and in the plan files of the phases they touch.
Phase 3 adds a `divergent` pass on the rule (ruling M7).

**Validation challenges** that deserve their own reviewer when reached: the Stellarscope boundary
gate; the IRescue 4/2 versus 3/3 allocation fixture; the registration conservation query; the
same-day and concurrent publication tests on the host filesystem.

**Context budget.** One phase per implementer session, roughly a third of the context. The
orchestrator reads reviews and diffs, never whole artifacts.

## Standing authorizations and environment facts (owner, 2026-09-16)

- **Fan-out is pre-authorized.** Codex units (`launch.sh`) and harness agents (`Agent` tool: `opus-reviewer`,
  `divergent`, `general-purpose`) launch without asking the owner for permission, one implementer at a
  time on the repository, reviewers in parallel with each other. The owner asked to stop being prompted
  per agent; asking again is a protocol violation. Only destructive actions (deleting published builds,
  pushes, force operations) still need the owner's word.
- **Commits are part of the protocol.** The owner's "proceed with orchestration as agreed" authorizes the
  per-phase commits on branch `redesign-2026-09` in te-tracks. No push. Umbrella pin bumps at milestones.
- **Prompts are records.** Every implementer, fix, review and re-review prompt is kept under
  `docs/_internal/redesign-2026-09/prompts/` (`p<N>_impl.md`, `p<N>_fix.md`, `review_template.md`,
  `opus_template.md`); reviews land in `docs/_internal/redesign-2026-09/reviews/p<N>_{codex,opus}.md`.
  Anything given to a running unit is appended to its prompt file under an `Amendments at run time`
  heading before the review launches (milestone 2 ruling L3).
- **Exit 32 from `launch.sh`** is the blind-run detector reacting to skill prose in the stream; read
  `codex_exit` from `status.sh --unit <unit>` and the final message; codex_exit 0 plus disk truth decide.
- **`/tmp` is mounted noexec**; scratch that must execute lives under `/workspaces/Meta-Aging/_scratch/`.
  `TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`,
  `TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` (all four mm39 sources
  cached with matching checksums; the GENCODE vM37 GTF is in the read-only refcache at
  `/data2/users/shared/refcache/mm39/mm39_20260911/`).
- **Absent in-container:** irescue, featureCounts, stellarscope, TEsingle, TEcount, TElocal, duckdb, bgzip,
  shellcheck. Present: python3 (pyarrow 25, pandas 2.2, numpy, pysam 0.24, pytest), bedtools, samtools, jq.
- **te-tracks git identity** is set repo-locally (Anton Zhelonkin, anton.bioinf.md@gmail.com), matching
  the umbrella and the earlier te-tracks commits.
- **Phase 8 opens with a design consult.** Before any phase 8 implementation prompt, the orchestrator runs a
  codex consult on the gene child family's topology, architecture and approach (one child per gene annotation
  pin or many views in one child; exon mask, piece registration and transcript-context relation; what the
  consuming projects' combined-mode counting needs), records it under `redesign-2026-09/consults/`, and the
  owner rules on it; plan 18 is rewritten to the ruled design before `p8_impl.md` is finalized (owner,
  2026-09-16). The consult is followed by an ADR discussion between the orchestrator and the owner on the
  transcript-context relation and `gene_context`, held once the orchestrator has gathered the material;
  candidate ADRs are drafted for that discussion and land in `docs/DECISIONS.md` only by the owner's ruling.
