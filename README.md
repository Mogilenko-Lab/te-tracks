# te-tracks

te-tracks builds a reference projection of RepeatMasker for one assembly. Canonical tables,
named universes, registered exports and consumer fixtures share record identities and source
provenance. The redesign contract below lands in phases 1–9.

## Sources

| Source | Role in the redesign |
|---|---|
| Checksum-pinned RepeatMasker `.out` | Primary records, instance keys, source labels, consensus coordinates and overlap flags |
| UCSC browser `rmsk` table | One-time source qualification against the `.out`, with a retained report |
| UCSC `chromAlias` | Contig mappings across UCSC, Ensembl, GenBank and RefSeq namespaces |
| UCSC `chrom.sizes` | Contig lengths and coordinate bounds |

The gene GTF belongs to the child family `te_<assembly>_gene`, which pins its parent core build
and one gene annotation.

## Build

`./build.sh --genome mm39 --build-dir <dir>` runs the registered stages, writes
`MANIFEST.json`, `BUILD_ID` and `CATALOG_ID`, and verifies the completed directory in place.
`./build.sh --genome mm39 --root <refroot>` builds in a unique staging directory, verifies,
installs at `te_mm39/archive/<BUILD_ID>/` and selects the relative `current` symlink.
Add `--no-select` to install while preserving the existing selection.
`BUILD_ID` identifies the complete build; `CATALOG_ID` binds the record-producing RepeatMasker
`.out`, run identity, source-wide instance scope and decompressed canonical text tables for consumer
ledger keys, so a serializer or compressor change moves `BUILD_ID` alone.
[docs/RELEASES.md](docs/RELEASES.md) describes publication and transfer.
Set `TE_TRACKS_SOURCE_CACHE` to reuse checksum-matching cached sources; in-container builds use
a scratch directory, and host builds compare the recorded toolchain versions.

Tests run in-container against a scratch reference root:

```bash
tests/run.sh core
tests/run.sh consumers
tests/run.sh acceptance --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
```

The default reference root is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`.
Each mode reports `pass`, `fail` or `unsupported` per check. Core checks cover the parser fixtures,
the qualification report, the record schema, instances, universes, the record fixtures,
taxonomy (30 to 32), exports (40 to 42), contigs (60 to 62) and identity and publication (70 to 72).

## Outputs

Each build contains `source/`, `tables/`, `universes.json`, `exports/`, `MANIFEST.json`,
`BUILD_ID` and `CATALOG_ID`. Publication installs that directory under `archive/<BUILD_ID>/`
and selects it through the relative `current` symlink.

The truth table tracks the redesign artifacts: `delivered` means generated, `tested` means
verified against their contract, and `deferred` names the phase that supplies them.
Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.

| artifact | status | phase |
|---|---|---|
| `source/{mm39.fa.out.gz,rmsk.txt.gz,mm39.chromAlias.txt,mm39.chrom.sizes,SOURCES.json}` | delivered, tested | 1 |
| `source/qualification.md` | delivered, tested | 1 |
| `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` | delivered, tested | 1 |
| `tests/fixtures/source/` | delivered, tested | 1 |
| `tests/fixtures/records/` | delivered, tested | 2 |
| `tests/expectations/mm39/` | delivered, tested | 2 |
| `tests/expectations/mm39/taxonomy_census.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/dfam_snapshot.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/dfam_snapshot.provenance.json` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/rule_cases.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/rollup_counts.tsv` | delivered, tested | 3 |
| `tests/fixtures/taxonomy/weighting_context.tsv` | delivered, tested | 3 |
| `tests/fixtures/exports/` | delivered, tested | 4 |
| `tests/fixtures/consumers/` | tested: IRescue identity, TEsingle, TEtranscripts and TElocal parsers; MATES adapter supported in isolation, installed package needs `pkg_resources` (setuptools below 82); Stellarscope parser exercised, unsupported on observed `0,1,1,1` right-boundary defect (expected `0,1,1,0`); IRescue `chrcat` unsupported (`gawk` absent); bedtools and samtools supported; executables `irescue`, `featureCounts`, `stellarscope`, `TEsingle`, `TEcount`, `TElocal` absent; DuckDB query unsupported (`duckdb` absent); `00_tool_inventory.required.py` reporting-only | 5 |
| `tests/lib/consumers.py` | delivered, tested | 5 |
| `tests/lib/records.py` | delivered, tested | 2 |
| `tests/fixtures/contigs/` | delivered, tested | 6 |
| `tests/fixtures/publication/` | delivered, tested | 7 |
| `tables/rmsk_records.tsv.gz` | delivered, tested | 2 |
| `tables/rmsk_records.parquet` | delivered, tested | 2 |
| `tables/rmsk_instance_members.tsv.gz` | delivered, tested | 2 |
| `tables/rmsk_taxonomy.tsv` | delivered, tested | 2 |
| `tables/taxonomy_canonical.tsv` | delivered, tested | 3 |
| `tables/taxonomy_resolution_report.tsv` | delivered, tested | 3 |
| `universes.json` | delivered, tested | 2 |
| `tables/universe_members.tsv.gz` | delivered, tested | 2 |
| `tables/universe_summary.tsv` | delivered, tested | 2 |
| `tables/export_feature_members.tsv.gz` | delivered, tested | 4 |
| `tables/exports.tsv` | delivered, tested | 4 |
| `tables/contig_aliases.tsv` | delivered, tested | 6 |
| `tables/contig_coverage.tsv` | delivered, tested | 6 |
| `exports/ucsc/interspersed/full/record.bed` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/subfamily.bed` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/family.bed` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/record.gtf` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/subfamily.gtf` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/subfamily.saf` | delivered, tested | 4 |
| `exports/ucsc/interspersed/full/taxonomy_triple.saf` | delivered, tested | 4 |
| `exports/ensembl/interspersed/full/record.bed` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/subfamily.bed` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/family.bed` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/record.gtf` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/subfamily.gtf` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/subfamily.saf` | delivered, tested | 6 |
| `exports/ensembl/interspersed/full/taxonomy_triple.saf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/record.bed` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/subfamily.bed` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/family.bed` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/record.gtf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/subfamily.gtf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/subfamily.saf` | delivered, tested | 6 |
| `exports/gencode/interspersed/full/taxonomy_triple.saf` | delivered, tested | 6 |
| `exports/ucsc/all_rmsk/full/record.bed` | delivered, tested | 6 |
| `exports/ensembl/all_rmsk/full/record.bed` | delivered, tested | 6 |
| `exports/gencode/all_rmsk/full/record.bed` | delivered, tested | 6 |
| `te_mm39_gene`: `exports/ucsc/interspersed/exon_subtracted/subfamily.saf` | deferred | 8 |
| `te_mm39_gene`: `exports/ensembl/interspersed/exon_subtracted/subfamily.saf` | deferred | 8 |
| `te_mm39_gene`: `exports/gencode/interspersed/exon_subtracted/subfamily.saf` | deferred | 8 |
| `te_mm39_gene`: `exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/taxonomy_triple.saf` | deferred | 8 |
| `te_mm39_gene`: `tables/exon_subtraction_status.tsv` | deferred | 8 |
| `MANIFEST.json` | delivered, tested | 7 |
| `BUILD_ID` | delivered, tested | 7 |
| `CATALOG_ID` | delivered, tested | 7 |
| `bin/te-tracks-preflight` | delivered, tested | 6 |
| `docs/RUNBOOK.md` | deferred | 9 |
| `docs/RELEASES.md` | delivered, tested | 7 |

[docs/OUTPUTS.md](docs/OUTPUTS.md) specifies the schemas, serialization and deferred export contracts.

## Guarantees

The redesign contract establishes these guarantees as the listed phases land:

- Four feature levels describe record, instance, subfamily and canonical family. Family and
  class rollups use `taxonomy_canonical`.
- Universes are named predicates over raw source classification in the complete catalog;
  `interspersed` is the default.
- `rmsk_record_id` is `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`. Export membership
  registers each emitted feature and interval block to its source records.
- The `interspersed` full-interval exports contain seven files in each of `ucsc`, `ensembl` and
  `gencode`: `record.bed`, `subfamily.bed`, `family.bed`, `record.gtf`, `subfamily.gtf`,
  `subfamily.saf` and `taxonomy_triple.saf`.
- Tables, GTF and SAF use 1-based inclusive coordinates; BED uses 0-based half-open coordinates.
  Contig aliases preserve record identity across `ucsc`, `ensembl` and `gencode` exports.
- Exon subtraction guarantees exon-disjoint sequence support under the declared mask;
  molecule exclusivity between gene and TE counts is a property of the joint counting run.
- `BUILD_ID` is the SHA-256 of the manifest `identity` section, computed as
  `sha256("te-tracks-build-v1\n" + canonical_json(identity))`. The identity covers the schema,
  sources, declared run identity, universe predicates, export contracts and complete file
  inventory; builder and validation evidence live in `provenance` outside the hash.
- Builds complete and verify in staging, install once into `archive/<BUILD_ID>/`, and become
  selected by an atomic replacement of the single `current` symlink. Every published build stays
  on disk; consumers pin the full id and the digests of the files they read.
- Scripts use `LC_ALL=C` for stable sort order.

## Genomes

mm39 builds and publishes through `build.sh --genome mm39 --root <refroot>`; admitting a genome
config requires its `SPECIES` entry in `src/lib/manifest.py`. hg38 is deferred pending source pins,
a class census, packaged-file reconciliation and source-wide instance numbering or a contig-scoped instance key.

## Design

[docs/DECISIONS.md](docs/DECISIONS.md) records the redesign choices and recorded deferrals.
[docs/PROVENANCE.md](docs/PROVENANCE.md) retains the legacy derivation and comparison evidence.
