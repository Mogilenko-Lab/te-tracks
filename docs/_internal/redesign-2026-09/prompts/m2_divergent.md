Milestone review after phase 2 of the te-tracks redesign: what the design still assumes. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, commit c28caea). You are a
read-only reviewer working from the documented artifacts; write exactly one file,
docs/_internal/redesign-2026-09/reviews/m2_divergent.md, and change nothing else. No git writes.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/00_INDEX.md, 01_decisions.md,
   02_orchestration.md, then 10_ to 19_ (the phase files).
2. docs/_internal/redesign-2026-09/audit/AUDIT.md and the consults under docs/_internal/redesign-2026-09/consults/.
3. The public contract: README.md, AGENTS.md, docs/DECISIONS.md, docs/OUTPUTS.md, docs/RELEASES.md.
4. The reviews so far: docs/_internal/redesign-2026-09/reviews/*.md.
5. The consuming project's need, as stated in /workspaces/Meta-Aging/14761-DM/AGENTS.md and the D2/D3 plan
   under /workspaces/Meta-Aging/14761-DM/docs/_internal/_project/ (read what exists; the te-tracks
   redesign is the gate for those agents).

Your question is the one the other two reviewers (schema/identity; numbers/fixtures) do not ask: what does
this design take for granted that the record does not defend? Attack, with a specific failure each:
- the source: one RepeatMasker run per assembly, UCSC as the single pin, checksum stability of UCSC URLs,
  the `.out` ID as a source-wide instance key, class labels stable across RepeatMasker library versions;
- the taxonomy rule (phase 3): a deterministic majority over raw labels replaces curation; the Dfam snapshot
  as test evidence only; the `unresolved` bucket;
- the universes: predicates over raw class only; `interspersed` as the default carrying Unknown/Unspecified/DNA?
  as provisional; the compat universe as the bridge to the legacy quantifications;
- the exports (phases 4 to 6): one GTF at record level with consumers grouping by attribute; the safe-name
  alphabet; three contig namespaces from one alias table; the preflight as the only guard;
- publication (phase 7): identity hashing of the file inventory; the single `current` symlink; host-only
  builds with a read-only container;
- the gene child (phase 8) and the deferred transcript-context design: what the seam leaves undecided that a
  consumer will need before D2/D3 can run;
- process: nine phases with codex implementers and two reviewers per phase; what fails silently in that
  loop (prompt drift, numbers copied from prompts into expectations, reviewers sharing the orchestrator's
  measurements);
- scale and time: hg38 later, RepeatMasker updates, a second species, a colleague on the CRI cluster with a
  different Python.

For each assumption: state it in one sentence, give the concrete failure it predicts (inputs and the wrong
output or the silent gap), rate the cost of being wrong (low, medium, high), and say which phase should
address it or whether it is a recorded deferral already. If an assumption is defended somewhere in the
record, cite the file and line and move on.

Format:
# Milestone 2 review: unstated assumptions (divergent)
## High
- [H1] assumption — failure — evidence — phase
## Medium
- [M1] ...
## Low
- [L1] ...
## Defended already
- one line each, with citation
Under 150 lines. Specific over general.
