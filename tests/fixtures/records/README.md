# Canonical record fixtures

- `beyond_end.out` pins end 101 on a 100-base contig through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `beyond_end.tsv` pins end 101 on a 100-base contig through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `chrom.sizes` pins 100-base chr2/chr10 bounds and C-locale contig order; `tests/checks/core/23_records_fixtures.py` reads it.
- `classes.tsv` pins fixture class dispositions, including provisional, satellite and simple-repeat classes; `tests/checks/core/23_records_fixtures.py` reads it.
- `colon_chrom.out` pins a colon in the contig name and the coordinate-separator boundary through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `colon_chrom.tsv` pins a colon in the contig name and the coordinate-separator boundary through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `colon_name.out` pins a colon in the repeat name and the record-key parsing boundary through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `colon_name.tsv` pins a colon in the repeat name and the record-key parsing boundary through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `duplicate_key.out` pins duplicate record identity despite different scores, taxonomy and instance IDs; `tests/checks/core/23_records_fixtures.py` reads it.
- `expected_instances.tsv` pins distinct text IDs 001/1 and two records in instance 001; `tests/checks/core/23_records_fixtures.py` reads it.
- `expected_records.tsv` pins exact typed canonical rows and serialization; `tests/checks/core/23_records_fixtures.py` reads it.
- `expected_taxonomy.tsv` pins source-triple record, instance and length totals; `tests/checks/core/23_records_fixtures.py` reads it.
- `expected_universes.tsv` pins six universe censuses, including the tRNA-family exclusion; `tests/checks/core/23_records_fixtures.py` reads it.
- `family_disagreement.tsv` pins the single hAT-to-hAT2 value change from rmsk.tsv and the named source-family disagreement; `tests/checks/core/23_records_fixtures.py` reads it.
- `missing_chrom.out` pins a contig absent from chrom.sizes through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `missing_chrom.tsv` pins a contig absent from chrom.sizes through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `pipe_name.out` pins a pipe in the repeat name and the record-key separator boundary through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `pipe_name.tsv` pins a pipe in the repeat name and the record-key separator boundary through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `records.out` pins text IDs 001/1, a cross-strand instance, equal-coordinate names, signed fields and universe boundaries; `tests/checks/core/23_records_fixtures.py` reads it.
- `rmsk.tsv` pins the matching UCSC taxonomy and signed coordinate encoding for the source records; `tests/checks/core/23_records_fixtures.py` reads it.
- `slash_name.out` pins a slash in the repeat name and the rank-token separator boundary through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `slash_name.tsv` pins a slash in the repeat name and the rank-token separator boundary through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `spanning_instance.out` pins instance 007 shared across two contigs through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `spanning_instance.tsv` pins instance 007 shared across two contigs through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.
- `unlisted_class.out` pins a source class outside the disposition table and an extra UCSC join row through the primary source; `tests/checks/core/23_records_fixtures.py` reads it.
- `unlisted_class.tsv` pins a source class outside the disposition table and an extra UCSC join row through the matching UCSC row(s); `tests/checks/core/23_records_fixtures.py` reads it.

The pipe, colon and slash cases vary the invalid value to pin separate identifier boundaries; each `.out`/`.tsv` pair supplies the two source formats for one gate. `family_disagreement.tsv` differs from `rmsk.tsv` only in one family value.
