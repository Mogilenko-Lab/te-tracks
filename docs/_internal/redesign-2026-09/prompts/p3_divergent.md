Divergent pass on phase 3 of the te-tracks redesign: the canonical taxonomy rule. Repository:
/workspaces/Meta-Aging/01_modules/te-tracks (git branch redesign-2026-09). You are a read-only reviewer working
from the documented artifacts and the tables; write exactly one file,
docs/_internal/redesign-2026-09/reviews/p3_divergent.md, and change nothing else. No git writes.

Read, in order:
1. docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/13_phase3_taxonomy.md (the rule and its contract)
2. docs/_internal/redesign-2026-09/reviews/m2_rulings.md, sections "Phase 3" and "Opus review"
3. docs/_internal/redesign-2026-09/reviews/m2_divergent.md item H7 (your predecessor's objection and its ruling)
4. docs/_internal/redesign-2026-09/taxonomy/README.md, dfam_lookup_20names.tsv, out_token_census_20names.tsv
5. The implementation: src/lib/build_taxonomy.py, tests/checks/core/3*.py, tests/fixtures/taxonomy/*, and the
   phase 3 sections of docs/OUTPUTS.md
6. The tables: /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/te_mm39/build/tables/rmsk_taxonomy.tsv,
   taxonomy_canonical.tsv, taxonomy_resolution_report.tsv (read-only)

Your question: what does `taxonomy_rule_v1` take for granted that a different RepeatMasker library, a different
assembly, or a downstream rollup will break? Attack, with a specific failure each: record-count weighting against
length weighting or instance weighting; stripping `?` before the vote; class-only tokens abstaining from the family
vote; precedence of statuses per rank; the `unresolved/<rmsk_name>` bucket spelling against BED, GTF and SAF
consumers; the Dfam snapshot as the only oracle and set equality as the admission gate; Dfam's vocabulary against
RepeatMasker's (`repeat_type`/`repeat_subtype` spellings, missing subtypes, names Dfam lacks); the median divergence
as a per-name statistic; the resolution report's `rule_fired` column; what hg38 (Alu, SVA, L1 subfamilies with
`?` labels) would do to the status census. Where the record already defends an assumption, cite the file and line.

Format:
# Phase 3 review: what the rule assumes (divergent)
## High
- [H1] assumption — failure — evidence — where it should land
## Medium
- [M1] ...
## Low
- [L1] ...
## Defended already
- one line each, with citation
Under 120 lines. Specific over general; measure from the tables where a measurement settles the point.
