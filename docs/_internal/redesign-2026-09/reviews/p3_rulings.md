# Phase 3 rulings (orchestrator, 2026-09-16, implementer tree over `4eb31f9`)

Inputs: `p3_codex.md` (BLOCKING: B1 to B3, A1 to A3), `p3_divergent.md` (H1 to H5, M1 to M7, L1 to L3),
`p3_opus.md` (appended when it lands). The rule is unpublished, so design corrections land now through
`prompts/p3_fix.md` (unit `te-tracks-p3-fix`); the plan file `13_phase3_taxonomy.md` is rewritten to the
corrected contract and stays authoritative.

## Codex

- **B1 winning class without a specified family.** Accept: publish the class token with `family_status =
  unspecified`; losing classes contribute no family evidence. Fixture row and OUTPUTS sentences follow.
- **B2 Dfam release response.** The taxonomy evidence holds per-family versions and the fetch date and no release
  response; no network here. Recorded deferral: the provenance file states what was retained and names the release
  response as the item the next refresh adds. Plan bullet amended.
- **B3 manifest identity.** Deferred to phase 7, which owns the manifest; plan bullet amended.
- **A1 table integrity.** Accept: check 30 recomputes every row from `rmsk_taxonomy` and the parquet and compares
  all columns exactly.
- **A2 diagnostics first.** Accept.
- **A3 stale paths.** Plan synced to `src/lib/build_taxonomy.py` and `31_taxonomy_dfam_agreement.py`.

## Divergent

- **H1 record weighting rewards fragmentation.** Accept: votes weight by RepeatMasker instance (distinct
  `rmsk_instance_id` among a label's records). `rmsk_taxonomy` gains `instance_count`; the rule, the shares and the
  report use it; record counts stay as context. Every mm39 winner is unchanged; the acceptance minimum share moves to
  the measured instance-weighted value recorded in `tests/expectations/mm39/taxonomy_census.tsv`.
- **H2 gate keyed on raw spelling; refresh path breaks literals.** Report membership stays defined over distinct raw
  labels, since the `?` decisions are what the report exists to show. Check 31 becomes a subset gate: every report
  name has a snapshot row, every snapshot name exists in the canonical table and agrees with Dfam; count and date
  come from the fixture and provenance, the count from the expectations file. The snapshot may then grow to
  concordant names without touching the check.
- **H3 oracle one class wide; type compared unguarded.** Guard the type comparison like the subtype. Record that the
  snapshot speaks to class `DNA` alone and that `Unknown` and `Unspecified` have no Dfam counterpart.
- **H4 median float noise.** Round `median_divergence_pct` to two decimals (source carries one; even-count midpoints
  need two) and compare exactly in check 30.
- **H5 one token for two ranks, carrying the separator.** Tokens spelled apart by rank and free of separators:
  `unresolved_class_<rmsk_name>` and `unresolved_family_<rmsk_name>`. `family.bed` names, GTF `class_id` and
  `family_id`, and the triple GeneID use them positionally. Supersedes the milestone 2 spelling.
- **M1 share denominators.** Keep the two plurality shares with their stated denominators and add
  `family_support_share`, the winning family's instances over every instance vote of the name.
- **M2 plurality named majority.** Rename the status and share columns: `resolved_plurality`,
  `class_plurality_share`, `family_plurality_share`.
- **M3 hg38 `?` families.** Recorded in the deferred list: size the `?`-family footprint before admission.
- **M4 census hardcoded.** Accept: the phase 3 census lives in `tests/expectations/mm39/taxonomy_census.tsv`; check 30
  reads it, including the zero unresolved counts.
- **M5 four spellings of no family.** OUTPUTS names them all.
- **M6 family token unique within class only.** OUTPUTS states it.
- **M7 `rule_fired` carries no information.** Column renamed `rule_version`.
- **L1** report membership over raw labels is the audit intent; stated in OUTPUTS. **L2** the pure function is total
  and the build validates its inputs; stated. **L3** ties are decided on integer instance counts; shares are display;
  stated.

## Opus (FAIL; B1 to B3, A1 to A5)

Independent re-derivation of all rows from `rmsk_taxonomy` alone: zero mismatches; digest parity with the
orchestrator's build; check 30 shown to pass on a corrupted single-label row.

- **B1** same defect as codex B1; fixed as ruled.
- **B2 table integrity for every name.** Accept as blocking: check 30 recomputes every row and compares all columns.
- **B3 provenance residue.** Accept: the file carries `version_evidence` and the release-response keys and check 31
  asserts every key with a named diagnostic (also A5).
- **A1 median digits.** Rounded to two decimals, the exact precision of a median over one-decimal values.
- **A2** as codex A2. **A3 weighting incidentally guarded.** Accept: one rule fixture where record count and length
  would elect a different winner than instances, so the instance weighting is pinned as behaviour.
- **A4 degenerate inputs poison the name.** Recorded; the build rejects them upstream and the pure function stays total.

## Orchestrator verification of the fix (`te-tracks-p3-fix`)

Ten core checks pass. Every table other than `rmsk_taxonomy.tsv` and the two taxonomy outputs is byte-identical
to the milestone 2 build; new digests `rmsk_taxonomy.tsv` 26a9110f…, `taxonomy_canonical.tsv` a3663b64…,
`taxonomy_resolution_report.tsv` 1f8c068f…. An independent instance-weighted implementation of the four rule
sentences, written from the plan and run over the parquet alone, reproduces all 15 columns on all 18,484 rows.
Census as measured: 20 multi-label names, 7 / 5 / 5 / 3 family statuses over them, 6 class
`resolved_uncertainty_suffix`, 1,095 / 17,372 family `concordant` / `unspecified`, minimum plurality share 0.840
(`MER63C`), 4,727,623 label instances over 18,504 triples, no tie. One README truth-table row
(`tests/fixtures/taxonomy/weighting_context.tsv`) rides the phase 4 prompt. A codex re-review of the fix
(`prompts/p3_review2.md` → `reviews/p3_codex2.md`) closes the round.

## Codex re-review of the fix (`p3_codex2.md`; PASS WITH ADVISORIES)

Every earlier finding is closed except the refresh-policy residue of H2. Rulings on the three advisories:

- **A1 endpoint literals and the null release response in check 31.** Accepted residue for the pinned snapshot: a
  refresh that records the release response updates that one assertion in the same change as the snapshot.
- **A2 bare `unresolved_family_<name>` in the phase 4 section of OUTPUTS.md.** Phase 4 rewrites that section and
  emits the token positionally inside `<class>/<family>`; the prompt says so explicitly.
- **A3 a name carrying `/` would put a separator inside an unresolved token.** `rmsk_name` rejects `/` at build time
  alongside `|`, `:` and whitespace, with a fixture row; the component alphabet becomes `[A-Za-z0-9_.+?()-]+` and
  emitted ids add `|`, `:` and `/` as separators. Lands in phase 4, which owns the alphabet validation.
