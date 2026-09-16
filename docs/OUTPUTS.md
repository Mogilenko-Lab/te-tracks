# Outputs

Tables, GTF and SAF use **1-based inclusive** coordinates; BED uses **0-based half-open**
coordinates. The redesign artifacts below are deferred to their listed phases.

## Built today

The current build generates `te_loci.tsv.gz`, `te_dim.tsv`, `MANIFEST.json` and `BUILD_ID`; the redesign replaces them.

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

The RepeatMasker `.out` ID column is the instance key; its record membership lands in phase 2
as `tables/rmsk_instance_members.tsv.gz`.

### `te_dim.tsv` — legacy dimension table

Columns are `subfamily`, `family`, `class`, `n_loci` and `total_bp`. Each row summarizes one
source `(subfamily, family, class)` triple.

### `MANIFEST.json` — legacy manifest

The manifest records source URLs and md5s, output md5s and byte counts, row counts, class and
identity policy, and the builder's git SHA. A re-run over an existing snapshot retains its
manifest and producing SHA.

### `BUILD_ID` — legacy fingerprint

The legacy id is the SHA-256 of the sorted `<md5>  <relative path>` inventory of delivered
outputs. Source files, scratch files, `MANIFEST.json` and `BUILD_ID` sit outside that inventory.
[RELEASES.md](RELEASES.md) describes the current publication layout.

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
| `te_subfamily.gtf` | `record.gtf`: one GTF; consumers group by attribute (phase 4) |
| `te_locus.gtf` | `record.gtf`: one GTF; consumers group by attribute (phase 4) |
| `te_locus.locInd` | `record.gtf` read as `.locInd` (fixture, phase 5) |
| `te_subfamily_noExon.saf` | `exon_subtracted/subfamily.saf` in `te_mm39_gene` (phase 8) |
| `te_context_*.saf` | Deferred to the transcript-context design session after phase 8 |
| `locus_context.tsv` | Deferred to the transcript-context design session after phase 8 |
| `rename_map.tsv` | Superseded by `taxonomy_triple.saf` and the `compat_tetranscripts_mm39` universe |
| `te_loci.parquet` | `tables/rmsk_records.parquet` (phase 2) |
| `ensembl_named/` | `exports/ensembl/` (phase 6) |

### Phase 2: canonical records and universes

| Artifact | Contract |
|---|---|
| `tables/rmsk_records.{tsv.gz,parquet}` | Complete source catalog; one row per `rmsk_record_id`, with `start_1` and `end_1` |
| `tables/rmsk_instance_members.tsv.gz` | `rmsk_instance_id`, `rmsk_record_id`; one instance per record |
| `tables/rmsk_taxonomy.tsv` | Distinct raw name, family and class triples with record counts and summed lengths |
| `universes.json` | Six named predicates over raw source classification |
| `tables/universe_members.tsv.gz` | `universe_name`, `rmsk_record_id` membership for each universe except `all_rmsk` |

The record key is `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`. The four feature levels are
record, instance, subfamily and canonical family.

### Phase 3: canonical taxonomy

`tables/taxonomy_canonical.tsv` supplies one row per name with canonical class and family,
rank-specific resolution statuses and median record divergence under `taxonomy_rule_v1`.
`tables/taxonomy_resolution_report.tsv` records names with multiple raw labels and the rule used.
Family and class rollups join through `taxonomy_canonical`; unresolved names enter an explicit
`unresolved` bucket, distinct from RepeatMasker's literal `Unknown`.

### Phase 4: UCSC full-interval exports

All six exports land under `exports/ucsc/interspersed/full/`.

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
