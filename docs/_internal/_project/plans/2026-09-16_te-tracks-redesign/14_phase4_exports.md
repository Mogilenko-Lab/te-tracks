# Phase 4: `interspersed` exports in the UCSC namespace

Goal: the files consumers read, each registered back to records.

Deliverables under `exports/ucsc/interspersed/full/`
- `record.bed` (BED6; name = `rmsk_record_id`; score = min(sw_score, 1000)).
- `subfamily.bed` (BED6; name = `rmsk_name`).
- `family.bed` (BED6; name = `<canonical_class>/<canonical_family>`; a rank unresolved for the name
  reads `unresolved_class_<rmsk_name>` or `unresolved_family_<rmsk_name>` in that position, one bucket
  per name per rank; phase 3 review H5).
- `record.gtf` (exon rows; `gene_id`=rmsk_name, `transcript_id` and `locus` = colon-free record
  alias `R|mm39|<name>|<chrom>|<start_1>|<end_1>|<strand>`, `family_id`/`class_id` = canonical,
  `rmsk_family`/`rmsk_class` = raw, `instance_id` = `I|mm39|<id>`).
- `subfamily.gtf` (exon rows; `gene_id` and `transcript_id` = rmsk_name, `family_id`/`class_id` =
  canonical, `rmsk_family`/`rmsk_class` = raw): the subfamily-grain input for TEsingle and TElocal,
  whose feature key includes `transcript_id`; TEtranscripts reads either GTF at `gene_id` grain. Named
  consumer: the owner's TEsingle sensitivity run at subfamily grain (milestone 2 ruling H2).
- `subfamily.saf` (GeneID = rmsk_name; 1-based).
- `taxonomy_triple.saf` (GeneID = `<rmsk_name>:<canonical_family>:<canonical_class>`, the legacy lab
  grouping made visible by its name; 1-based).
- `tables/export_feature_members.tsv.gz`: `(universe_name, variant, feature_level, emitted_feature_id,
  rmsk_record_id, block_start_1, block_end_1)`; emitted ids carry UCSC contig names inside the record
  alias and are namespace-invariant, so one registration serves the three namespaces; for `full`
  variants one block per record equal to the record bounds (milestone 2 ruling M5).
- `tables/exports.tsv`: one row per export path with `namespace, universe_name, variant, feature_level,
  format, rows, distinct_features, sha256`. Eight registration rows per selected record (milestone 5 ruling B1): level `record` registers
  `rmsk_record_id` (BED), the record alias (GTF `locus`) and the TEsingle and TElocal tuple
  `<alias>:<name>:<family_id>:<class_id>`; level `subfamily` registers `rmsk_name` (BED, SAF, GTF `locus`) and the
  tuple `<name>:<name>:<family_id>:<class_id>`; levels `family` and `taxonomy_triple` register their bucket and
  triple; level `instance` registers `I|mm39|<rmsk_instance_id>` for a Stellarscope instance run (mm39: 30,119,592
  rows, 3,152,636 distinct instances; a mixed-name instance attributes to a subfamily only through an explicit
  allocation). Uniqueness holds over the key plus `(block_start_1, block_end_1)`; `full` registers one block.
- Name validation: every id component (`rmsk_name`, contig, canonical label, unresolved token) matches
  `[A-Za-z0-9_.+?()-]+`; emitted ids add the separators `|`, `:` and `/`; no emitted id contains `, # ~ % ; "`
  or whitespace; a violation fails the export (milestone 2 ruling L1). The build rejects `/` in `rmsk_name`
  beside `|`, `:` and whitespace, so unresolved tokens are separator-free by construction (phase 3 re-review A3).
- Export builders read `universes.json` and `universe_members.tsv.gz` from the build and never
  re-evaluate predicates (ruling A2). Exports carry no provisional flag; the status is a class property
  recoverable by joining names to `rmsk_taxonomy` (ruling L2). The `compat_tetranscripts_mm39` universe
  ships as membership only; the legacy comparison is the phase 9 reconciliation (ruling H1).

Acceptance
- Row counts: `record.bed` 3,764,949; `subfamily.bed` 3,764,949 rows over 1,220 names; `family.bed`
  3,764,949 rows; `record.gtf` and `subfamily.gtf` 3,764,949 rows each; `subfamily.saf` and `taxonomy_triple.saf` 3,764,949 rows
  + header; `taxonomy_triple.saf` has 1,220 distinct GeneIDs (canonical labels collapse the 20 doubled names).
- Round trip: BED start = start_1 - 1 for every row; GTF and SAF coordinates equal the table.
- Every emitted feature id resolves to at least one record through `export_feature_members`;
  registration conservation fixture (count 7 over 3 records stays 7) as a pandas query in the core check and
  as the same query in DuckDB in a `consumers`-mode check that reports `unsupported` naming the module where `duckdb` is absent
  (phase 4 review B1). Resolved canonical tokens beginning with `unresolved_` are rejected by the exporter,
  reserving the prefix for generated tokens (review A3).

Review focus: attribute mapping documented once in `docs/OUTPUTS.md`; no consumer or modality
vocabulary in file names.
