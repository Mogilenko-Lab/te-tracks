# Phase 2 re-review (Opus)
Verdict: PASS WITH ADVISORIES

## Blocking

- None. Every contract deliverable exists at its prescribed path, every acceptance number recomputes with independent code, all five prescribed mutations (plus two extras) make their check exit 1, and my own build is byte-identical to the reference build and to codex's.

## Advisory

- [A1] `README.md:40-42` — the "## Outputs" paragraph still says "the current build produces the source layer under `source/`, and the redesign phases supply the remaining artifacts", which the same file contradicts at `:106` ("the source layer, phase 2 canonical tables and universes") and in its own rows at `:55-56,64-72`. `README.md:35-36` is stale in the same way ("Core checks cover parser fixtures and the source qualification report" — core now runs four more checks over records, instances, universes and fixtures). Fix: rewrite `:35-42` in one pass with `:106`. Same finding as codex A1; I add `:35-36` and note that the truth table lists `tests/lib/consumers.py` (deferred) but has no row for the delivered `tests/lib/records.py`.
- [A2] `docs/OUTPUTS.md:125-138` — the diff deletes the 15-column `te_loci.tsv.gz` dictionary and the `te_dim.tsv` field list, and the surviving disposition table carries a row only for `te_loci.parquet`, so the two files a reader is still pointed at have no schema anywhere. `README.md:40` still identifies that release as published in the reference cache, and `docs/PROVENANCE.md:71` still cites `te_dim.tsv` as the rollup. Fix: add `te_loci.tsv.gz` and `te_dim.tsv` disposition rows or keep a linked legacy schema, including the UCSC `rmsk_id` meaning. Same as codex A2, extended with the PROVENANCE reference.
- [A3] `src/15_build_universes.sh:12` — the production builder reads `$REPO_ROOT/tests/expectations/$GENOME/class_census.tsv`, so a packaged builder shipped without the test tree cannot publish universes. I confirmed the coupling is looser than it looks and in a way that compounds the problem: `build_universes.check_class_census` compares only the class *set*; I built the fixture catalog against a census asserting `DNA 999` where 1 record exists and the build accepted it. The `records` column has a reader only in `tests/checks/core/22_universes.py:23`. Fix: ship the reviewed class policy as runtime data under `config/`, keeping the count expectation in tests. Same as codex A3.
- [A4] `src/lib/build_records.py:98-100` — the UCSC ↔ `.out` class/family equality gate has no fixture. Check 23 exercises duplicate, missing and extra UCSC join rows only. I confirmed the gate is live by hand (`rmsk.tsv` `hAT` → `hAT2` raises `UCSC rmsk_family disagreement: {...'rmsk_name': 'Split'}`), so this is coverage, not behaviour. Fix: add a `disagree.tsv` fixture to the `23` join loop.
- [A5] `src/lib/build_universes.py:28-29,36-37,58-59` — the nine-class interspersed list is written out three times, because `interspersed_plus_satellites` is spelled as an `or` of two `class_in` lists rather than a reference to `interspersed`. A future class added to one copy and missed in another produces a silently inconsistent pair. The expectation file pins today's numbers, so this is drift risk.
- [A6] `tests/checks/core/20_records_schema.py:27-28` — the 10,000-index sample comparison is unreachable as a failure: line 26 already asserts full-table equality. Delete it or delete line 26's redundancy.
- [A7] `tests/checks/core/22_universes.py:23` — reads the census with pandas default NA handling while `build_universes.py:88`, `load_ucsc` and `tests/lib/records.py` all pin `keep_default_na=False` / `null_values=[]`. A class literally named `NA` would fail the check rather than pass it, so it fails closed; it is a consistency nit.
- [A8] `src/lib/rmsk_out.py:118` — `RecordStats.add` keys instances by `int(rmsk_instance_id)` while `build_records` keeps the token as text, and `docs/OUTPUTS.md:88` promises leading zeros survive. mm39 has none, so `05_qualify` and `10_build_records` both report 4,696,900; the fixture's `001` vs `1` pair is exactly the case where the two stages would disagree.

## Numbers recomputed

All from my own build at `opus-p2/build`, with pyarrow/pandas code that imports nothing from `src/lib/`.

| quantity | contract | observed | command |
|---|---|---|---|
| records (TSV and parquet) | 5,320,771 | 5,320,771 | `pq.ParquetFile(...).metadata.num_rows`; `pacsv.read_csv` |
| columns / order / types / nullability | 24, ADR5 §2 order, int64+float64+bool+string, non-null | exact match, all 24 `nullable=False`, `null_count==0` | `schema_arrow` vs a hand-typed list |
| `rmsk_record_id` | unique, `<name>\|<chrom>:<s>-<e>\|<strand>` | unique; reconstruction equals the column | string concat over the parquet |
| distinct `rmsk_instance_id` | 4,696,900 | 4,696,900 | `groupby(...).size()` |
| instance sizes 1 / 2 / 3+ | 4,251,251 / 338,697 / 106,952 | identical | same |
| instances on one contig | all | `nunique().eq(1).all()` true | same |
| six universes: records/names/triples/length_sum_bp | `expectations/mm39/universe_summary.tsv` | recomputed frame `.equals(expectation)`; built file `.equals(expectation)` | independent masks over `rmsk_class`/`rmsk_family` |
| `universe_members.tsv.gz` rows | 14,997,840 | 14,997,840 = sum of the five non-`all_rmsk` universes | `pacsv.read_csv` |
| `provisional=true` | 5,893 in each of two universes, none elsewhere | `{interspersed: 5893, interspersed_plus_satellites: 5893}`, total 11,786 | `groupby("universe_name")` |
| provisional composition | Unknown 5,786 + Unspecified 98 + DNA? 9 | 5,893 in the census | `class_census.tsv` |
| class census | `expectations/mm39/class_census.tsv` | 17 classes, exact match | `value_counts().sort_index()` |
| multi-label names / records | 20 / 6,517 | 20 / 6,517 | regrouped taxonomy, `duplicated(keep=False)` |
| `rmsk_taxonomy.tsv` | distinct triples + counts | 18,504 rows, `.equals()` my regroup | `groupby(TRIPLE).agg` |
| coordinate-only collisions | 3 pairs, 6 records admitted | chr11:67327101-67327210− (B1F, ORR1B1-int); chr13:58658238-58658287− (B1_Mus1, ORR1B1-int); chr16:37859046-37859109+ (B1_Mur3, ID_B1) | `duplicated(KEY[:4])` |
| `consensus_left_bp < 0` / `query_left_bp < 0` | 6 / 0 | 6 / 0 | boolean sums |
| `length_bp` | `end_1 - start_1 + 1` | holds on all rows | vectorized compare |
| `source_row_number` | permutation of 1..5,320,771 | `np.array_equal(np.sort(...), arange)` | same |
| TSV ≡ parquet | equal typed rows | `Table.equals` true over all 5,320,771 rows; no differing column | `pacsv.read_csv` vs `pq.read_table` |
| gzip header bytes 4..7 | zero | `1f8b08000000000000ff` on all three `.gz` | `open(...).read(10)` |
| build reproduction | — | all 7 artifacts sha256-identical to the reference build and to codex's | `diff <(sha256sum ...) <(sha256sum ...)` → exit 0 |

Probe (d) results. All `chrom` and `rmsk_name` values are ASCII, so pandas' code-point sort equals C-locale byte order; the claim at `docs/OUTPUTS.md:45` holds regardless, since UTF-8 byte order preserves code-point order. The sort key is unique, so `sort_values`' non-stable default is harmless. Float round-trip is bit-exact: reinterpreting `divergence_pct`, `deletion_pct` and `insertion_pct` as int64 gives arrays equal between the TSV reader and the parquet, and every serialized value is plain decimal with no exponent form. `evaluate_predicate` rejects an unknown key inside an `or` branch as well as at top level. No universe lists a `provisional_class` its predicate cannot select.

Probe (c) results, each on a scratch copy of the repo and a scratch refroot; the 26 tracked source/fixture/expectation files verified by md5 before and after, `git status --short` unchanged at 21 lines, no `__pycache__` anywhere.

| mutation | check | exit | restored |
|---|---|---|---|
| `universe_summary.tsv` satellites 37228 → 37229 | 22 | 1 | 0 |
| `universe_members.tsv.gz` one `false` → `true` | 22 | 1 | 0 |
| `rmsk_instance_members.tsv.gz` drop row 5 | 21 | 1 | 0 |
| `rmsk_records.tsv.gz` row 1 `sw_score` +1 | 20 | 1 | 0 |
| `expected_records.tsv` row 1 `sw_score` +1 | 23 | 1 | 0 |
| `class_census.tsv` `DNA? 9` → `10` (extra) | 22 | 1 | 0 |
| drop `DNA?` from the `interspersed` predicate (extra) | 23 | 1 | 0 |

Probe (f): `git reflog -1` is `8fe7bb5 HEAD@{0}: commit: Phase 1: pinned .out source, parser profile, qualification`, and all phase-2 work is uncommitted. No git write, install or network access occurred in this review.

Probe (e): the new `src/lib/*.py`, `src/1*.sh`, `tests/lib/records.py` and the four checks carry one-line intent comments and contract docstrings with no contrastive negation, no dates, names, or review/history chatter; the only `not`/`without` hits are code negations. The new `docs/OUTPUTS.md` prose is affirmative throughout. The wording defect is the README self-contradiction in A1.

## Agreement with codex review

- A1 (`README.md:41` stale) — agree; I add `:35-36` and the missing `tests/lib/records.py` truth-table row.
- A2 (legacy schema continuity) — agree; I add that the disposition table has no `te_loci.tsv.gz`/`te_dim.tsv` rows and `docs/PROVENANCE.md:71` still cites `te_dim.tsv`.
- A3 (test data as production build input) — agree; I add the measured evidence that the gate ignores the census counts entirely (a census claiming `DNA 999` against 1 observed record is accepted).
- "All measured acceptance numbers match" — agree, independently recomputed above.
- Collision starts are `start_1` (1-based) at `22_universes.py:93` — agree; UCSC `genoStart` is one lower.
- Six signed `consensus_left_bp` against ADR5 §2's "nonnegative" wording — agree it is the sanctioned phase-1 correction, and `docs/OUTPUTS.md` now states the signed contract. `consults/ADR5_consult.md:58` still reads "nonnegative"; the consult is a record rather than a live contract, so I leave it.
- Census restores 2,548 tRNA-family SINE records (1,492,624 → 1,495,172) and seven classes — agree; confirmed against `git show HEAD:tests/expectations/mm39_class_counts.tsv`.
- Digests and the four mutation results — agree; my independent build reproduces codex's seven sha256 values exactly, which is stronger evidence for the byte-identity claim at `docs/OUTPUTS.md:112` than either run alone.
- "Python data object for the universe definitions is acceptable under the present contract" — agree; the serialize-parse-evaluate round trip at `build_universes.py:105-112` means the published JSON is the object that ran. I would still prefer a tracked JSON input, for the same reason as A3.

Portable line: recomputed all 24 acceptance quantities independently, reproduced the build byte-for-byte, and broke each of the four new checks on scratch copies — phase 2 is sound; the open items are three documentation-continuity advisories plus five small code and coverage nits.
