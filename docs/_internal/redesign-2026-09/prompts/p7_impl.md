# te-tracks phase 7: manifest, BUILD_ID, publication

You are the implementer for phase 7 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 6 have landed: read
`AGENTS.md`, `build.sh`, `src/*.sh`, `src/lib/*.py`, `tests/run.sh`, `docs/OUTPUTS.md`, `docs/RELEASES.md`
(legacy, to be rewritten), and the build under `$TE_TRACKS_REFROOT/te_mm39/build`.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/17_phase7_publication.md` (your phase, carrying
   the milestone 2 rulings: `CATALOG_ID`, instance scope, grammar version, byte profile, reader settings,
   toolchain provenance, retention, deferrals) and `docs/_internal/redesign-2026-09/reviews/m2_rulings.md`
   ("Phase 7")
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 6, 7
3. `docs/_internal/redesign-2026-09/consults/ADR67_consult.md` (identity/provenance split, canonical
   encoding, publication failure cases) and `C_identity_publication.md` sections 2, 3, 5
4. `docs/_internal/redesign-2026-09/audit/AUDIT.md` F4, F5, F7 (the legacy failure modes to close)
5. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Layout and interfaces to implement
```
<root>/te_mm39/                      family root (explicit argument, never inferred)
  .staging/<mkdtemp>/                a build in progress; removed on success or left for inspection on failure
  archive/<BUILD_ID>/                immutable installed build; MANIFEST.json, BUILD_ID and CATALOG_ID inside
  current -> archive/<BUILD_ID>      the single selector, a relative symlink
```
- `build.sh --genome <name> --build-dir <dir>` keeps working exactly as today (stages, then manifest, then
  verify; no publication) for in-container test builds.
- `build.sh --genome <name> --root <refroot> [--no-select]`: creates `.staging/<tmp>` under the family
  root, runs the stages there, writes the manifest, verifies, installs into `archive/<BUILD_ID>/`, and
  selects `current` unless `--no-select`.
- `src/90_manifest.py <build-dir> <config.env>` writes `MANIFEST.json`, `BUILD_ID` and `CATALOG_ID`.
- `src/99_verify.py <build-dir>` verifies a build directory in place; exit 0 or 1 with the discrepancy.
- `src/release.py install --root <refroot> --family <te_x> --staging <dir> [--select]`,
  `src/release.py select --root <refroot> --family <te_x> --build-id <id>`,
  `src/release.py verify-current --root <refroot> --family <te_x>`.

## Manifest contract
Two top-level sections. `identity` (hashed): `schema_version` ("te-tracks-manifest-1"), `family`, `species`
(`{"name": "Mus musculus", "taxon_id": 10090}`), `assembly` (`{"ucsc": "mm39", "name": "GRCm39"}`),
`declared_assembly` (the `SOURCES.json` object: FASTA url, md5, status), `contig_set_sha256` (digest of the
`chrom.sizes` bytes), `catalog` (see below), `universes` (the full `universes.json` object; its
`schema_version` owns the predicate grammar), `taxonomy_rule_version` (read from
`build_taxonomy.TAXONOMY_RULE_VERSION`), `export_contracts` (derived from `build_exports.EXPORT_JOBS` and the
inventory, one entry per export path across the 24 namespace copies: universe, format, level, feature identity
field or attribute, the attribute-to-source-column mapping, the output key each named consumer constructs (BED
name; GTF `locus` and `instance_id`; the TEsingle and TElocal `transcript_id:gene_id:family_id:class_id` tuple;
the TEtranscripts `gene_id:family_id:class_id` triple; SAF `GeneID`), the selectable levels, coordinate
convention (milestone 5 ruling A3); source it from one dict in `src/lib/build_exports.py` so the exporter
and the manifest agree, and cross-check it against `tables/exports.tsv`), `parent_build_id` and
`parent_catalog_id` (null for the core family), `inventory` (sorted list of `{path, bytes, sha256}` for every
regular file under the build dir except `MANIFEST.json`, `BUILD_ID` and `CATALOG_ID`; `source/` files
included; symlinks and paths with `..` rejected).
`identity.catalog` (the record catalog alone): `sources` (per source: url, md5, sha256, bytes), `run_identity`
(rm_version, rm_library, rm_run_evidence, rmsk_out_profile), `instance_id_scope` (`"source_run"`: one
source-wide RepeatMasker run numbers the instances), and the sha256 of `tables/rmsk_records.parquet`,
`tables/rmsk_records.tsv.gz`, `tables/rmsk_instance_members.tsv.gz` and `tables/rmsk_taxonomy.tsv`.
`CATALOG_ID = sha256(b"te-tracks-catalog-v1\n" + canonical_json(identity.catalog)).hexdigest()`: consuming
ledgers key records on `(te_catalog_id, rmsk_record_id)` and record `te_build_id` as provenance; a new export,
universe or taxonomy rule version mints a new `BUILD_ID` and keeps `CATALOG_ID`.
`provenance` (outside the hash): builder git sha and dirty flag, invocation argv, python, pyarrow, pandas and
zlib versions, the devcontainer image identity (read `/etc/os-release` and any image label file the container
exposes; state what you found), `built_at` UTC, `source_acquisition` (cache path or URL per source),
`validation` (verifier summary), `peak_rss_bytes` of the export writer when measurable. Canonical encoding:
`json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)` encoded UTF-8;
`BUILD_ID = sha256(b"te-tracks-build-v1\n" + canonical_bytes(identity)).hexdigest()`; the `BUILD_ID` and
`CATALOG_ID` files hold the hex digest and a newline. `docs/DECISIONS.md` entry 7 publishes both ids and the ledger
key `(te_catalog_id, rmsk_record_id)`, and the README names both (milestone 5 ruling M1). State both encodings in
`docs/RELEASES.md` once, and the
`universes.json` byte profile (insertion order, indent 2, `ensure_ascii=False`, UTF-8, final LF) in
`docs/OUTPUTS.md` beside the serialization contract, together with reader settings for pandas, DuckDB and R
(`data.table`, `arrow`): text instance ids, signed int64 fields, no quoting, empty strings literal.

## Verifier contract (`99_verify.py`)
Recomputes the inventory from disk and requires exact equality with the manifest (no missing, no extra
files, equal bytes and digests); recomputes `BUILD_ID` from the manifest identity and requires equality with
the file; loads `rmsk_records.parquet` and asserts id uniqueness, bounds against `source/mm39.chrom.sizes`,
row count equal to `universe_summary` `all_rmsk`; asserts export row counts and digests equal `exports.tsv`;
recomputes `CATALOG_ID` from `identity.catalog` and requires equality with the file; rejects
symlinks inside the build; writes nothing inside the build (scratch under a `tempfile` directory outside).
Prints one line per assertion and a final `verified <BUILD_ID>`.

## Release contract (`release.py`)
- `install`: verifies the staging dir; if `archive/<id>` exists, verifies it too and, when both verify,
  removes the staging dir and reports `converged <id>` (identical rebuild); an existing archive that fails
  verification aborts naming it. Otherwise installs by `os.rename(staging, archive/<id>)` with a no-replace
  guarantee (create `archive/` with mode 2775 if absent; rename fails when the target exists; a target that
  is an empty directory or a symlink is refused before the rename). Normalizes modes: payload files 0444,
  payload directories 0555, under `umask 002`. Never writes into an installed archive afterwards.
- `select`: requires `archive/<id>/BUILD_ID` to equal `<id>` and the archive to verify; if `current` exists
  and its target lacks a `BUILD_ID` or that id fails recomputation, aborts with the discrepancy (a corrupt
  selection is a human decision); otherwise creates `current.tmp.<pid>` beside `current` as a relative
  symlink and `os.replace`s it onto `current`.
- `verify-current`: resolves `current`, runs the verifier on the target, prints the id.
- Concurrency: two identical builds racing to install must both end with one archive and a valid
  selector (the loser converges); different valid builds racing to select leave the last successful
  selection.

## Deliverables
1. `src/lib/manifest.py`, `src/90_manifest.py`, `src/99_verify.py`, `src/release.py`, `build.sh` rewritten
   as above. Remove nothing under `src/` that later phases use; `INDEX.tsv`, `CURRENT_BUILD.tsv`, dated
   snapshots and archive-on-supersede are gone with the legacy scripts.
2. `docs/RELEASES.md` rewritten: layout, the two `build.sh` modes, the manifest sections, the encoding, the
   install and select procedure, the transfer procedure (copy into the destination's `.staging/`, verify
   there, install, select), interruption recovery (an unselected complete archive is a valid state;
   abandoned staging is removed by hand after checking no builder is alive), and what a consumer pins
   (full id, raw manifest sha256, relative export paths and their digests).
3. Checks under `tests/checks/core/`:
   - `70_manifest_identity.py`: on the real build dir: `BUILD_ID` and `CATALOG_ID` recompute; changing a
     `provenance` value in a copied manifest leaves both unchanged; changing a universe predicate in a copy
     changes `BUILD_ID` and keeps `CATALOG_ID`; changing a source digest changes both; every file on disk except
     the three is in the inventory; every inventory digest matches; `identity.catalog.instance_id_scope` equals
     `source_run`; `taxonomy_rule_version` equals `taxonomy_rule_v1`.
   - `71_verify_build.py`: `99_verify.py` exits 0 on the real build dir; on a copy with one byte flipped in
     a small file it exits 1 naming the path; on a copy with an extra file it exits 1 naming it.
   - `72_publication_cases.py`: synthetic tiny builds (a few small files, produced by a fixture builder
     that calls `manifest.py` on them) in a scratch family root under `$TE_TRACKS_REFROOT/pubtest/`:
     identical rebuild converges to one archive; a changed file yields a second archive and `current`
     moves; a failing verification leaves `current` untouched and staging in place; a new file yields a
     new `BUILD_ID` and the same `CATALOG_ID`; two concurrent identical installs (threads or subprocesses)
     converge; an old id resolves at
     `archive/<id>/` after a newer selection; a forged `BUILD_ID` file is rejected by `select`; a `current`
     pointing at a corrupted archive makes `select` abort with the discrepancy; an empty directory at the
     archive target is refused; payload modes are 0444/0555 after install.
4. README truth table: `MANIFEST.json`, `BUILD_ID`, `CATALOG_ID` to `tested`, phase 7; Build section states the
   two modes. `docs/RELEASES.md` restates retention from the measured sizes (exports 3,021,713,838 / 2,926,268,559 /
   3,021,138,299 bytes for `ucsc` / `ensembl` / `gencode`, registration 347,526,106 bytes, 10,461,962,113 bytes per
   build before the child) and names the host floor (5.7 GB resident for the
   export writer) and the requirement that the host build runs inside the same devcontainer image. Recorded
   deferrals in `docs/DECISIONS.md`'s deferred list (one sentence each): cross-build record correspondence on
   `(chrom, start_1, end_1, strand)`; hg38 admission needs a source-wide instance numbering or a contig-scoped
   instance key.

## Rules
- Touch only: `build.sh`, `src/90_manifest.py`, `src/99_verify.py`, `src/release.py`, `src/lib/manifest.py`,
  `src/lib/build_exports.py` (only to expose the export contracts dict), `tests/checks/core/7*`,
  `tests/fixtures/publication/**`, `docs/RELEASES.md`, `docs/OUTPUTS.md` (byte profile and reader settings),
  `docs/DECISIONS.md` (the two deferral sentences), `README.md` (Build section and truth table).
- No git writes. No installs. No network. Never write into `/data2/users/shared/refcache` (read-only here).
- Report a deviation instead of editing a number or a plan file to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
python3 src/90_manifest.py "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env && cat "$TE_TRACKS_REFROOT/te_mm39/build/BUILD_ID" "$TE_TRACKS_REFROOT/te_mm39/build/CATALOG_ID"
python3 -c "import json;m=json.load(open('$TE_TRACKS_REFROOT/te_mm39/build/MANIFEST.json'));print(sorted(m));print(sorted(m['identity']));print(len(m['identity']['inventory']))"
python3 src/99_verify.py "$TE_TRACKS_REFROOT/te_mm39/build"; echo "exit=$?"
rm -rf "$TE_TRACKS_REFROOT/pubroot" && time ./build.sh --genome mm39 --root "$TE_TRACKS_REFROOT/pubroot"; echo "exit=$?"
ls -la "$TE_TRACKS_REFROOT/pubroot/te_mm39/" "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/"
readlink "$TE_TRACKS_REFROOT/pubroot/te_mm39/current"; cat "$TE_TRACKS_REFROOT/pubroot/te_mm39/current/BUILD_ID"
diff <(cat "$TE_TRACKS_REFROOT/te_mm39/build/BUILD_ID") <(cat "$TE_TRACKS_REFROOT/pubroot/te_mm39/current/BUILD_ID") && echo "same id from both modes"
time ./build.sh --genome mm39 --root "$TE_TRACKS_REFROOT/pubroot"; echo "exit=$? (expect converged, one archive)"
ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/" | wc -l
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
tests/run.sh core; echo "exit=$?"
git status --short
```

## Final message
Every file created, changed or deleted; acceptance outputs verbatim including `BUILD_ID` and `CATALOG_ID`; the
image identity you recorded; any deviation.
