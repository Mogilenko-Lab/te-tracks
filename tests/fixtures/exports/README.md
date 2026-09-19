# Export fixtures

- `records.tsv` pins six records with byte-order contigs, clipped scores, one-base support, equal-coordinate names and a shared instance; `tests/checks/core/42_exports_fixtures.py` reads it.
- `taxonomy.tsv` pins canonical labels beside changing raw labels and unresolved class/family ranks; `tests/checks/core/42_exports_fixtures.py` reads it.
- `universe_members.tsv` selects five interspersed records and places Excluded in satellites; `tests/checks/core/42_exports_fixtures.py` reads it.
- `universes.json` pins membership authority despite all-record predicates and declares the complete-catalog universe; `tests/checks/core/42_exports_fixtures.py` reads it.
- `conservation_counts.tsv` pins one measured feature with count 7; `tests/checks/core/41_export_registration.py` and `tests/checks/consumers/30_registration_duckdb.py` read it.
- `conservation_members.tsv` pins that feature to three records sharing a subfamily and family; `tests/checks/core/41_export_registration.py` and `tests/checks/consumers/30_registration_duckdb.py` read it.
- `conservation_totals.tsv` pins count 7 per target after distinct-feature selection; `tests/checks/core/41_export_registration.py` and `tests/checks/consumers/30_registration_duckdb.py` read it.
- `expected/README.md` maps hand-authored export bytes and registration to `tests/checks/core/42_exports_fixtures.py`.
