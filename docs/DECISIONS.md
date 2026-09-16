# Decisions

## 1. Feature identity and taxonomy

A subfamily is the set of records carrying one RepeatMasker `repName` within a pinned build.
The canonical tables publish four feature levels—record, instance, subfamily and canonical
family—and every quantification records its assigned and reported levels.
Each record keeps its exact source class and family; `taxonomy_canonical` supplies one row per
name through a versioned deterministic rule with rank-specific statuses, checked against a pinned
Dfam snapshot in the test suite.
Family and class rollups read only that table.

## 2. Universes

A universe is a named predicate over raw source classification selecting records from the complete
catalog, defined in `universes.json`.
The build defines `all_rmsk`, `interspersed` as the default, `interspersed_plus_satellites`,
`retrotransposon_derived`, `satellites` and `compat_tetranscripts_mm39`.
`interspersed` keeps the tRNA-ancestry SINE families and carries Unknown, Unspecified and `DNA?`
records as flagged provisional members.
Each new assembly passes a class census before any biological universe publishes.

## 3. Delivered scope

The parked mm39 release contains the canonical tables, instance membership, raw and canonical
taxonomy, universe definitions, and the `interspersed` full-interval exports: BED at record,
subfamily and family level, GTF at record level, SAF at subfamily level and at the legacy
taxonomy-triple grouping, each in the `ucsc`, `ensembl` and `gencode` contig namespaces, with an
alias table and a coverage report.
Every export ships with a known-answer consumer fixture, a local test runner, a preflight command,
a host-build runbook and `AGENTS.md`.
Additional adapters enter a release together with a named consumer and a passing fixture.

## 4. Gene-dependent views

Gene-dependent views form a child build family `te_<assembly>_gene` that pins its parent core build
and one gene annotation.
The first child view is the exon-subtracted SAF: subtraction of the unstranded union of all
annotated exons, with every retained piece registered to its record.
The record-by-transcript context relation follows in its own design session.
Exon subtraction guarantees exon-disjoint sequence support under the declared mask; molecule
exclusivity between gene and TE counts is a property of the joint counting run.

## 5. Namespace

Source-derived tables carry the `rmsk_` qualifier: `rmsk_records`, `rmsk_instance_members` and
`rmsk_taxonomy`.
Derived artifacts carry plain names: `taxonomy_canonical`, `export_feature_members` and
`universes.json`.
Coordinate columns state their convention as `start_1` and `end_1`; exports follow
`exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`, with
`full` and `exon_subtracted` as variants.
Consuming projects keep their quantification ledger in their own tables,
`peak_record_overlaps` and `te_feature_registration`, keyed to `rmsk_records`, with
`feature_level` as the measurement grain column.

## 6. Source

The primary source is the checksum-pinned RepeatMasker `.out` for the assembly, parsed under a
declared format profile that keeps raw strand, raw class/family token, consensus coordinates and
the overlap flag.
The manifest records the assembly, contig set and declared RepeatMasker software and library
identity with their evidence.
The UCSC browser table is compared once at source qualification and the report is retained.

## 7. Build identity and publication

`BUILD_ID` is the SHA-256 of the manifest's `identity` section: schema version, sources, declared
run identity, universe predicates, export contracts and the complete file inventory.
Builder commit and validation evidence live in the `provenance` section outside the hash.
A build completes and verifies in staging, installs once into `archive/<BUILD_ID>/`, and becomes
selected by an atomic replacement of the single `current` symlink.
Every published build stays on disk, and consumers pin the full id and the digests of the files
they read.

## 8. Wording

Each decision states the chosen behaviour and its reason in two to four brief affirmative
sentences.
Contracts and test evidence live in [OUTPUTS.md](OUTPUTS.md), [RELEASES.md](RELEASES.md) and
[PROVENANCE.md](PROVENANCE.md).
Deferred work names the evidence its next decision needs.

## Recorded deferrals

- Young versus old tiers: `divergence_pct` per record lands in phase 2; per-subfamily median
  divergence lands with the phase 3 taxonomy table; curated evolutionary ages and full-length or
  ORF status wait for a structural stage.
- ERV units: the instance relation and consensus coordinates are prerequisites; validated
  LTR-internal membership defines the unit later.
- hg38: source pins and packaged-file reconciliation follow parking, using the shared schema,
  class-census gate and config shape.
- Transcript context: a dedicated design session follows the
  [phase 8 gene child seam](_internal/_project/plans/2026-09-16_te-tracks-redesign/18_phase8_gene_child_seam.md).
