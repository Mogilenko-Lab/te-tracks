Re-review phase 8 of the te-tracks redesign. Repository: /workspaces/Meta-Aging/01_modules/te-tracks
(git branch redesign-2026-09, HEAD cf1b150). You are read-only: no edits, no git writes anywhere (the checkouts under
/workspaces/Meta-Aging/01_modules/.ref/ are git repositories too; 14839-DM-cGAS and sene there are plain directories
you leave alone), no installs, no network. Scratch work goes under
/workspaces/Meta-Aging/_scratch/te-tracks-audit/opus-p8/ (the /tmp filesystem is noexec) and is removed when you
finish; set PYTHONDONTWRITEBYTECODE=1 for every python invocation. Read-only for you: the parent core build at
/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build (BUILD_ID 9ddf3622…, CATALOG_ID 90cc18be…), the
implementer's child at /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39_gene/build (BUILD_ID
1804f94e…), and the published root /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/pubroot/ holding
te_mm39/archive/9ddf3622… and te_mm39_gene/archive/1804f94e…. Environment for any command:
TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot,
TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source. bedtools v2.31.1 is at
/usr/local/bin/bedtools. A codex review runs in parallel and may be running tests/run.sh core; that suite writes only
under $TE_TRACKS_REFROOT/pubtest and /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl/.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md (the contract) and
   docs/_internal/redesign-2026-09/prompts/p8_impl.md (the exact interfaces and numeric targets)
2. docs/DECISIONS.md sections 4, 8, 9, 10, 12 and 16; docs/_internal/redesign-2026-09/consults/gene_child_consult.md
   Q1 to Q4, Q7 and Q8; consults/mask_policy_consult.md Q1 and Q6; reviews/m7_rulings.md A1 and A2
3. /workspaces/Meta-Aging/AGENTS.md sections "Prose" and "Comments"
4. The implementer's changes: `git status --short` and `git diff HEAD` (plus untracked files' contents). Every
   uncommitted entry in the tree is phase 8 work.
5. Last, after your own work: the codex review at docs/_internal/redesign-2026-09/reviews/p8_codex.md if it exists
   by then (it is being written in parallel); if absent, say so and skip the agreement table.

Your job is adversarial and independent: recompute every number with your own read-only code written from the
contracts (import nothing from src/ or tests/, except where a point below names a fixture you may call as a black
box), try to make each check fail, look for what the implementer assumed silently, and judge the public prose
against the wording rules.

Phase-8 specifics:
(a) Geometry: with the retained GTF (child source/gencode.vM37.primary_assembly.annotation.gtf.gz) and the parent's
    exports/ucsc/interspersed/full/record.bed, recompute the unstranded exon union and the exon-subtracted blocks
    with bedtools merge and bedtools subtract for one whole chromosome other than chr19 and for one annotated
    scaffold, and compare block count, retained bases and the exact block set (start, end, strand, name) with the
    child's exports/ucsc/interspersed/exon_subtracted/subfamily.saf. The orchestrator measured chr19: 10,373
    exon-union intervals, 4,434,265 bp, 86,429 records, 84,268 blocks, 21,565,706 bp, identical block sets. Include
    one contig without annotation and confirm its records stay whole.
(b) Census: recompute tables/exon_subtraction_summary.tsv for all three universes from
    tables/exon_subtraction_status.tsv joined to the parent's tables/rmsk_records.parquet, deriving `interspersed`
    membership from the parent's record.bed rather than from any predicate code, and compat membership from the
    predicate text in universes.json evaluated by your own code; confirm records_on_unannotated_contigs against
    tables/gene_annotation_coverage.tsv; confirm the three GTF row totals and the exon union of 160,549,642 bp.
(c) Identity: recompute BUILD_ID and CATALOG_ID from the child's MANIFEST.json with your own canonical encoder
    (docs/RELEASES.md states the rule) for the build directory and for pubroot/te_mm39_gene/current; confirm the
    child CATALOG_ID bytes equal the parent's; confirm the 21 inventory entries (path, bytes, sha256) against disk
    and that no file on disk outside the three identity files is missing from the inventory; name the provenance
    keys the child adds (stage_metrics, peak_rss_measurement) and confirm they sit outside both hashes. With your
    own code on copies of the manifest, confirm each of the GTF digest, every policy_bundle value, the roster, a
    parent id and child_universes moves BUILD_ID while CATALOG_ID stays.
(d) Verification depth: read src/lib/gene_child.py verify_products and src/lib/manifest.py verify_child_identity
    and state exactly what binds SAF row content to the registration beyond row count, distinct features, header
    and the exports.tsv digest; state whether registration row order is part of the contract (check 82 accepts a
    reversed registration with an updated inventory). Confirm 99_verify.py writes nothing (mtimes and sizes
    unchanged) on the child build, and that it exits 1 with "child verification requires the parent archive" when
    the parent is unnamed.
(e) Dependency refusals: using tests/fixtures/publication/build_fixture.py make_build and make_child as black boxes
    on a scratch family root, exercise release.py install/select/verify-current of the child with the parent absent,
    corrupt (one flipped byte) and of another family; a repeated child publication converging; an earlier core
    staying selectable after the child lands; modes 0444/0555 and the relative current symlink in the real
    published root; .staging empty. State any contract case of plan item 7 that check 82, check 83 or
    tests/fixtures/gene/publication_cases.py leaves uncovered.
(f) Check independence: tests/checks/core/80_exon_subtraction.py imports the production annotation_mask for its
    residual-overlap sample and coverage comparison; verify_products recomputes with the same subtract_batch that
    wrote the tables. State which mask or subtraction defects they cannot detect and whether the twelve
    hand-authored cases in tests/fixtures/gene/geometry.json (check 81) cover plan item 7's list. Make checks 80,
    81 and 82 fail on scratch copies (one mutation each) and confirm the real builds and tracked files are
    unchanged by md5 before and after.
(g) Dispatch: build.sh refusals (a `current` parent path, a non-hex id, a symlinked parent, a child directory
    overlapping the parent, mixed --parent-dir and --parent-build-id) with exit 2 and a usage message; the core
    invocation unchanged (`./build.sh --genome mm39 --build-dir X --help`); config_values unsetting an ambient
    FAMILY; the child's RSS_FILE under the build directory removed before the manifest; resolve_parent inferring
    the root from a `.staging` or `archive` parent directory name.
(h) Scratch convention: checks 81 and 82 and tests/fixtures/gene/publication_cases.py hardcode
    /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl while checks 71 and 72 use $TE_TRACKS_REFROOT/pubtest;
    judge against the runner's --refroot option.
(i) Every number and claim in docs/OUTPUTS.md (phase 8 section), docs/RELEASES.md ("Gene child snapshots" and the
    transfer sentence), docs/RUNBOOK.md (new; run its commands or state why not) and README.md touched by this
    phase: confirm against disk or mark unverifiable. Judge the prose and the code comments against the wording
    rules.
(j) Confirm no git write happened: `git reflog -3` shows cf1b150 as the latest entry, the phase 8 changes
    uncommitted, every checkout under 01_modules/.ref/ clean and free of __pycache__.

Report as:
# Phase 8 re-review (Opus)
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
docs/_internal/redesign-2026-09/reviews/p8_opus.md.
