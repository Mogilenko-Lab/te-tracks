# Milestone 2 re-review: numbers and fixtures (Opus)
Verdict: PASS WITH ADVISORIES

Every published number reproduced from the pinned `.out` bytes by code I wrote from the format
specifications in `docs/OUTPUTS.md` and plan files 11–12, importing nothing from `src/` or `tests/`.
All 24 columns matched on all 5,320,771 rows with zero mismatches; my rebuild is byte-identical to
the orchestrator's; every named failure mode has a check that fails when its subject is wrong.

## Blocking

- None.

## Advisory

- [A1] `tests/run.sh:50-55,80-82` — two runner behaviours have no check and no fixture: the
  dangling-symlink `fail` path and the `*.required.{sh,py}` unsupported-to-exit-1 path. No
  `.required.*` check exists anywhere in the tree, and nothing exercises `tests/run.sh` itself.
  Evidence: I injected both probes on a scratch copy — a dangling `90_dangling.sh` gave
  `fail  90_dangling.sh  dangling symlink`, exit 1; a `91_probe.required.sh` exiting 3 gave
  `unsupported`, exit 1; the same check without `.required` gave exit 0. Both mechanisms work; the
  suite does not demonstrate it. Fix: register a runner self-test check, or a fixture check
  directory the runner is pointed at, before phase 5 multiplies the modes.
- [A2] `tests/checks/core/23_records_fixtures.py:63-73` — the five single-row gate fixtures
  (`beyond_end.out`, `missing_chrom.out`, `spanning_instance.out`, `invalid_name.out`,
  `invalid_chrom.out`) are each passed with the 8-row `rmsk.tsv`, so each also violates the UCSC
  1:1 join. With the named gate removed the check still fails, but on the wrong message: e.g.
  removing the bounds gate yields `AssertionError: ('outside contig bounds', "UCSC join requires a
  1:1 match: {'chrom': 'chr10', …")`. Mutation detection holds; the fixture pins gate *ordering*
  (validate before merge) rather than isolating the gate. Fix: give each fixture a matching
  one-row UCSC table so the failure it proves is the one it names.
- [A3] `docs/DECISIONS.md:21` — "Each new assembly passes a class census before any biological
  universe publishes" overstates the gate. `build_universes.check_class_set` compares the class
  *set* against `config/mm39.classes.tsv`; the counts live only in
  `tests/expectations/mm39/class_census.tsv`, whose sole reader is `22_universes.py:23`.
  `docs/OUTPUTS.md:87-88` already states this precisely. Fix: say "class set" in DECISIONS.md.
- [A4] `docs/OUTPUTS.md:33-34` — two records carry `consensus_start_1 > consensus_end_1`:
  `L1MdFanc_II|chr1:9847889-9847905|-` (5301 > 5296) and `L1MdF_III|chr2:116363011-116363342|-`
  (2462 > 2461). Both are faithful to the source and satisfy the UCSC signed-encoding relation, and
  no stated contract requires ordering. Any consensus-match length derived in phase 3 or 4 goes
  negative on these two. Fix: state the absent ordering invariant beside the signed-column
  contract.
- [A5] `tests/expectations/mm39/universe_summary.tsv` — byte-identical to the build's
  `tables/universe_summary.tsv` (sha256 `66c205df…` for both), so the golden file's provenance is
  the artifact it gates. `22_universes.py:91` still compares an independently recomputed frame to
  it, which is the real oracle, and the numbers match `audit/policy_universes.tsv` measured in a
  prior session plus my derivation. Fix: keep the recompute comparison primary, and regenerate the
  expectation from a recompute rather than a copy.
- [A6] `tests/checks/core/` — no core check re-derives any of the 24 columns from the build's own
  `.out`, and `ucsc_rep_{start,end,left}` is never compared to `rmsk.txt.gz` at check time. A build
  whose consensus normalization was wrong is caught only through `source/qualification.md`:
  `tools/qualify_source.py` compares parsed `.out` fields against the UCSC table, and
  `11_source_qualification.sh:23-37` asserts zero disagreements plus `cmp` against the tracked
  report. That seam holds — I confirmed the report's stated encoding on all 5,320,771 rows — but it
  rests on a build product, so phase 7's manifest is what makes "this report describes these
  tables" checkable.

## Numbers recomputed

Route abbreviations: **P** = my own `.out` parser (15 fields plus optional `*`, parentheses stripped
from numeric fields only, `C`→`-`, `+`: start,end,left / `C`: left,end,start), **U** = my own
`rmsk.txt.gz` reader, **B** = my rebuild with `TE_TRACKS_SOURCE_CACHE`.

| quantity | published | observed | route |
|---|---|---|---|
| annotation rows | 5,320,771 | 5,320,771 | P; 2 header lines, 1 blank, 0 malformed |
| starred rows / raw strand values | 0 / `+`,`C` | 0 / `+`,`C` | P |
| distinct `rmsk_record_id` / duplicates | unique | 5,320,771 / 0 | P |
| coordinate-only collisions | 3 pairs, 6 records | chr11:67327101-67327210− (B1F, ORR1B1-int); chr13:58658238-58658287− (B1_Mus1, ORR1B1-int); chr16:37859046-37859109+ (B1_Mur3, ID_B1) | P |
| bound violations vs `chrom.sizes` | 0 | 0 over 61 contigs, all 61 used | P |
| distinct `rmsk_instance_id` | 4,696,900 | 4,696,900, min 1 max 4,696,900 contiguous | P |
| instances spanning contigs | 0 | 0 | P |
| instance sizes 1 / 2 / 3+ | 4,251,251 / 338,697 / 106,952 | identical | second independent ID-only pass |
| class census (17 classes) | `expectations/mm39/class_census.tsv` | exact match, sum 5,320,771; equals `audit/class_census.tsv` `n_source` | P |
| `config/mm39.classes.tsv` vs observed | equal sets | equal, 17 / 17 | P |
| all_rmsk records/names/triples/bp | 5,320,771 / 18,484 / 18,504 / 1,201,573,004 | identical | P |
| interspersed | 3,764,949 / 1,220 / 1,240 / 1,116,605,808 | identical | P |
| interspersed_plus_satellites | 3,802,177 / 1,228 / 1,248 / 1,121,742,599 | identical | P |
| retrotransposon_derived | 3,593,857 / 868 / 868 / 1,084,886,912 | identical | P |
| satellites | 37,228 / 8 / 8 / 5,136,791 | identical | P |
| compat_tetranscripts_mm39 | 3,799,629 / 1,225 / 1,245 / 1,121,476,301 | identical | P |
| `tRNA` family-prefix drop | 2,548 | 2,548 = LFSINE_Vert 1,235 + MamSINE1 925 + AmnSINE2 388 | P; families `tRNA`, `tRNA-Deu`, `tRNA-RTE` |
| `universe_members.tsv.gz` | 5 universes | member sets and `provisional` flags equal mine in all 5; 14,997,840 rows; 5,893 provisional in each of two universes (5,786+98+9) | P |
| `rmsk_taxonomy.tsv` | 18,504 rows | equal to my regroup row for row, name-sorted | P |
| multi-label names / records / triple rows | 20 / 6,517 / 40 | 20 / 6,517 / 40; classes DNA and DNA? only; name list equals `audit/subfamily_multiplicity.tsv` | P |
| parquet: 24 columns, names, order, types, non-null | ADR5 §2 | exact; `nullable=False` on all 24 | `schema_arrow` |
| parquet rows, all 24 columns | — | **0 mismatches on 5,320,771 rows in every column**, including `ucsc_rep_start/end/left` | P joined 1:1 to U |
| `rmsk_records.tsv.gz` | equals parquet | 0 byte-level row mismatches against my derivation, floats as shortest decimal repr | P |
| `rmsk_instance_members.tsv.gz` | one row per record | 5,320,771 rows, sorted, record set equals the catalog | P |
| UCSC join | 1:1, 0 field disagreements | 5,320,771 / 5,320,771, 0 duplicate keys, 0 unmatched either side | U |
| UCSC class/family after class-only projection | agrees | 0 mismatches; 1,576,224 class-only `.out` tokens | U |
| swScore / milliDiv / milliDel / milliIns / genoLeft | agree | 0 mismatches under `round(pct*10)` and `-query_left_bp` | U |
| stated `ucsc_rep_*` encoding | `qualification.md` | holds on 3,415,491 `+` and 1,905,280 `−` rows, 0 violations | parquet |
| negative `consensus_left_bp` / `query_left_bp` | 6 / 0 | 6 / 0; all six rows match `AUDIT.md:160-165` on name, coords, cons_left, cons_end, cons_start | P |
| `ID2 chr1:3051045-3051146 -` | start 5, end 104, left 48 | 5 / 104 / 48 | P |
| `length_bp`, `source_row_number` | `end−start+1`, 1..N permutation | hold on all rows | P |
| gzip headers | `mtime=0`, empty name | `1f8b08000000000000ff` on all three `.gz` | `head -c 10` |
| source md5 pins | 4 pins in `config/mm39.env` | all 4 match the pinned bytes and `SOURCES.json` | `md5sum` |
| rebuild digests | — | all 6 `tables/` files, `universes.json`, `SOURCES.json` and `qualification.md` sha256-identical to the orchestrator's build; `qualification.md` `cmp`-identical to the tracked audit copy | B, ~5 min |
| truth-table statuses | 13 delivered build artifacts, 4 delivered test paths | all present; every `deferred` row absent from disk | `test -f` |
| `.gitignore` claims | `docs/_internal/**/*.tsv` and `tests/fixtures/` tracked | 13 internal `.tsv` and 19 fixture files tracked, none ignored | `git check-ignore`, `git ls-files` |
| contrastive negation in public prose | none | `grep -n '\bnot \b'` on README, DECISIONS, OUTPUTS returns nothing | grep |
| `bash -n` | clean | clean on `build.sh`, `lib/common.sh`, `src/*.sh`, `tests/run.sh`, check `.sh` | `bash -n` |

Plan-file numbers all confirmed: plan 11's 5,320,771 / 4,696,900 / no spanning ids / the ID2 parse /
the two md5 pins; plan 12's six-universe table (all_rmsk 18,484 subfamilies, triples left blank), the
3 collision pairs and the 20 names / 6,517 records. Unverifiable-until-their-phase, correctly marked
deferred: the `BUILD_ID` formula, `score = min(sw_score, 1000)`, the eighteen export paths,
`taxonomy_canonical`, and the Dfam snapshot fixtures.

## Fixture coverage

Each mutation applied to one subject on a scratch copy of the repo plus a symlink refroot, one at a
time, with a full restore between runs. Baseline first: `tests/run.sh core` on the scratch copy gave
`checks=6 pass=6 fail=0 unsupported=0`, exit 0. All 137 tracked files md5-identical before and after.

| failure mode | check | fixture | mutation result |
|---|---|---|---|
| malformed row | 10 | `source/malformed.out` line 4 (unparenthesized `C` cons-left) | made well-formed → exit 1, `accepted malformed row` |
| malformed row, 16 variants | 10 | in-check synthesis (field count, `nan`, stray parens, `+7`, `1_000`, `٧`) | covered by the same check |
| unreadable input | 10 | in-check gzip bytes in a `.out`-named file | `open_text` forced to `gzip.open` → exit 1 |
| signed consensus, no silent abs | 10 | `source/records.out` Charlie17 `(-1847)` | `consensus_left_bp` → `abs(...)` → exit 1, `AssertionError: 1847` |
| plus/minus/`(TGCT)n`/starred/class-only/split-family rows | 10 | `source/records.out` + `expected.tsv` (6 rows) | covered |
| source qualification metrics | 11 | build `source/qualification.md` + tracked audit copy | `distinct_ids` 4,696,900→4,696,899 → exit 1 |
| genomic bounds (full build) | 20 | build `source/mm39.chrom.sizes` | chr1 → 1000 bp → exit 1; chr1 row dropped → exit 1 |
| genomic bounds, 1 bp margin | 20 | same | chr1 −1 bp → exit 0: chr1's last record ends 100,000 bp short of the contig end, so the mutated file is still a correct bound — not a wrong subject |
| one instance per record | 21 | build `rmsk_instance_members.tsv.gz` | one instance id reassigned → exit 1 |
| universe predicate | 22 | build `universes.json` | `DNA?` dropped from `interspersed` → exit 1 |
| class census counts | 22 | `expectations/mm39/class_census.tsv` | `DNA? 9`→`10` → exit 1 |
| duplicate key | 23 | `records/duplicate.out` | gate removed → exit 1 |
| contig bounds | 23 | `records/beyond_end.out` | gate removed → exit 1 (see A2) |
| missing chrom | 23 | `records/missing_chrom.out` | gate removed → exit 1 (see A2) |
| spanning instance | 23 | `records/spanning_instance.out` (ID `007`, chr2+chr10) | gate removed → exit 1 (see A2) |
| unparseable record identity | 23 | `records/invalid_name.out`, `invalid_chrom.out` | gate removed → exit 1 (see A2) |
| UCSC join duplicate / missing / extra | 23 | `records/rmsk.tsv` mutated in-check, `unreviewed.tsv` | covered |
| UCSC class/family disagreement | 23 | `records/disagree.tsv` (`hAT2`) | gate self-compared → exit 1, `accepted invalid fixture` |
| class set gate | 23 | `records/unreviewed.{out,tsv}` + `classes.tsv` | `check_class_set` call removed → exit 1 |
| tRNA family-prefix exclusion | 23 | `records/records.out` `A` (`SINE/tRNA-X`) + `expected_universes.tsv` | prefix → `tRNAX` → exit 1 |
| equal coords, different names | 23, 22 | `records/records.out` `A`/`B` at chr2:10-20; check 22 pins the 3 real pairs | covered |
| two-record instance, leading zeros | 23 | `expected_instances.tsv` (`001` holds `A` and `Split`, sorts before `1`) | covered |
| dangling symlink | — | **none** | injected probe → `fail`, exit 1 (A1) |
| required check unsupported | — | **none** | injected `.required.sh` exiting 3 → exit 1; same check without `.required` → exit 0 (A1) |
| zero checks / missing dir / bad usage | — | none | `consumers` → `no checks registered`, exit 0; dir removed → exit 2; no args → usage, exit 2 |

## Probe (f)

`git reflog -3` is unchanged — `c28caea HEAD@{0}: commit: Phase 2: canonical records, instances, raw
taxonomy and universes`, then `8fe7bb5`, then `9ac83d4`. `HEAD` is `c28caea8fe9908bb801e79827216de2e00f974ba`.
`git status --porcelain` shows the three modified `m2_*.md` prompts I started with plus the two other
reviewers' untracked reports, which I ignored. All 137 tracked files md5-identical before and after.
No `__pycache__`, no `.pyc`, no stash. No git write, install or network access occurred. Scratch
under `_scratch/te-tracks-audit/m2-opus/` is removed; the orchestrator's `source/` and `refroot/` are
untouched.

Portable line: rebuilt mm39 byte-for-byte and re-derived all 24 published quantities from the pinned
`.out` with independent code — zero mismatches across 5,320,771 rows and 24 columns — and broke every
named gate on scratch copies; the open items are two coverage gaps in the runner and the gate
fixtures, plus four documentation-precision notes.
