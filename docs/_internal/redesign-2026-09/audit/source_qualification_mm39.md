# RepeatMasker source qualification

Status: PASS. Parser profile: `rm_out_v1`.

| source | md5 | bytes |
|---|---|---:|
| `mm39.fa.out.gz` | `ffc8399d05f3388d80b78c93482a5b95` | 169,199,039 |
| `rmsk.txt.gz` | `ca2e5542cab0390b5458e7935e891430` | 142,017,372 |

The multiset join uses `(chrom, start_1, end_1, strand, name)` and preserves row multiplicity.
The key converts `genoStart + 1` and maps `.out` strand `C` to `-`.
Shared fields compare score directly, percentages as `round(perc * 10)`, and query left as `-(query_left_bp)`.
Class/family splits once at `/`; class-only tokens project the class into both UCSC fields.
On `+`, `(repStart, repEnd, repLeft) = (consensus_start_1, consensus_end_1, -consensus_left_bp)`.
On `-`, `(repStart, repEnd, repLeft) = (-consensus_left_bp, consensus_end_1, consensus_start_1)`.
The `.out` ID supplies grouping statistics; UCSC `bin` and its independent one-character `id` remain table metadata.
Exact shared values pair first; remaining values pair in sorted order within each key for field diagnostics.

Measurement references: `docs/_internal/redesign-2026-09/audit/audit_out.py` and `docs/_internal/redesign-2026-09/audit/audit_rmsk.py`.

## Summary

| metric | value |
|---|---:|
| out_rows | 5,320,771 |
| table_rows | 5,320,771 |
| matched_rows | 5,320,771 |
| unmatched_out_rows | 0 |
| unmatched_table_rows | 0 |
| field_disagreements | 0 |
| distinct_ids | 4,696,900 |
| id_min | 1 |
| id_max | 4,696,900 |
| ids_contiguous | 1 |
| ids_spanning_contigs | 0 |
| starred_rows | 0 |
| coordinate_collision_pairs | 3 |

## Shared-field disagreements

| field | disagreements |
|---|---:|
| swScore | 0 |
| milliDiv | 0 |
| milliDel | 0 |
| milliIns | 0 |
| genoLeft | 0 |
| repClass | 0 |
| repFamily | 0 |
| repStart | 0 |
| repEnd | 0 |
| repLeft | 0 |

## Unmatched .out rows

Count: 0.

## Unmatched UCSC table rows

Count: 0.

## Coordinate-only collision pairs

Pairs group `.out` rows by `(chrom, start_1, end_1, strand)` and distinct names; `start_0` aligns with the audit coordinates.

| chrom | start_0 | start_1 | end_1 | strand | name_a | name_b |
|---|---:|---:|---:|---|---|---|
| chr11 | 67327100 | 67327101 | 67327210 | - | B1F | ORR1B1-int |
| chr13 | 58658237 | 58658238 | 58658287 | - | B1_Mus1 | ORR1B1-int |
| chr16 | 37859045 | 37859046 | 37859109 | + | B1_Mur3 | ID_B1 |
