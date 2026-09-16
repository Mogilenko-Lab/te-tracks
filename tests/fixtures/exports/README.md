# Export fixtures

`records.tsv` supplies six records for a typed scratch parquet; `universe_members.tsv` selects
five records, and `taxonomy.tsv` supplies their canonical rank labels and statuses.
`universes.json` declares the default universe with an all-record predicate, so the selected
five rows establish membership as the export authority.

`expected/` contains hand-authored export bytes and the decompressed feature registration.
The rows cover C-locale contig order, score clipping, a one-base interval, two names at equal
coordinates, two records in instance `007`, changing raw labels, and unresolved family and class
ranks. Check 42 builds the scratch inputs, compares every expected file and exercises invalid
identifier components and membership gates.
