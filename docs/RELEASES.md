# Releases

A core release binds one RepeatMasker catalog and its registered exports to `BUILD_ID`.
`CATALOG_ID` binds the record-producing RepeatMasker `.out`, run identity, source-wide instance
scope and four canonical table digests across builds.

## Layout and build commands

```text
<refroot>/te_mm39/
  .staging/<unique>/
  archive/<BUILD_ID>/
    MANIFEST.json
    BUILD_ID
    CATALOG_ID
    source/
    tables/
    universes.json
    exports/
  current -> archive/<BUILD_ID>
```

The family is explicit in every publication command. The relative `current` symlink is the
single selector; an archive keeps its full identity path for its entire lifetime.

```bash
./build.sh --genome mm39 --build-dir /scratch/te_mm39/build
./build.sh --genome mm39 --root /scratch/refroot
./build.sh --genome mm39 --root /scratch/refroot --no-select
```

`--build-dir` runs the stages, writes the manifest and verifies the directory in place.
`--root` creates a unique family staging directory, runs those same steps, installs the archive
and selects it. `--no-select` completes installation and preserves the existing selection.
`TE_TRACKS_SOURCE_CACHE` supplies checksum-matching retained inputs. Container tests use a scratch
reference root. Host publication uses a writable destination reference root and compares against
the recorded Python, pandas, pyarrow and zlib versions; image identity is recorded when the
container exposes one.

## Manifest and identities

`MANIFEST.json` has two top-level sections. `identity` contains the manifest schema version,
family, species, assembly, declared FASTA pins and status, contig-byte digest, catalog, build sources,
complete universe definitions, taxonomy rule version, export contracts, parent identities and
sorted file inventory. Each inventory entry records a relative path, byte count and SHA-256;
all regular payload files, including retained sources, belong to that inventory. The three
identity files form the inventory's explicit self-reference exclusions. Paths are confined to
the build, and the payload consists of regular files and directories.

`identity.catalog.sources` holds `rmsk_out` alone, with its URL and observed MD5, SHA-256 and bytes.
The sibling `identity.build_sources` holds `rmsk_table`, `chromAlias` and `chrom_sizes` with the
same fields, binding these inputs to `BUILD_ID`.
`identity.catalog` also contains the declared
RepeatMasker version, library, run evidence and parser profile, `instance_id_scope: source_run`,
and the digests of `rmsk_records.parquet`, `rmsk_records.tsv.gz`, `rmsk_instance_members.tsv.gz`
and `rmsk_taxonomy.tsv`. One source-wide RepeatMasker run numbers the instances. A new export,
universe or taxonomy rule version changes build identity while an unchanged catalog keeps its
catalog identity. The core family has null `parent_build_id` and `parent_catalog_id`.

The 24 export contracts derive from the export writer's shared contract dictionary and job
roster, cross-checked against `tables/exports.tsv`: path, namespace, universe, variant, format,
feature level, identity field, attribute source mapping, consumer output keys, selectable levels
and coordinate convention. `consumer_keys` names each reader's key column and grammar for a file,
a fact of the file format that holds for every universe of that file, while tested routes per
universe live in the [OUTPUTS.md route table](OUTPUTS.md#consumer-contracts-phase-5).
`universes.schema_version` owns predicate grammar; adding a predicate
key requires a new version.

`provenance` records builder Git SHA and dirty status, invocation arguments, Python, pyarrow,
pandas and zlib versions, exposed devcontainer image evidence, UTC build time, source acquisition
locations, verifier results and measured export-writer peak RSS. Image evidence includes
`/etc/os-release` and available image metadata files, with the limits of that identification.
A standalone manifest invocation records RSS as null when the writer measurement is unavailable.

Both identities use this encoding, with zero terminal whitespace in the hashed bytes:

```python
canonical_bytes = lambda obj: json.dumps(
    obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False
).encode("utf-8")
BUILD_ID = hashlib.sha256(b"te-tracks-build-v1\n" + canonical_bytes(identity)).hexdigest()
CATALOG_ID = hashlib.sha256(b"te-tracks-catalog-v1\n" + canonical_bytes(identity["catalog"])).hexdigest()
```

The `BUILD_ID` and `CATALOG_ID` files contain their full lowercase hex digest and one final LF.
Duplicate JSON keys and nonfinite numbers fail verification. Provenance remains outside both
hashes, so identical builds can carry different raw manifests. Convergence retains the first
installed manifest and its producer evidence. Transfer preserves that manifest's exact bytes.

## Installation and selection

```bash
python3 src/90_manifest.py <build-dir> config/mm39.env
python3 src/99_verify.py <build-dir>
python3 src/release.py install --root <refroot> --family te_mm39 --staging <staging-dir> --select
python3 src/release.py select --root <refroot> --family te_mm39 --build-id <full-id>
python3 src/release.py verify-current --root <refroot> --family te_mm39
```

The verifier reads the complete inventory from disk, checks exact file-set equality, sizes and
hashes, recomputes both identities, validates the typed record schema, unique keys and contig
bounds, and compares observed record and export counts with their published tables. It leaves
build bytes and directories unchanged and uses memory for its working state.
It judges an archive against its own manifest and the published schema, taxonomy-rule and
predicate-grammar versions, recomputing `catalog.sources` for `rmsk_out` and `build_sources` for
`rmsk_table`, `chromAlias` and `chrom_sizes` from `source/SOURCES.json` and the inventory.

Installation verifies staging before acquiring an advisory lock on the `archive/` directory.
Cooperating publishers hold that lock across destination checks, `os.rename` and selection,
which guarantees installation preserves any occupied destination. An existing complete archive
with the same ID must verify before the redundant staging directory is removed and `converged`
is reported. Empty directories, symlinks and damaged archives abort installation with their path.

Publication uses `umask 002` and creates `archive/` with mode 2775. Payload files receive 0444
and nested directories 0555 before rename. The build root retains owner write permission for the
cross-parent rename and receives 0555 immediately afterwards, inside the installation lock and
before selection. Installed payloads retain those modes and bytes. Publishers own their private
staging trees exclusively until installation completes.

Selection verifies the candidate's directory name, `BUILD_ID` and manifest, and verifies an
existing `current` target before proceeding. A damaged selection stays in place with its
discrepancy reported for human repair. A relative `current.tmp.<pid>` symlink beside `current`
is atomically replaced onto the selector using `os.replace`. Concurrent identical installations
converge to one archive; concurrent selections of different valid builds leave the last successful
selection. This protocol requires one filesystem with POSIX rename and advisory-lock semantics;
it guarantees atomic visibility. Power-loss durability depends on the host filesystem.

## Transfer and recovery

Resolve the source `current` once and record its full ID and raw manifest SHA-256. Create a
fresh directory under the destination family's `.staging/`, copy the resolved archive contents
there, and compare the manifest's raw SHA-256 with the source pin. Run `99_verify.py` on that
staging directory, then run `release.py install` with the destination root and family.
An existing identical archive retains its first manifest on convergence; compare the installed
manifest checksum with the consumer pin before `release.py select`. Keep the source archive
and destination staging paths explicit in the copy command.
Required parent archives transfer and verify before selecting their child.
The publication checks leave interrupted transfer into staging, readers during selector replacement,
disk exhaustion during rename, staging on another filesystem and ACL access for consumers to host qualification.

An interrupted build or transfer leaves its staging directory for inspection. Remove abandoned
staging by hand after confirming that its builder or transfer process has exited. A complete
unselected archive is a valid state; verify it and select its full ID to finish publication.
A selector discrepancy requires a human decision after verifying a candidate independently and
preserving the damaged archive for diagnosis. A leftover `current.tmp.<pid>` can be removed after
confirming that publisher has exited.

## Consumer pins and retention

A consumer resolves `current` once and reads every input from that immutable archive. It pins
the full `BUILD_ID`, `CATALOG_ID`, raw `MANIFEST.json` SHA-256, relative export paths and their
SHA-256 digests, universe, feature level and required parent IDs. Record ledgers use
`(te_catalog_id, rmsk_record_id)` and retain `te_build_id` as provenance. Historical builds resolve
directly at `archive/<BUILD_ID>/` after newer selections.

Every installed build and its dependency closure stays on disk. Identical rebuilds converge;
retention planning reserves space for each distinct build at each reference root. Measured sums
of regular file sizes for mm39 exports are 3,021,714,346 bytes for `ucsc`, 2,926,266,953 for
`ensembl` and 3,021,140,740 for `gencode`. Registration occupies 347,526,106 bytes, and the
43-file payload totals 10,461,884,289 bytes. The `all_rmsk` record BED occupies 332,554,184 /
316,524,255 / 332,461,688 bytes in `ucsc` / `ensembl` / `gencode` respectively. The whole build
directory measures about 10.46 GB by `du -sb`, the provisioning size, with the exact total varying
by a few hundred bytes with the manifest's provenance. Reserve additional working space for
staging and sorting.
The export writer peaks near 6.0 GB resident, measured between 5.5 GB and 6.0 GB across
in-container builds; `provenance.peak_rss_bytes` records each build's own measurement.
