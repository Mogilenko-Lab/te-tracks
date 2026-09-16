# Phase 4: `interspersed` exports in the UCSC namespace

Goal: the files consumers read, each registered back to records.

Deliverables under `exports/ucsc/interspersed/full/`
- `record.bed` (BED6; name = `rmsk_record_id`; score = min(sw_score, 1000)).
- `subfamily.bed` (BED6; name = `rmsk_name`).
- `family.bed` (BED6; name = `<canonical_class>/<canonical_family>` or `unresolved/<rmsk_name>`).
- `record.gtf` (exon rows; `gene_id`=rmsk_name, `transcript_id` and `locus` = colon-free record
  alias `R|mm39|<name>|<chrom>|<start_1>|<end_1>|<strand>`, `family_id`/`class_id` = canonical,
  `rmsk_family`/`rmsk_class` = raw, `instance_id` = `I|mm39|<id>`).
- `subfamily.saf` (GeneID = rmsk_name; 1-based).
- `taxonomy_triple.saf` (GeneID = `<rmsk_name>:<canonical_family>:<canonical_class>`, the legacy lab
  grouping made visible by its name; 1-based).
- `tables/export_feature_members.tsv.gz`: `(export_path, feature_level, emitted_feature_id,
  rmsk_record_id, block_start_1, block_end_1)`; for `full` exports one block per record.
- Name validation: every emitted id matches `[A-Za-z0-9_.+/?()|:-]+`, contains no `, # ~ % ; "` or
  whitespace; a violation fails the export.

Acceptance
- Row counts: `record.bed` 3,764,949; `subfamily.bed` 3,764,949 rows over 1,220 names; `family.bed`
  3,764,949 rows; `record.gtf` 3,764,949 rows; `subfamily.saf` and `taxonomy_triple.saf` 3,764,949 rows
  + header; `taxonomy_triple.saf` has 1,220 distinct GeneIDs (canonical labels collapse the 20 doubled names).
- Round trip: BED start = start_1 - 1 for every row; GTF and SAF coordinates equal the table.
- Every emitted feature id resolves to at least one record through `export_feature_members`;
  registration conservation fixture (count 7 over 3 records stays 7) as a DuckDB query in tests.

Review focus: attribute mapping documented once in `docs/OUTPUTS.md`; no consumer or modality
vocabulary in file names.
