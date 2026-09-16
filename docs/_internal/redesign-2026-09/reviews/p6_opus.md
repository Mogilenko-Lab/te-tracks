# Phase 6 re-review (Opus)
Verdict: FAIL

Every measured artifact is exactly right: I reproduced the alias table, the coverage table, all 16 renamed exports, the three `all_rmsk` BEDs and the whole registration from the sources with my own code, byte for byte. The failures are in three checks, one exit rule and four README statuses.

## Blocking
- [B1] `tests/checks/core/60_contig_aliases.py:59` — asserts zero `records_all` on `chr4_JH584295v1_random` and `chrM`; both are populated. — Baseline run fails at line 60: `('records_all', {'chr4_JH584295v1_random': 2, 'chrM': 4})`; my own per-contig tally from `rmsk_records.parquet` gives the same 2 and 4 (Low_complexity, Simple_repeat; plus rRNA, tRNA) and zero *interspersed* on exactly those two. — Assert the two interspersed zeros, `records_all` 2 and 4 there with no catalog-zero contig, and the sums 5,320,771 / 3,764,949.
- [B2] `bin/te-tracks-preflight:90`, `tests/checks/core/62_preflight.sh:54,57,61`, `docs/OUTPUTS.md:547` — the exit rule counts `only_in_reference`, so the primary gate cannot reach 0; plan 16 on disk now carries the amended contract (ruling B2). — My 24-scenario matrix (3 namespaces × 2 universes × 4 reference kinds, expectations computed by my own set algebra) matches the implementation on every list and every exit under M1-as-written; only `gencode`/interspersed vs the 61-contig FASTA diverges between contracts (M1 → 2, amended → 0). Check 62 reports 3 deviations of its 10 runs: gencode `extra: ['JH584295.1','chrM']`, ucsc 40/38 against an expected 39/39, ensembl 23/21 against 22/22. — `return 2 if only_export else 0`; rewrite OUTPUTS.md:547 and check 62's three expectations (0 with two reference-only names; 40/38; 23/21) and add the `all_rmsk` legs (0; 39 each way; 22 each way; 1).
- [B3] `src/lib/build_exports.py:217` and `:229` — two build entries; `main()` writes both universes and no longer reads `default_universe`, `build_exports()` writes the interspersed set alone and keeps that guard. — Check 42 fails at line 74: `build_exports: undeclared export universe: 'all_rmsk'` (fixture `universes.json` declares `interspersed` and `satellites`); its gate at `:146` now exercises a function the pipeline never calls, so `default_universe` is unvalidated on the stage path. — One entry with explicit jobs called by `main()`; fixture declares `all_rmsk`; hand-author the 6-row catalog BED; 46 registration rows (40 + 6); 8 inventory rows (seven with `rows=5`, one with `rows=6`, `distinct_features=6`); assert function and CLI rebuilds identical.
- [B4] `README.md:68,81,82,114` — four rows read `delivered, tested` while the checks that verify them fail and the suite exits 1; README:46 defines `tested` as "verified against their contract". — `tests/run.sh core` → `checks=16 pass=13 fail=3`, failing 42, 60, 62; those four artifacts are covered only by 60 and 62. Line 114 also states "GENCODE interspersed versus the 61-contig FASTA exits 2", which the amended contract makes 0. — Land B1/B2, then restate; until then the rows are not `tested`.

## Advisory
- [A1] `tests/checks/core/61_namespace_exports.py:64` hides a real cross-namespace divergence: the `ucsc` `family.bed` is ordered by `rmsk_name` (invisible in the file), the renamed copies by the family bucket. `LC_ALL=C sort -c -s` with the documented keys reports disorder at `ucsc/.../family.bed:537383`; 3 coordinate ties exist and 2 swap, so 4 of 3,764,949 rows sit at different line numbers across namespaces. Sort `family.bed` by its emitted name in stage 30 (then drop the exception), or state the two orders in OUTPUTS.md.
- [A2] `src/lib/build_exports.py:210` — the `all_rmsk` pass logs `subfamilies=0 families=0 taxonomy_triples=0 instances=4696900`; the instance number is the catalog's, and that pass registers no instance rows. Report only what the pass emits.
- [A3] `src/lib/contigs.py:126` — the docstring says "Register renamed files", while the phase's own invariant is that renamed files add no registration rows; they add inventory rows.
- [A4] Phase 7 retention is stale beyond the registration size: exports now measure 3,021,713,838 / 2,926,268,559 / 3,021,138,299 bytes for ucsc / ensembl / gencode (was "2.6 GB per namespace") and the build totals 10,461,962,113 bytes (was "about 9 GB"); registration is 347,526,106 bytes. `docs/OUTPUTS.md:285` still says "All seven exports land under `exports/ucsc/interspersed/full/`" while stage 30 also writes the `ucsc` `all_rmsk` BED.
- [A5] `tests/checks/core/60_contig_aliases.py:26` ties a public test fixture to `docs/_internal/redesign-2026-09/audit/`; the check breaks wherever internal docs are excluded. Pin the fixture by digest instead.
- [A6] `bin/te-tracks-preflight:37` resolves the export path before walking up for `tables/`, so the alias table read is the resolved build's. Demonstrated: against a root whose `exports/` is a symlink and whose alias table I had mutated, preflight reported `reference_length 195154280 / export_length 195154279` — the lengths came from two different builds.
- [A7] Check 61 compares payloads on 10,000 of 3,764,949 rows (0.27%); regenerating one file through the documented rename and sort is a total check and costs a minute. A stale `src/lib/__pycache__/build_records.cpython-311.pyc` (11:31) predates this phase.

## Numbers recomputed
| quantity | contract | observed | route |
|---|---|---|---|
| `contig_aliases.tsv` | 61 rows, 5 name columns + length | 61 rows, every cell equal, 5/5 injective and complete, sorted by `chrom_ucsc` | own parse of `chromAlias.txt` + `chrom.sizes` |
| gencode rule | reproduces the 61 FASTA names | names and lengths identical; fixture byte-identical to the audit file | own rule vs fixture |
| `contig_coverage.tsv` | per-contig counts, alias, length agreement | all 6 columns equal on all 61 rows; sums 5,320,771 / 3,764,949 | own derivation from parquet + membership |
| zero-interspersed contigs | 2, catalog 2 and 4 | `chr4_JH584295v1_random` 2/0, `chrM` 4/0 | parquet |
| ucsc interspersed inventory | unchanged from milestone 5 | header + 7 rows digest `55a1eb21…` = `m5fix_before.sha` | reconstruct and hash |
| renamed exports | sha256 in `exports.tsv` | 16/16 MATCH, tie-independent (plain `sort`, no `--stable`) | own awk rename + `LC_ALL=C sort` on the documented keys |
| `all_rmsk` ucsc BED | 5,320,771 rows, `min(sw_score,1000)` | `801cc731…` on disk, in the inventory and from my build under both tiebreaks | own build from parquet |
| `all_rmsk` BEDs | 61 contigs, equal rows per namespace | 5,320,771 × 3, 61 contigs each | awk |
| interspersed registration | 30,119,592 rows, `314098c5…` | equal, one contiguous leading block | zcat + awk + sha256sum |
| `all_rmsk` registration | one row per record, `record`/`rmsk_record_id`, own bounds | 5,320,771; each record once; emitted id = record id; bounds equal parquet | own join |
| inventory | 24 rows | 24, sorted, no stale or missing path; renamed rows agree with their ucsc source on every column but path, namespace and digest | own comparison |
| export contigs | 59 interspersed, 61 all_rmsk | 59 in all 7 files × 3 namespaces; 61 | awk |
| preflight | ruling M1 exits | 24/24 scenarios match my independent lists and M1 exits | own set algebra; FASTA, 21-chrom sizes, my `.fai`, pysam BAM |
| check teeth | each fails under one mutation | 41 → `:132`, 60 → `:24`, 61 → `:75`, 62 → 7 deviations | symlink-farm roots, one mutated table each |
| hygiene | no writes | 14 phase-6 files md5-identical; refroot untouched after 17:00; no new bytecode in the repo or `.ref`; nine consumer checkouts clean (`14839-DM-cGAS` dirty and carrying bytecode, as the rulings record) | md5sum, find, `--no-optional-locks` status |
| git | `c2a7a43`, uncommitted | reflog head `c2a7a43`; phase 6 in the working tree | `git reflog -3` |

## Exit-contract recommendation (task d)
Adopt the amended contract: exit 0 when every export contig is present at an agreeing length, print `only_in_reference` for information, exit 2 when the export names contigs the reference lacks with a nonempty shared set, exit 1 for a length disagreement, an empty intersection or an unreadable input. Ruling M1 as written makes `te-tracks-preflight <export> <bam> && featureCounts …` unsatisfiable for the interspersed exports against any complete reference — a universe legitimately names 59 of 61 contigs — so the gate is deleted rather than obeyed, which is worse than a loose gate. The hazard the amended rule leaves open: exit 0 says nothing about completeness or assembly identity. A truncated export naming one contig at the right length passes, and matching names and lengths cannot distinguish mm39 from an identically-named custom build. Completeness belongs to the inventory digests in the phase 7 manifest and identity to the pinned reference; plan 16 says so and OUTPUTS.md must too.

## Agreement with codex review
- B1 (zero catalog records) — agree; my independent tally gives the same 2 and 4 and the same baseline failure.
- B2 (preflight exits) — agree, and my 24-scenario matrix reproduces its 0 / 40-38 / 23-21 numbers and extends them to the `all_rmsk` legs and to the `.fai` and BAM readers; I reach the same recommendation and the same hazard.
- B3 (two builds) — agree, with added evidence: `main()` also drops the `default_universe` guard, so check 42's `:146` gate now covers a code path the pipeline never runs; fixture arithmetic confirmed at 6 catalog records, 46 registration rows, 8 inventory rows.
- A1 (`export_contracts` from job definitions; stage 35's own path set) — agree; registration is 347,526,106 bytes, and the per-namespace and per-build retention numbers are stale by the same token.
- A2 (phase 8 cannot reuse these entry points; child preflight needs an alias source) — agree, and A6 above sharpens it: the alias table preflight reads is the *resolved* build's.
- A3 (ADR 3 enumerates interspersed exports alone) — agree; entry 3 names the three namespaces but not the complete-catalog record BED.
- Codex missed A1 (the `family.bed` order divergence behind check 61's exception), B4 (four README statuses claiming `tested` against failing checks), A2 and A3 (the all_rmsk log line and the "Register" docstring), and A6.

Prose and comments in the new files are clean: no contrastive negation in the added public prose, no banners, dates or provenance in comments, docstrings state contracts.
