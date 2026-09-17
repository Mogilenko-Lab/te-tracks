# Milestone 7 re-review: numbers and checks (Opus)
Verdict: PASS WITH ADVISORIES

Every number phases 6 and 7 publish reproduced on an independent route; four historical RSS figures in plan 17 have no surviving carrier and are marked unverifiable. All six mutated subjects fail their check. Every accepted ruling in `p6_rulings.md` and `p7_rulings.md` landed as observable behaviour; one ruling's named check list is off by one check (advisory A2).

## Blocking
- none.

## Advisory
- **[A1] README.md:41-43 — the core-suite description stops at phase 4.** "Core checks cover … taxonomy (30 to 32) and exports (40 to 42)" omits 60-62 (aliases, namespaces, preflight) and 70-72 (identity, verifier, publication); `tests/checks/core/` holds 19 checks and the suite prints 19 lines. Milestone 5 ruling A5 set that sentence's shape, and phases 6 and 7 added six checks without extending it. Fix: name contigs (60-62) and identity and publication (70-72).
- **[A2] p7 codex A4's check list names 14 and omits 11.** `declared_key()` assertions sit in checks 10, 11, 12, 13 and 16 (`tests/lib/consumers.py:422`); check 14 has none, because MATES reads fixture-only CSV/BED and carries no `consumer_keys` entry to assert. `featureCounts`'s declared `GeneID` on both SAF files is likewise unasserted — its check 21 is unsupported here. The behaviour the ruling wanted is real: mutating `record.bed`'s `consumer_keys` `IRescue: name -> column4` in a scratch repo fails check 10 (exit 1; unmutated exit 0).
- **[A3] no archive on disk was produced by the reviewed commit.** Both manifests record `builder_git_sha` 99bf646 with `builder_git_dirty` true, so the published bytes come from the phase-6 commit plus uncommitted phase-7 work. I closed the gap rather than leaving it open: re-manifesting the same payload with the committed tree yields `BUILD_ID` 0e053139… and `CATALOG_ID` 0c0a959d… with an identity section equal to the published one (37.7 s).
- **[A4] four RSS figures in plan 17 are historical.** 5,891,116 KiB, 5,698,908 KiB, 5,968,367,616 B and stage 35's 3,853,776 KiB have no carrier now: the manifests that held the first three are superseded and `build.sh` instruments `30_*` alone, so no stage-35 measurement exists in any artifact. RELEASES' public claim is verifiable only at its 5.5 GB end (`provenance.peak_rss_bytes` 5,498,744,832). The unit arithmetic checks out (5,891,116 KiB = 6,032,502,784 B = 6.03 GB).

## Numbers recomputed

| quantity | published | observed | route |
|---|---|---|---|
| `BUILD_ID`, both roots | 0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a | identical in build dir and `pubroot/te_mm39/current`; both files match with final LF | own canonical encoder (`sort_keys`, `separators=(",",":")`, `ensure_ascii=False`, `allow_nan=False`) over `identity`, prefix `te-tracks-build-v1\n` |
| `CATALOG_ID`, both roots | 0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4 | identical, both files match | own encoder over `identity.catalog` |
| `identity` sections, two roots | equal | objects and canonical bytes equal | duplicate-key-rejecting parse, byte comparison |
| provenance keys differing | provenance only | `built_at`, `invocation_argv`, `peak_rss_bytes`, `peak_rss_measurement`; 10 keys equal including `validation` (36 assertions) | key-by-key diff |
| raw `MANIFEST.json` bytes | may differ | differ (39,372 vs 39,382) | byte comparison |
| inventory entries | 43 | 43, unique sorted, equal to the on-disk regular files outside the three identity files | manifest parse + `os.walk` |
| 43 digests and byte counts, both roots | all match | 86/86 `OK`, 0 size mismatches | `sha256sum -c`, `stat -c %s` |
| export contracts | 24 | 24: 8 per namespace, 21 `interspersed` + 3 `all_rmsk`, unique sorted paths | manifest |
| `tables/exports.tsv` | 24 rows | 24; paths equal the contract paths; every `sha256` equals the inventory entry | own csv pass |
| source bindings | four roles | md5/sha256/bytes agree with `SOURCES.json`, config pins and inventory; `catalog.sources` = `rmsk_out`; `build_sources` = `rmsk_table`, `chromAlias`, `chrom_sizes` | own md5/sha256 |
| `exports/ucsc` (8 files) | 3,021,714,346 | 3,021,714,346 | sum of `os.stat` sizes |
| `exports/ensembl` (8 files) | 2,926,266,953 | 2,926,266,953 | same |
| `exports/gencode` (8 files) | 3,021,140,740 | 3,021,140,740 | same |
| `all_rmsk` record BED per namespace | 332,554,184 / 316,524,255 / 332,461,688 | identical | same |
| registration gz | 347,526,106 | 347,526,106 | same |
| 43-file payload | 10,461,884,289 | 10,461,884,289 = exports 8,969,122,039 + tables 1,181,535,059 + source 311,224,840 + `universes.json` 2,351 | same |
| directory entries | 77,824 on ext4 | 19 directories × 4,096 | `os.stat` on directories |
| `du -sb` | "about 10.46 GB", provisioning size | 10,462,001,615 (build) / 10,462,001,625 (archive) = payload + dirs + identity files | `du -sb` |
| `provenance.peak_rss_bytes` | 5.5-6.0 GB, near 6.0 | 5,498,744,832 in the published archive; `null`/"unavailable for this invocation" in the build dir | manifest |
| plan 17's other RSS figures | 5,891,116 / 5,698,908 / 3,853,776 KiB, 5,968,367,616 B | unverifiable: superseded manifests; only stage 30 is instrumented | — |
| `contig_aliases.tsv` | 61 rows, injective, sorted | 61; all six columns injective and complete; sorted by `chrom_ucsc` | own csv pass |
| GENCODE rule | UCSC name without `_`, GenBank otherwise | recomputed column equals the published one on all 61 rows | own recomputation |
| alias lengths | pinned `chrom.sizes`; all 61 agree | equal to `source/mm39.chrom.sizes` and to the 61-name FASTA fixture (sha256 69070f84…, byte-identical to `audit/`) | own dict comparison |
| scaffold and chrM mappings | GL456210.1/GL456210.1; MT/chrM | identical | alias table |
| catalog records | 5,320,771 | 5,320,771 unique `rmsk_record_id` across 61 contigs | parquet scan |
| `interspersed` records | 3,764,949 | 3,764,949 | `universe_members.tsv.gz` scan |
| zero-interspersed contigs | `chr4_JH584295v1_random`, `chrM` with 2 and 4 catalog records | exactly those two; 2 and 4 | parquet + membership |
| contigs named | 59 interspersed / 61 `all_rmsk`, per namespace | 59/59/59 and 61/61/61 | `cut -f1 \| sort -u` |
| registration rows | 30,119,592 + one per catalog record | 35,440,363 total; 8 grammars × 3,764,949; `all_rmsk` contiguous from data row 30,119,593 | single `awk` pass |
| registration digests | decompressed 0726aa7b…, interspersed subset 314098c5… | identical | `zcat \| sha256sum` |
| distinct instance aliases | 3,152,636 | 3,152,636 (registration and parquet agree) | `awk` + parquet |
| mixed-name instances | 30,569 holding 95,830 records | identical | parquet |
| interspersed score > 1,000 | 1,224,713 (32.5 %) | 1,224,713 (32.54 %) | parquet |
| interspersed names / triple GeneIDs / two-label names | 1,220 / 1,220 / 20 | 1,220 names; 1,220 `distinct_features` on `taxonomy_triple.saf`; 20 names with >1 raw label | parquet + `rmsk_taxonomy.tsv` |
| preflight exits (plan 16) | 0; 39/39; 22/22; 0 with 2 reference-only; 40/38; 23/21; 1 | every leg reproduced, plus exit 1 on a bumped length, an empty intersection and an unreadable input | own runs + own set algebra |
| `universes.json` byte profile | insertion order, indent 2, `ensure_ascii=False`, final LF | round-trips byte-identical; keys unsorted; `schema_version` int 1 | re-serialize and compare |
| JSON gates | duplicate keys and nonfinite numbers fail | duplicate key, `NaN`, `Infinity` each exit 1; restored manifest verifies | tampered fixture manifest |
| committed builder reproduces the identity | — | `90_manifest.py` at 9d16506 on the same payload: both ids and the identity section identical | hardlinked copy with the three identity files unlinked first |

## Rulings audit

| ruling | landed at | command | observed |
|---|---|---|---|
| p6 codex B1 / Opus B1 | `tests/checks/core/60_contig_aliases.py:61-67` | `tests/run.sh core` | interspersed zeros on exactly the two contigs, `records_all` 2 and 4, `ge(1)` everywhere, sums 5,320,771 / 3,764,949; pass |
| p6 codex B2 / Opus B2 | `bin/te-tracks-preflight:5-8,105-110`; `docs/OUTPUTS.md:565-568`; plan 16 | check 62; own preflight runs | 82 cases pass; 0 / 2 / 1 per the amended gate |
| p6 codex B2 pointer | `reviews/m2_rulings.md:69-72` | `sed -n '67,74p'` | M1 carries the amendment |
| p6 codex B3 / Opus B3 | `src/lib/build_exports.py:322-333` (single entry, `default_universe` guard), `:342`; check 42:84,103-104 | check 42 | 46 registration rows, 8 inventory rows; undeclared-universe gate; pass |
| p6 codex A1 | `src/lib/contigs.py:131-134`; plan 17:19 | grep | UCSC roster derived from `EXPORT_JOBS` |
| p6 codex A2 | plan `18_phase8_gene_child_seam.md:8-10` | grep | explicit universe/variant/block inputs, own inventory, pinned alias source recorded |
| p6 codex A3 | `docs/DECISIONS.md` §3 | read | GTF at record and subfamily level plus the `all_rmsk` record BED, three namespaces |
| p6 Opus B4 | README truth table (24 export rows, contigs fixtures) | core suite | rows read `delivered, tested`; 60-62 pass |
| p6 Opus A1 | `build_exports.py:199,305`; check 61:35-61 (no exception); `OUTPUTS.md:305-307` | check 61 | all 24 files sorted by their own name column; `ucsc family.bed` c14ccf42… |
| p6 Opus A2 | `build_exports.py:314-317` | grep | `ranks` empty on the record-only pass |
| p6 Opus A3 | `src/lib/contigs.py:126` | read | "Add renamed files to the inventory" |
| p6 Opus A4 | plan 17:21-24; `OUTPUTS.md:299-301` | read, own sums | eight-file statement; figures later superseded by p7 codex B2 |
| p6 Opus A5 | check 60:27-28 | check 60 | fixture pinned by literal sha256 69070f84… |
| p6 Opus A6 | `bin/te-tracks-preflight:43-46,94` | own runs; check 62 symlink case | walks up from `path.absolute()`; prints `alias_table` |
| p6 Opus A7 | check 61:63-111 | check 61 | 16 renamed files regenerated, digests equal |
| p7 codex B1 / Opus A1 | `src/lib/manifest.py:194-241` (`verify_export_contracts`, no `EXPORT_JOBS`/`EXPORT_CONTRACTS`), `:27-28`, `:416-425`; check 71:71-84; check 72:73-88; `RELEASES.md:104-107` | checks 71, 72; own driver case 4 | 24 → 27 contracts installs and selects; A stays selectable and verifiable; unpublished rule version and roster drift rejected |
| p7 codex B2 / Opus B1 | `RELEASES.md:157-164`; plan 17:21-24 | own `stat` sums | all five figures exact; `du -sb` stated separately as provisioning size |
| p7 codex A1 | check 71:44-86 | core suite | fixture cases 1.620 s; real build verified unchanged |
| p7 codex A2 / Opus A3 | `src/release.py:84-95,130-135` | own driver cases 2, 4b | `converged`, then `selected` once under the held lock |
| p7 codex A3 | `README.md:154-155`; `manifest.py:258` | grep | `SPECIES` admission sentence present |
| p7 codex A4 (first half) / Opus A5 | `build_exports.py:38`; `RELEASES.md:63-66`; `OUTPUTS.md:482` | grep; consumers suite | `14761 ATAC` gone from `record.bed`; key-drift fails check 10; see advisory A2 |
| p7 codex A5 | `RELEASES.md` (no "supplied retention baseline" / "phase 6 fix verification"); `DECISIONS.md` §7; `README.md:47-49,154-156` | grep | phrases absent; entry 7 is four sentences |
| p7 codex A6 | check 72:107-118; `RELEASES.md:139` | check 72; own driver case 9 | `Barrier`-synchronised installs; five host-qualification items named |
| p7 Opus A2 | `manifest.py:135-141,274-283`; check 70:38-40 | own driver case 12 | chromAlias byte change → new `BUILD_ID`, `CATALOG_ID` unchanged, re-verify exit 0 |
| p7 Opus A4 | `src/release.py:78-81`; check 72:137,189,201 | own driver cases 7, 8 | `current -> archive/<id>: <fault>` on dangling and removed selectors |
| p7 Opus A6 | `RELEASES.md:165-166`; plan 17:24 | grep | 6.0 GB with `provenance.peak_rss_bytes`; no stage-35 figure in public prose |
| p7 Opus A7 | `RELEASES.md:36-38` | grep | toolchain versions are the comparable evidence; image identity recorded when exposed |
| p7 Opus A8 | check 72:186-243 | check 72; own driver cases 5-8 | all seven cases exit 1 with their message, state preserved |

## Check coverage

| failure mode | check | mutation result |
|---|---|---|
| coverage counts drift from the membership table | 60 | `contig_coverage.tsv` `chr19` `records_interspersed` +1 → **fail** at 60:59 (recomputed dict) |
| a renamed export payload drifts while `exports.tsv` agrees with it | 61 | `ensembl subfamily.saf` last row `End` +1 with its `exports.tsv` digest updated → **fail** at 61:108, the independent regeneration route alone |
| preflight stops gating export-only contigs | 62 | `return 2 if only_export else 0` → `return 0` in a scratch repo → **fail**, six deviations reported |
| a payload file drifts from its declared digest | 70 | `universes.json` +1 byte → **fail** at 70:56 |
| the verifier accepts a payload the manifest does not describe | 71 | `contig_coverage.tsv` `chrM` → `chrm` → **fail**, `verify: inventory bytes or sha256 mismatch: tables/contig_coverage.tsv` |
| installed payloads are not read-only | 72 | `normalize_modes` 0444 → 0644 in a scratch `release.py` → **fail** at 72:248 |
| declared consumer key drifts | consumers 10 | `record.bed` `IRescue: name` → `column4` → **fail** (exit 1) |

`tests/run.sh core --refroot <mine>` (real build hardlinked, so the orchestrator's inodes were never written): 19 lines, all `pass`, `checks=19 pass=19 fail=0 unsupported=0`, exit 0, 13 m 8 s — 01 runner selftest; 10 parser (6 records); 11 qualification (13 metrics, 10 disagreements); 20 records schema (5,320,771 / 24 columns); 21 instances (4,696,900); 22 universes (17 classes, 3 collision pairs, 20 multi-label names); 23 record fixtures; 30 taxonomy canonical (18,484 names, min share 0.840 MER63C); 31 Dfam agreement (`[]`); 32 rule fixtures (31 cases); 40 exports shape (3,764,949 rows; 1,220/49/1,220); 41 registration (30,119,592 + 5,320,771; instances 3,152,636; 24 inventory hashes); 42 export fixtures (8 exports, 46 rows); 60 aliases (61 injective; 5,320,771 / 3,764,949; 2 and 4); 61 namespaces (24 sorted, 16 regenerated); 62 preflight (82 cases); 70 identity (both ids, 43 payloads); 71 verifier (real build unchanged; four named discrepancies; 1.620 s); 72 publication (4 archives after evolution, 6 after concurrency, modes).

`tests/run.sh consumers --refroot <mine>`: `checks=13 pass=8 fail=0 unsupported=5`, exit 0. Supported: 00 tool inventory (bedtools 2.31.1, samtools 1.21, five executables absent); 10 IRescue 1.2.0 (record 11, subfamily 8); 12 TEsingle 1.0 (UR cutoff 999/1000); 13 TEtranscripts 2.2.4 / TElocal 1.1.3 (8 groups; locInd 11/8); 14 MATES 0.1.8 (eight-column pair); 16 family/triple readers (8 GeneIDs, three `TwoLab` rows one triple); 22 bedtools; 23 samtools (ARC 13, OCM 26, bulk 26; UB 11, UR 12). Unsupported with reasons: 11 Stellarscope right-boundary defect, observed `0,1,1,1`, expected `0,1,1,0`; 15 IRescue `chrcat`, `gawk` absent; 20 `irescue` absent; 21 `featureCounts` absent; 30 DuckDB module absent.

Publication cases, my own driver over `build_fixture.py` as a black box (13/13 as documented): install; converge (one archive, first manifest bytes retained, staging removed); changed payload (new `BUILD_ID`, same `CATALOG_ID`, two archives); added export under an extended roster (24 → 27 contracts, installs with `--select`, A re-verified and re-selectable, `verify-current` exit 0, `CATALOG_ID` held); corrupt staging (`inventory extra file: stowaway.txt`, staging kept, selector unchanged); forged `BUILD_ID` (exit 1 naming the archive); dangling `current` (exit 1, link and staging preserved, archive set unchanged); removed archive under `current` (`select` and `verify-current` both exit 1 with the selector-scoped message); two concurrent installs behind a barrier (1 installed + 1 converged, one archive); two concurrent selects (last valid selection stands, `verify-current` exit 0); modes (`archive/` 2775, 0 payload entries off 0444/0555); chromAlias byte change (new `BUILD_ID`, `CATALOG_ID` stable, re-verify exit 0); install of the re-manifested build.

No git write happened. `git reflog -3` still leads with `9d16506 HEAD@{0}: commit: Phase 7: identity and publication`; HEAD 9d16506; no `__pycache__` anywhere in the repository; all eleven consumer checkouts under `.ref/` report 0 dirty paths, 0 `__pycache__` and 0 `.pyc` (`14839-DM-cGAS` and `sene/` untouched). 265 of 266 tracked files are byte-identical to my start-of-review md5s; the one difference, `plans/…/19_phase9_acceptance_park.md`, plus the four new untracked files (`reviews/m7_codex.md`, `reviews/m7_divergent.md`, `reviews/m7_rulings.md`, `consults/gene_child_consult.md`) are the orchestrator's own concurrent writes. The build directory ends with 43 payload files at 0664 summing to 10,461,884,289 bytes and both identity files intact; `pubroot` holds one archive, a relative selector, all payload entries at 0444/0555, `archive/` 2775, and `.staging` and `pubtest` empty. Scratch under `_scratch/te-tracks-audit/m7-opus/` is removed (1,021 files, 344 directories; the 214 mode changes were confined to my own single-link copies, never a hardlinked build inode).

Portable line: *a check earns its keep only when you can name the wrong build it would have caught.*