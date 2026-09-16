# te-tracks milestone 5 fix: register the keys consumers emit

You are the implementer for the milestone 5 fix round of the te-tracks redesign. Working directory (absolute):
`/workspaces/Meta-Aging/01_modules/te-tracks`, git branch `redesign-2026-09`, HEAD `9ac66fb`. Phases 0 to 5 have
landed. Read `AGENTS.md`, `src/lib/build_exports.py`, `tests/checks/core/4*`, `tests/fixtures/exports/**`,
`tests/lib/consumers.py`, `tests/checks/consumers/1*`, `docs/OUTPUTS.md` (the export and registration sections and
the consumer contracts table).

## Read first
1. `docs/_internal/redesign-2026-09/reviews/m5_rulings.md` (every item below is a ruling there) and the reviews it
   rules on: `reviews/m5_codex.md`, `reviews/m5_opus.md`, `reviews/m5_divergent.md`.
2. `docs/_internal/redesign-2026-09/consults/ADR5_consult.md` sections 4 and 5 (exact output tuples; the
   conservation rule; mixed instances need an allocation).
3. `docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/14_phase4_exports.md` (amended: eight registration
   rows per record).
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments" (binding).

## Facts (measured by the orchestrator on the current build)
- Reviews ruled in `reviews/m5_rulings.md`: codex B1 and A1 (items 1 to 5), divergent H4/M2/M4/M5/M6/M7/L1/L3
  (items 1, 2, 8 to 12), Opus A1 to A5 (items 6, 13 to 15).
- `interspersed` selects 3,764,949 records over 1,220 names and 3,152,636 distinct `rmsk_instance_id` values;
  30,569 instances hold records of more than one name (95,830 records); 1,224,713 records carry `sw_score > 1000`.
- The registration holds 18,824,745 rows (five per record); `tables/exports.tsv` sha256
  `55a1eb211f91c9ffb12c89b378aeecb9a538fd97ebeb4a20f85627bda9aef501`. The seven export files change by no byte in
  this round; `exports.tsv` stays byte-identical.
- The TEsingle and TElocal parsers emit `transcript_id:gene_id:family_id:class_id`; from `record.gtf` that is
  `<record alias>:<rmsk_name>:<family_id>:<class_id>`, from `subfamily.gtf` `<rmsk_name>:<rmsk_name>:<family_id>:<class_id>`,
  where `family_id` and `class_id` are the canonical tokens (unresolved rank tokens in position). A Stellarscope
  run with `--attribute instance_id` emits `I|mm39|<rmsk_instance_id>`.

## Items
1. **Eight registration rows per record with a `key_grammar` column** (`src/lib/build_exports.py`). Columns become
   `universe_name, variant, feature_level, key_grammar, emitted_feature_id, rmsk_record_id, block_start_1, block_end_1`.
   For every selected record, in this order (level / grammar / id):
   `record` / `rmsk_record_id` / the record id; `record` / `record_alias` / `R|mm39|…`; `record` / `four_tuple` /
   `<alias>:<name>:<family_id>:<class_id>`; `subfamily` / `rmsk_name` / the name; `subfamily` / `four_tuple` /
   `<name>:<name>:<family_id>:<class_id>`; `family` / `family_bucket` / `<class>/<family>`; `taxonomy_triple` /
   `taxonomy_triple` / `<name>:<family_id>:<class_id>`; `instance` / `instance_alias` / `I|mm39|<rmsk_instance_id>`.
   Validate the two tuples with `IDENTIFIER`. `distinct` gains `instance`; the summary line reports eight rows per
   record. The seven export streams and the inventory are untouched.
2. **Check 41** (`tests/checks/core/41_export_registration.py`): eight slots; `rows == 8 * len(records)` with each
   slot once per record; for each GTF, compose the TEsingle tuple from the four attributes of every row and assert
   the composed key is registered at that file's level with the row's `rmsk_record_id`; for `record.gtf`, assert
   every `instance_id` is registered at level `instance` with the row's record; the `instance` distinct count equals
   the number of distinct `rmsk_instance_id` values among the selected records (compute it from the parquet); the
   conservation selection selects `key_grammar` explicitly (`rmsk_record_id`, `rmsk_name`, `family_bucket`) in place
   of the implicit alias filter and asserts three grammars at level `record`; `30_registration_duckdb.py` carries the
   same explicit selection. Update the printed summary.
3. **Check 42 and its fixture**: re-author `tests/fixtures/exports/expected/export_feature_members.tsv` by hand with
   eight rows per fixture record (say so in your report; the orchestrator confirms independently); keep every other
   expected file byte-identical.
4. **Consumer checks join the fixture registration**: in `11_stellarscope_parser.py`, `12_tesingle_parser.py` and
   `13_tetranscripts_telocal_parser.py`, read `$TE_TRACKS_REFROOT/fixtures/consumers/tables/export_feature_members.tsv.gz`
   and assert every key the parser produced is registered at its level (Stellarscope `locus` at `record`,
   `instance_id` at `instance`; TEsingle and TElocal tuples at `record` or `subfamily`; the TEtranscripts triple at
   `taxonomy_triple`) and resolves to exactly the roster records that carry that feature. Add one helper in
   `tests/lib/consumers.py` for the join. `I|mm39|7` resolves to the two `SubB`/`SubB-int` records.
5. **Contract** (`docs/OUTPUTS.md`): the registration section states the eight spellings and their order, the
   `instance` level, the `key_grammar` column and its seven values, uniqueness over `(universe_name, variant,
   feature_level, key_grammar, emitted_feature_id, rmsk_record_id, block_start_1, block_end_1)` with `full`
   registering one block per member, and these sentences: a run's matrix binds to one `(feature_level, key_grammar)`;
   counts join the registration through the run's measured feature ids at that pair; a traversal from records to the
   registration without a matrix join lists possible support and is never summed; a mixed-name instance attributes
   to a subfamily only through an explicit allocation. The consumer contracts table gains, per consumer, the
   `(feature_level, key_grammar)` its key joins. The `feature_level` row lists the five levels.
6. **Phase 5 notes** (`reviews/p5_rulings.md`, end): `14_mates_parser.py` creates its scratch directory with
   `exist_ok=True` after removing any leftover, or uses `TemporaryDirectory` as checks 12 and 15 do; check 12 derives
   the flagged-molecule subtraction from `expected.json`'s `flagged_reads` instead of the literal `2`.
7. **Measure** the new registration size in bytes and the export writer's peak resident set (`/usr/bin/time -v` on
   stage 30 when available, otherwise report that it is unavailable); paste both. The orchestrator writes them into
   plan 17.
8. **Family and triple readers** (new `tests/checks/consumers/16_family_triple_readers.required.py`): `family.bed`
   through `bedtools intersect -wa -wb` over a `TwoLab` record returns bucket `DNA/hAT-Tip100` and over `DupX`/`DupY`
   both `LINE/L1`; `taxonomy_triple.saf` through a SAF column reader yields 8 distinct GeneIDs with
   `TwoLab:hAT-Tip100:DNA` on all three `TwoLab` rows (the doubled-name case aggregates once); both key sets join the
   fixture registration at (`family`, `family_bucket`) and (`taxonomy_triple`, `taxonomy_triple`). The featureCounts
   execution check counts the triple SAF as well when the executable exists.
9. **Checkout provenance in every support line** (`tests/lib/consumers.py`): `checkout_version` returns the declared
   version and `git describe --tags --always` (a read), for example `1.2.0 (v1.2.0-20-g26f36fb)`; the consumer contracts
   table names the checkout commit each fixture authorizes and states that an installed release may differ in the
   exercised entry points (`makeRmsk`, `split_count_10X_data`).
10. **EM fixed point** (`irescue_check`): assert A = 6.0, B = 3.0 for the 4/2 fixture and 4.5/4.5 for 3/3, within
    0.05, and keep writing the observed allocation. The check stays latent until `irescue` is installed.
11. **Required checks**: rename `00_tool_inventory`, `10_irescue_parser`, `12_tesingle_parser`,
    `13_tetranscripts_telocal_parser`, `14_mates_parser` to `.required.py` and `22_bedtools_exec`,
    `23_samtools_fixture_integrity` to `.required.sh`; `11`, `15`, `20`, `21`, `30` stay optional. Update
    `docs/OUTPUTS.md` and the README truth table where they name check files.
12. **Contract sentences** (`docs/OUTPUTS.md`): every fixture BAM carries one barcode, so whitelist, empty-cell and
    per-barcode threshold behaviour are the consumer's audit; the clipped BED score is a display convention and
    `rmsk_records.sw_score` the filterable value (32.5% of interspersed records exceed 1,000); the MATES pair is
    fixture-only, its index the fixture roster's ordinal, and a MATES release export waits for a named consumer.
13. **Check 14 rebuilds first** (`14_mates_parser`): call `build_fixture()` at the top of `check()` as checks 10 to 13
    do, so the check validates the bytes it just built.
14. **Which check proves what** (`docs/OUTPUTS.md`, taxonomy section, one or two sentences): check 30 proves the
    published table equals the rule's output on every row; `tests/fixtures/taxonomy/rule_cases.tsv` through check 32
    proves the rule itself, including cases mm39 never exercises (ties, plurality, weighting).
15. **README** (`README.md`): the build and checks paragraphs name `exports/` among the build outputs, the taxonomy
    (30 to 32) and export (40 to 42) checks among the core checks, and phases 6 to 9 as the outstanding ones; the
    truth table rows stay as they are except where item 11 renames a check file.

## Rules
- Touch only: `src/lib/build_exports.py`, `tests/checks/core/41_export_registration.py`,
  `tests/checks/core/42_exports_fixtures.py`, `tests/fixtures/exports/expected/export_feature_members.tsv`,
  `tests/checks/consumers/30_registration_duckdb.py` (the explicit grammar selection), `tests/lib/consumers.py`,
  `tests/checks/consumers/**` (renames included), `docs/OUTPUTS.md`, `README.md` (truth table rows that name the
  registration or the check files).
- No git writes (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too). No
  installs. No network. Never write into the refcache.
- Report a deviation instead of editing a number, an expectation or a plan file to fit.
- Prose and comments: affirmative, intent only, one line where one line does it.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
B="$TE_TRACKS_REFROOT/te_mm39/build"
sha256sum "$B/tables/exports.tsv"                      # before: 55a1eb21…
( /usr/bin/time -v bash src/30_build_exports.sh "$B" config/mm39.env ) 2>&1 | tail -25; echo "exit=${PIPESTATUS[0]}"
sha256sum "$B/tables/exports.tsv"                      # unchanged
zcat "$B/tables/export_feature_members.tsv.gz" | wc -l # 30119593 with header
zcat "$B/tables/export_feature_members.tsv.gz" | awk -F'\t' 'NR>1{n[$3]++} END{for(k in n) print k, n[k]}' | sort
zcat "$B/tables/export_feature_members.tsv.gz" | awk -F'\t' 'NR>1 && $3=="instance"{print $4}' | sort -u | wc -l   # 3152636
ls -l "$B/tables/export_feature_members.tsv.gz"
tests/run.sh core; echo "exit=$?"
tests/run.sh consumers; echo "exit=$?"
git status --short
for d in irescue stellarscope TEsingle MATES TEtranscripts TElocal; do git -C /workspaces/Meta-Aging/01_modules/.ref/$d status --short | head -3; done
```

## Final message
Every file created or changed; acceptance outputs verbatim; the registration size and peak RSS; the hand-authored
fixture rows; any deviation.
