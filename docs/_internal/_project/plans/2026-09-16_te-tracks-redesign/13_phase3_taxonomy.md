# Phase 3: canonical taxonomy by rule

Goal: one canonical (class, family) per name, derived from the source labels by a total,
deterministic rule, checked against a pinned Dfam snapshot. The sources define the labels; the
build derives, the test checks, a human reads.

Input: `tables/rmsk_taxonomy.tsv` from phase 2 (distinct raw labels per name with record counts).

## The rule, `taxonomy_rule_v1`

Applied per `rmsk_name` over its distinct raw `(rmsk_class, rmsk_family)` labels, weighted by
record count. Class resolves first, family within the winning class.

1. Strip a trailing `?` from every class and family token. A name whose records carried any `?`
   gets `has_uncertain_source = true`.
2. A family token equal to its class token, or empty, means the run gave no family (UCSC copies the
   class into the family column for those rows). Such labels vote for the class and abstain from the
   family vote.
3. Class: the class with the most records wins. Family: among specified families within the winning
   class, the one with the most records wins. A name with no specified family anywhere publishes
   `canonical_family = canonical_class`, the RepeatMasker convention.
4. A tie at either rank publishes `unresolved` at that rank and below.

A refinement-aware variant, where a family token extending another with `-` outranks the coarser
token, would be `taxonomy_rule_v2` and waits for a measured source in which the coarse token holds the
majority. mm39's three parent/child competitions (`MER53`, `UCON44`, `X4b_DNA`) resolve to the specific
token by count (milestone 2 ruling H7).

Rank-specific statuses, chosen by the most consequential step that fired:
`class_status` in {`concordant`, `resolved_uncertainty_suffix`, `resolved_majority`, `unresolved`};
`family_status` in {`concordant`, `resolved_uncertainty_suffix`, `resolved_unspecified`,
`resolved_majority`, `unspecified`, `unresolved`}. Precedence: majority over unspecified over
uncertainty suffix over concordant.

Examples from mm39: `MER63C` (hAT-Tip100 273, hAT-Blackjack 99) → family `resolved_majority`,
share 0.734; `Eutr2` (MULE-MuDR 40, DNA-only 7) → family `resolved_unspecified`; `Eulor5B`
(Crypton-A 34, `DNA?` 1) → class `resolved_uncertainty_suffix`, family `resolved_unspecified`;
`MER124` (DNA 247, `DNA?` 2) → class `resolved_uncertainty_suffix`, family `unspecified`,
canonical `DNA/DNA`.

## Deliverables

- `src/20_build_taxonomy.py` (called from a `src/20_build_taxonomy.sh` stage): reads
  `rmsk_taxonomy`, applies the rule, writes `tables/taxonomy_canonical.tsv` with columns
  `rmsk_name, canonical_class, canonical_family, class_status, family_status,
  class_majority_share, family_majority_share, label_count, record_count, record_length_sum_bp,
  median_divergence_pct, has_uncertain_source, has_multiple_labels`, one row per name, sorted by
  name. `median_divergence_pct` comes from `rmsk_records`.
- `tables/taxonomy_resolution_report.tsv`: one row per name with `label_count > 1`:
  `rmsk_name, rmsk_labels` (`class/family=count;...`, counts descending), `rule_fired`,
  `canonical_class, canonical_family, class_status, family_status`.
- Manifest identity carries `taxonomy_rule_version = "taxonomy_rule_v1"`.
- `tests/fixtures/taxonomy/dfam_snapshot.tsv`: the Dfam API lookup for the multi-label names,
  copied from `docs/_internal/redesign-2026-09/taxonomy/dfam_lookup_20names.tsv`, with a
  `fetched_on` column (2026-09-16) and the Dfam version endpoint response recorded in a sibling
  `dfam_snapshot.provenance.json`.
- Test `tests/checks/core/taxonomy_dfam_agreement.py`: for every name in the snapshot,
  `canonical_class == dfam_repeat_type` and, where Dfam names a subtype,
  `canonical_family == dfam_repeat_subtype`; every snapshot name appears in the resolution report
  and every report name appears in the snapshot. A disagreement fails with the name and both
  labels.
- Rule fixtures under `tests/fixtures/taxonomy/`: synthetic `rmsk_taxonomy` inputs covering each
  status, a class-level competition, a two-way tie (expects `unresolved`), a name mixing `?`
  and unspecified family, and a parent/child family competition where the specific token holds the
  majority (`MER53` shape). Expected outputs authored by hand.
- Rollup rule documented in `docs/OUTPUTS.md`: family and class rollups join through
  `taxonomy_canonical`; a name unresolved at a rank carries an empty canonical label there, and every
  rollup at that rank names it `unresolved/<rmsk_name>`, one bucket per name, distinct from
  RepeatMasker's literal `Unknown` (milestone 2 ruling M2).

## Acceptance

- 18,484 rows in `taxonomy_canonical`; 20 rows with `has_multiple_labels`; 0 rows `unresolved` at
  either rank; 7 `family_status = resolved_majority`, 5 `resolved_unspecified`, 5
  `resolved_uncertainty_suffix`, 3 `unspecified`; every one of the 20 has `canonical_class = DNA`;
  minimum `family_majority_share` among resolved_majority rows is 0.734.
- Dfam agreement test: 20 of 20 pass.
- Fixture: a name with two labels and one count contributes once to its family rollup.
- Rule fixtures pass; the tie fixture publishes `unresolved` and `family.bed` (phase 4) names it
  `unresolved/<rmsk_name>`.

Review focus: the rule is total and deterministic over any input; raw tables stay untouched;
the build reads no network and no Dfam data; the snapshot is test evidence only. Reviewers: codex,
Opus and a `divergent` pass on the rule (milestone 2 ruling M7).

Deferred, recorded: extending the Dfam snapshot from the 20 multi-label names to every
`interspersed` name (one clade-scoped API pull) so the agreement test covers concordant names too.
The agreement test asserts set equality between the resolution report and the snapshot, so a source
whose multi-label names outgrow the snapshot fails the check until the snapshot covers them; that
assertion is the admission gate for a new source or assembly.
