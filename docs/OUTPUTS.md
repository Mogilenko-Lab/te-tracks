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

Rows sort by `(chrom, start_1, end_1, strand, rmsk_name)`, with text columns in C-locale byte
order and coordinate columns ascending numerically. Source and UCSC rows join one-to-one
on these five fields. Class-only `.out` tokens project the
class into both raw taxonomy fields under the qualified UCSC convention.

Record components remain authoritative for computation. Names and contig names are free of
`|`, `:` and whitespace, so each record key parses back into its
components. Repeat names also exclude `/`, keeping unresolved rank tokens separator-free.
Genomic bounds satisfy `1 <= start_1 <= end_1 <= contig length`. Equal coordinates
with different names retain separate record identities; exact duplicate keys fail the build.

### `tables/rmsk_instance_members.tsv.gz`

Columns are `rmsk_instance_id` (text) and `rmsk_record_id` (text), sorted by both columns.
Every record has exactly one membership row. The `.out` token defines the instance, and all
members of an instance share one contig. Instance text sorts lexically, preserving leading zeros.

### `tables/rmsk_taxonomy.tsv`

Columns are `rmsk_name` (text), `rmsk_family` (text), `rmsk_class` (text), `record_count`
(int64), `instance_count` (int64) and `record_length_sum_bp` (int64), in that order.
Each distinct source triple has one row, sorted by name, family and class. `instance_count`
counts distinct `rmsk_instance_id` values among the triple's records. The length sum retains
overlapping records. A name may carry several source labels; canonical rollups join through
`taxonomy_canonical`.

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

## Canonical taxonomy (phase 3)

### `tables/taxonomy_canonical.tsv`

One row per `rmsk_name`, sorted by name, derives canonical labels and rank statuses from the raw
taxonomy. The 15 columns appear in this order. `canonical_family` is unique within `canonical_class`.

| Column | Type | Contract |
|---|---|---|
| `rmsk_name` | text | Unique source repeat name within the build. |
| `canonical_class` | text | Winning normalized class; empty for an unresolved class. |
| `canonical_family` | text | Winning normalized family, class token for an unspecified family, or empty for an unresolved family. |
| `class_status` | text | Class resolution status under `taxonomy_rule_v1`. |
| `family_status` | text | Family resolution status under `taxonomy_rule_v1`. |
| `class_plurality_share` | float64 | Largest normalized class instance count divided by every label instance of the name, rounded to three decimals. |
| `family_plurality_share` | float64 | Largest specified family instance count divided by specified-family instances within the winning class, rounded to three decimals. |
| `family_support_share` | float64 | Largest specified family instance count within the winning class divided by every label instance of the name, rounded to three decimals. |
| `label_count` | int64 | Number of distinct raw class/family labels for the name. |
| `record_count` | int64 | Sum of raw label record counts for the name. |
| `instance_count` | int64 | Sum of raw label instance counts for the name. |
| `record_length_sum_bp` | int64 | Sum of raw label record lengths for the name, retaining overlaps. |
| `median_divergence_pct` | float64 | Median of `divergence_pct` across the name's records, rounded to two decimals. |
| `has_uncertain_source` | bool | Any raw class or family token carries a trailing `?`. |
| `has_multiple_labels` | bool | `label_count > 1`. |

The versioned rule `taxonomy_rule_v1` weights each raw label by `instance_count` and resolves
class first, then family within the winning class. Record counts and lengths supply context.

1. Strip a trailing `?` from every class and family token and set `has_uncertain_source = true` when any raw token carries that suffix.
2. Treat an empty family or a normalized family equal to its normalized class as unspecified, contributing its instance count to the class vote and abstaining from the family vote.
3. Select the class with the most instances and the specified family with the most instances within that class; a winning class with zero specified-family votes publishes `canonical_family = canonical_class` and `family_status = unspecified`.
4. Publish `unresolved` at a tied rank and below, with empty canonical fields at those ranks; ties use integer instance counts, and shares supply display values.

Class statuses are `concordant`, `resolved_uncertainty_suffix`, `resolved_plurality` and
`unresolved`. Family statuses are `concordant`, `resolved_uncertainty_suffix`,
`resolved_unspecified`, `resolved_plurality`, `unspecified` and `unresolved`.
Status precedence per rank is plurality over unspecified abstentions over uncertainty suffix
over concordant. `resolved_plurality` identifies a contested vote's winner;
`resolved_unspecified` identifies a specified family chosen alongside abstentions;
`unspecified` identifies the class-token family convention.

Family votes come exclusively from specified families within the winning class. A rank with zero
available votes publishes share `0`; tied ranks retain their tied shares. Both family shares are
`0` when class is unresolved or the winning class has zero specified-family votes.
The pure `resolve` function is total over typed votes: empty inputs, empty normalized classes
and nonpositive counts return both ranks unresolved. The build validates distinct raw triples,
names, normalized classes, positive counts and lengths, instance counts bounded by record counts,
and agreement with parquet name sets and record counts.

### `tables/taxonomy_resolution_report.tsv`

One row per name with `label_count > 1`, sorted by name, records its raw votes and canonical decision.
Membership counts distinct raw labels, so a `?` variant alone places a name in the report and
exposes its suffix decision. Columns appear in this order:

| Column | Type | Contract |
|---|---|---|
| `rmsk_name` | text | Source repeat name with multiple distinct raw labels. |
| `rmsk_labels` | text | Raw `class/family=<instances>;...` labels sorted by descending instance count, then class and family. |
| `rmsk_label_records` | text | Raw `class/family=<records>;...` labels in the same order as `rmsk_labels`. |
| `rule_version` | text | Applied rule version, `taxonomy_rule_v1`. |
| `canonical_class` | text | Canonical class from `taxonomy_canonical`. |
| `canonical_family` | text | Canonical family from `taxonomy_canonical`. |
| `class_status` | text | Class status from `taxonomy_canonical`. |
| `family_status` | text | Family status from `taxonomy_canonical`. |

Family and class rollups join each name once through `taxonomy_canonical` and conserve each
name's count. Resolved family buckets use `<canonical_class>/<canonical_family>`; resolved class
buckets use `<canonical_class>`. Unresolved ranks retain empty canonical fields, and rollups use
`unresolved_class_<rmsk_name>` or `unresolved_family_<rmsk_name>`, one bucket per name per rank.
These tokens are free of `/`, `:` and `|` and occupy the corresponding rank's export field.

The four spellings of "no family" are `<class>/<class>` under the abstention convention,
`Unknown/Unknown`, `Unspecified/Unspecified` and `unresolved_family_<name>` for a tied family
rank. `Unknown` and `Unspecified` retain their literal source classification.

The pinned Dfam snapshot under `tests/fixtures/taxonomy/` supplies test evidence; the build derives
labels from the two source tables under `tables/`. Every report name requires a snapshot row,
and every snapshot name belongs to the canonical table. Agreement compares each type and subtype
that Dfam names. Snapshot rows may also cover concordant names. The current snapshot covers class
`DNA`; `Unknown` and `Unspecified` have their evidence in the raw source labels.
`tests/expectations/mm39/taxonomy_census.tsv` records the measured acceptance census, including
snapshot row count. The snapshot provenance records its fetch date, endpoint pattern, source,
role and per-family version evidence; the next refresh adds the release endpoint response.

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

## Exports and later phases

Exports follow `exports/<contig_namespace>/<universe>/<interval_variant>/<level>[_<profile>].<format>`.
The core release supplies seven `interspersed` full-interval exports in each of the `ucsc`,
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

### Phase 4: UCSC full-interval exports

All seven exports land under `exports/ucsc/interspersed/full/`.
The builder reads the default universe from `universes.json` and selects its records through
`tables/universe_members.tsv.gz`. Provisional status is a class property recoverable by joining
names to `rmsk_taxonomy` or records to `universe_members`.

Every file is uncompressed UTF-8 with LF endings, sorted by
`(chrom, start_1, end_1, strand, rmsk_name)`, with text columns in C-locale byte order and
coordinate columns ascending numerically. Each selected record supplies
one full interval in every export. Identifier components match `[A-Za-z0-9_.+?()-]+`; emitted
identifiers additionally admit the separators `|`, `:` and `/`. The builder validates every
BED name, GTF attribute value and SAF GeneID and reports the offending value and file on failure.

| File | Coordinates | Feature identity |
|---|---|---|
| `record.bed` | 0-based half-open | BED6 name = `rmsk_record_id` |
| `subfamily.bed` | 0-based half-open | BED6 name = `rmsk_name` |
| `family.bed` | 0-based half-open | BED6 name = `<class>/<family>`; each position carries its canonical label or `unresolved_<rank>_<rmsk_name>` token |
| `record.gtf` | 1-based inclusive | Exon rows; `gene_id` = `rmsk_name`; `transcript_id` and `locus` = record alias |
| `subfamily.gtf` | 1-based inclusive | Exon rows; `gene_id`, `transcript_id` and `locus` = `rmsk_name` |
| `subfamily.saf` | 1-based inclusive | `GeneID` = `rmsk_name` |
| `taxonomy_triple.saf` | 1-based inclusive | Canonical taxonomy-triple grouping; `GeneID` = `<rmsk_name>:<canonical_family>:<canonical_class>` |

#### `record.bed`

BED6 columns are `chrom`, `start_1 - 1`, `end_1`, `rmsk_record_id`, `min(sw_score, 1000)` and
`strand`. Coordinates are 0-based half-open. Column 4 identifies the source record for IRescue
and interval operations.

Check contig and coordinate order with `LC_ALL=C sort -c -t$'\t' -k1,1 -k2,2n -k3,3n record.bed`.

#### `subfamily.bed`

BED6 uses the same 0-based half-open columns and clipped score as `record.bed`, with
`rmsk_name` in column 4. Repeated names group records into subfamilies for IRescue.

#### `family.bed`

BED6 uses 0-based half-open coordinates and the clipped score, with `<class>/<family>` in
column 4. The two positions carry the name's canonical labels. An unresolved class occupies
the class position as `unresolved_class_<rmsk_name>`; an unresolved family occupies the family
position as `unresolved_family_<rmsk_name>`. Family identity includes its class.
The prefix `unresolved_` is reserved for generated rank tokens; the exporter rejects resolved
canonical class or family labels beginning with it.

#### `record.gtf`

One exon row per record uses the nine GTF columns: `chrom`, `te-tracks`, `exon`, `start_1`,
`end_1`, `sw_score`, `strand`, `.`, and attributes. Coordinates are 1-based inclusive and the
score retains its source value. The colon-free record alias is
`R|mm39|<rmsk_name>|<chrom>|<start_1>|<end_1>|<strand>`; the instance alias is
`I|mm39|<rmsk_instance_id>`. Record aliases retain UCSC contig names; both aliases stay fixed
across namespace exports.

Attributes appear in this order: `gene_id`, `transcript_id`, `locus`, `family_id`, `class_id`,
`rmsk_family`, `rmsk_class`, `instance_id`, `rmsk_record_id`. Each is written as `key "value";`,
with one space between attributes. Stellarscope's default `locus` groups by record;
`--attribute instance_id` selects the source instance grouping.

#### `subfamily.gtf`

One exon row per record uses the same fixed GTF columns and 1-based inclusive coordinates.
Attributes appear in this order: `gene_id`, `transcript_id`, `locus`, `family_id`, `class_id`,
`rmsk_family`, `rmsk_class`. The first three values equal `rmsk_name`, supplying subfamily
identity for Stellarscope, TEsingle and TElocal.

The following attribute mapping applies to both GTFs. TEtranscripts groups by
`gene_id:family_id:class_id`; TEsingle and TElocal use
`transcript_id:gene_id:family_id:class_id`. Canonical ranks come from the name's row in
`taxonomy_canonical`; an unresolved rank emits `unresolved_<rank>_<rmsk_name>` in its position.

| Attribute | Source column or transformation | Consumer that reads it |
|---|---|---|
| `gene_id` | `rmsk_records.rmsk_name` | TEtranscripts, TEsingle, TElocal |
| `transcript_id` | Record alias in `record.gtf`; `rmsk_name` in `subfamily.gtf` | TEsingle, TElocal |
| `locus` | Record alias in `record.gtf`; `rmsk_name` in `subfamily.gtf` | Stellarscope default grouping |
| `family_id` | `taxonomy_canonical.canonical_family` or unresolved family token | TEtranscripts, TEsingle, TElocal |
| `class_id` | `taxonomy_canonical.canonical_class` or unresolved class token | TEtranscripts, TEsingle, TElocal |
| `rmsk_family` | `rmsk_records.rmsk_family` | Source-taxonomy audit readers |
| `rmsk_class` | `rmsk_records.rmsk_class` | Source-taxonomy audit readers |
| `instance_id` (record GTF) | `I\|mm39\|<rmsk_instance_id>` | Stellarscope with `--attribute instance_id` |
| `rmsk_record_id` (record GTF) | `rmsk_records.rmsk_record_id` | Registration and catalog joins |

#### `subfamily.saf`

Tab-separated SAF starts with the header `GeneID`, `Chr`, `Start`, `End`, `Strand`.
Each data row contains `rmsk_name`, `chrom`, `start_1`, `end_1`, `strand`, using 1-based
inclusive coordinates. featureCounts groups intervals sharing the subfamily GeneID.

#### `taxonomy_triple.saf`

Tab-separated SAF uses the same header and 1-based inclusive intervals as `subfamily.saf`.
GeneID is `<rmsk_name>:<canonical_family>:<canonical_class>`, with unresolved rank tokens in
their family or class positions. Canonical labels are a function of the name, so the 1,220
interspersed names yield 1,220 GeneIDs, including the 20 names carrying two raw labels.
The filename identifies the legacy lab taxonomy grouping read by featureCounts.

#### `tables/export_feature_members.tsv.gz`

Columns appear in this order:

| Column | Type | Contract |
|---|---|---|
| `universe_name` | text | Selected membership, `interspersed`. |
| `variant` | text | Interval support, `full`. |
| `feature_level` | text | `record`, `subfamily`, `family` or `taxonomy_triple`. |
| `emitted_feature_id` | text | Exact emitted feature identifier at that level. |
| `rmsk_record_id` | text | Member record in the canonical table. |
| `block_start_1` | int64 | Retained block start, 1-based inclusive. |
| `block_end_1` | int64 | Retained block end, inclusive. |

Each `(universe_name, variant, feature_level, emitted_feature_id, rmsk_record_id)` occurs
once. Full intervals register one block equal to the record bounds. Record level registers
both `rmsk_record_id` for BED and the record alias for GTF. Subfamily level registers each
name-record pair once for BED, GTF and SAF. Family and taxonomy-triple levels each register
one name-derived feature per record, yielding five registration rows per selected record.

Emitted IDs retain UCSC names inside record identities and are namespace-invariant; the same
registration serves phase 6 namespaces. Rows follow export record order, then record BED,
record GTF, subfamily, family and taxonomy-triple spelling. Gzip uses the deterministic table
serialization above. Counts remain at their measured feature grain; selecting supporting
records selects each distinct measured feature once before summing its count.

#### `tables/exports.tsv`

One row per export file, sorted by `export_path`, inventories these columns in order:

| Column | Type | Contract |
|---|---|---|
| `export_path` | text | Path relative to the build directory. |
| `namespace` | text | Contig-column namespace, `ucsc` in phase 4. |
| `universe_name` | text | Registered universe, `interspersed`. |
| `variant` | text | Registered interval variant, `full`. |
| `feature_level` | text | Export's default feature level. |
| `format` | text | `bed`, `gtf` or `saf`. |
| `rows` | int64 | Data rows; SAF headers are counted separately. |
| `distinct_features` | int64 | Distinct BED names, GTF `locus` values or SAF GeneIDs. |
| `sha256` | text | SHA-256 of the complete emitted file bytes. |

### Consumer contracts (phase 5)

`tests/run.sh consumers` reports parser and executable support separately. The local checkout
parsers establish feature identity; executable fixtures establish the stated counting and overlap
behavior. Generated inputs live under `$TE_TRACKS_REFROOT/fixtures/consumers/`.
`00_tool_inventory.py` is reporting-only for executable availability; its in-process import
self-test verifies exit 1 for a missing symbol and exit 3 for an absent external module.
Parser versions are read from the checkouts on each run.

| Consumer | Export read | Feature identity | Fixture in `tests/checks/consumers/` | Support in-container |
|---|---|---|---|---|
| IRescue 1.2.0 | `record.bed`, `subfamily.bed` | BED column 4 | `10_irescue_parser.py`: roster identities and coordinates, 11 record features, 8 names, comma splitting and exporter rejection; `15_irescue_chrcat.py`: real `chrcat` serialization; `20_irescue_exec.sh`: 2 molecules versus 1+1, 4/2 and 3/3 allocation | Identity parser supported; `chrcat` unsupported: system tool `gawk` absent; execution unsupported: `irescue` absent |
| Stellarscope 1.5 | `record.gtf` | `locus` for records; `instance_id` for instances | `11_stellarscope_parser.py`: isolated annotation package, 11 records, 10 instances, attributes, endpoint gate | Parser exercised; unsupported: right-boundary overlap defect, observed `0,1,1,1`, expected `0,1,1,0`; executable `stellarscope` absent |
| TEsingle 1.0 | `record.gtf`, `subfamily.gtf` | `transcript_id:gene_id:family_id:class_id` | `12_tesingle_parser.py`: 11 record tuples, 8 subfamily tuples, BAM `UR` cutoff at 1,000, reverse-strand annotation and duplicate/QC-fail read filtering | Parser supported; executable `TEsingle` absent |
| TEtranscripts 2.2.4 | `record.gtf`, `subfamily.gtf` | `gene_id:family_id:class_id` | `13_tetranscripts_telocal_parser.py`: 8 groups through either GTF | Parser supported; executable `TEcount` absent |
| TElocal 1.1.3 | `.locInd` built from `record.gtf` by TElocal's own indexer; `subfamily.gtf` supplies subfamily grain | `transcript_id:gene_id:family_id:class_id` | `13_tetranscripts_telocal_parser.py`: index construction and the checkout's pickle loader, semantic feature-tuple comparison, 11 record or 8 subfamily features; the pickle embeds the GTF path | Parser and index round trip supported; executable `TElocal` absent |
| MATES 0.1.8, optional adapter | Fixture-only `record_mates.csv` and `record_mates.bed`, eight columns each | Column 5 integer index; column 4 `TE_Name` group; column 7 raw class/family model group | `14_mates_parser.py`: isolated source functions, pair agreement, companion stem, `?`/`Unknown` model filters; minimal `pkg_resources.resource_filename` stand-in | Adapter supported in isolation; installed package depends on `pkg_resources` (setuptools below 82), absent here |
| featureCounts | `subfamily.saf`; fixture `onebase.saf` | SAF `GeneID` | `21_featurecounts_exec.sh`: `-s 0`, shared feature counts 2 fragments; one-base feature counts 1 read | Execution unsupported: `featureCounts` absent |
| bedtools 2.31.1 | `record.bed` | BED column 4 retained by `intersect -wa -wb` | `22_bedtools_exec.sh`: equal-coordinate names, right-adjacent query, `-s`/`-S` | Execution supported |
| samtools 1.21 | Fixture BAMs and their sequence dictionaries | BAM query name, strand and filter flags, `CB`/`UB`/`UR` tags | `23_samtools_fixture_integrity.sh`: sort order, indexes, alignment accounting, molecule counts by tag and flagged read names | Execution supported |

The authored oracle in `tests/fixtures/consumers/expected.json` specifies 11 records, 8 names and
10 instances. The production taxonomy resolver elects `TwoLab`'s `hAT-Tip100` family by 2:1
instance plurality; both GTFs retain its raw family labels. The production exporter writes all
seven exports from those tables. TElocal's loader branch is executed directly from its checkout.

The FASTA has seed 1729 and contigs `chrA` (5,000 bp) and `chrB` (3,000 bp). The ARC, OCM and
bulk BAMs each encode eleven molecules: one unique, one repeated, one multimapping, one in the
instance gap, four at the `Edge` boundaries, one on minus-strand `TwoLab` and two carrying
duplicate/QC-fail flags. They contain 13, 26 and 26 alignment records, respectively. Both
minus-strand roster records have reverse-strand reads. The ARC and OCM layouts carry `CB`, `UB`
and raw `UR`: `unique_a` copy 0 and `duplicate_b` copy 1 have one-base raw errors, yielding
11 corrected `UB` identities and 12 raw `UR` identities. The oracle includes flagged molecules
in these totals and records flagged query names per BAM. Bulk carries query and mate identities.
Separate counting fixtures preserve each assay layout and report IRescue's fitted
allocation in `irescue_allocation.json` when its executable is available.

Stellarscope's endpoint gate expects `0,1,1,0` for the four reads against GTF `101..110`.
The checkout observes `0,1,1,1` and reports the right-boundary defect as unsupported. The gate
passes on `0,1,1,0` and fails on every other result. Its annotation dependency is `intervaltree`.
MATES resolves
`record_mates.csv` to its companion correctly; a dotted stem resolves to `record.bed`.
Its preparation fixture supplies coverage vectors and executes the upstream model-group filter.
MATES works in `$TE_TRACKS_REFROOT/fixtures/consumers_scratch/mates/` and removes that directory.
IRescue's five parser `.tsv.gz` files have mtime 0 and an empty gzip filename. TElocal indexes
are compared by feature tuples across GTF paths.
The existing registration query remains unsupported through the missing Python module `duckdb`.

### Phase 6: contig namespaces and qualification

The seven full-interval exports also land under `exports/ensembl/interspersed/full/` and
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
