# Phase 8 rulings (the gene child family, first snapshot)

Implementer `te-tracks-p8-impl` (codex `gpt-6-astra`, xhigh, 3,011 s) from `prompts/p8_impl.md` against plan 18 as
rewritten from the ADR rulings; codex exit 0.

## Orchestrator verification before the reviews

- The child at `$TE_TRACKS_REFROOT/te_mm39_gene/build`: `BUILD_ID`
  `1804f94e51df733c9a2da078a0a4ec943763dddd24f01a260f8e029fa201880b`; `CATALOG_ID` bytes equal to the parent's
  (`90cc18be…`); the archive published into the scratch root carries the same `BUILD_ID`, `current` is the relative
  `archive/<id>` link.
- `tables/exon_subtraction_summary.tsv` equals plan 18's acceptance table in every cell for `all_rmsk`, `interspersed`
  and `compat_tetranscripts_mm39`; the twelve SAF files hold 3,684,934 and 3,717,740 data rows with 1,220 and 1,225
  distinct `GeneID`s in every namespace for both groupings; registration groups 3,684,934 × 2 and 3,717,740 × 2
  (7,369,868 and 7,435,480; 14,805,348 rows); coverage 38 annotated contigs of 61 with 2,638 records on the 23
  unannotated ones; GTF totals 78,317 / 278,369 / 1,298,921 rows and a 160,549,642 bp exon union.
- `99_verify.py` with `--parent-dir` exits 0 with the eleven `ok` lines; without a parent it exits 1 with `child
  verification requires the parent archive`; `release.py verify-current` exits 0 for both families.
- Independent geometry: `bedtools merge` and `bedtools subtract` (unstranded, v2.31.1) over the retained GTF and the
  parent's `interspersed` record BED on chr19 give 10,373 exon-union intervals (4,434,265 bp, equal to the coverage
  row), 84,268 blocks and 21,565,706 retained bases from 86,429 records, and the block set (start, end, strand,
  name) is identical to the child's `ucsc/interspersed/exon_subtracted/subfamily.saf` rows on chr19. One SAF checked
  for the declared sort order (contig bytes, numeric bounds, strand, `GeneID`) and for `Start <= End`.
- `tests/run.sh core`: 23 pass, exit 0, 15 min 31 s wall with the two reviews running alongside. The suite leaves an
  empty `_scratch/te-tracks-audit/p8impl/` behind because checks 81 to 83 create that hardcoded path.
- Tree: nine modified and ten untracked entries, the touch list exactly; every checkout under `.ref` clean; the
  implementer's scratch removed; HEAD `cf1b150`, no git writes by the unit.
- Measured by the implementer: scratch child build 406 s wall, whole-build peak 3,571,302,400 bytes resident by
  `RUSAGE_CHILDREN` (stage 50 alone 886,882,304 bytes, 165 s); the `--root` publication 493 s.

## Deviations reported by the implementer

1. `docs/RUNBOOK.md` was named as a pre-read and did not exist; the implementer created it with the gene child
   invocation, the parent-id resolution through `verify-current` and the scratch build commands, and split the README
   truth table row into a phase 8 row (`delivered, tested`) and a deferred phase 9 row for host qualification.
   Accepted: plan item 8 asked for that content, and phase 9b writes the host runbook into the same file.

## Codex review (`p8_codex.md`, verdict BLOCKING)

Codex rebuilt the child into its own scratch (442 s; publication 536 s), reproduced the census with independently
evaluated predicates, recomputed the geometry on chr18 (9,708 exon-union intervals, 116,425 blocks, 34,253,394 bp,
block multiset equal) and on the unannotated `chr1_MU069434v1_random` (4 records whole), moved `BUILD_ID` with ten
independent mutations while `CATALOG_ID` stayed, confirmed modes 0444/0555 and the relative selector, confirmed
verifier purity over 216 paths, and ran the core suite (23 pass). Its findings and my rulings:

- **B1 accepted (blocking).** `verify_products` binds each SAF to the registration by row count, distinct-feature
  count, header and the `exports.tsv` digest alone; a SAF row moved onto masked bases, with the registration intact and
  the digest and inventory rehashed, passes `write_manifest` and `99_verify.py` (codex reproduced it on the tiny
  fixture; the orchestrator confirmed the gap by reading `gene_child.py:385-390` and had named it for both reviewers).
  Ruling: verification compares every SAF's full row content (`GeneID`, `Chr`, `Start`, `End`, `Strand`) with the
  registration rows of its universe and grouping joined to the parent's strand and contig and renamed through the
  alias table for its namespace, as a multiset, and requires each SAF sorted by the declared order; check 82 gains
  the self-consistently rehashed mutation, and check 80 asserts the same equality with its own code.
- **B2 accepted (blocking).** `[ -L "$PARENT_DIR" ]` follows a trailing slash into the directory, and `realpath`
  then hides the symlink before `validate_parent`, so `--parent-dir parent-link/` runs the child stages against a
  symlinked parent (the orchestrator confirmed the shell semantics). Ruling: `build.sh` strips trailing slashes and
  judges the lexical path before resolving it; both spellings exit 2 with usage, and check 82 covers both.
- **A1 accepted.** Checks 81 and 82 and `tests/fixtures/gene/publication_cases.py` write under the hardcoded
  `_scratch/te-tracks-audit/p8impl` while checks 71 and 72 use `$TE_TRACKS_REFROOT/pubtest`, so `--refroot` selects
  where the new checks read and leaves where they write. Ruling: the new checks use `$TE_TRACKS_REFROOT/pubtest` with
  `TemporaryDirectory`, as checks 71 and 72 do.
- **A2 accepted in two parts.** Check 80 recomputes the mask with the production `annotation_mask`, and the verifier
  subtracts with the production `subtract_batch`, so a coherent defect in either passes both; the hand-authored cases
  of check 81 catch the specified geometry (codex broke a copied implementation on the central split). Ruling: check
  81 gains nested exons, overlapping exons of different extents and a record cut into four blocks; phase 9b's
  acceptance suite gains an independent bedtools oracle over two chromosomes and one unannotated contig, reporting
  `unsupported` when `bedtools` is absent (plan 19 amended).
- **A3 recorded for phase 9.** Policy validation and payload admission describe the vM37 snapshot alone, so later
  mask, context and table additions add verifier branches and keep vM37 archives verifiable; the core verifier compares
  source roles against the live `SOURCE_CONFIG` set, so the 9a `dfam_snapshot` role joins `build_sources` as a
  declared role while four-source parent archives stay admitted; the 9a core changes move the core `BUILD_ID` and the
  child's parent pin while `CATALOG_ID` holds; the pair-only binding sentence at `docs/OUTPUTS.md:436` is the
  scheduled 9a amendment with its fixture across the two overlapping universes. Plan 19 carries these constraints.

Codex confirmed the documentation against plan item 8, the RUNBOOK creation, the prose and comment rules, the
dispatch refusals apart from B2, the ambient-`FAMILY` guard, the removal of the stage-metrics file before the 21-file
inventory, the root inference and `root=family.parent` on every release verification, and the dependency cases of
check 83. It noted the two review prompts and the schema consult as untracked entries beyond the implementation touch
list; those are the orchestrator's files.

## Opus re-review (`p8_opus.md`, verdict FAIL)

Opus recomputed every plan 18 number with its own code (census for all three universes from its own GTF pass, merge
and prefix-sum subtraction; all 5,320,771 status rows; the coverage table cell for cell; chr19, chr18, two annotated
scaffolds and `chrUn_GL456359v1` with bedtools, block sets identical), compared all 14,805,348 registration rows with the
twelve SAFs and the eight renamed files (no discrepancy), reproduced both identities with its own encoder in the build and
the published archive, moved `BUILD_ID` with thirteen mutations while `CATALOG_ID` stayed, exercised the dependency and
dispatch refusals in its own scenarios, made checks 80, 81 and 82 fail on hardlinked copies, and ran the core suite on a
`--refroot` copy (23 pass). The codex review landed during its run and its agreement table covers every codex finding.
Rulings:

- **B1 accepted;** identical to codex B1, reproduced with the same accepted `BUILD_ID 6f492ec1…`. Opus adds that the
  delivered archive is correct row for row, so the finding is verification depth. Fix item 1.
- **B2 accepted;** identical to codex B2. Opus confirms the `current` refusal holds lexically in three spellings, so the
  plan's original letter survived; the amended plan makes the lexical rule cover symlinks. Fix items 2 and 3.
- **B3 accepted.** The twelve geometry cases cover plan item 7 as the implementer received it; the nested exon, the
  overlapping exons of different extents and the four-block record are the amendment's cases, and they exercise the
  mask-widening arm and the internal-gap arm of the code that no hand-authored answer touches. Fix item 6.
- **A1 accepted;** identical to codex A1. Fix item 4.
- **A2 accepted as delivered.** The two overlap refusals exit 1 through `die` with a named message while the usage
  gates exit 2; plan item 1 names exit 2 for the `current` path and the non-hex id alone, and the overlap messages are
  the more useful ones. No change.
- **A3 accepted.** Registration row order is outside the contract (the verifier matches blocks by record and bounds,
  and check 82 reverses the registration deliberately), while each SAF's sort order is part of it; `docs/OUTPUTS.md`
  states both in one sentence. Fix item 7.
- **A4 accepted.** The README truth table gains the row for `tests/expectations/mm39/exon_subtraction_summary.tsv`.
  Fix item 7.
- **A5 accepted.** `min_retained_block_bp` and `context_capability` are declared policy values pinned to one legal value
  each in this snapshot; `docs/OUTPUTS.md` says so in one sentence, so a reader expects no block-size filter. Fix item 7.
- **A6 accepted.** Check 80 recomputes the coverage table with its own GTF pass instead of comparing with the production
  `annotation_mask`; the plan-authored sums stay as the census anchor. Fix item 5.
- **A7 noted.** The entries beyond the touch list are the orchestrator's records, prompts, plan amendments and the
  schema consult, all written after the implementation.

## Fix loop (`prompts/p8_fix.md`, unit `te-tracks-p8-fix`)

Seven items: SAF content and order bound to the registration in the verifier (B1), the lexical parent path in `build.sh`
(B2), both mutations in check 82, the scratch root through `$TE_TRACKS_REFROOT/pubtest` (A1), check 80's own SAF
equality and coverage recomputation (B1, Opus A6), three geometry cases (codex A2, Opus B3), and the documentation
sentences with the README row (B1, B2, Opus A3 to A5). No rebuild and no republication: the fix changes verification and
tests alone, and the builds stay byte-identical.

The fix unit (`te-tracks-p8-fix`, run `20260917T164350Z-3711107`, codex exit 0, 1,765 s) implemented the seven items in
twelve files (`build.sh`, `src/lib/gene_child.py`, checks 80 to 82, the four gene fixture files, `docs/OUTPUTS.md`,
`docs/RELEASES.md`, `README.md`), with no deviation: the verifier on the real child moved from 85.9 s to 158.6 s wall and
from 3,464,622,080 to 3,466,821,632 bytes peak; 23 checks passed; the builds and the published root stayed untouched.

## Orchestrator verification of the fix

- `99_verify.py` on the child with `--parent-dir`: exit 0, twelve `ok` lines including `ok child SAF rows: content and
  order equal the registration in every namespace`; 159.4 s wall; peak 3,493,396,480 bytes resident. The child build, the
  parent build and the published root are byte-untouched: 140 files identical in size, mtime and mode before and after.
- `build.sh --family gene --build-dir … --parent-dir <symlink>` and the same with a trailing slash both exit 2 with the
  usage text; no output directory is created. `build.sh` strips trailing slashes from `--parent-dir` and `--build-dir`
  and tests the lexical path before `realpath`.
- `verify_products` streams every SAF once, folds each row's five fields into an order-independent 128-bit blake2b sum
  compared per namespace with the registration joined to record contig and strand, and checks the declared sort order;
  refusals read `SAF rows differ from registration: <path>` and `SAF order differs: <path>`. Check 80 does the same with
  its own code and recomputes the coverage table from its own GTF pass; check 82 holds the rehashed content and order
  mutations and both symlink spellings.
- Geometry fixtures: 15 cases, 24 blocks, 96 registrations; the hand-authored `coverage.tsv` row (chr1: 21 exon rows,
  441 bp union) equals the orchestrator's own recomputation from the fixture GTF.
- Scratch: checks 81 and 82 and `tests/fixtures/gene/publication_cases.py` use `$TE_TRACKS_REFROOT/pubtest` with
  `TemporaryDirectory`; no `p8impl/` directory exists after the fix unit's suite run; the fix scratch is removed.
- Documentation: the verification, registration-order and declared-policy sentences are present in `docs/OUTPUTS.md`,
  the lexical-path sentence in `docs/RELEASES.md`, the expectations row in the README truth table; the public-file grep
  for contrastive wording finds only code conditionals and a pre-existing phase 5 sentence.
- Git: reflog head `cf1b150`, no git writes by any unit; the fourteen checkouts under `.ref` are clean; no
  `__pycache__` under `src/`, `tests/`, `bin/`.
- `tests/run.sh core` after the fix: 23 pass, exit 0, 15 min 14 s wall; `pubtest` empty and no `p8impl/` directory afterwards.

Committed as "Phase 8: the gene child family, first snapshot" (`393ca76`).
