# Releases

A core release binds one RepeatMasker catalog and its registered exports to `BUILD_ID`.
`CATALOG_ID` binds the record-producing RepeatMasker `.out`, run identity, source-wide instance
scope and decompressed canonical text tables across builds.

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
complete universe definitions, taxonomy rule and rank scheme versions, export contracts, parent identities and
sorted file inventory. Each inventory entry records a relative path, byte count and SHA-256;
all regular payload files, including retained sources, belong to that inventory. The three
identity files form the inventory's explicit self-reference exclusions. Paths are confined to
the build, and the payload consists of regular files and directories.

`identity.catalog.sources` holds `rmsk_out` alone, with its URL and observed MD5, SHA-256 and bytes.
The sibling `identity.build_sources` holds all four fetched roles with the same fields,
plus `dfam_snapshot` with its package-relative `path`, SHA-256, bytes, `dfam_version`
and provenance `fetch_finished`. The tracked snapshot, retained provenance JSON and four Dfam tables bind
to `BUILD_ID`. The verifier compares the fetch timestamp, Dfam version and payload digest
with the retained provenance when the archive retains that file. Earlier archives retain
their declared source layout and verify against their own source and payload roster.

The verifier detects corruption and accidental drift in an archive judged against its own
declaration. A consumer protects against a deliberately edited archive by pinning the full
`BUILD_ID` and the digests of the files it reads. Every archive this builder writes retains
the provenance unconditionally.

`identity.catalog` also contains the declared
RepeatMasker version, library, run evidence and parser profile, `instance_id_scope: source_run`,
and `tables`, a mapping from logical names `rmsk_records.tsv`, `rmsk_instance_members.tsv`
and `rmsk_taxonomy.tsv` to SHA-256 digests of their decompressed text bytes.
The first two tables are stored as gzip files; `rmsk_taxonomy.tsv` is plain text.
Parquet and compressed file bytes remain bound through the inventory to `BUILD_ID`, so a
serializer or compressor change moves `BUILD_ID` alone. One source-wide RepeatMasker run
numbers the instances. A new export, universe or taxonomy rule version changes build identity
while an unchanged catalog keeps its catalog identity. The core family has null `parent_build_id` and `parent_catalog_id`.

The 27 export contracts derive from the export writer's shared contract dictionary and job
roster, cross-checked against `tables/exports.tsv`: path, namespace, universe, variant, format,
feature level, identity field, attribute source mapping, selectable levels and coordinate convention.
Reader key columns and grammars are documented in [OUTPUTS.md](OUTPUTS.md#consumer-contracts)
and asserted by the consumer checks against the exporter's contract table; the identity binds
what bytes and semantics depend on.
`universes.schema_version` owns predicate grammar; adding a predicate
key requires a new version.

`provenance` records builder Git SHA and dirty status, invocation arguments, Python, pyarrow,
pandas and zlib versions, exposed devcontainer image evidence, UTC build time, source acquisition
locations, verifier results and measured export-writer peak RSS. Image evidence includes
`/etc/os-release` and available image metadata files, with the limits of that identification.
A standalone manifest invocation records RSS as null when the writer measurement is unavailable.

Both identities use this encoding, with zero terminal whitespace in the hashed bytes;
`CATALOG_ID` binds the RepeatMasker source, run identity, source-wide instance scope and
decompressed canonical text tables:

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
It judges taxonomy rule versions, predicate schemas and each schema's predicate keys against
published sets, and export contract fields against a required core that declarations may extend.
The manifest schema version stays single-valued; a new schema adds a verifier branch.
The feature-level tuple only grows; renaming a level is a contract break.
The verifier recomputes `catalog.sources` for `rmsk_out` and each declared `build_sources`
role from `source/SOURCES.json` and the inventory, and streams the decompressed canonical
text tables to verify `catalog.tables`.

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

Resolve the source `current` once and record its full ID and raw `MANIFEST.json` SHA-256 as the
transfer-integrity check. Create a fresh directory under the destination family's `.staging/`,
copy the resolved archive contents there, and compare the manifest's raw SHA-256 with the source pin. Run `99_verify.py` on that
staging directory, then run `release.py install` with the destination root and family.
An existing identical archive retains its first manifest on convergence; compare the installed
manifest checksum with the transfer pin before `release.py select`. Keep the source archive
and destination staging paths explicit in the copy command.
Parent archives transfer and verify before their children are installed or selected.
The publication checks leave interrupted transfer into staging, readers during selector replacement,
disk exhaustion during rename, staging on another filesystem and ACL access for consumers to host qualification.

Host publication requires clean builder provenance and a fresh complete build in private family
staging, followed by installation and explicit selection. An interrupted staging directory is for inspection and removal before republication.
After confirming that the builder or transfer process has exited, the owner restores write access
on the abandoned staging directories and removes staging with `shutil.rmtree`. A missing `MANIFEST.json`
or truncated table causes a named install refusal and leaves `current` unchanged;
check 72 exercises the failed-build staging and owner removal. A complete
unselected archive is a valid state; verify it and select its full ID to finish publication.
A selector discrepancy requires a human decision after verifying a candidate independently and
preserving the damaged archive for diagnosis. A leftover `current.tmp.<pid>` can be removed after
confirming that publisher has exited.

## Consumer pins and retention

A consumer resolves `current` once and reads every input from that immutable archive. It pins
the full `BUILD_ID`, `CATALOG_ID`, relative export paths and their SHA-256 digests, universe,
feature level and required parent IDs. Record ledgers use
`(te_catalog_id, rmsk_record_id)` and retain `te_build_id` as provenance. Historical builds resolve
directly at `archive/<BUILD_ID>/` after newer selections.

Every installed build and its dependency closure stays on disk. Every build a consumer pins is
retained beside `current`, including after a later selection. Identical rebuilds converge;
retention planning reserves space for each distinct build at each reference root. Measured sums
of regular file sizes for mm39 exports are 4,638,043,480 bytes for `ucsc`,
4,531,250,735 for `ensembl` and 4,637,401,144 for `gencode`. Registration occupies
347,526,106 bytes. The 52-file payload totals 15,301,538,537 bytes; the complete
acceptance core retains 15,301,581,825 regular-file bytes including its manifest and IDs,
about 15.30 GB.
Manifest provenance and filesystem directory sizes contribute to the whole-build total.
The `all_rmsk` record BED occupies 332,554,184 / 316,524,255 / 332,461,688 bytes
in `ucsc` / `ensembl` / `gencode` respectively.

| Addition | Measured bytes |
|---|---:|
| `exports/ucsc/interspersed/full/record_starsolo.gtf` | 1,616,329,134 |
| `exports/ensembl/interspersed/full/record_starsolo.gtf` | 1,604,983,782 |
| `exports/gencode/interspersed/full/record_starsolo.gtf` | 1,616,260,404 |
| `tables/taxonomy_dfam.tsv` | 780,296 |
| `tables/taxonomy_dfam_models.tsv` | 577,712 |
| `tables/dfam_lineage_nodes.tsv` | 75,154 |
| `tables/dfam_model_clades.tsv` | 367,180 |
| `source/dfam_interspersed_mm39_snapshot.json.gz` | 278,952 |
| `source/dfam_interspersed_mm39_snapshot.provenance.json` | 921 |

Reserve additional working space for staging and sorting. The export writer previously measured
5.5 GB to 6.0 GB resident across in-container builds, including 5,994,254,336 bytes.
The acceptance export writer measured 4,936,556,544 resident bytes, retained in the
acceptance core manifest’s `provenance.peak_rss_bytes`. The initial export observation is
recorded in the [resource rulings](_internal/redesign-2026-09/reviews/m9_rulings.md#observations-that-lost-their-carrier).
An earlier complete core rebuild peaked at 9,026,424,832 resident bytes and took 717.201 seconds.
The final acceptance child's subtraction stage measured 881,565,696 resident bytes and
154.376 seconds, retained in its manifest’s stage metrics. The initial child observations
are recorded in the [resource rulings](_internal/redesign-2026-09/reviews/m9_rulings.md#observations-that-lost-their-carrier).
The child payload adds 2,157,717,760 bytes, for 17,459,256,297 payload bytes per retained pair.
[RUNBOOK.md](RUNBOOK.md#resource-floors-and-consumer-pins) records these producer floors and the
measured consumer annotation-load floors.

## Gene child snapshots

Build the parent core first, then supply its full ID to the gene family:

```bash
./build.sh --genome mm39 --family gene --root <refroot> --parent-build-id <full-parent-id>
./build.sh --genome mm39 --family gene --build-dir <child-dir> --parent-dir <core-build-dir>
python3 src/99_verify.py <child-dir> --parent-dir <core-build-dir>
python3 src/release.py verify-current --root <refroot> --family te_mm39_gene
```

`--family gene` selects `config/mm39_gene.env` and the stages under `src/gene/`.
`--parent-dir` and `--parent-build-id` are exclusive; scratch builds require the directory,
and publication requires the full lowercase hexadecimal ID. Parent arguments name explicit
builds, with the lexical path judged after stripping trailing slashes and before symlink resolution.
Resolve a selected parent through `release.py verify-current` as shown in the runbook.
The builder verifies the parent before any child stage reads it and checks its family and assembly.

The child retains schema `te-tracks-manifest-1` with non-null `parent_build_id` and
`parent_catalog_id`, plus `parent_family`, `copied_inputs`, `gene_annotation`, `policy_bundle`
and `child_universes`. It inherits the parent's catalog, species, assembly, declared assembly,
contig digest, universes and taxonomy rule. Its `CATALOG_ID` bytes equal the parent's.
`build_sources` contains `gene_gtf` alone. `gene_annotation` binds name, URL, MD5, SHA-256 and
bytes; `policy_bundle` binds the mask identifier and definition, minimum retained block and
context capability. Each change to an annotation digest, policy value, export roster or parent
pin changes the child `BUILD_ID`. Parent identity stays fixed.

Child verification resolves the parent through `--parent-dir`, `--root`, or the sibling archive
under the root enclosing a `.staging` or `archive` build. A scratch child needs an explicit
parent location. Verification checks the parent's complete build, inherited catalog, copied-input
digests, every registration and status row against the parent and mask, SAF row counts, content and order against
registration and annotation coverage against the retained GTF.

`install`, `select` and `verify-current` require the pinned parent archive present and verified
under the same root. Earlier core archives remain selectable after a child is published.
Transfer the parent dependency first; then transfer, verify and install the child under
`te_mm39_gene`. Child provenance records each stage's wall time and maximum resident bytes
through `RUSAGE_CHILDREN`.


## Acceptance witness

The acceptance build publishes into
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/acceptance/` and retains the six earlier
development archives under `refroot/pubroot/`. Its independent census anchors precede the
comparison with `refroot/te_mm39/build` and `refroot/te_mm39_gene/build`.

| Family | Acceptance BUILD_ID | CATALOG_ID |
|---|---|---|
| `te_mm39` | `5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813` | `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` |
| `te_mm39_gene` | `198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1` | `90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` |

Every table's SHA-256 and both IDs agree exactly with the development builds for both families. The check performs that comparison whenever the development build is present.
A `CATALOG_ID` difference stops for investigation. With an equal `CATALOG_ID` and differing
`BUILD_ID`, compare the recorded toolchain and payload and publish the host build with this
in-container build recorded as its content witness. The in-container acceptance manifests record
revision `51c016243c8991b27f0da112a00d90a815ead929` with `builder_git_dirty: true`.
That revision follows the prompt's `d28336f` through documentation-only commits; the source
and configuration bytes retain the qualified core identities. The owner's clean host build supplies
the production provenance.

The host publisher tightens each family root to 0755 and `archive/` to 2755, with effective ACLs
matching owner-only write. The named backup target is the verified CRI mirror at
`/gpfs/data/rathmell-lab/data/refdata`, transferred parent first through fresh staging and
`release.py install`. The host gate records the image ID, complete-build resources, clean
revision, both family verifications, backup verification and filesystem/ACL qualification.
