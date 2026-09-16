# Outputs

Canonical tables, GTF and SAF use **1-based inclusive** coordinates. BED uses **0-based
half-open** coordinates: `[start_1 - 1, end_1)`. Record lengths sum `end_1 - start_1 + 1`,
with overlaps retained.

## Canonical records and universes (phase 2)

The build writes the complete source catalog under `tables/` and six executable universe
definitions in `universes.json`. The default universe is `interspersed`.

### `tables/rmsk_records.tsv.gz` and `tables/rmsk_records.parquet`

Each row represents one primary RepeatMasker annotation. The 24 required columns appear in
this order; `text` is Arrow UTF-8, and every column has a value.

| Column | Type | Contract |
|---|---|---|
| `rmsk_record_id` | text | Unique constructed key `<rmsk_name>\|<chrom>:<start_1>-<end_1>\|<strand>` within the build. |
| `chrom` | text | Source contig name matched to the pinned sequence dictionary. |
| `start_1` | int64 | Genomic start, 1-based inclusive. |
| `end_1` | int64 | Genomic end, inclusive and bounded by the contig length. |
| `strand` | text | `+` or `-`, with source `C` mapped to `-`. |
| `rmsk_name` | text | Exact source repeat name, preserving case and punctuation. |
| `rmsk_family` | text | Exact matched UCSC `repFamily`, verified against the parsed source label. |
| `rmsk_class` | text | Exact matched UCSC `repClass`, verified against the parsed source label. |
| `rmsk_instance_id` | text | Complete primary `.out` grouping token, preserving leading zeros. |
| `sw_score` | int64 | Source Smith–Waterman score. |
| `divergence_pct` | float64 | Source percent divergence; `6.7` denotes 6.7 percent. |
| `deletion_pct` | float64 | Source percent deletion. |
| `insertion_pct` | float64 | Source percent insertion. |
| `length_bp` | int64 | Genomic record length, `end_1 - start_1 + 1`. |
| `consensus_start_1` | int64 | Signed forward-model start, 1-based, with reverse-strand field order normalized. |
| `consensus_end_1` | int64 | Signed forward-model end, inclusive. |
| `consensus_left_bp` | int64 | Signed remaining model length; negative values retain alignments past the consensus end. |
| `query_left_bp` | int64 | Nonnegative remaining query length from the parenthesized source token. |
| `rmsk_overlap_flag` | bool | Presence of the source trailing `*` marker. |
| `rmsk_class_family` | text | Exact `.out` class/family token, including class-only spelling. |
| `ucsc_rep_start` | int64 | Raw signed UCSC `repStart`, retaining its strand-dependent encoding. |
| `ucsc_rep_end` | int64 | Raw signed UCSC `repEnd`. |
| `ucsc_rep_left` | int64 | Raw signed UCSC `repLeft`. |
| `source_row_number` | int64 | One-based ordinal among primary `.out` annotation rows before sorting. |

Consensus start and end follow the source; two mm39 records carry start above end
(`L1MdFanc_II|chr1:9847889-9847905|-`, `L1MdF_III|chr2:116363011-116363342|-`), so a derived
consensus-match length is signed.

Rows sort by `(chrom, start_1, end_1, strand, rmsk_name)` with C-locale text order. Source
and UCSC rows join one-to-one on these five fields. Class-only `.out` tokens project the
class into both raw taxonomy fields under the qualified UCSC convention.

Record components remain authoritative for computation. Names and contig names are free of
`|`, `:` and whitespace, so each record key parses back into its
components. Genomic bounds satisfy `1 <= start_1 <= end_1 <= contig length`. Equal coordinates
with different names retain separate record identities; exact duplicate keys fail the build.

### `tables/rmsk_instance_members.tsv.gz`

Columns are `rmsk_instance_id` (text) and `rmsk_record_id` (text), sorted by both columns.
Every record has exactly one membership row. The `.out` token defines the instance, and all
members of an instance share one contig. Instance text sorts lexically, preserving leading zeros.

### `tables/rmsk_taxonomy.tsv`

Columns are `rmsk_name` (text), `rmsk_family` (text), `rmsk_class` (text), `record_count`
(int64) and `record_length_sum_bp` (int64). Each distinct source triple has one row, sorted by
name, family and class. The length sum retains overlapping records. A name may carry several
source labels; canonical rollups arrive in phase 3.

### `universes.json`

Schema version `1` defines `default_universe: "interspersed"` and a `universes` array. Each
entry contains `name`, a one-sentence `description`, `predicate` and `provisional_classes`.
The build evaluates the same predicate objects that it publishes.

`class_in` selects exact raw class labels. `family_prefix_excluded` applies a case-sensitive
prefix exclusion to raw family labels. Clauses within an object combine with AND; `{}` selects
every record.

| Universe | Predicate |
|---|---|
| `all_rmsk` | Every record. |
| `interspersed` | Class in SINE, LTR, LINE, DNA, RC, Retroposon, Unknown, Unspecified, DNA?. |
| `interspersed_plus_satellites` | Class in the `interspersed` classes plus Satellite. |
| `retrotransposon_derived` | Class in SINE, LTR, LINE, Retroposon. |
| `satellites` | Class equals Satellite. |
| `compat_tetranscripts_mm39` | `interspersed_plus_satellites` classes with the `tRNA` family-prefix exclusion. |

`interspersed` and `interspersed_plus_satellites` flag Unknown, Unspecified and DNA? members
as provisional. The other universes have empty `provisional_classes` arrays.
`config/<genome>.classes.tsv` has exactly two columns, `rmsk_class` and `disposition`, with one
row per class and dispositions from `interspersed`, `satellite`, `simple_repeat`, `low_complexity`
and `structural_rna`. The build requires the observed class set to equal the reviewed set,
the disposition `interspersed` to agree with the authored predicate class by class, the
disposition `satellite` to mark exactly `Satellite`, and every provisional class to be dispositioned
`interspersed`. Core checks compare measured counts with `tests/expectations/<genome>/class_census.tsv`.

The `compat_tetranscripts_mm39` universe ships as membership, and the legacy comparison is a
phase 9 reconciliation.

### `tables/universe_members.tsv.gz`

Columns are `universe_name` (text), `rmsk_record_id` (text) and `provisional` (bool), sorted
by universe and record key. Each selected record appears once per universe. Membership for
`all_rmsk` is implicit in the complete canonical table; the file contains the other five universes.

### `tables/universe_summary.tsv`

Columns are `universe_name` (text), `records` (int64), `names` (int64), `triples` (int64) and
`length_sum_bp` (int64), sorted by universe name. All six universes appear. `triples` counts
distinct raw `(rmsk_name, rmsk_family, rmsk_class)` labels; summed record lengths retain overlaps.

### Serialization

TSV files use UTF-8, LF endings, tabs and one header. Integers use decimal notation, floating
point values use a period decimal separator, and booleans use `true` and `false`. Text retains
case, literal `Unknown` and empty strings. Every phase 2 field is required; source values must
be free of embedded tabs and line endings. Readers supply explicit schemas, including text
instance IDs. The reserved null token for future nullable companion fields is `\N`.

Gzip files have `mtime=0` and an empty embedded filename. Parquet uses an explicit required
schema with int64, float64, bool and UTF-8 string types. Both record serializations load to equal
typed rows. Identical input produces byte-identical tables and universe definitions under the
same builder and serialization libraries.

## Published legacy release

Published legacy releases in the reference cache carry `te_loci.tsv.gz`, `te_dim.tsv`,
`MANIFEST.json` and `BUILD_ID`.

### `te_loci.tsv.gz` — legacy canonical table, 1-based

One row per locus admitted by the legacy class and family filters.

| # | Column | Note |
|---|---|---|
| 1 | `locus_id` | `<subfamily>\|<chrom>:<start>-<end>\|<strand>`, the legacy join key |
| 2 | `chrom` | UCSC names |
| 3 | `start` | 1-based inclusive |
| 4 | `end` | Inclusive |
| 5 | `strand` | `+` or `-` |
| 6 | `subfamily` | UCSC `repName` |
| 7 | `family` | UCSC `repFamily` |
| 8 | `class` | UCSC `repClass` |
| 9 | `sw_score` | RepeatMasker Smith-Waterman score |
| 10 | `perc_div` | Percent divergence from the consensus |
| 11 | `perc_del` | Percent deletion |
| 12 | `perc_ins` | Percent insertion |
| 13 | `rmsk_id` | UCSC `id`, a one-character value without fragment-linking meaning |
| 14 | `length_bp` | `end - start + 1` |
| 15 | `dup_index` | Per-subfamily ordinal for `subfamily_dupN` compatibility |

The RepeatMasker `.out` ID column is the instance key; `tables/rmsk_instance_members.tsv.gz`
records its membership.

### `te_dim.tsv` — legacy dimension table

Columns are `subfamily`, `family`, `class`, `n_loci` and `total_bp`. Each row summarizes one
source `(subfamily, family, class)` triple.

## Deferred

Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.
The core release supplies six `interspersed` full-interval exports in each of the `ucsc`,
`ensembl` and `gencode` contig namespaces. The gene child family supplies `exon_subtracted`
intervals in phase 8. Each emitted feature and block registers to source records through
`tables/export_feature_members.tsv.gz`.

### Legacy names and their disposition

| Legacy name | Disposition |
|---|---|
| `te_subfamily.saf` | `subfamily.saf` (phase 4) |
| `te_locus.saf` | A record-level SAF enters a release with a named consumer and a passing fixture ([ADR 3](DECISIONS.md#3-delivered-scope)); record-level counting reads `record.bed` or `record.gtf` |
| `te_subfamily.bed` | `subfamily.bed` (phase 4) |
| `te_locus.bed` | `record.bed` (phase 4) |
| `te_subfamily.gtf` | `subfamily.gtf` (phase 4) |
| `te_locus.gtf` | `record.gtf` (phase 4) |
| `te_locus.locInd` | `.locInd` index built from `record.gtf` by TElocal's own indexer (fixture, phase 5) |
| `te_subfamily_noExon.saf` | `exon_subtracted/subfamily.saf` in `te_mm39_gene` (phase 8) |
| `te_context_*.saf` | Deferred to the transcript-context design session after phase 8 |
| `locus_context.tsv` | Deferred to the transcript-context design session after phase 8 |
| `rename_map.tsv` | Superseded by `tables/taxonomy_canonical.tsv` (phase 3); the legacy selection is reproducible as the `compat_tetranscripts_mm39` membership |
| `te_loci.tsv.gz` | `tables/rmsk_records.tsv.gz` (phase 2) |
| `te_loci.parquet` | `tables/rmsk_records.parquet` (phase 2) |
| `te_dim.tsv` | `tables/rmsk_taxonomy.tsv` and `tables/universe_summary.tsv` (phase 2) |
| Legacy `MANIFEST.json` | `MANIFEST.json` with `identity` and `provenance` sections (phase 7) |
| Legacy `BUILD_ID` | `BUILD_ID` computed from the manifest `identity` section (phase 7) |
| `ensembl_named/` | `exports/ensembl/` (phase 6) |

### Phase 3: canonical taxonomy

`tables/taxonomy_canonical.tsv` supplies one row per name with canonical class and family,
rank-specific resolution statuses and median record divergence under `taxonomy_rule_v1`.
`tables/taxonomy_resolution_report.tsv` records names with multiple raw labels and the rule used.
Family and class rollups join through `taxonomy_canonical`; unresolved names enter an explicit
`unresolved` bucket, distinct from RepeatMasker's literal `Unknown`.

### Phase 4: UCSC full-interval exports

All six exports land under `exports/ucsc/interspersed/full/`.
Exports carry no provisional flag; the status is a class property recoverable by joining names to `rmsk_taxonomy`.

| File | Coordinates | Feature identity |
|---|---|---|
| `record.bed` | 0-based half-open | BED6 name = `rmsk_record_id` |
| `subfamily.bed` | 0-based half-open | BED6 name = `rmsk_name` |
| `family.bed` | 0-based half-open | BED6 name = `<canonical_class>/<canonical_family>` or `unresolved/<rmsk_name>` |
| `record.gtf` | 1-based inclusive | Exon rows; `gene_id` = `rmsk_name`; `transcript_id` and `locus` = record alias |
| `subfamily.saf` | 1-based inclusive | `GeneID` = `rmsk_name` |
| `taxonomy_triple.saf` | 1-based inclusive | Canonical taxonomy-triple grouping; `GeneID` = `<rmsk_name>:<canonical_family>:<canonical_class>` |

Canonical labels are a function of the name, so `taxonomy_triple.saf` carries one `GeneID` per
`rmsk_name`, and a name whose raw labels differ across records appears once, under its canonical
triple.

BED6 columns are `chrom`, `start`, `end`, `name`, `score` and `strand`;
`score = min(sw_score, 1000)`. The GTF record alias is
`R|mm39|<name>|<chrom>|<start_1>|<end_1>|<strand>`.
GTF `family_id` and `class_id` carry canonical labels, `rmsk_family` and `rmsk_class` carry raw
labels, and `instance_id` is `I|mm39|<id>`.

`tables/export_feature_members.tsv.gz` carries `export_path`, `feature_level`,
`emitted_feature_id`, `rmsk_record_id`, `block_start_1` and `block_end_1`.
Full-interval exports register one block per record.

### Phase 5: consumer fixtures

Known-answer parser and execution fixtures establish each consumer contract. Additional adapters
enter a release with a named consumer and a passing fixture.

### Phase 6: contig namespaces and qualification

The six full-interval exports also land under `exports/ensembl/interspersed/full/` and
`exports/gencode/interspersed/full/`. They carry the same rows as their UCSC counterparts,
with contig columns renamed through `tables/contig_aliases.tsv`.
Record ids retain their UCSC contig names. `tables/contig_coverage.tsv` reports per-contig record
coverage, alias availability and length agreement. `bin/te-tracks-preflight <export> <bam|fai|sizes>`
checks contig sets and lengths for the selected export against an alignment, a FASTA index or a
chrom.sizes file.

### Phase 7: identity and publication

`MANIFEST.json` separates build `identity` from builder and validation `provenance`.
`BUILD_ID = sha256("te-tracks-build-v1\n" + canonical_json(identity))` covers the identity,
including the complete file inventory with SHA-256 digests. Verified staging builds install
once into `archive/<BUILD_ID>/`; an atomic replacement selects the single `current` symlink.

### Phase 8: gene child family

`te_mm39_gene` pins its parent core build and a gene GTF. Its
`exports/{ucsc,ensembl,gencode}/interspersed/exon_subtracted/{subfamily,taxonomy_triple}.saf` subtract the unstranded union
of all annotated exons and register every retained piece in `tables/export_feature_members.tsv.gz`.
`tables/exon_subtraction_status.tsv` records `unchanged`, `trimmed`, `split` or `fully_subtracted`
status with retained and removed base counts per record.

Exon subtraction guarantees exon-disjoint sequence support under the declared mask; molecule
exclusivity between gene and TE counts is a property of the joint counting run.
The record-by-transcript context relation follows phase 8 in a dedicated design session covering
annotation choice, interval blocks, relative strand, promoter parameters and distance conventions.

### Phase 9: acceptance and host runbook

`docs/RUNBOOK.md` supplies the host build, verification, publication, transfer and recovery
procedure. Full mm39 acceptance verifies the published contracts and updates artifact status.
