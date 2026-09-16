# Phase 7: manifest, BUILD_ID, publication

Deliverables
- `src/90_manifest.py`: two-section manifest. `identity`: schema_version, family, species, assembly,
  contig set digest, sources with url and observed digests, declared run identity, universe
  predicates, export contracts, taxonomy rule version, parent build id (child family), complete file
  inventory with SHA-256. `provenance`: builder sha, tool versions, invocation, validation summary.
  `BUILD_ID = sha256("te-tracks-build-v1\n" + canonical_json(identity))`.
- Catalog identity: `CATALOG_ID = sha256("te-tracks-catalog-v1\n" + canonical_json(catalog))` over
  `identity.catalog`: source digests, declared run identity, parser profile, `instance_id_scope =
  source_run`, and the digests of `rmsk_records.parquet`, `rmsk_records.tsv.gz`,
  `rmsk_instance_members.tsv.gz` and `rmsk_taxonomy.tsv`. Consuming ledgers key records on
  `(te_catalog_id, rmsk_record_id)` and record `te_build_id` as provenance; adding an export, a universe
  or a taxonomy rule version mints a new `BUILD_ID` and keeps `CATALOG_ID` (milestone 2 ruling H5).
- `canonical_json` sorts keys and emits UTF-8 without whitespace. `universes.json` keeps its writer's
  byte profile (insertion order, indent 2, `ensure_ascii=False`, UTF-8, final LF), published in
  `docs/OUTPUTS.md`; `schema_version` owns predicate semantics and a new key bumps it (rulings A2, A3).
- `provenance` records Python, pandas, pyarrow and zlib versions and the devcontainer image identity;
  the host build runs inside the same image (ruling H6). Retention is restated from a measured build
  size (ruling M4): the seven `interspersed` full exports measure 2.6 GB uncompressed per namespace and
  `export_feature_members.tsv.gz` 255 MB (milestone 5 fix, eight registration rows per record), so three namespaces plus the canonical
  tables approach 9 GB per build before the child family. The export writer peaks at 5.7 GB resident for mm39 (5,698,908 KiB, milestone 5 fix)
  (phase 4 Opus A5), the host floor the runbook states beside the disk figure.
- `docs/OUTPUTS.md` publishes reader settings for pandas, DuckDB and R (`data.table`, `arrow`): text
  instance ids, signed int64 fields, no quoting, empty strings literal; a nullable column defines its
  literal before it lands (ruling A5). The identity section publishes the single source-run
  requirement behind `rmsk_instance_id` (rulings A1, M6).
- Recorded deferrals: cross-build record correspondence keyed on `(chrom, start_1, end_1, strand)`
  (ruling M8); hg38 admission requires a source-wide instance numbering or a contig-scoped instance key
  decision (rulings A1, M6).
- `src/99_verify.py`: exact inventory equality, digests, id recomputation, schema and key
  assertions, bounds; scratch outside the snapshot.
- `src/release.py`: staging under `<root>/te_mm39/.staging/<tmp>/`; verify; no-replace install into
  `archive/<BUILD_ID>/`; `current` swapped by temporary symlink and `os.replace`; a corrupt existing
  `current` aborts with the discrepancy; explicit family root argument.
- `build.sh` rewritten around these; `INDEX.tsv`, `CURRENT_BUILD.tsv`, dated snapshots and
  archive-on-supersede removed; `docs/RELEASES.md` rewritten.
- `tests/run.sh core` publication smoke cases in a scratch root: identical rebuild converges;
  same-day changed policy yields a second archive; failed build leaves `current` valid; new export
  yields a new `BUILD_ID` and the same `CATALOG_ID`; two concurrent identical builds converge; an old id resolves at
  `archive/<id>/`; forged `BUILD_ID` file rejected; corrupt current detected.
- `docs/RELEASES.md` transfer procedure: copy into destination staging, verify there, install.

Acceptance: all smoke cases pass in-container against `_scratch`; permissions normalized under
`umask 002`; verifier leaves the snapshot byte-identical.

Milestone review after this phase: publication seam, run on the host root by the owner.
