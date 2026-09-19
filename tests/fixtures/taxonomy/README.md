# Taxonomy fixtures

- `dfam_snapshot.tsv` pins independent Dfam labels for all 20 multi-label names; `tests/checks/core/30_taxonomy_canonical.py` and `31_taxonomy_dfam_agreement.py` read it.
- `dfam_snapshot.provenance.json` pins the snapshot endpoint, date, source and version evidence; `tests/checks/core/31_taxonomy_dfam_agreement.py` reads it.
- `rule_cases.tsv` pins rank precedence, suffixes, abstention, plurality, ties and invalid votes; `tests/checks/core/32_taxonomy_rule_fixtures.py` reads it.
- `rollup_counts.tsv` pins one count per name and separate unresolved-name buckets; `tests/checks/core/32_taxonomy_rule_fixtures.py` reads it.
- `weighting_context.tsv` makes record and length weighting elect TcMar while instance weighting elects hAT; `tests/checks/core/32_taxonomy_rule_fixtures.py` reads it.
- `dfam_rank_cases.tsv` pins leaf/inherited/missing ranks, uncertainty, subclass rules, part sets, clade precedence and part disagreement; `tests/checks/core/34_dfam_rule_fixtures.py` reads it.

The `family_tie` and `family_tie_other` rows differ in vote values and name so the rollup proves separate unresolved buckets. Leaf/inherited and single/multiple-clade rows vary one field to pin status and precedence boundaries.
