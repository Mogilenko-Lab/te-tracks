# Expected export bytes

- `record.bed` pins record names, clipped scores, half-open one-base intervals and contig order; `tests/checks/core/42_exports_fixtures.py` reads it.
- `subfamily.bed` pins shared subfamily names on the record BED intervals; `tests/checks/core/42_exports_fixtures.py` reads it.
- `family.bed` pins canonical class/family buckets and positional unresolved tokens; `tests/checks/core/42_exports_fixtures.py` reads it.
- `record.gtf` pins subfamily gene IDs, record transcript/locus aliases and instance provenance; `tests/checks/core/42_exports_fixtures.py` reads it.
- `record_starsolo.gtf` pins record-as-gene aliases and ordered biotype/provenance attributes; `tests/checks/core/42_exports_fixtures.py` and `tests/checks/consumers/17_starsolo_profile.required.py` read it.
- `subfamily.gtf` pins shared gene/transcript/locus IDs with canonical and raw labels; `tests/checks/core/42_exports_fixtures.py` reads it.
- `subfamily.saf` pins subfamily GeneIDs and inclusive blocks; `tests/checks/core/42_exports_fixtures.py` reads it.
- `taxonomy_triple.saf` pins canonical taxonomy-triple GeneIDs on those same blocks; `tests/checks/core/42_exports_fixtures.py` reads it.
- `export_feature_members.tsv` pins forty interspersed spellings and six all_rmsk record registrations; `tests/checks/core/42_exports_fixtures.py` reads it.
- `all_rmsk/README.md` maps complete-catalog BED bytes to `tests/checks/core/42_exports_fixtures.py`.

BED and SAF companions differ in emitted identity values while preserving interval support; each pins its consumer grammar. GTF companions also pin their distinct attribute rosters.
