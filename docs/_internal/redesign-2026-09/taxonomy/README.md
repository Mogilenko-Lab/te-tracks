# Taxonomy evidence for the multi-label names (mm39)

Twenty repNames carry more than one raw (class, family) label across their mm39 RepeatMasker
records, 6,517 records in all, every one of class DNA. The canonical label for each name is
derived by `taxonomy_rule_v1` (plan phase 3) from the source labels alone. These files are the
evidence that the rule reproduces the public classification.

- `dfam_lookup_20names.tsv`: the Dfam API entry for each name (fetched 2026-09-16): accession,
  version, title, full classification path, repeat type and subtype. Dfam's type and subtype agree
  with the record-count majority of the RepeatMasker labels for all 20 names. Three names
  (`MER124`, `MER131`, `UCON2`) have no subtype at Dfam and no family in RepeatMasker; the rule
  publishes `DNA/DNA` for them, the RepeatMasker convention.
- `out_token_census_20names.tsv`: the raw `.out` class/family tokens per name with record counts,
  the input the rule sees.

The lookup becomes `tests/fixtures/taxonomy/dfam_snapshot.tsv`, and the agreement test fails the
build whenever the rule and the snapshot disagree. Refreshing the snapshot is the update path;
the build itself reads no Dfam data.
