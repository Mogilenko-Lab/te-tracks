# te-tracks phase 8: the gene child family, first snapshot (unit `te-tracks-p8-impl`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, tree clean at the commit
that carries this prompt). You implement phase 8 as specified in
`docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md`; that plan is authoritative
where this prompt and the plan disagree, and a disagreement is a deviation to report.

## Read first
1. The plan file above, in full.
2. `docs/DECISIONS.md` sections 4, 8, 9, 10, 12 and 16.
3. `docs/_internal/redesign-2026-09/consults/gene_child_consult.md` Q1 to Q4, Q7, Q8 and its fixture answers;
   `consults/mask_policy_consult.md` Q1 (the census) and Q6.
4. `docs/_internal/redesign-2026-09/reviews/m7_rulings.md` A1 and A2; `reviews/m5_rulings.md` A1 and A2;
   `reviews/p6_rulings.md` A2; `reviews/p7_rulings.md` A3.
5. The code you extend, in full: `build.sh`, `lib/common.sh`, `src/00_fetch_sources.sh`, `src/lib/manifest.py`,
   `src/lib/build_exports.py`, `src/lib/contigs.py`, `src/lib/records_io.py`, `src/release.py`, `src/99_verify.py`,
   `src/90_manifest.py`, `bin/te-tracks-preflight`, `tests/run.sh`, `tests/fixtures/publication/build_fixture.py`,
   `tests/checks/core/70_manifest_identity.py`, `71_verify_build.py`, `72_publication_cases.py`.
6. `docs/OUTPUTS.md` (exports, registration, namespaces, the phase 8 section), `docs/RELEASES.md`, `docs/RUNBOOK.md`,
   `README.md` (truth table), `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
  TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1`. The
  verified parent core build is `$TE_TRACKS_REFROOT/te_mm39/build` (`BUILD_ID`
  `9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d`, `CATALOG_ID`
  `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e`); the scratch published root is
  `$TE_TRACKS_REFROOT/pubroot` with that build under `te_mm39/archive/`. Leave the parent build and its archive
  untouched. Build the child into `$TE_TRACKS_REFROOT/te_mm39_gene/build` and publish a second copy into the scratch
  root with `--root`.
- The GTF is in the read-only refcache at
  `/data2/users/shared/refcache/mm39/mm39_20260911/gencode.vM37.primary_assembly.annotation.gtf.gz` (md5
  `702e27a8727db66cd23e9f66f5aa1d38`). Copy it once into `$TE_TRACKS_SOURCE_CACHE/` under the URL basename so the
  fetch stage finds it through the cache; never write into the refcache. No network otherwise.
- Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl/`, removed with Python `shutil` when you
  finish (`/tmp` is noexec). No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are
  git repositories too), no installs, no edits outside the touch list.
- Never weaken or delete a test. Report a blocking test by name. Every numeric target is measured; when an
  observation differs, report the deviation instead of editing an artifact or an expectation to match.
- Public prose (README, docs, docstrings, comments, check messages) is affirmative and brief; comments state intent
  in one line; no history, provenance or review chatter in package files.
- Streaming and vectorised work over the 5,320,771 records; record peak resident memory (per-stage
  `RUSAGE_CHILDREN`, as `build.sh` does for stage 30) and wall time in your report.

## Touch list
`build.sh`, `lib/common.sh` (only if a shared helper is needed), `config/mm39_gene.env` (new), `src/gene/*.sh` (new
stages), `src/lib/gene_child.py` (new: mask, subtraction, SAF and registration writers, coverage and status
tables), `src/lib/manifest.py` (child identity branch and verifier), `src/90_manifest.py`, `src/99_verify.py`
(parent resolution arguments), `src/release.py` (dependency requirement for child families),
`tests/checks/core/80_exon_subtraction.py`, `81_exon_subtraction_fixtures.py`, `82_child_identity.py`,
`83_child_publication_cases.sh` (new), `tests/fixtures/gene/**` (new), `tests/fixtures/publication/build_fixture.py`
(child extension), `tests/expectations/mm39/exon_subtraction_summary.tsv` (new, authored from the plan's table),
`docs/OUTPUTS.md`, `docs/RELEASES.md`, `docs/RUNBOOK.md`, `README.md`. Every other file stays as it is; the core
checks 01 to 72 keep passing unchanged in meaning.

## Deliverables
1. **Dispatch.** `build.sh --genome mm39 --family gene --build-dir DIR --parent-dir CORE_BUILD_DIR` and
   `build.sh --genome mm39 --family gene --root ROOT --parent-build-id ID [--no-select]`. `--family` selects
   `config/<genome>_<family>.env` and the stage set `src/<family>/[0-9][0-9]_*.sh`; without `--family` the core path
   is byte-for-byte the current behaviour. `--parent-dir` and `--parent-build-id` exclude each other; `--build-dir`
   requires the first, `--root` the second; a `current` path or a non-hex id is refused with exit 2 and a usage
   message. The parent is verified with `verify_build` before any stage reads it, and its `identity.family` and
   `identity.assembly.ucsc` must equal `PARENT_FAMILY` and `GENOME`.
2. **Config** `config/mm39_gene.env` with the keys and values of plan item 3; comments state intent only.
3. **Stages** `src/gene/00_fetch_gene_sources.sh` (the `gene_gtf` role through the cache, md5 verified, child
   `source/SOURCES.json`), `src/gene/10_copy_parent_inputs.sh` (exact copies of `universes.json` and
   `tables/contig_aliases.tsv` with digests recorded), `src/gene/50_build_exon_subtracted.sh` calling
   `src/lib/gene_child.py`: alias normalisation of the GTF (fail on an unmapped contig), the mask, subtraction of
   every catalog record, the four tables, the twelve SAF files, the registration and the child `tables/exports.tsv`,
   all as plan items 4 and 5 specify. Sorting, identifier validation, namespace renaming and inventory writing reuse
   the parent's primitives from `build_exports.py` and `contigs.py`, parameterised with explicit parent directory,
   child directory, universe, variant, block bounds and roster; the exporter refuses a universe outside
   `CHILD_UNIVERSES`.
4. **Identity and verification** as plan item 6: the child identity fields, the verifier branch on non-null parent
   ids, `99_verify.py BUILD_DIR [--parent-dir DIR | --root ROOT]` (a child without a resolvable parent exits 1 with
   the message `child verification requires the parent archive`), `release.py` resolving the sibling parent archive
   for `install`, `select` and `verify-current` of a family whose manifest carries parent ids, and refusing when it is
   absent or fails verification. The child's `CATALOG_ID` file equals the parent's bytes.
5. **Checks** `80_exon_subtraction.py` (child build present, else exit 3): conservation on every record; zero residual
   overlap on a 200,000-record sample against the mask; blocks disjoint, ordered and contained; the summary table
   equals `tests/expectations/mm39/exon_subtraction_summary.tsv`; SAF data rows equal blocks per universe;
   registration rows 7,369,868 and 7,435,480; coverage table with 38 annotated contigs and 2,638 records on the 23
   unannotated ones. `81_exon_subtraction_fixtures.py`: every geometry case of plan item 7 with hand-authored
   expected outputs under `tests/fixtures/gene/`, run through the production writers in a scratch directory.
   `82_child_identity.py`: identity fields, parent pins equal to the parent's ids, `CATALOG_ID` bytes equal, each
   mutation of plan item 6 moving `BUILD_ID` while the parent ids stay, verification refusals with their messages.
   `83_child_publication_cases.sh`: the dependency cases of plan item 7 through the tiny publication fixture extended
   with a child on the tiny core (`build_fixture.py`), including the refusals of `install`, `select` and
   `verify-current` without the parent archive and the convergence of a repeated child publication.
6. **Documentation** as plan item 8; README truth table rows for phase 8 to `tested`, with the compat pair added.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1
for f in build.sh lib/common.sh src/*.sh src/gene/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
C="$TE_TRACKS_REFROOT/te_mm39_gene/build"
time ./build.sh --genome mm39 --family gene --build-dir "$C" --parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
cat "$C/tables/exon_subtraction_summary.tsv"
cat "$C/BUILD_ID" "$C/CATALOG_ID" "$TE_TRACKS_REFROOT/te_mm39/build/CATALOG_ID"
python3 -c "import json;i=json.load(open('$C/MANIFEST.json'))['identity'];print(i['family'],i['parent_build_id'],i['parent_catalog_id'],i['policy_bundle'],i['copied_inputs'],i['gene_annotation']['md5'])"
cat "$C/tables/exports.tsv"
for ns in ucsc ensembl gencode; do for u in interspersed compat_tetranscripts_mm39; do wc -l "$C/exports/$ns/$u/exon_subtracted/"*.saf; done; done
zcat "$C/tables/export_feature_members.tsv.gz" | tail -n +2 | cut -f1,3 | sort | uniq -c
python3 src/99_verify.py "$C" --parent-dir "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
python3 src/99_verify.py "$C"; echo "exit=$? (expected 1: parent required)"
time ./build.sh --genome mm39 --family gene --root "$TE_TRACKS_REFROOT/pubroot" --parent-build-id 9ddf36220830761e74cf1fa5ce02fd993dff8214075ee094e973ed8bfdd1fd8d; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39_gene; echo "exit=$?"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
ls "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/archive"; readlink "$TE_TRACKS_REFROOT/pubroot/te_mm39_gene/current"
./build.sh --genome mm39 --build-dir /workspaces/Meta-Aging/_scratch/te-tracks-audit/p8impl/core_smoke --help >/dev/null; echo "core usage exit=$?"
tests/run.sh core; echo "exit=$?"
git status --short
```
Expected: the summary equals the plan's table exactly; the child `CATALOG_ID` bytes equal the parent's; twelve SAF
files with data rows 3,684,934 (`interspersed`) and 3,717,740 (compat) in every namespace; registration groups
`interspersed subfamily 3684934`, `interspersed taxonomy_triple 3684934`, `compat_tetranscripts_mm39 subfamily
3717740`, `compat_tetranscripts_mm39 taxonomy_triple 3717740`; both verifications exit as stated; the scratch root
holds the child archive whose `BUILD_ID` equals the scratch child's when inputs and serializer match (report if the
two differ and why); `tests/run.sh core` exits 0 with checks 80 to 83 passing; `git status --short` lists only the
touch list.

## Final message
Every file created or changed; acceptance outputs verbatim; the measured status counts beside the plan's table;
distinct `GeneID`s per SAF; peak resident memory and wall time of the child build; any deviation, with the
observation and your reading of it.
