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

`./build.sh --genome mm39 --build-dir <dir>` runs the registered stages and writes four pinned
sources, `source/SOURCES.json` and `source/qualification.md`.
Set `TE_TRACKS_SOURCE_CACHE` to reuse checksum-matching cached sources; in-container builds use
a scratch directory, and host publication lands in phase 7.

Tests run in-container against a scratch reference root:

```bash
tests/run.sh core
tests/run.sh consumers
tests/run.sh acceptance --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
```

The default reference root is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`.
Each mode reports `pass`, `fail` or `unsupported` per check. Core checks cover parser fixtures
and the source qualification report at `<refroot>/te_mm39/build/source/qualification.md`.

## Outputs

Published legacy releases in the reference cache carry `te_loci.tsv.gz`, `te_dim.tsv`,
`MANIFEST.json` and `BUILD_ID`; the current build produces the source layer under `source/`, and
the redesign phases supply the remaining artifacts.

The truth table tracks the redesign artifacts: `delivered` means generated, `tested` means
verified against their contract, and `deferred` names the phase that supplies them.
Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.

| artifact | status | phase |
|---|---|---|
| `source/{mm39.fa.out.gz,rmsk.txt.gz,mm39.chromAlias.txt,mm39.chrom.sizes,SOURCES.json}` | delivered, tested | 1 |
| `source/qualification.md` | delivered, tested | 1 |
| `docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md` | delivered, tested | 1 |
| `tests/fixtures/source/` | delivered, tested | 1 |
| `tests/fixtures/records/` | deferred | 2 |
| `tests/expectations/mm39/` | deferred | 2, 9 |
| `tests/fixtures/taxonomy/dfam_snapshot.tsv` | deferred | 3 |
| `tests/fixtures/taxonomy/dfam_snapshot.provenance.json` | deferred | 3 |
| `tests/fixtures/taxonomy/rule_cases.tsv` | deferred | 3 |
| `tests/fixtures/exports/` | deferred | 4 |
| `tests/fixtures/consumers/` | deferred | 5 |
| `tests/lib/consumers.py` | deferred | 5 |
| `tests/fixtures/contigs/` | deferred | 6 |
| `tests/fixtures/publication/` | deferred | 7 |
| `tables/rmsk_records.tsv.gz` | deferred | 2 |
| `tables/rmsk_records.parquet` | deferred | 2 |
| `tables/rmsk_instance_members.tsv.gz` | deferred | 2 |
| `tables/rmsk_taxonomy.tsv` | deferred | 2 |
| `tables/taxonomy_canonical.tsv` | deferred | 3 |
| `tables/taxonomy_resolution_report.tsv` | deferred | 3 |
| `universes.json` | deferred | 2 |
| `tables/universe_members.tsv.gz` | deferred | 2 |
| `tables/universe_summary.tsv` | deferred | 2 |
| `tables/export_feature_members.tsv.gz` | deferred | 4 |
| `tables/export_summary.tsv` | deferred | 4 |
| `tables/contig_aliases.tsv` | deferred | 6 |
| `tables/contig_coverage.tsv` | deferred | 6 |
| `exports/ucsc/interspersed/full/record.bed` | deferred | 4 |
| `exports/ucsc/interspersed/full/subfamily.bed` | deferred | 4 |
| `exports/ucsc/interspersed/full/family.bed` | deferred | 4 |
| `exports/ucsc/interspersed/full/record.gtf` | deferred | 4 |
| `exports/ucsc/interspersed/full/subfamily.saf` | deferred | 4 |
| `exports/ucsc/interspersed/full/taxonomy_triple.saf` | deferred | 4 |
| `exports/ensembl/interspersed/full/record.bed` | deferred | 6 |
| `exports/ensembl/interspersed/full/subfamily.bed` | deferred | 6 |
| `exports/ensembl/interspersed/full/family.bed` | deferred | 6 |
| `exports/ensembl/interspersed/full/record.gtf` | deferred | 6 |
| `exports/ensembl/interspersed/full/subfamily.saf` | deferred | 6 |
| `exports/ensembl/interspersed/full/taxonomy_triple.saf` | deferred | 6 |
| `exports/gencode/interspersed/full/record.bed` | deferred | 6 |
| `exports/gencode/interspersed/full/subfamily.bed` | deferred | 6 |
| `exports/gencode/interspersed/full/family.bed` | deferred | 6 |
| `exports/gencode/interspersed/full/record.gtf` | deferred | 6 |
| `exports/gencode/interspersed/full/subfamily.saf` | deferred | 6 |
| `exports/gencode/interspersed/full/taxonomy_triple.saf` | deferred | 6 |
| `te_mm39_gene`: `exports/ucsc/interspersed/exon_subtracted/subfamily.saf` | deferred | 8 |
| `te_mm39_gene`: `exports/ensembl/interspersed/exon_subtracted/subfamily.saf` | deferred | 8 |
| `te_mm39_gene`: `exports/gencode/interspersed/exon_subtracted/subfamily.saf` | deferred | 8 |
| `te_mm39_gene`: `exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/taxonomy_triple.saf` | deferred | 8 |
| `te_mm39_gene`: `tables/exon_subtraction_status.tsv` | deferred | 8 |
| `MANIFEST.json` | deferred | 7 |
| `BUILD_ID` | deferred | 7 |
| `bin/te-tracks-preflight` | deferred | 6 |
| `docs/RUNBOOK.md` | deferred | 9 |
| `docs/RELEASES.md` | deferred | 7 |

[docs/OUTPUTS.md](docs/OUTPUTS.md) describes the legacy columns and deferred export contracts.

## Guarantees

The redesign contract establishes these guarantees as the listed phases land:

- Four feature levels describe record, instance, subfamily and canonical family. Family and
  class rollups use `taxonomy_canonical`.
- Universes are named predicates over raw source classification in the complete catalog;
  `interspersed` is the default.
- `rmsk_record_id` is `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`. Export membership
  registers each emitted feature and interval block to its source records.
- The `interspersed` full-interval exports contain six files in each of `ucsc`, `ensembl` and
  `gencode`: BED at record, subfamily and family level; GTF at record level; SAF at subfamily
  level and at the legacy taxonomy-triple grouping.
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

mm39 is built in the legacy layout. Its redesign artifacts follow the phases above. hg38 is
deferred; source pins, a class census and packaged-file reconciliation follow the mm39 release.

## Design

[docs/DECISIONS.md](docs/DECISIONS.md) records the redesign choices and recorded deferrals.
[docs/PROVENANCE.md](docs/PROVENANCE.md) retains the legacy derivation and comparison evidence.
