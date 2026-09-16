# Milestone 5 re-review: numbers and fixtures (Opus)

Verdict: PASS WITH ADVISORIES

Scope: commit `9ac66fb` on `redesign-2026-09`. Every phase 3–5 number re-derived with code written from the plan and OUTPUTS contracts, importing nothing from `src/` or `tests/`. Consumer seam and unstated assumptions left to codex and divergent.

## Blocking

None. No published number differs from my derivation, and no check passed on a mutated subject.

## Advisory

- [A1] `tests/checks/consumers/14_mates_parser.py:53` — the only fixture-reading consumer check that never calls `build_fixture()`; it validates whatever `record_mates.csv` already sits in the refroot. Evidence: run in isolation against a refroot populated by an earlier revision, it passes on stale bytes (my first mutation pass did exactly that); rebuild the fixture with a seven-column writer and it fails as designed, and against an empty refroot it fails with `FileNotFoundError`. In the registered order check 10 rebuilds first, so the suite is sound today. Fix: call `build_fixture()` at the top of `check()`, as checks 10–13 do.
- [A2] `tests/checks/consumers/14_mates_parser.py:60` — `scratch.mkdir(parents=True)` without `exist_ok`, so an interrupted run leaves a directory the next run trips on. The orchestrator recorded this after the p5 fix; confirmed still present at `9ac66fb`. Check 12 uses `exist_ok=True` at line 39. Fix: match check 12.
- [A3] `tests/checks/consumers/12_tesingle_parser.py:30` — `…["molecules_by_tag"]["UR"] - 2` writes the two flagged molecules as a literal where `expected.json` names them in `flagged_reads`. Recorded by the orchestrator; confirmed present. Fix: derive the subtrahend from `len(flagged["duplicate"]) + len(flagged["qcfail"])`.
- [A4] `tests/checks/core/30_taxonomy_canonical.py:15` — check 30 recomputes the table through the production `resolve`, so a rule defect that fires on no mm39 row passes it. Evidence, both directions measured: mutating tie handling to elect the first label leaves check 30 passing (mm39 carries no tie) while check 32 fails on `family_tie`; swapping the family-status precedence so the uncertainty suffix outranks the unspecified abstention makes check 30 fail on the published table. This is the plan's intended division — the rule's own oracle is `rule_cases.tsv` — and is worth stating in the contract so a later reader does not read check 30 as rule coverage.
- [A5] `README.md:20-22`, `README.md:35-36`, `README.md:42-43` — three sentences describe the phase-2 build while the truth table below them marks phases 3 and 4 delivered: the build section omits `exports/`; "Core checks cover the parser fixtures, the qualification report, the record schema, instances, universes and the record fixtures" names six of the thirteen registered core checks; "the current build produces `source/`, `tables/` and `universes.json`, and phases 3 to 9 supply the remaining artifacts" omits `exports/` and overstates what is outstanding. Fix: name `exports/`, the taxonomy and export checks, and phases 5 to 9.
- [A6] Five consumer checks cannot fail on a wrong subject in this container, so their coverage claim rests on the host: `00_tool_inventory.py` (reporting-only by contract, p5 ruling A6), `15_irescue_chrcat.py` (`gawk` absent), `20_irescue_exec.sh` (`irescue` absent), `21_featurecounts_exec.sh` (`featureCounts` absent), `30_registration_duckdb.py` (`duckdb` absent). The phase 9 host run is where they first earn their entry in the README row.
- [A7] `01_modules/.ref/stellarscope/stellarscope/annotation/__pycache__/` holds three `.pyc` files written at 15:11:09 during this review window. Not mine: re-running `11_stellarscope_parser.py` under my invocation leaves their mtimes untouched, and every invocation I made carried `PYTHONDONTWRITEBYTECODE=1`. The directory is gitignored upstream, so all nine checkouts report a clean status. The same residue was removed once after the p5 fix; a concurrent process is recreating it.

Context, outside my verdict: the working tree now carries an orchestrator edit to `14_phase4_exports.md` raising registration from five spellings to eight (milestone 5 ruling B1). My review is against the committed contract, where the plan, `OUTPUTS.md` and the build all say five and agree.

## Numbers recomputed

| quantity | published | observed | route |
|---|---|---|---|
| `taxonomy_canonical` rows | 18,484 | 18,484 | own rule implementation over `rmsk_taxonomy.tsv` + parquet; file byte-identical (`36625592…`) |
| `taxonomy_resolution_report` rows | 20 | 20 | same; file byte-identical (`f933a84e…`) |
| raw triples / instance sum | 18,504 / 4,727,623 | 18,504 / 4,727,623 | own sum over `rmsk_taxonomy.tsv` |
| class_status concordant / suffix / plurality / unresolved | 18,478 / 6 / 0 / 0 | identical | own census, matches `taxonomy_census.tsv` |
| family_status concordant / suffix / unspecified-resolved / plurality / unspecified / unresolved | 1,095 / 5 / 5 / 7 / 17,372 / 0 | identical | own census |
| multi-label family statuses | 7 / 5 / 5 / 3 | identical, all `canonical_class = DNA` | own census |
| minimum `family_plurality_share` | 0.840 (`MER63C`) | 0.840 (`MER63C`) | own shares; record-weighted 0.734 as plan 13 states |
| winners stable across weightings | every mm39 winner | 0 names differ | own re-run weighting by `record_count` |
| Dfam snapshot rows | 20 | 20 | row count, all 20 report names covered |
| hand-authored rule cases | 31 | 31 reproduced, 0 mismatches | own resolver over `rule_cases.tsv` |
| `median_divergence_pct` | 2 dp | exact match on 18,484 names | own median over parquet `divergence_pct` |
| interspersed records / names / triples | 3,764,949 / 1,220 / 1,240 | identical | own membership read of `universe_members.tsv.gz` |
| rows per export (×7) | 3,764,949 | 3,764,949 | own row generation |
| distinct features: record.bed / record.gtf / subfamily ×3 / family.bed / triple.saf | 3,764,949 / 3,764,949 / 1,220 / 49 / 1,220 | identical | own distinct sets |
| seven `sha256` in `exports.tsv` | as published | all 7 match the files **and** my independently generated byte stream | own line emission + sha256 |
| `export_feature_members` rows | 18,824,745 | 18,824,745 = 5 × 3,764,949 | own registration emission; content sha256 `7ff0eaaf…` reproduced |
| registration rows per level | record 7,529,898; subfamily / family / taxonomy_triple 3,764,949 each | identical | same pass |
| identifier alphabet | `[A-Za-z0-9_.+?()-]+` plus `\|:/` | 0 violations over 18.8M emitted ids | own regex and forbidden-character scan |
| parquet sort order | `(chrom, start_1, end_1, strand, rmsk_name)`, text C-locale | holds on all 5,320,771 rows | own byte-key monotonicity assertion |
| records with consensus start > end | 2, named in OUTPUTS | exactly those 2 | own parquet scan |
| stage 20 + 30 rebuild | — | 8 of 8 artifacts byte-identical to the orchestrator, gzip bytes included | own build dir over symlinked phase-2 tables |
| consumer fixture rebuild | — | 53 of 53 files, 51 byte-identical; the 2 `.locInd` differ only in `__srcfile`, equal `getElements()` and `getNames()` | `tests/run.sh consumers --refroot <mine>`, own pickle comparison |
| eleven fixture BAMs | `expected.json` | every `alignments`, `templates`, `molecules`, `UB`, `UR`, `flagged_reads` value matches; all coordinate-sorted and indexed | own pysam recount |
| boundary reads | `[99,100) [100,101) [109,110) [110,111)` | identical | own `get_blocks()` |
| raw `UR` ≠ corrected `UB` | `unique_a` copy 0, `duplicate_b` copy 1 | exactly those two | own tag comparison |
| reverse reads on minus-strand records | both | `duplicate_b` on `SubA`, `minus_twolab` on `TwoLab` | own flag scan |
| IRescue parser `.tsv.gz` | mtime 0, empty name | 5 of 5 | own gzip header read |
| `tests/run.sh consumers` | 7 pass, 5 unsupported, exit 0 | identical | own refroot |

Unverifiable at this commit, all deferred by the plan: `BUILD_ID`, `MANIFEST.json`, the ensembl and gencode export rows, `contig_aliases.tsv`, `contig_coverage.tsv`, `bin/te-tracks-preflight`, the phase 8 exon-subtraction tables, `docs/RUNBOOK.md`, `docs/RELEASES.md`.

## Fixture coverage

One mutation per check on scratch copies of the repository and a symlinked build; the tracked tree was untouched throughout (`git status --porcelain -- src tests config lib README.md docs/OUTPUTS.md build.sh` empty before and after).

| failure mode (plan) | check | fixture | mutation result |
|---|---|---|---|
| canonical row wrong at any of 15 columns (13) | core/30 | build `taxonomy_canonical.tsv` | `MER63C` share 0.84→0.85 → **fail**, column diff |
| resolution report drifts from the multi-label subset (13) | core/30 | same | covered by the same frame comparison |
| census drift (13) | core/30 | `expectations/mm39/taxonomy_census.tsv` | precedence swap in `resolve` → **fail** |
| Dfam rank disagreement (13) | core/31 | `taxonomy/dfam_snapshot.tsv` | `Eulor5B` subtype Crypton-A→Crypton-B → **fail**, 1 disagreement |
| snapshot admission gate, provenance keys (13) | core/31 | `dfam_snapshot.provenance.json` | subset and key assertions present; exercised by the above |
| rule totality, statuses, ties, instance weighting (13) | core/32 | `taxonomy/rule_cases.tsv` (31 cases) | `family_tie` expectation flipped → **fail**; and mutating `resolve`'s tie handling → **fail** |
| one count per name in a rollup (13) | core/32 | `taxonomy/rollup_counts.tsv`, `weighting_context.tsv` | asserted in the same check; my resolver reproduces all 31 cases |
| wrong offsets, names or attribute values (14) | core/40 | build exports | `family.bed` row 1 `LINE/L1`→`LINE/L2` → **fail** |
| BED round trip `start_1 - 1` (14) | core/40 + consumers/22 | build exports | exporter loses the conversion → bedtools check **fails** on boundary expectations |
| emitted id unresolvable through registration (14) | core/41 | `export_feature_members.tsv.gz` | subfamily id `L1MdA_VI`→`L1MdA_VX` → **fail**, `('registered ID', 2)` |
| count 7 over 3 records stays 7 (14) | core/41 | `exports/conservation_{members,counts,totals}.tsv` | the same mutation hits a conservation record; targets and totals both asserted |
| the same query in DuckDB (14) | consumers/30 | same fixtures | cannot exercise — `duckdb` absent, exits 3 naming it |
| inventory rows, digests, distinct features (14) | core/41 | `exports.tsv` | digest recomputed per file; my independent byte stream matches all seven |
| hand-authored export bytes (14) | core/42 | `fixtures/exports/expected/*` | `DNA/unresolved_family_Mystery`→`DNA/Mystery` → **fail** |
| separator and reserved-prefix gates (14) | core/42 | same | 16 character gates and 6 reserved-prefix gates run inside the check and pass |
| IRescue record and subfamily identity (15) | consumers/10 | roster, `record.bed`, `subfamily.bed` | exporter emits `rmsk_name` in BED column 4 → **fail** |
| IRescue `chrcat` name handling (15) | consumers/15 | synthetic intersection rows | cannot exercise — `gawk` absent, exits 3 naming it |
| Stellarscope grouping, attributes, boundary (15) | consumers/11 | `record.gtf`, ARC BAM | exporter drops the `locus` attribute → **fail**; unmutated, exits 3 at the documented `0,1,1,1` defect |
| TEsingle four-attribute tuple, both grains (15) | consumers/12 | `record.gtf`, `subfamily.gtf` | `transcript_id` gains an `X` suffix → **fail** |
| TEsingle 999/1,000 `UR` cutoff, read filtering (15) | consumers/12 | ARC BAM, synthetic cutoff BAM | asserted in the same check; passes unmutated |
| TEtranscripts and TElocal grain, `.locInd` round trip (15) | consumers/13 | both GTFs | GTF `class_id` emits the raw class → **fail** |
| MATES eight-column pair (15) | consumers/14 | `record_mates.{csv,bed}` | writer drops column 8 → **fail** once the fixture is rebuilt (see [A1]) |
| BAM integrity: sort, index, molecules, flags (15) | consumers/23 | eleven BAMs, `expected.json` | raw `UR` stops differing from `UB` → **fail**, `('arc_3prime.bam', 'UR', 11)` |
| featureCounts shared and one-base features (15) | consumers/21 | `subfamily.saf`, `onebase.saf` | cannot exercise — `featureCounts` absent |
| IRescue allocation 4/2 vs 3/3 (15) | consumers/20 | allocation BAMs | cannot exercise — `irescue` absent |
| executable availability report (15) | consumers/00 | none | reporting-only by contract; no oracle to break |

Thirteen mutations plus two resolver probes: every runnable check failed on a wrong subject, none passed.

## Git state

`git reflog -3` shows `9ac66fb HEAD@{0}: commit: Phase 5: consumer fixtures` as the latest entry. Nothing under `src/`, `tests/`, `config/`, `lib/`, `README.md`, `docs/OUTPUTS.md` or `build.sh` is modified. The working tree carries orchestrator edits under `docs/_internal/` alone (plan 14 and 18, the m5 prompts, p6–p8 prompts, and new `reviews/m5_{codex,divergent,rulings}.md` and `prompts/m5_fix.md`), none of them mine. All nine checkouts under `.ref` sit at their clone commits with clean status; the one residue there is the gitignored `__pycache__` of [A7]. My scratch at `_scratch/te-tracks-audit/m5-opus/` is removed, and the orchestrator's build is intact.
