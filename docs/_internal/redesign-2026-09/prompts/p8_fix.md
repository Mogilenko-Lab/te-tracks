# te-tracks phase 8 fix (unit `te-tracks-p8-fix`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, HEAD `cf1b150`; the phase 8
implementer's tree sits uncommitted on top and is your starting point). You implement the rulings in
`docs/_internal/redesign-2026-09/reviews/p8_rulings.md`; the reviews they answer are `reviews/p8_codex.md` and
`reviews/p8_opus.md`.

## Read first
1. `docs/_internal/redesign-2026-09/reviews/p8_rulings.md` (every item below is a ruling there).
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md` items 2, 5, 6 and 7 (the
   contract you are refining) and `docs/_internal/redesign-2026-09/prompts/p8_impl.md`.
3. `docs/_internal/redesign-2026-09/reviews/p8_codex.md` B1, B2, A1, A2; `reviews/p8_opus.md` B1 to B3 and A1 to A6.
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The files in the touch list, in full, before editing them.

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
  TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1`. The parent
  core build `$TE_TRACKS_REFROOT/te_mm39/build`, the child `$TE_TRACKS_REFROOT/te_mm39_gene/build` and the published
  root `$TE_TRACKS_REFROOT/pubroot` stay byte-identical: this fix changes verification and tests, so no rebuild and no
  republication. Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8fix/`, removed with Python `shutil`
  when you finish (`/tmp` is noexec).
- No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too), no
  installs, no network, no edits outside the touch list. Files under `docs/_internal/` are the orchestrator's.
- Never weaken or delete a test beyond what an item below rules. Report a blocking test by name. Every numeric target
  below is measured; when an observation differs, report the deviation instead of editing an artifact or an expectation
  to match.
- Public prose (docs, docstrings, comments, check messages) is affirmative and brief; comments state intent in one line;
  no history, provenance or review chatter in package files.

## Touch list
`build.sh`, `src/lib/gene_child.py`, `tests/checks/core/80_exon_subtraction.py`, `81_exon_subtraction_fixtures.py`,
`82_child_identity.py`, `tests/fixtures/gene/geometry.json`, `annotation.gtf`, `coverage.tsv`, `publication_cases.py`,
`docs/OUTPUTS.md`, `docs/RELEASES.md`, `README.md` (one truth-table row). Every other file stays as it is.

## Items

1. **Verification binds SAF content to the registration** (`src/lib/gene_child.py` `verify_products`, ruling B1). For
   every row of `tables/exports.tsv`, the SAF's data rows (`GeneID`, `Chr`, `Start`, `End`, `Strand`) equal, as a
   multiset, the registration rows of that universe and grouping (`emitted_feature_id`, `block_start_1`,
   `block_end_1`) joined to the parent record's `chrom` and `strand` and with `chrom` renamed through
   `tables/contig_aliases.tsv` for the file's namespace; and the SAF is sorted by the declared order (contig bytes,
   `Start`, `End`, `Strand`, `GeneID`). Stream both sides with bounded memory: an order-independent 128-bit digest
   (for example the sum modulo 2^128 of `blake2b(digest_size=16)` over each row's five fields joined by tabs) with the
   row count, computed once per (universe, grouping) over the registration with the namespace renames applied, and
   once per SAF file, is an acceptable route; sorting both sides is another. Measure the verifier's wall time and peak resident
   bytes on the real child before and after this item and report both; the after figure stays below 3.6 GB. Refusal message: `SAF
   rows differ from registration: <export_path>`; sort refusal: `SAF order differs: <export_path>`. Emit one new line,
   `ok child SAF rows: content and order equal the registration in every namespace`, and keep the existing lines.
2. **`build.sh` judges the lexical parent path** (ruling B2). Strip every trailing slash from `--parent-dir` before
   the `current` and symlink tests, keep both tests on that lexical path, and resolve with `realpath` only afterwards;
   the same for `--build-dir` where a trailing slash could hide a symlink. `--parent-dir parent-link` and
   `--parent-dir parent-link/` both exit 2 with the usage message and write nothing.
3. **Check 82 gains both mutations** (`tests/checks/core/82_child_identity.py`, rulings B1 and B2). (a) On the tiny
   child from `make_child`: move one SAF row's `Start` by one base onto masked ground in one namespace file, rehash
   that file's `exports.tsv` digest and its inventory entry, recompute `BUILD_ID` with `build_id` and save; verification
   fails with `SAF rows differ from registration`; restore. Then swap two adjacent SAF rows in one file with the same
   rehash; verification fails with `SAF order differs`; restore and verify clean. (b) A symlink to the tiny core,
   passed as `--parent-dir` with and without a trailing slash, exits 2 with `usage:` and leaves `root/out` absent.
4. **Scratch through the reference root** (`81_exon_subtraction_fixtures.py`, `82_child_identity.py`,
   `tests/fixtures/gene/publication_cases.py`, ruling A1). Replace the hardcoded
   `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl` with `Path(os.environ["TE_TRACKS_REFROOT"]) / "pubtest"`
   created with `mkdir(parents=True, exist_ok=True)`, and keep `TemporaryDirectory(dir=...)` for each case, as checks
   71 and 72 do. After a suite run nothing exists under `_scratch/te-tracks-audit/p8impl`.
5. **Check 80 asserts SAF content with its own code** (`80_exon_subtraction.py`, ruling B1). While it streams the
   registration and reads each SAF, compute the same multiset equality as item 1 in the check's own code (no import
   of the verifier's routine), mapping each SAF's `Chr` back to `chrom_ucsc` through the alias table, and assert
   sortedness of each SAF. Recompute `tables/gene_annotation_coverage.tsv` cell for cell with the check's own GTF pass
   (per-contig gene, transcript and exon row counts, an exon union by the check's own touching merge, and the
   `annotated` flag) instead of comparing with the production `annotation_mask` (Opus A6); keep the plan-authored sums.
   Update the success message.
6. **Check 81 gains three geometry cases** (`geometry.json`, `annotation.gtf`, `coverage.tsv`, ruling A2), all on
   `chr1`, hand-authored: `Nested`, record 2101..2200 `+`, exons 2141..2160 and 2145..2150, blocks 2101..2140 and
   2161..2200, `split`, retained 80, removed 20; `Overlapping`, record 2301..2400 `+`, exons 2341..2360 and
   2355..2370, blocks 2301..2340 and 2371..2400, `split`, retained 70, removed 30; `FourBlocks`, record 2501..2600
   `-`, exons 2521..2530, 2551..2560 and 2581..2590, blocks 2501..2520, 2531..2550, 2561..2580 and 2591..2600,
   `split`, retained 70, removed 30. `coverage.tsv`'s `chr1` row moves to 21 exon rows and a 441 bp union (author
   these by hand from the GTF, then compare with the build). Registration rows become 96 (24 blocks × 2 universes × 2
   groupings); the check's count assertion and its success message (`15 geometry cases, 12 SAFs, 96 registrations`)
   follow.
7. **Documentation** (rulings B1, B2; Opus A3, A4, A5). `docs/OUTPUTS.md` phase 8 section: one sentence stating that
   verification compares every SAF's rows and order with the registration joined to record strand and contig in each
   namespace; one sentence stating that registration row order is outside the contract while each SAF's sort order is
   part of it; one sentence stating that `min_retained_block_bp` and `context_capability` are declared policy values
   pinned to one legal value each in this snapshot, so the build refuses other values and applies no block-size
   filter. `README.md` truth table gains a row for `tests/expectations/mm39/exon_subtraction_summary.tsv`
   (`delivered, tested`, phase 8) beside the taxonomy census row.
   `docs/RELEASES.md` "Gene child snapshots": the verification sentence lists SAF content and order beside row counts,
   and the parent-argument sentence states that the lexical path is judged before symlink resolution.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1
S=/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8fix; mkdir -p "$S"
C="$TE_TRACKS_REFROOT/te_mm39_gene/build"; P="$TE_TRACKS_REFROOT/te_mm39/build"
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
find "$C" "$P" -type f -printf '%s %T@ %p\n' | sort > "$S/before.txt"
python3 - <<'PY'
import resource, subprocess, sys, time, os
t=time.perf_counter(); r=subprocess.run(["python3","src/99_verify.py",os.environ["TE_TRACKS_REFROOT"]+"/te_mm39_gene/build","--parent-dir",os.environ["TE_TRACKS_REFROOT"]+"/te_mm39/build"])
print("verify exit",r.returncode,"wall_s",round(time.perf_counter()-t,1),"peak_rss_bytes",resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss*1024)
PY
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
find "$C" "$P" -type f -printf '%s %T@ %p\n' | sort | cmp - "$S/before.txt" && echo "builds untouched"
ln -sfn "$P" "$S/parent-link"
./build.sh --genome mm39 --family gene --build-dir "$S/out" --parent-dir "$S/parent-link"; echo "exit=$? (expected 2)"
./build.sh --genome mm39 --family gene --build-dir "$S/out" --parent-dir "$S/parent-link/"; echo "exit=$? (expected 2)"
ls -d "$S/out" 2>&1
tests/run.sh core; echo "exit=$?"
ls -d /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl 2>&1; ls "$TE_TRACKS_REFROOT/pubtest"
git status --short
```
Expected: the verifier exits 0 with the new `ok` line and the real child's peak below 3,571,302,400 bytes; both builds
untouched (identical size and mtime listings); both symlink spellings exit 2 with usage and `$S/out` absent;
`tests/run.sh core` exits 0 with 23 checks passing, check 81 reporting 15 cases and 96 registrations and check 82 naming
the SAF content, order and symlink refusals; no `p8impl` directory; `pubtest` empty; `git status --short` lists the phase
8 touch list and the orchestrator's `docs/_internal/` files alone.

## Final message
Every file changed; acceptance outputs verbatim; the verifier's wall time and peak resident bytes on the real child
before and after item 1 (measure the before figure first, from the tree as you found it); any deviation, with the
observation and your reading of it.
