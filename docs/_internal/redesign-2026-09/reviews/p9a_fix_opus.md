# Phase 9a fix re-review (Opus)
Verdict: PASS WITH ADVISORIES

All eleven items bite. The two blocking check defects are closed under my own mutations, 7 IRescue and 30
STARsolo replays, each refused by its named message except the five legal by design; the blocking
documentation clause is true of the table cell by cell. 64 mutations: 57 refused by name, 5 accepted by
design, 2 archives verifying clean and both discussed in A1. Identity moved where items 5 and 7 said: core
`5e2a156362cddc58c10ca90a4afee06be53086134a746937de4dc651c63bf813`, child
`198f39f0ef16875121fa65e1b1301f0d58c894488cc557765ce7f50c57a38bd1`, `CATALOG_ID`
`90cc18be5d4ee9342b57b58e4b8ad19e59f9e6b48b9a94bab9db615db1091b5e` in both, roster 52. Read-only
throughout; no git write, no rebuild, no publication; scratch removed with `shutil.rmtree`.

## Blocking

None.

## Advisory

- [A1] `src/lib/manifest.py:172` and `:628-632` — the retained provenance anchors `fetch_finished` only when
  `identity` carries `rank_scheme_version`: `expected_payload` adds the provenance path under that condition,
  and `sources_from_payload` falls back to `tracked_metadata[role]`, which `verify_build` supplies as
  `identity["build_sources"]`, when the file is absent. That branch has a live caller — the published
  implementation archive `763815187e…` is five-role with `dfam_snapshot.fetch_finished`, no retained
  provenance and no rank scheme, and it verifies (51 files, exit 0) only through it — so the condition is
  backward compatibility of the kind the phase-8 archive gets. Its cost is that the old shape is presentable:
  on a copy of the current archive I dropped `rank_scheme_version`, removed the provenance from the payload
  and the inventory, wrote `fetch_finished` as `1999-01-01T00:00:00.000000Z`, recomputed `BUILD_ID`, and the
  verifier exited 0 (`verified cc62cb4012516a636332c6d503419e675e984887c6…`), comparing the field with itself
  again. Not blocking: every archive this builder writes carries the provenance (`identity_from_payload`
  requires it unconditionally), both drift directions are refused on that shape, and an editor moving identity
  and provenance together keeps the anchor consistent anyway (case 9, exit 0). What is wrong today is
  `docs/RELEASES.md:54`, "The verifier compares
  the fetch timestamp, Dfam version and payload digest with the retained provenance", which states
  unconditionally what the code does for archives that retain it. Fix: say so in that sentence, or require the
  provenance whenever `dfam_snapshot` is declared and let `763815187e…` retire with the rebuild.
- [A2] `tests/checks/core/33_taxonomy_dfam_view.py:235` — the refusal list prints before the census, and
  `tests/run.sh:92` shows a passing check's first line alone, so the suite line for check 33 is now the ten
  mutation messages and the Dfam census the reviews and the rulings quote has left the suite output. Checks 34
  and 71 keep the summary first and append `refused: …`; fix: print in that order here too.
- [A3] Two of the ten rank-column mutations are refused by an earlier assertion than the new one, so their
  diagnostic does not name the column: `wicker_class_status` trips `assert dict(census) == expected`
  (`33:213`, a dict diff) because that status feeds `exact_wicker_*`, and giving an uncoded row a class trips
  the message-less `33:202`. Both refuse. Fix: call `check_rank_cells` before the census comparison, and give
  `33:202` a message.
- [A4] `config/mm39.env:15-16` pins `DFAM_SNAPSHOT_PATH` and `DFAM_SNAPSHOT_SHA256`; the provenance file that
  now anchors `fetch_finished` carries no pin, so an edited `data/dfam/*.provenance.json` flows through
  `00_fetch_sources.sh` into `identity.build_sources` with no refusal at build time. Fix: pin its digest beside
  the snapshot digest.
- [A5] Pre-existing, noted because item 9 touches the file: the pinned provenance JSON came from the ad-hoc
  `docs/_internal/redesign-2026-09/taxonomy/dfam_snapshot_fetch_20260917.py` and carries `census_sha256`,
  while `data/dfam/fetch_dfam_snapshot.py:96-103` writes `taxonomy_sha256` and `universe`, so a refresh
  yields a different key set. The four keys `verify_build` reads are in both, so nothing breaks.

## Item-by-item

| item | bites | evidence |
|---|---|---|
| 1 IRescue conservation | yes | `consumers.py:567-570` compares `matrix.shape` with `(len(features), len(barcodes))`, feature-name uniqueness and `matrix.sum()` against `molecule_total` (9, from `bam_manifest.json` and `record.bed`) before the dict. My 6 replays of `irescue_arc_allocation_4_2/counts`: extra 100-count row, duplicate feature line with counts, one count +1, one count zeroed, extra barcode column, dropped feature line — all refused, named. Allocation recorded in `irescue_allocation.json` and unasserted: any point on the EM line (A 5.5/6.5/7.0) passes the enclosing block, off-line values fail conservation. |
| 2 STARsolo confinement | yes | `consumers.py:738-763` derives the supported set per case from `starsolo_molecules.tsv` rows against the combined GTF spans (`GeneFull` uses the min/max envelope), so it is fixture-derived, not hardcoded; I proved derivation by adding one fixture row over `Edge` with 1.0 of matching support, which turns the same refused replay into a pass. 16 replays (4 cases × `Gene`/`GeneFull` × `matrix.mtx`/`UniqueAndMult-EM.mtx`) placing 0.5 on the chrB record `R|mm39|Edge|chrB|101|110|+`, plus codex's 4 HostGene→Edge shifts, all refused `STARsolo support outside fixture genes`. Host against TE stays observational: moving 0.4 between `HostGene` and the `SubB` record inside the allowed set passes, while adding 1.0 to `HostGene` inside the set refuses `STARsolo supported molecule total differs from fixture` in all four overlap replays, so the second clause bites too. |
| 3 class-less rank claim | yes | Measured on `taxonomy_dfam.tsv`: 54 names carry a class-less raw class (53 `Unknown`, 1 `Unspecified`), 53 leave every Wicker rank `missing`, and that set equals the 53 names whose `classification_leaf` is `Unknown` exactly; `UCON4` is the one class-less name with a code (leaf `Kolobok`, `wicker_code` `D`, class `Class II (DNA transposons)`, status `inherited`). `OUTPUTS.md:332-335` states label retention and the leaf-keyed rank rule as separate sentences and names `UCON4`, so the old rule is not readable back out. |
| 4 rank cell guards | yes | `check_rank_cells` re-derives from `wicker_code` plus `dfam_lineage_nodes.tsv`, both bound to the snapshot at `33:113-115` and `33:199`. Mutating each of the ten columns in a scratch copy of the materialized table and rerunning the real check refused all ten (8 named `Dfam rank cell differs: AmnSINE1: <column>`, 2 earlier, A3). Rewriting all ten cells coherently as a Class II TIR/hAT row with `wicker_code` untouched is refused, so the check is not comparing the table with itself. Check 34's two branches execute once each under `trace --count`: `build_dfam.py:116` and `:135`, refusing `Dfam invalid Wicker code: R/I/L/X` and `Dfam unknown Wicker superfamily letter: TIR/Z`. |
| 5 retained provenance | yes | `source/dfam_interspersed_mm39_snapshot.provenance.json` is in the build, byte-identical to the tracked file, in the inventory and in the 52-entry roster. Reseal to `1999-01-01T00:00:00.000000Z` and to a neighbouring instant (`…831393Z`), each with `BUILD_ID` recomputed, refused `dfam_snapshot: fetch_finished differs from retained provenance`; drifting the retained file instead, with its inventory digest updated, refused the same way. `build_fixture.py:108-112` writes a real provenance file and no `patch("manifest.tracked_provenance"…)` survives anywhere, so check 71's three provenance refusals come from the real branch. Residual: A1. |
| 6 enumerated layouts | yes | `SOURCE_LAYOUTS` at `manifest.py:49`. Refused on the real archive: the hybrid keeping `dfam_snapshot` without `rmsk_out`, dropping `chromAlias`, the legacy three-role set on a snapshot-carrying archive, and a sixth role — all `identity.build_sources: source roles differ`. The phase-8 archive still verifies, 43 files, exit 0. |
| 7 clades and rank scheme | yes | `clade_count` agrees with the snapshot on all 1,220 rows (`{1: 1185, 0: 26, 2: 7, 3: 1, 7: 1}`); the 9 snapshot models with several clades sit in 9 names, each with `clade_count > 1` (Tigger1 7, Charlie12 3, seven at 2), and no name reaches `clade_count > 1` without one. `OUTPUTS.md:346-347` names `clades` a display field and `dfam_model_clades.tsv` the join key; `:300` states `identity.rank_scheme_version`, which holds `rank_scheme_wicker_v1` in core and child. |
| 8 producer range | yes | `RELEASES.md:197-201` gives 5.5 GB to 6.0 GB as a range for the export writer, its 5,994,254,336 peak, `provenance.peak_rss_bytes` (5,525,536,768 in this build, inside the range) and, separately attributed, the 9,026,424,832 / 717.201 s complete rebuild. `docs/RUNBOOK.md` carries its phase-9a consumer-environment section and no producer figures; its mtime predates the fix run. |
| 9 fetch output name | yes | `fetch_dfam_snapshot.py:93` builds `dfam_{universe}_{genome}_snapshot.json.gz` with `genome` read from the build's `SOURCES.json`, and the provenance name from it; `interspersed`/`mm39` reproduces both current names, `all_rmsk`/`hg38` gives `dfam_all_rmsk_hg38_snapshot.json.gz`. The tracked snapshot is still `ac1885c87963ca28071e7312a31220fc918111c057e3bbc6375fdda9255c701f`, identical in `data/dfam/`, `config/mm39.env` and `source/`, and `manifest.provenance_path` derives the same name the writer uses. |
| 10 contig roster message | yes | `contigs.py:134` interpolates `len(expected)`; a fixture missing one ucsc row refuses `namespace exports require the 9 UCSC inventory entries`, and `EXPORT_JOBS` yields 9. The file's whole diff is that one line. |
| 11 cellranger pin | yes | `OUTPUTS.md:676` "the check pins 3 GB with `mkref --nthreads=1 --memgb=3`" and `consumers.py:896` "mkref pins 3 GB"; no doc states a requirement or a minimum. |

## Mutations run

| target | mutation | outcome |
|---|---|---|
| `irescue_counts` | extra matrix row carrying 100; extra barcode column; dropped feature line | 3 refusals, `IRescue matrix dimensions differ from rosters` |
| `irescue_counts` | duplicate feature line carrying 100 | refused, `IRescue duplicate feature name` |
| `irescue_counts` | one feature's count +1; one count zeroed | refused both, `IRescue matrix molecule total differs from fixture` |
| `irescue_counts` | 1.0 moved between the two features | accepted, and correctly: on the EM line, conservation holds |
| `starsolo_support` | 0.5 on `Edge` (chrB), 4 cases × 2 features × 2 matrices | 16 refusals, `STARsolo support outside fixture genes` |
| `starsolo_support` | 0.3 moved HostGene→Edge, overlap × 2 features × 2 matrices | 4 refusals, same message |
| `starsolo_support` | 0.4 moved HostGene→SubB inside the allowed set | accepted, split stays observational |
| `starsolo_support` | +1.0 on HostGene inside the set, overlap × 2 features × 2 matrices | 4 refusals, `STARsolo supported molecule total differs from fixture` |
| `starsolo_support` | 1.0 on `Edge` with a matching fixture molecule added | accepted with the row, refused without it |
| check 33 | each of the ten Wicker value and status columns := `MUTATED` | 10 refusals, 8 naming the column (A3) |
| check 33 | all ten cells rewritten as a coherent Class II row; all five statuses := `inherited`; uncoded row given a class | 3 refusals |
| check 34 | `trace --count` over `build_dfam.derive_ranks` | both guard lines hit once, both raise |
| `verify_build` | `fetch_finished` reseal, two instants; provenance-side drift | 3 refusals, `dfam_snapshot: fetch_finished differs from retained provenance` |
| `verify_build` | `rank_scheme_version` dropped alone | refused, `payload roster differs: ['source/…provenance.json']` |
| `verify_build` | rank scheme + provenance + inventory entry dropped, `fetch_finished` forged | **verified clean** (A1) |
| `verify_build` | provenance and identity `fetch_finished` moved together | verified clean, inherent to a self-describing archive |
| `verify_build` | four role sets: no `rmsk_out`, no `chromAlias`, legacy three, six roles | 4 refusals, `identity.build_sources: source roles differ` |
| `build_namespaces` | exports roster missing one ucsc row | refused, names the roster size 9 |

## Copy method and artifact integrity

Reported because the orchestrator asked, and because one copy was hardlinked. Method per target:

| mutation target | copy method | files I wrote |
|---|---|---|
| IRescue and STARsolo replays | `shutil.copytree` with the default `copy2`, real bytes | `matrix.mtx*`, `features.tsv*` inside my own copies |
| check 33 rank cells | symlink shadow root, `TE_TRACKS_REFROOT` repointed; the symlink is unlinked before every write and recreated after | `tables/taxonomy_dfam.tsv` in the shadow only |
| `build_namespaces` roster | fresh directory of symlinks; `exports.tsv` written as a new file after removing the symlink | `tables/exports.tsv` in that directory |
| `verify_build` cases | **`cp -al`, a hardlinked copy of archive `5e2a1563…`**, directories chmod 0755, files left 0444 | `MANIFEST.json`, `BUILD_ID`, `source/dfam_interspersed_mm39_snapshot.provenance.json` |

Every write into the hardlinked copy went through one helper, `replace(path, data)`, which calls
`path.unlink()` and then `path.write_bytes(data)`, so each write created a new inode and broke the link
rather than writing through it; case 4's `PROV.unlink()` removed only my link. The evidence: in the archive
those three paths now hold `links=1` at their original inodes with mode 0444 and their published digests,
while my copy holds different inodes at mode 0664, and a file I never wrote (`universes.json`) still shows
one shared inode with `links=2` in both trees. The archive's bytes match its own inventory for every entry.
The reviewed build was never copied or written: the shadow was symlinks, and `tables/taxonomy_dfam.tsv`
carries `links=1`. The orchestrator's point stands on principle — the isolation rested on that discipline
plus the 0444 modes, and one `open("w")` would have reached the published archive — so a real copy is the
right instrument and `cp -al` the wrong one. Nothing I ran wrote into either build directory or `pubroot`.

On the one failing check in the orchestrator's concurrent run: I ran `tests/run.sh core` and six archive
verifies in that window, and check 41 alone holds about 9.4 GB resident, so two concurrent instances
approach 19 GB here. Checks 71 and 72 isolate themselves with unique `TemporaryDirectory` names under the
shared `pubtest`, so resource pressure explains it better than a shared path; naming the check would settle it.

## Identity and scope

Both ids recomputed from the canonical identity JSON with my own `sha256("te-tracks-build-v1\n" + …)`: core
`5e2a1563…` and child `198f39f0…` match their `BUILD_ID` files, and `catalog_id` gives `90cc18be…` for both,
so `CATALOG_ID` did not move. Core inventory 52 entries, 25 of them outside `exports/`, 27 export contracts,
five `build_sources` roles, `rank_scheme_version` `rank_scheme_wicker_v1`; payload bytes 15,301,538,537 and
`du -sb` 15,301,659,615, both as `RELEASES.md` states, as do all nine rows of its addition table, the three
namespace export sums and the 347,526,106 registration bytes. Every statement of 51 is gone; 52 appears in
`README.md:93`, `OUTPUTS.md:265`, `RELEASES.md:179` and `70_manifest_identity.py:53`. The child pins parent
`5e2a1563…` and parent catalog `90cc18be…`, inherits the rank scheme, and its
`exon_subtraction_summary.tsv` is byte-identical to `tests/expectations/mm39/exon_subtraction_summary.tsv`.
All six published archives verify: core 9ddf3622 (43 files), 763815 (51), 5e2a1563 (52) and the three child
archives, with `release.py verify-current` exit 0 for both families. `tests/run.sh core` is 26 of 26 pass, exit 0, zero
unsupported, with check 70 reporting the new ids and 52 payloads and check 71 the five new refusals;
`tests/run.sh consumers` under the te-consumers venv is 16 checks, 15 pass, 1 unsupported, Stellarscope's
boundary defect alone, so no new unsupported check appeared.

Scope: fifteen files carry mtimes inside the fix run (18:04–18:25 local, the run is `20260917T230459Z`), and
nothing else in the working tree does, so the fix wrote exactly `src/lib/manifest.py`,
`src/00_fetch_sources.sh`, `src/lib/build_dfam.py`, `src/lib/contigs.py`,
`data/dfam/fetch_dfam_snapshot.py`, `tests/lib/consumers.py`, `tests/lib/records.py`,
`tests/fixtures/publication/build_fixture.py`, checks 33, 34, 70 and 71, `docs/OUTPUTS.md`,
`docs/RELEASES.md` and `README.md`. Each maps onto the eleven items — `records.py` and `build_dfam.py` on
item 7's `clade_count`, `contigs.py` on the one-line allowance — and nothing is touched beyond them.
`docs/RUNBOOK.md`, `docs/DECISIONS.md`, `config/mm39.env`, `.gitignore` and the other checks keep their
implementation-run mtimes, so item 8's "add nothing to the runbook" holds. The working tree is 39
`git status --short` entries, the implementation's 38 plus `src/lib/contigs.py`. Added prose and comments
follow the wording rules: affirmative, no contrastive negation, one-line intent comments, contract
docstrings, no review or defect provenance; the one sentence stronger than the code is A1.
