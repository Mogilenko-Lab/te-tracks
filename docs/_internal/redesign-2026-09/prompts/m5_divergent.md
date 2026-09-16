Milestone review after phase 5 of the te-tracks redesign: what the consumer seam still assumes. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, commit 9ac66fb). You are a
read-only reviewer working from the documented artifacts and the tables; write exactly one file,
docs/_internal/redesign-2026-09/reviews/m5_divergent.md, and change nothing else. No git writes.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md, 14_ to 19_ (the remaining phases).
2. docs/_internal/redesign-2026-09/reviews/{m2_rulings,m2_divergent,p3_rulings,p3_divergent}.md and any
   p4_rulings.md / p5_rulings.md: your predecessors' findings and how they were ruled.
3. docs/_internal/redesign-2026-09/consults/{owner_context_2026-09-15,A_consumer_contracts,ADR5_consult}.md.
4. The public contract: README.md, docs/DECISIONS.md, docs/OUTPUTS.md (exports, consumer contracts).
5. The consumer's need: /workspaces/Meta-Aging/14761-DM/AGENTS.md and the D2/D3 plan under
   /workspaces/Meta-Aging/14761-DM/docs/_internal/_project/.
6. The code and fixtures: src/lib/build_exports.py, tests/lib/consumers.py, tests/checks/consumers/*,
   tests/fixtures/consumers/**; the tables and exports under
   /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/ (read-only).

Your question is the one the other two reviewers do not ask: what does the consumer seam take for granted that
the record does not defend? Attack, with a specific failure each:
- the fixtures: synthetic BAM layouts (3' ARC, 5' PE OCM, bulk) against the real libraries 14761 and 14616 carry;
  molecule definitions (CB+UB) against the pipelines' own deduplication; the boundary gate; EM allocation
  expectations; a fixture that passes because the executable is absent;
- the exports: one universe (`interspersed`) for every consumer; the record alias as `transcript_id`; the
  subfamily GTF as TEsingle's subfamily input; `family.bed` with 49 buckets; `min(sw_score, 1000)`; the
  `unresolved_*` tokens no tool has ever seen; 2.6 GB per namespace on disk;
- the registration: namespace-invariant keying; both id spellings at level `record`; the conservation rule proven
  on pandas while the ledger is DuckDB;
- support honesty: `unsupported` as a passing state in `tests/run.sh consumers`; parser-level tests as evidence for
  tools whose executables never ran here; vendored checkout versions against what the owner will install;
- the remaining phases: namespace renames without re-registration (6); `CATALOG_ID` and `BUILD_ID` against the
  ledger keys (7); the child family's split pieces and the deferred `gene_context` (8); the compat reconciliation
  against the legacy SAF and the host-versus-container comparison (9);
- process: five phases of rulings files; prompts as records; reviewers reading the orchestrator's build.

For each assumption: state it in one sentence, give the concrete failure it predicts (inputs and the wrong output
or the silent gap), rate the cost of being wrong (low, medium, high), and say which phase should address it or
whether it is a recorded deferral already. If an assumption is defended somewhere in the record, cite the file
and line and move on.

Format:
# Milestone 5 review: unstated assumptions (divergent)
## High
- [H1] assumption — failure — evidence — phase
## Medium
- [M1] ...
## Low
- [L1] ...
## Defended already
- one line each, with citation
Under 150 lines. Specific over general; measure from the tables and exports where a measurement settles the point.
