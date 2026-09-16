# Phase 3: canonical taxonomy by rule

Goal: one canonical (class, family) per name, derived from the source labels by a total,
deterministic rule, checked against a pinned Dfam snapshot. The sources define the labels; the
build derives, the test checks, a human reads.

Input: `tables/rmsk_taxonomy.tsv` from phase 2: distinct raw labels per name with `record_count`,
`instance_count` (distinct `rmsk_instance_id` among the label's records) and `record_length_sum_bp`.

## The rule, `taxonomy_rule_v1`

Applied per `rmsk_name` over its distinct raw `(rmsk_class, rmsk_family)` labels, each weighted by its
instance count. Class resolves first, family within the winning class. Record counts and lengths travel
as context.

1. Strip a trailing `?` from every class and family token. A name whose records carried any `?`
   gets `has_uncertain_source = true`.
2. A family token equal to its class token, or empty, means the run gave no family (UCSC copies the
   class into the family column for those rows). Such labels vote for the class and abstain from the
   family vote.
3. Class: the class with the most instances wins. Family: among specified families within the winning
   class, the one with the most instances wins. A name whose winning class carries no specified family
   publishes `canonical_family = canonical_class` with `family_status = unspecified`, the RepeatMasker
   convention; specified families under losing classes take no part in the family vote.
4. Equal instance counts at a rank publish `unresolved` at that rank and below: the canonical field is
   empty in the table, and every rollup at that rank names the bucket `unresolved_class_<rmsk_name>` or
   `unresolved_family_<rmsk_name>`, one bucket per name per rank, tokens free of `/`, `:` and `|`.
   Ties are decided on integer instance counts; the share columns are display.

Weighting by instance follows from a measurement: a record count rewards fragmentation, and in every mm39
family competition the losing label is the more fragmented one (`MER63C`: hAT-Blackjack 99 records over
47 instances against hAT-Tip100 273 over 246). By instance the `MER63C` share is 0.840; by record it was
0.734. Every mm39 winner is the same under both weightings (phase 3 review H1).

A refinement-aware variant, where a family token extending another with `-` outranks the coarser
token, would be `taxonomy_rule_v2` and waits for a measured source in which the coarse token holds the
plurality. mm39's three parent/child competitions (`MER53`, `UCON44`, `X4b_DNA`) resolve to the specific
token by count (milestone 2 ruling H7).

Rank-specific statuses, chosen by the most consequential step that fired:
`class_status` in {`concordant`, `resolved_uncertainty_suffix`, `resolved_plurality`, `unresolved`};
`family_status` in {`concordant`, `resolved_uncertainty_suffix`, `resolved_unspecified`,
`resolved_plurality`, `unspecified`, `unresolved`}. Precedence per rank: plurality over unspecified
over uncertainty suffix over concordant. `resolved_plurality` names the winner of a contested vote; the
share columns carry its support.

Examples from mm39 (instances): `MER63C` (hAT-Tip100 246, hAT-Blackjack 47) → family
`resolved_plurality`, plurality share 0.840; `Eutr2` (MULE-MuDR 40, DNA-only 4) → family
`resolved_unspecified`; `Eulor5B` (Crypton-A 34, `DNA?` 1) → class `resolved_uncertainty_suffix`,
family `resolved_unspecified`; `MER124` (DNA 246, `DNA?` 1) → class `resolved_uncertainty_suffix`,
family `unspecified`, canonical `DNA/DNA`.

## Deliverables

- Phase 2's `tables/rmsk_taxonomy.tsv` carries `instance_count` (columns `rmsk_name, rmsk_family,
  rmsk_class, record_count, instance_count, record_length_sum_bp`); the phase 2 contract states it.
- `src/lib/build_taxonomy.py` (called from the `src/20_build_taxonomy.sh` stage): reads
  `rmsk_taxonomy` and `rmsk_records`, applies the rule, writes `tables/taxonomy_canonical.tsv` with
  columns `rmsk_name, canonical_class, canonical_family, class_status, family_status,
  class_plurality_share, family_plurality_share, family_support_share, label_count, record_count,
  instance_count, record_length_sum_bp, median_divergence_pct, has_uncertain_source,
  has_multiple_labels`, one row per name, sorted by name. `class_plurality_share` is the winning
  class's instances over every label instance of the name; `family_plurality_share` is the winning
  family's instances over the specified-family instances within the winning class;
  `family_support_share` is the winning family's instances over every label instance of the name; a
  rank with no vote publishes 0 and a tied rank keeps the tied share. Shares round to three decimals.
  `median_divergence_pct` is the median of `divergence_pct` over the name's records, rounded to two
  decimals (the source carries one; even-count midpoints need two). `canonical_family` is unique only
  within `canonical_class`.
- `tables/taxonomy_resolution_report.tsv`: one row per name with `label_count > 1`: `rmsk_name,
  rmsk_labels` (`class/family=<instances>;...`, instances descending, then class and family),
  `rmsk_label_records` (the same order with record counts), `rule_version`, `canonical_class,
  canonical_family, class_status, family_status`. Membership counts distinct raw labels, so a `?`
  variant alone places a name in the report: the report shows every suffix decision.
- Phase 7's manifest identity carries `taxonomy_rule_version = "taxonomy_rule_v1"`, read from the module
  constant `TAXONOMY_RULE_VERSION` (deferred there; phase 3 review B3).
- `tests/fixtures/taxonomy/dfam_snapshot.tsv`: the Dfam API lookup for the multi-label names,
  copied from `docs/_internal/redesign-2026-09/taxonomy/dfam_lookup_20names.tsv`, with a
  `fetched_on` column (2026-09-16) and a sibling `dfam_snapshot.provenance.json` recording the family
  endpoint pattern, the fetch date, the per-family `dfam_version` values as the retained version evidence,
  and the Dfam release endpoint response as the item the next snapshot refresh adds (the 2026-09-16 fetch
  recorded none; phase 3 review B2, recorded deferral).
- `tests/expectations/mm39/taxonomy_census.tsv` (`metric, value`): names, multi-label names, every
  status count at both ranks, the minimum `family_plurality_share` among `resolved_plurality` rows and
  the name carrying it, the snapshot row count.
- Test `tests/checks/core/30_taxonomy_canonical.py`: recomputes every row of `taxonomy_canonical` from
  `rmsk_taxonomy` and the parquet through `resolve` and compares all columns exactly; asserts the census
  file; asserts the resolution report equals the multi-label subset.
- Test `tests/checks/core/31_taxonomy_dfam_agreement.py`: every report name has a snapshot row; every
  snapshot name exists in `taxonomy_canonical`; where Dfam names a type, `canonical_class ==
  dfam_repeat_type`, and where it names a subtype, `canonical_family == dfam_repeat_subtype`; the
  snapshot row count equals the census value and every row's `fetched_on` equals the provenance date.
  Missing and extra names are printed before any assertion; a disagreement fails with the name and
  both labels. The report-subset assertion is the admission gate for a new source: a new multi-label
  name fails the check until the snapshot covers it, and the snapshot may grow to concordant names.
- Rule fixtures under `tests/fixtures/taxonomy/rule_cases.tsv`: synthetic inputs covering each status,
  a class-level competition, a two-way tie at each rank (expects `unresolved`), a name mixing `?` and
  unspecified family, a parent/child family competition where the specific token holds the plurality
  (`MER53` shape), a winning class with no specified family beside a losing class with one (expects the
  class token, `unspecified`). Expected outputs authored by hand.
- Rollup rule documented in `docs/OUTPUTS.md`: family and class rollups join through
  `taxonomy_canonical`; unresolved tokens by rank as above; the four spellings of "no family"
  (`<class>/<class>` from the abstention convention, `Unknown/Unknown`, `Unspecified/Unspecified`,
  `unresolved_family_<name>`); `canonical_family` unique within `canonical_class`; report membership
  over raw labels; the pure function total while the build validates its inputs.

## Acceptance

- 18,484 rows in `taxonomy_canonical`; 20 rows with `has_multiple_labels`; 0 rows `unresolved` at
  either rank; over the 20: 7 `family_status = resolved_plurality`, 5 `resolved_unspecified`, 5
  `resolved_uncertainty_suffix`, 3 `unspecified`, every one `canonical_class = DNA`; over the table:
  `class_status` 18,478 `concordant` and 6 `resolved_uncertainty_suffix`; `family_status` 1,095
  `concordant` and 17,372 `unspecified` beside the 17 resolved rows; minimum `family_plurality_share`
  among `resolved_plurality` rows 0.840 (`MER63C`); `instance_count` sums to 4,727,623 over 18,504
  raw triples.
- Dfam agreement test: 20 of 20 pass.
- Fixture: a name with two labels and one count contributes once to its family rollup.
- Rule fixtures pass; the tie fixtures publish `unresolved` with empty canonical fields.

Review focus: the rule is total and deterministic over any input; raw tables stay untouched;
the build reads no network and no Dfam data; the snapshot is test evidence only. Reviewers: codex,
Opus and a `divergent` pass on the rule (milestone 2 ruling M7).

Deferred, recorded: extending the Dfam snapshot from the 20 multi-label names to every
`interspersed` name (one clade-scoped API pull); the snapshot speaks to class `DNA` alone today and
`Unknown` and `Unspecified` have no Dfam counterpart (phase 3 review H3); sizing hg38's `?`-family
footprint before admission, since a `?` family under an existing class passes the class gate and enters
through the report (phase 3 review M3); `taxonomy_rule_v2` for refinement.
