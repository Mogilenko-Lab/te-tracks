# Publication fixtures

`build_fixture.py` writes one typed record with text instance `007`, four tiny pinned sources,
canonical tables and all 24 exports through the production writers, then calls `manifest.py`.
The fixture matches the core payload roster, with `source/qualification.md` carrying the build note.
Check 72 uses these builds under `$TE_TRACKS_REFROOT/pubtest/` to exercise installation,
selection, concurrent publication, corruption and payload permissions.
An extended roster adds `all_rmsk/full/record_extra.bed` in all three namespaces to exercise archive evolution.
