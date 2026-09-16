# Milestone 5 rulings

Reviews after the phase 5 commit `9ac66fb`: `m5_codex.md` (consumer seam; BLOCKING, B1 and A1 to A3),
`m5_opus.md` (numbers and fixtures) and `m5_divergent.md` (unstated assumptions). Every finding below carries a
ruling; the package changes land in one fix round (`prompts/m5_fix.md`), the plan and prompt changes are the
orchestrator's.

## Codex (consumer seam)

- **B1 the registration lacks the keys TEsingle, TElocal and a Stellarscope instance run emit.** Accept. The ADR5
  consult (section 4) asks for the exact TEsingle output tuple to be registered and names the instance run a feature
  level of its own; phase 4 registered five spellings, and the seam probe finds zero exact matches for
  `<alias>:<name>:<family>:<class>`, `<name>:<name>:<family>:<class>` and `I|mm39|<id>` on 1,000 sampled rows of
  every export. Fix: `export_feature_members` registers eight rows per selected record, in this order:
  (`record`, `rmsk_record_id`), (`record`, record alias), (`record`, `<alias>:<name>:<family_id>:<class_id>`),
  (`subfamily`, `rmsk_name`), (`subfamily`, `<name>:<name>:<family_id>:<class_id>`), (`family`, family bucket),
  (`taxonomy_triple`, triple), (`instance`, `I|mm39|<rmsk_instance_id>`), where `family_id` and `class_id` are the
  canonical tokens the GTFs emit. The level vocabulary gains `instance`. mm39 targets: 30,119,592 rows; distinct
  features at `instance` 3,152,636; every other distinct count, every export byte and `exports.tsv` unchanged. Check
  41 asserts the eight slots and joins each GTF's composed TEsingle tuple and `record.gtf`'s `instance_id` to the
  registration; the check 42 expected registration is re-authored by hand; consumer checks 11, 12 and 13 join every
  parser key to the fixture registration at its level. `docs/OUTPUTS.md` states the eight spellings and, for
  `instance`, that a mixed-name instance (mm39: 30,569 instances holding 95,830 records) attributes to a subfamily
  only through an explicit allocation, membership supplying possible support. Plan 14 states the eight rows; plan 17
  records the re-measured registration size.
- **A1 one row per feature and record excludes phase 8's split pieces.** Accept. `docs/OUTPUTS.md` states
  uniqueness over the key plus `(block_start_1, block_end_1)`, `full` registering one block per member; plan 18 and
  `p8_impl.md` carry the same sentence.
- **A2 `ucsc`, `interspersed` and `full` hardcoded; the inventory writer replaces `exports.tsv`.** Accept for phases
  6 and 8. `p6_impl.md`: the namespace stage writes the inventory as the union of the seven existing rows and the
  fourteen renamed rows, sorted by `export_path`, through an inventory function that takes rows; check 41's path-set
  and namespace assertions extend to the three namespaces, so the phase 6 touch list gains that check. `p8_impl.md`:
  the child exporter takes universe, variant and block bounds as explicit inputs and writes the child build's own
  inventory.
- **A3 `export_contracts` lacks the semantic contract.** Accept for phase 7: per export path the attribute-to-source
  mapping, the output key each named consumer constructs, the selectable levels and the coordinate convention, all
  sourced from the one dict in `build_exports.py`.
- **Conservation note: a mixed instance copied into both subfamilies sums to 14.** Defended in the consult (section
  5) and restated in the `instance` contract sentence under B1.

## Divergent (unstated assumptions)

- **H1 the compat universe misses the legacy selection by 1,235 records (`LFSINE_Vert`).** Rejected on its premise;
  the hazard it exposes is accepted. The directory it measured, `_scratch/te-tracks-audit/refroot/te_mm39/te_mm39_20260917`,
  was built on 2026-09-15 by `6ff3ee9-dirty` with `exclude_family_prefix: "tRNA-"` as the audit's changed-policy
  experiment of the legacy release mechanics (its sibling archive, built clean, holds 3,762,401 loci without
  satellites; neither is the lab's published annotation). The legacy rule is `^tRNA` in `config/mm39.env`,
  `src/10_build_master.sh` and `docs/PROVENANCE.md` on `main`, which removes `LFSINE_Vert` 1,235, `MamSINE1` 925 and
  `AmnSINE2` 388 and yields 3,799,629, the count the legacy PROVENANCE measured on the packaged annotation and the
  count `compat_tetranscripts_mm39` reproduces (audit §3, m2 Opus). The interspersed-to-legacy delta of 34,680 stands.
  The orchestrator moved the experiment directories to `_scratch/te-tracks-audit/legacy_release_experiments/` so no
  later reviewer or the phase 7 `--root` smoke reads them as a release; the phase 9 reconciliation reads the host
  refcache alone and exits 3 in-container, as planned.
- **H2 one universe serves every consumer; 14761's ATAC route needs the full catalog and never registers.** Accept for
  phase 6, subject to the owner (it widens ADR 3's export matrix): `exports/<ns>/all_rmsk/full/record.bed` in the three
  namespaces, registered under universe `all_rmsk`, level `record`, grammar `rmsk_record_id` (5,320,771 rows); the
  inventory grows to 24 rows; the consumer contracts table names the ATAC route and its export.
- **H3 an 11-row parser pass authorizes a 3,764,949-row export; Stellarscope projects to 10.2 GB.** Accept for phase 9:
  `docs/RUNBOOK.md` states a measured floor per consumer, projected from a 50,000-row head of `record.gtf` through
  Stellarscope's `IntervalTreeAnnotation` and TElocal's `TEindex`, beside the producer's 5.5 GB.
- **H4 two record spellings at one level double a record-keyed rollup; the proofs filter the alias out silently.**
  Accept, with M3: the registration gains a `key_grammar` column naming how each spelling is constructed
  (`rmsk_record_id`, `record_alias`, `four_tuple`, `rmsk_name`, `family_bucket`, `taxonomy_triple`, `instance_alias`);
  uniqueness holds over `(universe_name, variant, feature_level, key_grammar, emitted_feature_id, rmsk_record_id,
  block_start_1, block_end_1)`; both conservation checks select the grammar explicitly and assert three grammars at
  level `record`; the contract states that a run's matrix binds to one `(feature_level, key_grammar)`, that counts join
  the registration through the run's measured feature ids at that pair, and that a traversal from records to the
  registration without a matrix join lists possible support and is never summed.
- **M1 `CATALOG_ID` reaches no public document.** Accept for phase 7: `docs/DECISIONS.md` entry 7 publishes both ids
  and the ledger key `(te_catalog_id, rmsk_record_id)`; the README names both.
- **M2 `family.bed` and `taxonomy_triple.saf` meet no consumer fixture; the doubled-name case.** Accept: a new consumer
  check reads `family.bed` through bedtools and the triple SAF through a SAF column reader, asserts `TwoLab`'s three
  records carry one GeneID (`TwoLab:hAT-Tip100:DNA`) and one bucket (`DNA/hAT-Tip100`), and joins both to the
  registration; the featureCounts execution check counts the triple SAF when the executable exists.
- **M3 the TEtranscripts group from `record.gtf` equals the triple SAF GeneID byte for byte.** Defended after H4 and
  codex A3: the same grammar over the same records is the same feature space by construction, the registration row
  carries `key_grammar = taxonomy_triple` once, and the manifest's `export_contracts` list the grammars each file
  supports.
- **M4 the checkouts sit past their tagged releases; `makeRmsk` and `split_count_10X_data` changed.** Accept: every
  support line reports the declared version and `git describe --tags --always`; the consumer contracts table names the
  checkout commit each fixture authorizes and that an installed release may differ in those entry points; the phase 9
  runbook pins consumer installs to the checkout commits or records the divergence.
- **M5 the allocation fixture asserts conservation alone.** Accept: it asserts the EM fixed point, 6.0/3.0 for 4/2 and
  4.5/4.5 for 3/3, within 0.05, and still writes the observed allocation.
- **M6 one barcode per fixture; the threshold audit is unexercised.** Accept as contract wording: the fixtures carry one
  barcode; whitelist, empty-cell and per-barcode threshold behaviour are the consumer's audit, named in the phase 9
  handoff.
- **M7 no consumer check is required, so an all-unsupported run exits 0.** Accept: the checks the plan calls always
  supported become `.required.py` / `.required.sh` (inventory, IRescue identity, TEsingle, TEtranscripts/TElocal,
  MATES, bedtools, samtools); the Stellarscope defect gate, `chrcat`, the two absent executables and DuckDB stay
  optional.
- **M8 split pieces violate the published unique key.** Defended by codex A1 (block columns in the key).
- **L1 the clipped BED score.** Accept: `docs/OUTPUTS.md` names the clipped score a display convention and
  `rmsk_records.sw_score` the filterable value.
- **L2 no real parser has read an `unresolved_*` token.** Defended by the codex seam probe (`m5_codex.md`, `seams.py`):
  every vendored parser preserves the tokens in position; one bucket per unresolved name is the phase 3 design.
- **L3 the MATES index is a row ordinal.** Accept as wording: the pair is fixture-only, its index the fixture roster's
  ordinal, and a MATES release export waits for a named consumer.
- **L4 every expectation descends from the builder.** Accept for phase 9 with the H1 correction: plan 19 names the
  oracles the builder did not produce (the UCSC `rmsk` table from phase 1, the pinned Dfam snapshot, the host legacy
  release for the compat count).
- **L5 the milestone prompts are stamped after the commit they cite.** Process; the milestone commit carries them.

## Opus (numbers and fixtures)

PASS WITH ADVISORIES. Every phase 3 to 5 number re-derived by an independent route agrees (taxonomy table
byte-identical, all seven export digests reproduced from an independent byte stream, registration content digest
reproduced, stages 20 and 30 rebuilt byte-identical, every fixture BAM recounted); thirteen mutations and two resolver
probes each failed their check. Advisories:

- **A1 check 14 never rebuilds the fixture, so in isolation it validates stale bytes.** Accept: it calls
  `build_fixture()` first, as checks 10 to 13 do.
- **A2 and A3 the MATES scratch `mkdir` and the literal `2` in check 12.** Accept; already items of the fix (the
  orchestrator's phase 5 notes).
- **A4 check 30 recomputes the table through the production resolver, so a rule defect firing on no mm39 row passes
  it; `rule_cases.tsv` is the rule's oracle.** Accept as contract wording: `docs/OUTPUTS.md` states which check proves
  what.
- **A5 three README sentences still describe the phase 2 build.** Accept: the build and checks paragraphs name
  `exports/`, the taxonomy and export checks and the phases still outstanding.
- **A6 five consumer checks cannot fail here.** Defended: the README row names them and the phase 9 host run is where
  they first execute (divergent M7 makes the always-supported checks required, so an environment regression fails
  the runner).
- **A7 bytecode residue under the Stellarscope checkout, written at 15:11:09 by a concurrent process.** The divergent
  reviewer's memory measurement imported the annotation package without `PYTHONDONTWRITEBYTECODE`; the orchestrator
  removed the directory (gitignored upstream, every checkout clean). Later reviewer prompts carry that variable.
