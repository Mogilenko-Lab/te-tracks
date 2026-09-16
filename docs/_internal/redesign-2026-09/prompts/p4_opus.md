Re-review phase 4 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p4_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.

Phase-4 specifics:
(a) Run the export stage into your own directory `/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p4/build/`
whose `tables/` and `universes.json` are symlinks to the orchestrator's build under
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/` (read-only; `/tmp` is noexec). Compare
every export digest and the two registration tables with the orchestrator's. Remove your directory when done.
(b) Re-derive with your own code from `rmsk_records.parquet`, `universe_members.tsv.gz` and `taxonomy_canonical.tsv`,
importing nothing from `src/` or `tests/`: row counts of all seven exports; BED offsets; the GTF attribute values on
a 10,000-row sample of each GTF (record alias, instance alias, canonical and raw labels); the SAF GeneIDs; the
distinct-feature counts in `exports.tsv`; that every emitted id resolves through `export_feature_members` and that
level `record` carries both id spellings for every record.
(c) Conservation: build your own synthetic count table over three records with count 7 and roll it up through the
registration at record, subfamily and family level; confirm 7 at each.
(d) Alphabet: scan every emitted id in every export for characters outside the component alphabet plus `|` and `:`,
and for the forbidden set; report counts.
(e) Make each check fail on a scratch copy: an offset error in `record.bed`, a swapped attribute order in
`record.gtf`, a dropped registration row, a stale sha256 in `exports.tsv`, an id with a forbidden character in a
fixture (tracked files verified by md5 before and after).
(f) Silent assumptions: sort stability with C-locale contigs; the `min(sw_score, 1000)` score; how unresolved tokens
would appear if a tie existed (mm39 has none; read the code path); memory and time of the writer.
(g) Confirm no git write happened: `git -C /workspaces/Meta-Aging/01_modules/te-tracks reflog -3` shows the phase 3
commit as the latest entry and the phase 4 changes uncommitted.

Report as:
# Phase 4 re-review (Opus)
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
