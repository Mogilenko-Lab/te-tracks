# Phase 9a re-review (Opus)

Verdict: PASS WITH ADVISORIES — with one blocking documentation clause (B1); docs-only, no rebuild, `BUILD_ID` unaffected. None of
the three FAIL conditions holds: every acceptance number I recomputed matches, every contract deliverable is present and correct,
and every new check refused the mutations I aimed at it (33 mutations run, 24 refusals, 9 named gaps in A1). Read-only throughout;
the reviewed build verifies unchanged after my run (`release.py verify-current` → `763815187e…`, exit 0) and the working tree
still holds the implementer's 38 entries. `reviews/p9a_codex.md` appeared mid-run and I left it unread.

## Blocking

- [B1] `docs/OUTPUTS.md`, Dfam section, "RepeatMasker tokens span several ranks" — "Class-less annotations retain their source
  `Unknown` or `Unspecified` labels and explicit missing ranks." The table lacks that behaviour. Of the 54 names whose raw class
  is `Unknown`/`Unspecified`/`DNA?`, 53 carry missing ranks, and they are exactly the 53 whose Dfam leaf is `Unknown`; `UCON4`
  (raw `Unspecified`/`Unspecified`, exact hit, leaf `Kolobok`) carries `wicker_code` `D`, `wicker_class` `Class II (DNA
  transposons)`, status `inherited`. A consumer filtering "class-less ⇒ ranks missing" mis-handles it. Fix: attach the claim to
  its cause — class-less annotations keep their source labels, and ranks are missing for the 53 names whose Dfam leaf is
  `Unknown`.

## Advisory

- [A1] `tests/checks/core/33_taxonomy_dfam_view.py` — nine of the ten Wicker value/status columns can be corrupted with no check
  failing: `wicker_class`, `wicker_subclass(_status)`, `wicker_order`, `wicker_order_status`, `wicker_superfamily(_status)`,
  `wicker_family(_status)`. I mutated each in a shadow build and check 33 passed every time. Guarded: `wicker_code`,
  `wicker_code_uncertain`, `wicker_class_status` (through the census) and the "no code ⇒ every rank missing" branch. The published
  values are right today — I rebuilt all 1,220 × 36 cells from the snapshot and every cell matches — so this is a drift gap. Fix:
  re-derive the ranks per row from `wicker_code` plus the node tree, or census every per-rank status distribution. Check 34 also
  lacks a malformed-code case (`len(tokens) > 3`) and an unknown-superfamily-letter case, leaving those two build-error branches
  untested.
- [A2] `src/lib/manifest.py:170-180,610` — `fetch_finished` is the one `identity.build_sources` field anchored to nothing in the
  archive: `verify_build` passes `identity["build_sources"]` back in as `tracked_metadata`, so the field is compared with itself
  and only its syntax is checked. Rewritten to `1999-01-01T00:00:00.000000Z` with `BUILD_ID` recomputed, the archive verifies
  clean; dropping the `Z` refuses. The `.provenance.json` is not retained in the payload and `tracked_provenance()` reads the
  working checkout, which `verify_build` never consults; check 71 covers sha256/bytes/dfam_version, not this. Fix: retain the
  provenance JSON under `source/` so it joins the inventory and roster, compare against it, and add the 71 case.
- [A3] `tests/fixtures/publication/build_fixture.py:140` — `patch("manifest.tracked_provenance", …)` leaves the real
  provenance-reading branch and its `"{role}: provenance sha256 differs"` refusal exercised by no check; only a real build touches
  them.
- [A4] `clades` in `taxonomy_dfam.tsv` and `taxonomy_dfam_models.tsv` joins whole clade paths with `;`, the separator used inside
  each path, so the cell cannot be split back for the 9 multi-clade models (`DF000000891` holds 7 paths in one cell). The plan
  specified that join and `dfam_model_clades.tsv` is the parseable form. Fix: one sentence naming `clades` a display field and the
  clade table the join key.
- [A5] `docs/DECISIONS.md:173`, `docs/OUTPUTS.md:299` — "The rank scheme is `rank_scheme_wicker_v1`", yet no artifact records that
  identifier (absent from `MANIFEST.json` and every table; `taxonomy_rule_version` holds only `taxonomy_rule_v1`), so a consumer
  asked to pin the scheme has nothing to pin. Fix: record it in `identity` beside `taxonomy_rule_version` (moves `BUILD_ID`), or
  say it is documented, not pinned.
- [A6] `docs/RELEASES.md` — the phase-8 range "measured between 5.5 GB and 6.0 GB across in-container builds" became the single
  figure 5,994,254,336, and the new "peaks at 9,026,424,832 resident bytes and takes 717.201 seconds" is recorded in no artifact
  (`provenance` carries only stage 30's `peak_rss_bytes`). Milestone 5 H3 wants that range in the runbook; it now sits in neither
  document.
- [A7] `data/dfam/fetch_dfam_snapshot.py:92` — the output name is hardcoded `dfam_interspersed_mm39_snapshot.json.gz` while
  `--universe` is required, so a refresh for another universe or assembly writes a file whose name contradicts its contents.
- [A8] `src/lib/contigs.py:134` (D6) — "the eight UCSC inventory entries" against nine in `EXPORT_JOBS`. Reported rather than
  silently fixed, correctly, since the file is outside the touch list. Fix under an explicit one-line allowance.
- [A9] D8 is not reproduced: `cellranger mkref --genome=tiny --fasta=… --genes=… --nthreads=1` with no `--memgb` completed exit 0
  and built the reference. `--memgb=3` is a defensive pin and the docs describe what the check runs, so nothing is wrong; the
  necessity claim is host-dependent.

## Seams

1. **Record profile vs catalog** — bound, not merely counted. Check 40 compares every row in order against records rebuilt from
  `universe_members` + `rmsk_records.parquet` + `taxonomy_canonical`: contig, `start_1`, `end_1`, strand, score and all twelve
  attributes. I mutated the real 1.6 GB file three ways — one row's start +1, one row deleted, one `gene_id` token altered — and
  check 40 refused each. Check 41 equates `gene_id` and `transcript_id` with the registration's `record_alias` identities
  row-by-row and requires `seen.all() and seen.sum() == distinct_features` (3,764,949), which is exactly-once multiset coverage;
  check 61 regenerates the ensembl and gencode files from the ucsc one and compares complete digests; check 70 recomputes the
  sha256 of all 51 inventory entries, so any byte change moves `BUILD_ID`.
2. **Dfam view vs snapshot** — no drift in the matched metadata; the rank derivation is the gap (A1). Per name, not in aggregate:
  my own match rule and tree walk reproduce all 36 columns of all 1,220 rows, all 1,263 model rows in order, all 300 nodes and all
  1,278 clade rows exactly. Every drift outcome has an explicit status — a name that leaves Dfam becomes `missing` (26 names,
  38,569 records); a name reaching only parts becomes `part_model_set` with `available_part_count` and `part_roles_present`; an
  uncoded path leaves every rank `missing`; a part-set path disagreement is a named build error; a catalog name absent from the
  snapshot fails check 33 at `names == sorted(snapshot["summaries"])`. `model_length_sum_bp` is never a denominator: it is only
  summed and asserted, and OUTPUTS states that full-length inference needs a validated projection to the pinned RepeatMasker model
  coordinates. Residual limit, documented elsewhere: the join crosses library versions (Dfam 4.0 against a 2018 library) and no
  status flags "same name, different model".
3. **Tracked source role vs verifier** — one input slips, `fetch_finished` (A2); nothing else does. Six manifest mutations on a
  hardlinked copy: `sha256`, `bytes`, `dfam_version` and the `path` directory each refuse, because the tracked branch compares
  against `source/SOURCES.json` and the inventory entry, both digest-bound. Dropping `rmsk_out` from `build_sources` also verifies
  — the role-set bound is laxer than needed so the phase-8 archive stays admissible — but loses no anchoring, since
  `catalog.sources` binds `rmsk_out` and `contig_set_sha256` binds `chrom_sizes`. Declaring the tracked role forces the four Dfam
  tables into the roster and vice versa, so tables and role are mutually binding.
4. **Do the new checks fail when they should?** Check 33 refused 13 of 16 table mutations — record_count, match_status,
  model_length_sum_bp, clade_compatibility, clades, subfamily_status, dfam_accessions, classification_path and leaf, wicker_code,
  wicker_code_uncertain, available_part_count, part_roles_present, clade_leaves, rmsk_class, dfam_repeat_type, dfam_release, a
  dropped clade row, a changed node code, a changed model length — and passed the nine rank mutations in A1. Check 34 refused all
  7 rule mutations, check 43 both registration mutations, check 17 all 5 profile mutations (attribute order, `gene_id` = name,
  `gene_type`, `gene_name` = family, shifted coordinates).
5. **IRescue rewrite** — correct and still load-bearing. It asserts identity joins (`assert_registered` on `(record,
  rmsk_record_id)` and `(subfamily, rmsk_name)`, plus `set(counts) <= registered`), roster and molecule conservation (`sum == 9`,
  B tied to A's residual), unique molecules on their feature in the simple cases, and floor ≤ count ≤ floor+3 bounds, and records
  the allocation in `irescue_allocation.json` without asserting a fixed point. Observed with the shims: 5.5/3.5 for 4/2 and
  4.5/4.5 for 3/3, in both ARC and OCM. Renaming one feature in the BED IRescue reads (identity) and doubling the returned counts
  (conservation) each fail the check.
6. **Public prose** — one blocking clause (B1) out of roughly 130 checkable claims; the rest matches the bytes. Verified against
  artifacts: every byte sum and the `du -sb` total, the addition table, the 51-file payload, 27 contracts and paths, 3,764,949
  rows and distinct genes on 59 contigs, 30,119,592 registration rows, the whole Dfam census, the four companion grains, the
  STARsolo allocations (Gene 1.5/1.5; GeneFull 2.98266/0.0173415; intronic 0.5/0.5; gap zero TE support), both suite outcomes, and
  every path named in the consumer-environment section. The label surprises hold in the data: all 10 `B1*` names sit under an
  `Alu` node with `wicker_superfamily` 7SL, the 65 `ERVL-MaLR` names resolve to the curated `MaLR` branch, `hAT-Charlie` splits
  into superfamily hAT and family Charlie. Plan 19's "node's RepeatMasker type and subtype equivalents" is satisfied in substance:
  the published `dfam_repeat_type`/`_subtype` equal the leaf node's values for all 1,194 matched names. Wording rules hold — no
  contrastive negation in the added prose, one-line intent comments, contract docstrings, no history or review chatter.

## Rulings on the reported deviations

- D1 accepted. All 53 uncoded exact names have Dfam leaf `Unknown` (own tree walk); plan 19 is authoritative and says so; OUTPUTS
  states the rule and fixture case `unknown_name` pins it.
- D2 accepted, reproduced. Phase-8 archive 43 entries / 24 contracts / 3 roles, verifies exit 0; new archive 51 / 27 / 5. The
  bound also admits dropping `rmsk_out`, without losing anchoring (seam 3).
- D3 accepted, reproduced exactly. The census TSV sums 3,760,582; 20 names differ; shortfall 4,367, because it counts only each
  name's plurality (class, family) row. The builder's `record_count` equals my catalog count for all 1,220 names and check 33
  recomputes it from the parquet.
- D4 accepted and necessary. Multi-record instances 445,649 (`all_rmsk`) against 434,707 (`interspersed`); mixed-name 30,699
  against 30,569; mixed-strand 23,245 against 23,244. LTR-only and L1-at-base-1 are universe-invariant predicates and OUTPUTS
  states the predicate for those two rows.
- D5 accepted. Deliverable 2 names `17_starsolo_profile.required.py` explicitly, so creating it was required; the touch list's
  omission is a prompt defect. The check earns `.required` (5 of 5 refusals).
- D6 accepted; the restraint was right (A8). D7 needs nothing further: my own `tests/run.sh core` on the frozen tree returned 26
  of 26, exit 0. D8 not reproduced (A9).

Scope: nothing is touched outside plan 19's phase 9a. The 38 status entries plus the three files under `data/dfam/` map onto the
touch list, with `17_starsolo_profile.required.py` the only file outside the enumerated list (D5). Allowed but unneeded, correctly
left alone: `build.sh` (stage discovery is a glob, so `src/25_build_dfam.sh` runs between 20 and 30 with no new argument),
`src/release.py`, checks 82 and 83, `20_irescue_exec.sh`, `tests/expectations/mm39/taxonomy_census.tsv`.

## Numbers recomputed

| quantity | contract | observed | command |
|---|---|---|---|
| `record_starsolo.gtf` rows / distinct `gene_id`, per namespace | 3,764,949 / 3,764,949 | 3,764,949 / 3,764,949, all three | own streaming parse, strict 12-key regex, catalog join |
| contigs / feature type / attributes | 59 / `exon` / twelve in order | 59 / `exon` only / exact order, 9 fields, no other key sequence | same parse |
| bytes ucsc / ensembl / gencode | 1,616,329,134 / 1,604,983,782 / 1,616,260,404 | identical | `stat -c%s` |
| `taxonomy_dfam.tsv` lines | 1,221 | 1,221 | `wc -l` |
| names exact / part / missing | 1,047 / 147 / 26 | 1,047 / 147 / 26 | own match rule over the snapshot |
| records under those | 2,797,852 / 928,528 / 38,569 | identical, sum 3,764,949 | own predicate over `rmsk_records.parquet` |
| part sets 3 / 2 / 1; L2-CR1 | 30 / 9 / 108; 6 | 30 / 9 / 108; 6 (L2a, L2b, L2c, L2d, L2d2, L3b) | same |
| model rows; nodes; coded nodes | 1,263; 300; 193 | 1,263; 300; 193 | own tree walk |
| multi-clade models; primate models and names | 9; 33 and 31 | 9; 33 and 31 | same |
| exact names mapped / inherited / missing | 884 / 110 / 53 | 884 / 110 / 53, all 53 leaves `Unknown` | own ancestor walk |
| companion lines models / nodes / clades | 1,264 / 301 / 1,279 | 1,264 / 301 / 1,279 | `wc -l` plus row-for-row equality |
| core `BUILD_ID` | `763815187e…` | identical | own `sha256("te-tracks-build-v1\n" + canonical identity)` |
| child `BUILD_ID` | `693ba1aa15…` | identical | same |
| `CATALOG_ID` core and child | `90cc18be5d…` | identical for both | same |
| new core inventory / contracts | 51 / 27 | 51 / 27 | `MANIFEST.json` identity |
| phase-8 archive inventory / contracts, verifies | 43 / 24, verifies | 43 / 24, `99_verify.py` exit 0 | direct run |
| snapshot sha256 | `ac1885c879…` | identical in `data/dfam/`, the taxonomy record, `source/` | `sha256sum` |
| binding fixture, pair-only then four-field | 2,000 / 1,001,000; 1,000 / 500,500 | identical | check 43 and its arithmetic |
| multi-record instances; LTR-only (`all_rmsk`) | 445,649; 722,280 | 445,649; 722,280 | own groupby and `-int` partition |
| mixed-name; mixed-strand (`interspersed`) | 30,569; 23,244 | 30,569; 23,244 | own groupby |
| records overlapping another | 8.07% | 429,440 / 5,320,771 = 8.0710% | own sweep, either strand |
| L1 records at model base 1 | 588 | 588 of 877,139 raw LINE/L1 | `consensus_start_1 == 1` |
| suites | 26 of 26; 16 checks, 15 pass, 1 unsupported | 26/26 exit 0; 15/1 with shims, 11/5 without | `tests/run.sh core`, `tests/run.sh consumers` |
| retention figures | RELEASES table | exports 4,638,043,480 / 4,531,250,735 / 4,637,401,144; payload 15,301,535,164; `du -sb` 15,301,655,992 | `find -printf`, `du -sb` |

## Agreement with codex review

Skipped by instruction (step 5 withdrawn for this pass). `reviews/p9a_codex.md` appeared in the tree during my run and I left it
unread, so these findings are independent.
