# Phase 3 review: what the rule assumes (divergent)

Read on `redesign-2026-09`: the phase 3 plan, the milestone 2 rulings, divergent H7, the `taxonomy/` evidence, the
implementation and the three phase 3 checks; measurements are read-only passes over the `te_mm39` build tables. Step 3
taken as ruled: a winning class with no specified family publishes `canonical_family = canonical_class`.

## High
- [H1] **Record-count weighting is a fragmentation weighting, and the acceptance's tightest number is its artifact.**
  `13_phase3_taxonomy.md:11-12` weights by record count without naming an alternative. Measured across the five names
  with a real family competition, the losing label is always the more fragmented: `MER63C` hAT-Blackjack 99 records
  over 47 instances (2.11 per instance) against hAT-Tip100 273 over 246 (1.11), a 1.90x inflation of the loser. The
  pinned minimum `family_majority_share = 0.734` (`:78`, `30_taxonomy_canonical.py:50`) is 0.840 by instance and 0.795
  by bp. Failure: the bias runs one way, toward the coarse-labelled, degraded copies, so the first library where a
  coarse parent holds a fragmented record majority publishes `TcMar` while losing the insertion vote, and
  `rule_cases.tsv:16` already pins `DNA/hAT=7;DNA/hAT-Blackjack=3` → `hAT resolved_majority` as expected;
  `m2_rulings.md:34-39` answered H7 on refinement alone. Lands: the rule section states the weighting as a decision
  with these numbers, or weights by `rmsk_instance_id`.
- [H2] **The admission gate keys on raw spelling, so it fires on cosmetic changes and its own refresh path breaks
  it.** `label_count` counts distinct pairs *before* `?`-stripping (`build_taxonomy.py:38,43`), so 5 of the 20
  snapshot names (`Eulor8`, `Eutr15`, `Eutr16`, `MER121`, `MER99`) are in the report only because a `?` variant
  exists, though they are unanimous after normalization. Failure: one added `DNA?` record on any of the 18,478
  class-concordant names flips it into the report, `31_taxonomy_dfam_agreement.py:48` fails set equality, and `core`
  goes red for a name whose canonical label never moved. Reverse direction: `:26` asserts `len(snapshot) == 20`,
  `:28`/`:31` assert `fetched_on == "2026-09-16"` and `:30` pins Dfam's URL shape, so refreshing the snapshot — the
  update path at `taxonomy/README.md:16-17` — fails the test until four literals are hand-edited. Lands: check 31
  reads count and date from the snapshot and provenance, asserts report ⊆ snapshot, and keeps the count in
  `tests/expectations/mm39/` beside phase 2's.
- [H3] **The oracle is one class token wide.** Measured: all 20 snapshot rows carry `dfam_repeat_type = DNA`; the test
  has ever compared 1 of the 16 canonical class tokens, 10 of the 59 canonical `<class>/<family>` labels, 6,517 of
  5,320,771 records. Failure: a systematic single-label misclassification — the whole 1,095-name family-`concordant`
  set — is unchecked by construction. The recorded extension (`:88-92`) cannot close it either: `31:41` compares the
  type unconditionally while `:42` guards the subtype, so the first Dfam entry with an empty type fails a name nothing
  is wrong with, and 53 `Unknown` plus 1 `Unspecified` canonical class (5,884 records) have no Dfam counterpart.
  Lands: guard the type comparison like the subtype; record which class tokens the oracle can speak to before
  scheduling the pull.
- [H4] **`median_divergence_pct` publishes binary-float noise and is checked looser than it is written.** The source
  carries one decimal (measured: every `divergence_pct` equals its 1-dp rounding). The published column carries 15
  decimals for 692 names, 16 for 72, 17 for 1 — `7.949999999999999`, `0.30000000000000004` — from even-count medians,
  and it is the one float left unrounded while both shares are rounded (`build_taxonomy.py:52,78`). Failure: `30:76`
  re-derives it with `assert_series_equal` at default `rtol=1e-5`, eleven orders looser than those digits, so a numpy
  line resolving mean-of-two differently passes every check while changing the bytes, the table digest and
  `CATALOG_ID` — H6's exposure inside a canonical table. It also mixes label populations (`Eulor5B`: Crypton-A 27.45
  against the `DNA?` record's 20.40) and couples the table to `rmsk_records` (`:109-114`). Lands: round to source
  precision and assert exactly.
- [H5] **`unresolved/<rmsk_name>` is one string doing duty at two ranks, carrying the separator that distinguishes
  them.** `m2_rulings.md:28-31` and `OUTPUTS.md:179-183` give class and family buckets the same spelling; `32:104-107`
  pins `unresolved/class_tie` as both. Failure: `family.bed`'s name is `<canonical_class>/<canonical_family>`
  (`OUTPUTS.md:262`), so splitting a family bucket on `/` to recover its class invents a class named `unresolved` —
  also a status value in the same schema — and a class-rank table stacked on a family-rank one merges ranks on an
  identical key. `taxonomy_triple.saf` (`:265`) emits `<name>:unresolved/<name>:unresolved/<name>` for a class tie,
  the only GeneID whose class field carries a `/`, and the phase 4 alphabet admits `/` inside a name (mm39: zero names
  carry `/`, `?` or `:`, measured). Lands: spell the ranks apart before phase 4 writes it.

## Medium
- [M1] **The two share columns have different denominators, and the family one reads 1.000 for contested names.**
  `family_majority_share` divides by specified-family votes inside the winning class (`build_taxonomy.py:78`,
  disclosed `OUTPUTS.md:140`); `class_majority_share` divides by all records. Measured: `Eutr2` publishes 1.000 with
  40 of 47 records on MULE-MuDR (0.851), `MER136` 1.000 vs 0.913; fixtures pin 0.571 where 4 of 13 records carry hAT
  and 0.700 where 7 of 30 do (`rule_cases.tsv:20,23`). Failure: filtering `>= 0.9` for confident families keeps a name
  at 0.851 real support. Lands: add `family_record_support`.
- [M2] **`resolved_majority` names a plurality.** The vocabulary promises a majority (`:30-34`); the code takes the
  argmax. `rule_cases.tsv:26` pins `class_majority_share = 0.444` with `resolved_majority`. Failure: a three-way hg38
  class split publishes `resolved_majority` at 0.40 — the winner with less support than its opponents combined — and a
  reader trusting the word never sees it. Lands: rename it `resolved_plurality`, or gate the status on share above one
  half.
- [M3] **hg38's `?` families enter through the one door with no gate on it.** A new `?` *class* stops at phase 2's
  disposition gate; a `?` *family* under an existing class touches no gate — it adds a distinct triple, so the name
  gains `has_multiple_labels`, enters the report, breaks `31:48`, and publishes `resolved_uncertainty_suffix`, an
  asserted token from records RepeatMasker marked uncertain. mm39's whole `?` footprint is 54 records (0.001%) over 10
  names deciding 10 of the 20 report rows; zero mm39 names are wholly `?`, so the branch publishing a clean label for
  a never-asserted name rests on one fixture (`rule_cases.tsv:5`). Lands: size hg38's `?`-family count before `:88-92`
  promises set equality as the admission mechanism.
- [M4] **The class arm has never fired in production.** Measured: `class_majority_share < 1` for 0 of 18,484 names, 0
  names span two `?`-stripped classes, `class_status` is `concordant` (18,478) or `resolved_uncertainty_suffix` (6)
  and never `resolved_majority` or `unresolved`. The class vote, the cross-class abstention the step-3 ruling governs,
  and every `unresolved` branch are fixture-only, while `30:37` asserts no `unresolved` exists and `:34,43-50`
  hardcode the census phase 2 keeps in `tests/expectations/mm39/`. Failure: the first tied name on any source turns
  `core` red with no expectation file to move. Lands: move the phase 3 census into `tests/expectations/mm39/`.
- [M5] **The family rank has four spellings of "no family" across two vocabularies.** `<class>/<class>` from the
  abstention convention (110 interspersed names, 24,652 records; `LTR/LTR` alone 18 names and 15,284 records, the ERV
  space H4 called the story's centre), `Unknown/Unknown` (53 names, 5,786), `Unspecified/Unspecified` (1 name, 98),
  `unresolved/<name>`. The plan contrasts only against `Unknown` (`:68-71`). Failure: dropping unclassified families
  with `family != "Unknown"` keeps 15,284 `LTR/LTR` records. Lands: `OUTPUTS.md` names all four.
- [M6] **Abstention by string equality makes one family token mean two things.** The test is `fam and fam != cls`
  (`build_taxonomy.py:68`). mm39 carries `SINE/tRNA` (1,235 records, a real family) and class `tRNA` with family
  `tRNA` (49 names, 3,508 records, an abstention), so `canonical_family == "tRNA"` spans 50 names and 4,743 records
  whose meaning lives in the class column. Failure: a group-by on `canonical_family` alone pools tRNA-derived SINEs
  with tRNA gene copies, and a library writing a class variant into the family column escapes the test and wins the
  vote. Lands: `OUTPUTS.md` states `canonical_family` is unique only within `canonical_class`.
- [M7] **`rule_fired` carries no information.** Every row gets the module constant (`build_taxonomy.py:134`, `30:53`):
  the one column named for a rule step cannot distinguish two rows. Lands: drop it, or name the steps that fired.

## Low
- [L1] **`has_multiple_labels` overstates disagreement in the table a human reads** — pre-strip, so 5 of the 20
  flagged names are unanimous after normalization, and `has_uncertain_source` is a name-level boolean naming neither
  the rank nor the 54 records.
- [L2] **One input, two behaviours.** `resolve` degrades nonpositive counts and empty classes to `unresolved`
  (`build_taxonomy.py:45-46`) while `build_taxonomy` raises (`:107`), so `rule_cases.tsv:29-31` pins three branches no
  build can reach.
- [L3] **Rounded decisions.** Shares are `round(x, 3)` on binary floats, so a 0.5005/0.4995 near-tie prints as
  0.5/0.5, indistinguishable from the tie that publishes `unresolved`.

## Defended already
- `?` classes cannot leave the default universe silently — `m2_rulings.md:11-16`, `config/mm39.classes.tsv`.
- One unresolved bucket per name, so unrelated names never pool — `m2_rulings.md:28-31`.
- The three mm39 parent/child competitions resolve to the specific token — `m2_rulings.md:34-39`, `rule_cases.tsv:15`.
- The build reads no Dfam data and no network: two table reads — `build_taxonomy.py:96-110`, `31:32`.
- Determinism: permutation invariance and byte-identical rebuild from reversed inputs — `32:40-41,121-125`.
- Totality over empty input, zero and negative counts, empty class — `rule_cases.tsv:28-31`, `OUTPUTS.md:161-163`.
- `DNA/DNA` for `MER124`, `MER131`, `UCON2` corroborated; Dfam names no subtype — `taxonomy/README.md:10-12`.
- R `make.names()` injective over the published 59 labels plus `unresolved/<name>`: zero collisions (measured).

Predicted first bite: H2 — the next library refresh moves a `?` spelling on one of 18,478 concordant names, set
equality reddens `core`, and the documented fix fails four literals in the same check.





