Re-review phase 7 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09, HEAD 99bf646). You are read-only: no edits, no git writes anywhere (the nine checkouts
under /workspaces/Meta-Aging/01_modules/.ref/ named DfamTEBrowser, irescue, mascarade, MATES, mLLMCelltype,
stellarscope, TElocal, TEsingle and TEtranscripts are git repositories too), no installs, no network. Scratch work
goes under /workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p7/ (the /tmp filesystem is noexec) and is removed
when you finish; set PYTHONDONTWRITEBYTECODE=1 for every python invocation. The orchestrator's build at
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build and the implementer's published root at
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/te_mm39/ are read-only for you.
Environment for any command: TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot,
TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/17_phase7_publication.md (the contract) and
   docs/_internal/redesign-2026-09/prompts/p7_impl.md (the exact interfaces and numeric targets)
2. docs/_internal/redesign-2026-09/reviews/m2_rulings.md ("Phase 7") and reviews/m5_rulings.md (codex A2, A3;
   divergent M1); docs/_internal/redesign-2026-09/consults/ADR67_consult.md
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments"
4. The implementer's changes: `git status --short` and `git diff HEAD` (plus untracked files' contents). Three
   modified files under docs/_internal/ (session.md, 02_orchestration.md, prompts/p7_impl.md) are orchestrator edits
   and out of scope.
5. Last, after your own work: the codex review at docs/_internal/redesign-2026-09/reviews/p7_codex.md if it exists
   by then (it is being written in parallel); if absent, say so and skip the agreement table.

Your job is adversarial and independent: recompute every number with your own read-only code written from the
contracts (import nothing from src/ or tests/), try to make each check fail, look for what the implementer assumed
silently, and judge the public prose against the wording rules.

Phase-7 specifics:
(a) Recompute BUILD_ID and CATALOG_ID from MANIFEST.json with your own canonical encoder for the build directory and
    for pubroot/te_mm39/current; compare with the BUILD_ID and CATALOG_ID files; confirm the two identity sections
    are equal and name the provenance keys that differ. Recompute the 43 inventory entries (path, bytes, sha256) with
    sha256sum and confirm no file on disk outside the three identity files is missing from the inventory.
(b) Confirm that changing any provenance value leaves both ids, that changing a universe predicate changes BUILD_ID
    and keeps CATALOG_ID, that changing a source digest or a canonical table digest changes both, and that adding an
    export path changes BUILD_ID alone, with your own code on copies of the manifest.
(c) Modes and selector in the published root: every payload file 0444, every payload directory 0555, archive/ 2775,
    current a relative symlink `archive/<id>`; .staging empty; one archive.
(d) Exercise src/release.py yourself on a scratch family root with tiny builds you construct (you may call
    tests/fixtures/publication/build_fixture.py's make_build as a black box, or write your own complete tiny build
    and run src/90_manifest.py on it): identical rebuild converges; changed payload yields a second archive and
    current moves; corrupted staging aborts and leaves current; a dangling current (archive directory removed)
    blocks select and install --select with a discrepancy; a forged BUILD_ID file; an empty or symlinked archive
    target; two concurrent identical installs; two concurrent selects of different valid builds; --no-select.
    State any listed contract case that release.py or check 72 leaves uncovered.
(e) Make checks 70, 71 and 72 fail on scratch copies (one mutation each) and confirm the real build and tracked
    files are unchanged by md5 before and after. Measure the wall time of check 71 alone and state whether
    `cp -a --reflink=auto` copies 10.5 GB on this filesystem.
(f) export_contracts: compare the consumer keys, attribute sources and selectable levels with the keys the consumer
    checks construct in tests/lib/consumers.py and tests/checks/consumers/; name misstatements.
(g) Retention numbers: measure the per-namespace export file sums and the 43-file payload sum; compare with
    docs/RELEASES.md (3,021,713,838 / 2,926,268,559 / 3,021,138,299; 10,461,962,113) and the implementer's observed
    figures (3,021,714,346 / 2,926,266,953 / 3,021,140,740); state which a public document should carry.
(h) Verifier purity: 99_verify.py on the build directory leaves every mtime and size unchanged; it exits 1 naming the
    path on a flipped byte and on an extra file (use a copy of the small files only if a full copy is too costly, and
    say what you did).
(i) Every number and claim in docs/RELEASES.md, docs/OUTPUTS.md, README.md and docs/DECISIONS.md touched by this
    phase: confirm against disk or mark unverifiable. Judge the prose and the code comments against the wording
    rules.
(j) Confirm no git write happened: `git reflog -3` shows 99bf646 as the latest entry, the phase 7 changes
    uncommitted, the nine checkouts clean and free of __pycache__.

Report as:
# Phase 7 re-review (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Numbers recomputed
<table: quantity | contract | observed | route>
## Agreement with codex review
<one line per codex finding: agree / disagree with evidence; or "codex review absent at HH:MM">
Under 150 lines. FAIL when a contract deliverable is missing or wrong, an acceptance number differs, or a check
cannot fail. Deliver the full report as your final message; the orchestrator saves it verbatim to
docs/_internal/redesign-2026-09/reviews/p7_opus.md.
