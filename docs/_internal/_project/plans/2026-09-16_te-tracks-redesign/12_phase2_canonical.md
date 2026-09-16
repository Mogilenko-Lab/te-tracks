# Phase 2: canonical tables and universes

Goal: the complete catalog with three identities, the raw taxonomy, and executable universes.

Deliverables
- `src/10_build_records.sh` (+ python): `tables/rmsk_records.tsv.gz` and `.parquet` with the
  24 columns and order in `redesign-2026-09/consults/ADR5_consult.md` §2; `rmsk_record_id` =
  `<rmsk_name>|<chrom>:<start_1>-<end_1>|<strand>`.
- `tables/rmsk_instance_members.tsv.gz`: `(rmsk_instance_id, rmsk_record_id)`.
- `tables/rmsk_taxonomy.tsv`: distinct `(rmsk_name, rmsk_family, rmsk_class)` with `record_count`,
  `instance_count` (distinct `rmsk_instance_id` among the label's records; phase 3 review H1) and
  `record_length_sum_bp`.
- `universes.json`: six predicates on raw `rmsk_class` and `rmsk_family`, each with a one-line
  description; `tables/universe_members.tsv.gz` `(universe_name, rmsk_record_id)` for every
  universe except `all_rmsk`.
- Assertions: record id unique over all rows; `1 <= start_1 <= end_1 <= contig length` from
  `chrom.sizes`; every record in exactly one instance; instances single-contig.

Acceptance (measured)
| universe | records | subfamilies | triples |
|---|---|---|---|
| all_rmsk | 5,320,771 | 18,484 | |
| interspersed | 3,764,949 | 1,220 | 1,240 |
| interspersed_plus_satellites | 3,802,177 | 1,228 | 1,248 |
| retrotransposon_derived | 3,593,857 | 868 | 868 |
| satellites | 37,228 | 8 | 8 |
| compat_tetranscripts_mm39 | 3,799,629 | 1,225 | 1,245 |
- coordinate-only collisions: exactly 3 pairs, all admitted as distinct records.
- 20 names with more than one triple in `rmsk_taxonomy`, 6,517 records.
- Fixtures: equal coordinates with different names stay two records; an exact duplicate key
  fails the build; a two-record instance; a record spanning a contig end fails bounds.

Milestone review after this phase: identity seam (schema, keys, universes, numbers).
