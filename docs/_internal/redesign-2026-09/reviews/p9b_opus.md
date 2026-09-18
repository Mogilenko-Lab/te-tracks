# Phase 9b review (Opus)
Verdict: PASS WITH ADVISORIES

Can `tests/run.sh acceptance` fail? I injected twenty-two defects into real copies of the two acceptance
archives, pointed the checks at the copies, and recomputed every literal in `areas.py` and in
`tests/expectations/mm39/` from the archive bytes. Twenty-one of the twenty-two make the suite fail: twenty
fail the area that owns them, and the off-by-one placed outside the geometry oracle's three contigs fails a
sibling area (A2). The twenty-second, an archive that lost its `MANIFEST.json`, leaves the runner at exit 0
(A1). All ten defects the brief names are caught. Mutation copies are real: a `cp -a` pair for the
publication area (distinct inodes, link count 1) and, elsewhere, a tree of per-file symlinks in which the
mutated file is a fresh regular file replacing its symlink; no `cp -al`, `cp -l` or linking `copytree`.

## Can the suite fail?

| defect injected | area that should catch it | caught | message |
|---|---|---|---|
| `source/qualification.md` `distinct_ids` 4,696,900 → 4,696,899 | 10_source | yes | `AssertionError: ('source qualification', {...'distinct_ids': 4696899...}, {...4696900...})` |
| one digit changed in retained `source/mm39.chrom.sizes` | 10_source | yes | `retained source pin differs: .../source/mm39.chrom.sizes` |
| `tables/universe_summary.tsv` interspersed `length_sum_bp` −1 bp | 20_records_universes | yes | `22_universes.py: exit 1` → `column "length_sum_bp" ... [left] 1116605807 [right] 1116605808` |
| `tables/rmsk_records.tsv.gz` removed (a declared core-check input) | 20_records_universes | yes | `20_records_schema.py: exit 3 / unsupported: run build.sh first` — an `unsupported` replay is an acceptance failure |
| last row of `tables/taxonomy_canonical.tsv` dropped (`tRNA-Val-GTY`) | 30_taxonomy | yes | `30_taxonomy_canonical.py: exit 1` → `shape mismatch [left] (18483,15) [right] (18484,15)` |
| last row of `tables/taxonomy_dfam.tsv` dropped (`hAT-N1a_Mam`) | 35_taxonomy_dfam | yes | `33_taxonomy_dfam_view.py: exit 1` → `names == sorted(set(names)) == sorted(snapshot["summaries"])` |
| one row dropped from `exports/ucsc/interspersed/full/record.bed` (chr2) | 40_exports | yes | `40_exports_shape.py: exit 1` → `('record.bed','end_1',1700000)`; 60_namespaces also fails with `record.bed 3764948` |
| one record's strand flipped `+`→`-` in `record.bed`, same byte count | 40_exports | yes | `40_exports_shape.py: exit 1` → `('record.bed','strand',1900000)` |
| `exports/gencode/.../subfamily.bed` rows 1 and 2 exchanged (same size, different bytes) | 60_namespaces | yes | `61_namespace_exports.py: exit 1` → `sort: -:2: disorder: GL456210.1 1274 1456 MERVL-int`; 40_exports also fails on the registered SHA-256 |
| `record_starsolo.gtf` row 2 re-emits row 1's record (duplicate `gene_id`) | 45_record_profile | yes | `('ucsc', 'duplicate gene_id', 'R\|mm39\|L1MdA_VI\|chr1\|3050294\|3050775\|+')` |
| `record_starsolo.gtf` row 1 swaps `gene_name` and `gene_type`, same byte count | 45_record_profile | yes | `('ucsc', 0, 'twelve ordered attributes')` |
| child `ucsc/.../exon_subtracted/subfamily.saf` chr19 `Start` +1 | 85_gene_child_oracle | yes | `('chr19','bedtools/SAF multiset differs',[((3050004,3050183,'+','IAPLTR3-int'),1)],[((3050005,...),1)])` |
| the same off-by-one on chr7, outside the oracle's three contigs | 85_gene_child_oracle | **no** (exit 0) | caught instead by 80_gene_child: `SAF rows differ from registration: exports/ucsc/interspersed/exon_subtracted/subfamily.saf` — see A2 |
| child `tables/exon_subtraction_status.tsv` first `retained_bp` +1 | 80_gene_child | yes | `80_exon_subtraction.py: exit 1` |
| one `compat_tetranscripts_mm39` member dropped from `universe_members.tsv.gz` | 90_legacy_reconciliation | yes | `compat membership=3799628 packaged GTF=3799629; ... compat_only=0 legacy_only=1` |
| `identity.rank_scheme_version` → `rank_scheme_wicker_v2`, unsigned | 70_publication | yes | `assert (archive/"BUILD_ID").read_text() == build_id + "\n"`; `verify-current` adds `unsupported rank_scheme_version` |
| two inventory `bytes` moved ±1 apart (payload sum preserved), unsigned | 70_publication | yes | same recomputed-BUILD_ID assert; `verify-current` adds `inventory bytes or sha256 mismatch: tables/contig_coverage.tsv` |
| payload edited, core inventory and core `BUILD_ID` re-signed, archive renamed and reselected | 70_publication | yes | core `verify-current` passes (`7b68aac3…`); the check fails on the child: `child source parent_build_id differs from identity` |
| payload edited, both families fully re-signed, child `source/SOURCES.json` parent link updated | 70_publication | yes | the rewrite moved the child's payload sum: `assert sum(r["bytes"] ...) == 2157717760` |
| the same re-sign made **byte-count preserving**, so both families verify clean | 70_publication | yes | `assert not discrepancies` → `te_mm39 BUILD_ID differs from the development pin: aa0b3c2390be…; equal CATALOG_ID` and the same for `te_mm39_gene` — the pinned `identity.tsv` BUILD_IDs are the only signal left |
| `tables/exports.tsv` `feature_level` `family` renamed on its 3 rows | 40_exports | yes | `41_export_registration.py: exit 1` → `(row.variant, row.feature_level, row.format) == ("full", level, ...)`; see A5 |
| archive loses `MANIFEST.json` (`current` still resolves) | all eleven | **no** | `checks=11 pass=0 fail=0 unsupported=11`, runner exit 0 — A1 |

## Blocking

None. Every named defect fails the area that owns it, and no stated number differs from the artifact.

## Advisory

- [A1] `tests/run.sh acceptance` cannot fail on a damaged archive. `lib/common.py:61-73` reports
  `unsupported` when `current` is missing or the archive lacks `BUILD_ID`, `CATALOG_ID` or `MANIFEST.json`,
  and no acceptance check is named `*.required.py`, so `run.sh:91-93` leaves `runner_exit` at 0. Evidence:
  with `MANIFEST.json` removed from a resolvable acceptance core, `checks=11 pass=0 fail=0 unsupported=11`,
  exit 0 — the same output an empty root gives. README.md and the commit body use "all four final commands
  exited 0" as the qualification witness, so the exit code is load-bearing. Fix: rename the eleven
  `*.required.py`, or fail once `<family>/current` resolves but the archive is incomplete.
- [A2] The independent geometry oracle covers 3 of 61 contigs. `oracles.py:20` fixes chr18, chr19 and
  `chr1_MU069434v1_random`: 200,697 of the child's 3,684,934 interspersed blocks, 5.4%. An off-by-one
  `Start` on chr7 passes 85_gene_child_oracle at exit 0; `80_gene_child` catches it through
  `80_exon_subtraction.py:164`, which compares the SAF against the builder's own registration table —
  self-consistency rather than an outside witness. Fix: name the coverage in the check's summary line and in
  `PROVENANCE.md`'s oracle table, or add one large annotated autosome.
- [A3] `oracles.py:124` sorts both interval streams with GNU `sort` under the ambient locale, then merges
  them at 127-141 with Python's codepoint `<`. `LANG=en_US.UTF-8` here and the two orders differ: `sort` puts
  `chr10\t1\t2\t+` before `chr1\t100\t200\t+`, Python does not. Equal multisets still compare line-for-line,
  so the passing verdict is sound and a real difference still fails the assert; the reported
  `compat_only`/`legacy_only` counts and sampled examples become unreliable. Fix: `env LC_ALL=C sort`.
- [A4] `common.py:17` hardcodes the acceptance scratch parent at `_scratch/te-tracks-audit/p9b`, independent
  of `--refroot`, so `--refroot` does not isolate a run and every `core_checks` replay writes into a path the
  runner never names. `tempfile.mkdtemp` keeps concurrent runs apart. Fix: derive it from `TE_TRACKS_REFROOT`.
- [A5] `areas.py:100-102` asserts 49 distinct family features only for rows whose `feature_level` is
  `family`, so a roster that renamed the level satisfies the loop vacuously. `41_export_registration.py:156`
  catches the rename and the suite still fails; the assertion alone does not.
- [A6] The milestone-2 H6 comparison at `areas.py:177-191` runs only when `$TE_TRACKS_REFROOT/<family>/build`
  exists, otherwise printing `development comparison unavailable` and passing. A later run on a host without
  the development builds yields the claim's summary line without its evidence.

## Replayed core checks

`core_checks()` aliases each archive as `<private>/<family>/build` and re-runs 15 of the 26 core checks
(20-22, 30-32, 33-34, 40/41/43, 60-62, 80).

- **No write reaches the archive.** None of the fifteen writes under `BUILD`; 32, 33, 61 and 62 write into
  `TemporaryDirectory`, and `core_checks` sets `TMPDIR` to the private root. The archive's 0444/0555 modes
  are the second guard: appending to and creating a file through the alias both return `PermissionError 13`,
  and `publication` asserts those modes, so the guard is itself tested.
- **The private root provides only `<family>/build`.** Every replayed check reads from there and from the
  repository. The five checks that need `$TE_TRACKS_REFROOT/pubtest` (71, 72, 81, 82) or a second family
  tree (83) are not replayed. `70_manifest_identity.py` runs clean through the alias (exit 0, 52 payloads);
  `71_verify_build.py` cannot, because `manifest.inventory()` refuses a symlinked build directory
  (`verify: invalid build directory: .../te_mm39/build`). `publication` covers that ground instead by
  recomputing both identities itself and calling `release.py verify-current` against the real acceptance root.
- **A silent pass on a missing input is visible.** `core_checks` asserts `returncode == 0`, so the
  `unsupported` exit 3 that `tests/lib/records.py:38` and `62_preflight.sh:24` use becomes an acceptance
  failure: deleting `tables/rmsk_records.tsv.gz` gives `20_records_schema.py: exit 3` and area exit 1.

Areas resting only on replayed core checks: **30_taxonomy** (30, 31, 32) and **60_namespaces** (60, 61, 62),
whose bodies add no measurement of their own. `35_taxonomy_dfam` adds four table row counts; every other area
measures the archive directly.

## Expectation provenance

| expectation file | value traced to | verdict |
|---|---|---|
| `source_pins.tsv` | `config/mm39.env:7,9,11,13,16,17` and `config/mm39_gene.env:6` carry all seven digests verbatim; the Dfam SHA-256 is also in `p9b_impl.md` | independent |
| `source_qualification.tsv` | `reviews/p1_codex.md:56` prints all thirteen summary metrics from the reviewer's own parse (`out_rows=5320771 … coordinate_collision_pairs=3`); `m2_opus.md:68,70,123` recomputes `distinct_ids`, the contiguous span and the three collision pairs; the ten shared-field zeros are stated in `PROVENANCE.md` and the committed audit report | independent |
| `record_census.tsv` | plan 19 (445,649; 30,569; 23,244; 8.07%; 722,280; 588); `reviews/p9a_codex.md:20` (429,440; 434,707; 588; overlap flags 0); `consults/field_practice_consult.md:199` (3,152,636; 434,707); `field_practice_synthesis.md:84` (95,830); `m5_divergent.md:111` and `OUTPUTS.md:494` (1,224,713); `m2_rulings.md:125` (two records with consensus start above end) | independent |
| `identity.tsv` | `reviews/p9a_rulings.md:301` (both BUILD_IDs, the CATALOG_ID, 52 inventory entries, 27 contracts) and `p9b_impl.md`; `reviews/p8_codex.md:102,107` (`ok inventory: 21 files`, `ok export contracts: 12 namespace paths`) | independent |
| `gene_oracle.tsv` | `reviews/p8_codex.md:178-179` and `p8_opus.md:35-36`, two reviewers' own `bedtools merge`/`subtract` runs on chr18, chr19 and `chr1_MU069434v1_random`; `p8_rulings.md:20-21,41-42` adopts them | independent |
| `README.md` | the nine rows describe the sources above; its own three literals (49 family features, 1,278 clade rows, 15,301,538,537 bytes) predate 9b in `RELEASES.md` and `p9a_rulings.md` | accurate |

No expectation traces only to the build under test; the five pre-9b files are anchored the same way
(`exon_subtraction_summary.tsv` matches `p8_codex.md:53-54,180-181` and plan 18 line 118 exactly).

## Numbers recomputed

Every literal in `areas.py` and in `tests/expectations/mm39/` matches the archives. Nothing below used
`src/`; the identity rows re-derive both digests from `MANIFEST.json` alone.

| quantity | stated | observed | command |
|---|---|---|---|
| export bytes ucsc / ensembl / gencode | 4,638,043,480 / 4,531,250,735 / 4,637,401,144 | equal | `sum(p.stat().st_size for p in (core/"exports"/ns).rglob("*") if p.is_file())` |
| `all_rmsk/full/record.bed`; `interspersed/full/record_starsolo.gtf`, three namespaces | 332,554,184 / 316,524,255 / 332,461,688; 1,616,329,134 / 1,604,983,782 / 1,616,260,404 | equal | `stat().st_size` |
| `export_feature_members.tsv.gz`; six Dfam/source file sizes | 347,526,106; 780,296 / 577,712 / 75,154 / 367,180 / 278,952 / 921 | equal | `stat().st_size` |
| export contracts / `exports.tsv` rows / family distinct features | 27 / 27 / 49 | equal | `len(identity["export_contracts"])`, `csv.DictReader` |
| core and child payload sums; inventory entries | 15,301,538,537; 2,157,717,760; 52 / 21 | equal, zero byte-count mismatches against the files | `sum(r["bytes"] for r in identity["inventory"])` |
| core regular-file bytes; retained pair (RELEASES, RUNBOOK) | 15,301,581,825; 17,459,256,297 | equal | `sum(... rglob("*") ...)`; 15,301,538,537 + 2,157,717,760 |
| Dfam table rows; file lines | 1,220 / 1,263 / 300 / 1,278; 1,221 / 1,264 / 301 / 1,279 | equal | pandas `len`; line count |
| `dfam_census.tsv` 22 metrics; `class_census.tsv` 17 classes; `universe_summary.tsv` 6 × 4 | see files | equal | own group-bys over the four Dfam tables; `value_counts()`; predicates re-evaluated from `universes.json` against the parquet |
| `taxonomy_census.tsv` 26 metrics | see file | equal | `value_counts()` over `taxonomy_canonical.tsv` and `taxonomy_resolution_report.tsv` |
| `record_census.tsv` 12 metrics | see file | equal | own group-bys; overlaps by an independent per-contig sort-and-sweep giving 429,440 |
| `exon_subtraction_summary.tsv` 3 × 10 | see file | equal | own chunked join of `exon_subtraction_status.tsv` to the parquet |
| `gene_oracle.tsv` 12 rows | see file | equal | chr18 9,708 / 116,425 / 34,253,394; chr19 86,429 / 10,373 / 4,434,265 / 84,268 / 21,565,706; random contig 0 / 4 / 4 |
| `record_starsolo.gtf` rows; contigs | 3,764,949; 59 | equal | `awk -F'\t' '{n++; c[$1]} END{print n, length(c)}'` |
| compat membership; packaged GTF data lines; its md5 | 3,799,629; 3,799,629; `1d6770be…` | equal | own membership count; `zcat \| awk 'NF && !/^#/'`; `md5sum` |
| core / child `BUILD_ID`; `CATALOG_ID` | `5e2a1563…`; `198f39f0…`; `90cc18be…` | equal | `sha256(b"te-tracks-build-v1\n" + json.dumps(identity, sort_keys=True, separators=(",",":"), ensure_ascii=False))`, and `-catalog-v1` over `identity["catalog"]` |
| development-build agreement (RELEASES) | every table digest and both IDs equal | equal; 16 core and 6 child table files, zero roster or digest differences | own `hashlib.file_digest` over `<refroot>/<family>/build/tables` |

The prose in the diff also checks out. The RUNBOOK version table reproduces exactly on this image (python3
3.11.15, pyarrow 25.0.0, pandas 2.2.3, numpy 1.26.4, pysam 0.24.0, zlib 1.2.11, bash 5.1.16(1)-release,
coreutils 8.32, bedtools v2.31.1, Ubuntu 22.04.5 LTS), and its consumer floors are
arithmetically consistent (2,688 B/row × 3,764,949 = 10.12 GB; 1,038 × 3,764,949 = 3.91 GB; the −974,848 B,
+0.157 s, −0.81 GB and +0.56 GB deltas are the stated subtractions). PROVENANCE's new numbers hold: 6
negative consensus-left values, 20 multi-label names all canonical `DNA` over 6,517 records, decompressed
snapshot SHA-256 `053c728b…`, `fetch_finished` `2026-09-17T15:10:29.831392Z`, UCON4 raw `Unspecified`
inheriting Class II from the Kolobok path, 3,799,629 − 3,764,949 = 34,680, and the child's 78,317 / 278,369
/ 1,298,921 / 160,549,642 / 38-of-61 / 2,638. RELEASES's witness line is accurate: both manifests record
`builder_git_sha 51c016243c8991b27f0da112a00d90a815ead929` with `builder_git_dirty: true`, and
`git diff --stat d28336f 51c0162` touches only `docs/_internal/`. All 60 expandable paths in the OUTPUTS
consumer map resolve inside one of the two archives. README's counts match the suites — 26 core, 11
acceptance, 16 consumer checks — and my own consumer run gave `checks=16 pass=15 fail=0 unsupported=1`,
exit 0. No repository code writes into `tests/expectations/`. The changed prose is affirmative, and the four
new library docstrings state intent in one line each.

## Closing verification

`tests/run.sh acceptance` against the untouched reference root: `checks=11 pass=11 fail=0 unsupported=0`,
exit 0, 54m33s, with `70_publication` reporting `development tables and IDs equal` for both families.

| target | verifier | verify-current |
|---|---|---|
| `pubroot/te_mm39/archive/{5e2a1563…,763815187e47…,9ddf36220830…}` | exit 0 ×3 | `pubroot/te_mm39` exit 0 → `5e2a1563…` |
| `pubroot/te_mm39_gene/archive/{198f39f0…,1804f94e51df…,693ba1aa15e8…}` | exit 0 ×3 | `pubroot/te_mm39_gene` exit 0 → `198f39f0…` |
| `acceptance/te_mm39/archive/5e2a1563…` | exit 0 | `acceptance/te_mm39` exit 0 → `5e2a1563…` |
| `acceptance/te_mm39_gene/archive/198f39f0…` | exit 0 | `acceptance/te_mm39_gene` exit 0 → `198f39f0…` |
| `te_mm39/build`, `te_mm39_gene/build` | exit 0 ×2 | — |

Ten verifier runs and four `verify-current` runs at exit 0, before and again after every mutation. The
publication-area copy diffs clean against its source (`diff -rq`, both families, no output), every file back
at 0444 and every directory at 0555. The repository is unchanged: `git status --short` shows only the two
files already modified when I started and the three `m9_*` files the orchestrator and the codex reviewer
wrote; no `__pycache__`, no `.pyc`, no git write. Every scratch artifact lived under
`_scratch/te-tracks-audit/p9b-opus/` and was removed with Python `shutil.rmtree`, leaving this report.
