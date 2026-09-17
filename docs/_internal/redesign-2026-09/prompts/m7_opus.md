Milestone review after phase 7 of the te-tracks redesign: numbers and checks. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09, commit 9d16506). You are read-only:
no edits, no git writes anywhere (the eleven consumer checkouts under /workspaces/Meta-Aging/01_modules/.ref/ are
git repositories too: DfamTEBrowser, irescue, mascarade, MATES, mLLMCelltype, scTE, scTEfinder, stellarscope,
TElocal, TEsingle, TEtranscripts; the directory also holds 14839-DM-cGAS and sene/, the owner's copies, which you leave alone), no installs, no
network. Export PYTHONDONTWRITEBYTECODE=1 for every Python process. Scratch work goes under
/workspaces/Meta-Aging/_scratch/te-tracks-audit/m7-opus/ (the /tmp filesystem is noexec) and is removed when you
finish. The orchestrator's build at /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build and the
published root /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot are read-only for you
(BUILD_ID 0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a, CATALOG_ID 0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4).

Your question: does every number phases 6 and 7 publish or assert follow from the build by an independent route,
does every check fail when its subject is wrong, and did every ruling in p6_rulings.md and p7_rulings.md land as
observable behaviour? Two other reviewers cover the publication seam (codex) and unstated assumptions
(divergent); leave those to them.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/{16_phase6_ensembl_preflight,17_phase7_publication}.md
2. docs/_internal/redesign-2026-09/reviews/{m5_rulings,p6_rulings,p7_rulings}.md
3. README.md (truth table), docs/OUTPUTS.md, docs/RELEASES.md, docs/DECISIONS.md
4. build.sh, src/90_manifest.py, src/99_verify.py, src/release.py, src/lib/manifest.py, src/lib/contigs.py,
   bin/te-tracks-preflight, tests/run.sh, tests/checks/core/{6,7}*, tests/fixtures/publication/**,
   tests/fixtures/contigs/**
5. docs/_internal/redesign-2026-09/reviews/p{6,7}_*.md

Do, with your own code (write it from the contracts; import nothing from src/ or tests/):
(a) Recompute both ids from MANIFEST.json in the build directory and in pubroot/te_mm39/current with your own
    canonical encoder; recompute all 43 inventory digests and byte counts with sha256sum and stat; confirm the
    identity sections equal and list the provenance keys that differ.
(b) Every number in README.md, docs/OUTPUTS.md, docs/RELEASES.md, docs/DECISIONS.md and plan files 16 and 17:
    confirm against disk (sums of regular file sizes per namespace and for the 43-file payload, du -sb of the build
    directory, provenance.peak_rss_bytes, contig counts, record and registration counts, export contract counts) or
    mark unverifiable, and say which.
(c) Rulings audit: for each accepted ruling in p7_rulings.md (codex B1, B2, A1 to A6; Opus B1, A1 to A8) and in
    p6_rulings.md, state the file and line where it landed and the command whose output shows the behaviour.
(d) Mutation tests on scratch copies (tracked files unchanged; verify by md5 before and after): one mutation per
    check for 60, 61, 62, 70, 71 and 72, each of which must fail; run tests/run.sh core --refroot <yours> with the
    real build symlinked or copied as the checks require and state every line; run tests/run.sh consumers --refroot
    <yours> and state every supported and unsupported line with its reason.
(e) Publication cases with your own driver over tests/fixtures/publication/build_fixture.py used as a black box:
    converge, changed payload, added export under an extended roster, corrupt staging, dangling and removed current,
    forged BUILD_ID, concurrent installs and selects, modes 0444/0555/2775, and the CATALOG_ID stability under a
    chromAlias byte change.
(f) Confirm no git write happened: git reflog -3 shows 9d16506 as the latest entry and a clean tree; each checkout
    under .ref shows a clean status and no __pycache__.

Report as:
# Milestone 7 re-review: numbers and checks (Opus)
Verdict: PASS | PASS WITH ADVISORIES | FAIL
## Blocking
- [B1] path:line — finding — evidence — fix
## Advisory
- [A1] ...
## Numbers recomputed
<table: quantity | published | observed | route>
## Rulings audit
<table: ruling | landed at | command | observed>
## Check coverage
<table: failure mode | check | mutation result>
Under 200 lines. FAIL when a published number differs from your derivation, a check passes on a mutated subject,
or a ruling did not land.
