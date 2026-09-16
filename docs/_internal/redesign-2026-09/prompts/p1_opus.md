Re-review phase 1 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09). You are read-only: no edits, no git writes, no installs, no network.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/11_phase1_source.md (the contract)
2. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments" (wording rules for public files)
4. The implementer's changes: `git -C /workspaces/Meta-Aging/01_modules/te-tracks status --short` and
   `git -C /workspaces/Meta-Aging/01_modules/te-tracks diff HEAD` (plus untracked files' contents)
5. The codex review already written: docs/_internal/redesign-2026-09/reviews/p1_codex.md

Your job is adversarial and independent of the codex review: recompute every acceptance number in the
contract with your own read-only shell or python (working copies under /tmp only), try to make each check
fail, look for what the implementer assumed silently, and judge the public prose against the wording rules.
Where you agree with a codex finding say so in one line; where you disagree, show the evidence.

Phase-1 specifics:
(a) Build into your own directory, `/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p1/build`, with
`TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source` (the `/tmp` filesystem is
noexec; scratch under `/workspaces/Meta-Aging/_scratch/` executes). Leave
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build` untouched; other processes read it.
Recompute: records 5,320,771; distinct ids 4,696,900, contiguous, none spanning two contigs; starred rows 0;
matched rows 5,320,771 with zero unmatched rows and zero field disagreements; three coordinate-only
collision pairs at chr11:67327100, chr13:58658237, chr16:37859045 (0-based starts); ID2
`chr1:3051045-3051146 -` → consensus start 5, end 104, left 48. Compare your build's
`source/qualification.md` byte-for-byte with `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md`.
Remove your build directory when done.
(b) Make each check fail on a copy: a `qualification.md` with one metric changed must fail
`tests/checks/core/11_source_qualification.sh` (point `TE_TRACKS_REFROOT` at a scratch tree holding the copy);
a changed value in a copy of `tests/fixtures/source/expected.tsv` must fail `10_rmsk_out_parser.py` (run
the check from a scratch copy of the repository tree, so the tracked fixtures stay untouched). Confirm the
`unsupported` path: with `TE_TRACKS_REFROOT` pointing at an empty directory, `tests/run.sh core` reports
check 11 `unsupported` and exits 0.
(c) Field names: compare `FIELDS` in `src/lib/rmsk_out.py` with the phase 2 record schema
(`12_phase2_canonical.md`, `docs/_internal/redesign-2026-09/prompts/p2_impl.md`, `docs/OUTPUTS.md` phase 2
section); name every field phase 2 publishes under a different name. `docs/OUTPUTS.md:28` describes the
legacy `rmsk_id` as the UCSC one-character field; judge the parser's reuse of that name for the `.out` ID.
(d) Silent assumptions to probe: negative consensus coordinates (fixture row `SplitName`), a `.out` row whose
class/family token contains two slashes, a chromosome name with a colon, an ID that is reused on two
contigs, a header variant with leading spaces, gzip versus plain input. Which does the parser define and which
does it merely tolerate?
(e) Wording: read every sentence and comment in `config/mm39.env`, `build.sh`, `src/00_fetch_sources.sh`,
`src/05_qualify_source.sh`, `src/lib/rmsk_out.py`, `tools/qualify_source.py`, the two checks, the README
diff and the retained report for contrastive negation, history or provenance chatter.
(f) Confirm no git write happened: `git -C /workspaces/Meta-Aging/01_modules/te-tracks reflog -3` shows
`9ac83d4` (phase 0 commit) as the latest entry and the phase 1 changes uncommitted.

Report as:
# Phase 1 re-review (Opus)
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
