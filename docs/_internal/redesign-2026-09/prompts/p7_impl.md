# te-tracks phase 7: manifest, BUILD_ID, publication

You are the implementer for phase 7 of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`. Phases 0 to 6 have landed: read
`AGENTS.md`, `build.sh`, `src/*.sh`, `src/lib/*.py`, `tests/run.sh`, `docs/OUTPUTS.md`, `docs/RELEASES.md`
(legacy, to be rewritten), and the build under `$TE_TRACKS_REFROOT/te_mm39/build`.

## Read first
1. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/17_phase7_publication.md` (your phase)
2. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/01_decisions.md` entries 6, 7
3. `docs/_internal/redesign-2026-09/consults/ADR67_consult.md` (identity/provenance split, canonical
   encoding, publication failure cases) and `C_identity_publication.md` sections 2, 3, 5
4. `docs/_internal/redesign-2026-09/audit/AUDIT.md` F4, F5, F7 (the legacy failure modes to close)
5. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding)

## Layout and interfaces to implement
```
<root>/te_mm39/                      family root (explicit argument, never inferred)
  .staging/<mkdtemp>/                a build in progress; removed on success or left for inspection on failure
  archive/<BUILD_ID>/                immutable installed build; MANIFEST.json and BUILD_ID inside
  current -> archive/<BUILD_ID>      the single selector, a relative symlink
```
- `build.sh --genome <name> --build-dir <dir>` keeps working exactly as today (stages, then manifest, then
  verify; no publication) for in-container test builds.
- `build.sh --genome <name> --root <refroot> [--no-select]`: creates `.staging/<tmp>` under the family
  root, runs the stages there, writes the manifest, verifies, installs into `archive/<BUILD_ID>/`, and
  selects `current` unless `--no-select`.
- `src/90_manifest.py <build-dir> <config.env>` writes `MANIFEST.json` and `BUILD_ID`.
- `src/99_verify.py <build-dir>` verifies a build directory in place; exit 0 or 1 with the discrepancy.
- `src/release.py install --root <refroot> --family <te_x> --staging <dir> [--select]`,
  `src/release.py select --root <refroot> --family <te_x> --build-id <id>`,
  `src/release.py verify-current --root <refroot> --family <te_x>`.

## Manifest contract
Two top-level sections. `identity` (hashed): `schema_version` ("te-tracks-manifest-1"), `family`, `species`
(`{"name": "Mus musculus", "taxon_id": 10090}`), `assembly` (`{"ucsc": "mm39", "name": "GRCm39"}`),
`contig_set_sha256` (digest of the `chrom.sizes` bytes), `sources` (per source: url, md5, sha256, bytes),
`run_identity` (rm_version, rm_library, rm_run_evidence, rmsk_out_profile), `universes` (the full
`universes.json` object), `taxonomy_rule_version`, `export_contracts` (per export path: format, level,
feature identity field or attribute, coordinate convention; source it from one dict in
`src/lib/build_exports.py` so the exporter and the manifest agree), `parent_core_build_id` (null for the core
family), `inventory` (sorted list of `{path, bytes, sha256}` for every regular file under the build dir except
`MANIFEST.json` and `BUILD_ID`; `source/` files included; symlinks and paths with `..` rejected).
`provenance` (outside the hash): builder git sha and dirty flag, invocation argv, python and pyarrow and
pandas versions, `built_at` UTC, `source_acquisition` (cache path or URL per source), `validation`
(verifier summary). Canonical encoding: `json.dumps(identity, sort_keys=True, separators=(",", ":"),
ensure_ascii=False, allow_nan=False)` encoded UTF-8, and
`BUILD_ID = sha256(b"te-tracks-build-v1\n" + canonical_bytes).hexdigest()`; `BUILD_ID` file holds the
hex digest and a newline. State this encoding in `docs/RELEASES.md` once.

## Verifier contract (`99_verify.py`)
Recomputes the inventory from disk and requires exact equality with the manifest (no missing, no extra
files, equal bytes and digests); recomputes `BUILD_ID` from the manifest identity and requires equality with
the file; loads `rmsk_records.parquet` and asserts id uniqueness, bounds against `source/mm39.chrom.sizes`,
row count equal to `universe_summary` `all_rmsk`; asserts export row counts equal `export_summary`; rejects
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
   - `70_manifest_identity.py`: on the real build dir: `BUILD_ID` recomputes; changing a `provenance`
     value in a copied manifest leaves the id unchanged; changing a universe predicate in a copy changes it;
     every file on disk except the two is in the inventory; every inventory digest matches.
   - `71_verify_build.py`: `99_verify.py` exits 0 on the real build dir; on a copy with one byte flipped in
     a small file it exits 1 naming the path; on a copy with an extra file it exits 1 naming it.
   - `72_publication_cases.py`: synthetic tiny builds (a few small files, produced by a fixture builder
     that calls `manifest.py` on them) in a scratch family root under `$TE_TRACKS_REFROOT/pubtest/`:
     identical rebuild converges to one archive; a changed file yields a second archive and `current`
     moves; a failing verification leaves `current` untouched and staging in place; a new file yields a
     new id; two concurrent identical installs (threads or subprocesses) converge; an old id resolves at
     `archive/<id>/` after a newer selection; a forged `BUILD_ID` file is rejected by `select`; a `current`
     pointing at a corrupted archive makes `select` abort with the discrepancy; an empty directory at the
     archive target is refused; payload modes are 0444/0555 after install.
4. README truth table: `MANIFEST.json`, `BUILD_ID` to `tested`, phase 7; Build section states the two modes.

## Rules
- Touch only: `build.sh`, `src/90_manifest.py`, `src/99_verify.py`, `src/release.py`, `src/lib/manifest.py`,
  `src/lib/build_exports.py` (only to expose the export contracts dict), `tests/checks/core/7*`,
  `tests/fixtures/publication/**`, `docs/RELEASES.md`, `README.md` (Build section and truth table).
- No git writes. No installs. No network. Never write into `/data2/users/shared/refcache` (read-only here).
- Report a deviation instead of editing a number or a plan file to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
python3 src/90_manifest.py "$TE_TRACKS_REFROOT/te_mm39/build" config/mm39.env && cat "$TE_TRACKS_REFROOT/te_mm39/build/BUILD_ID"
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
Every file created, changed or deleted; acceptance outputs verbatim including the BUILD_ID; any deviation.
