# Phase 7 rulings (identity and publication)

Implementer `te-tracks-p7-impl` (codex `gpt-6-astra`, xhigh, 2,477 s) from `prompts/p7_impl.md`; codex exit 0.

## Orchestrator verification before the reviews

- Identities: `BUILD_ID` `d9e6c18c638ece07db99e4650db05486ecee20ebd02a87c71ff20064a52f24d9` and `CATALOG_ID`
  `9a42ec53135a203c4b458b0c7e77584917db1cc205fe2b7ae1932dd1f491340b` recomputed by the orchestrator with its own
  encoder from `MANIFEST.json` for the build directory and for `pubroot/te_mm39/current`; both files match in both
  places. The two `identity` sections are equal; `provenance` differs in `built_at`, `invocation_argv`,
  `peak_rss_bytes` and `peak_rss_measurement` alone. The `--root` build from cached sources therefore reproduced the
  identity of the build assembled stage by stage across phases 1 to 6, and the implementer's second `--root` build
  converged on the same archive.
- Inventory: 43 entries; the sorted list of regular files on disk outside the three identity files equals the
  inventory; every size and sha256 recomputed with `sha256sum` agrees (0 mismatches). 24 export contracts.
- Published root: one archive, `current -> archive/<BUILD_ID>` relative, `.staging` empty, `archive/` mode 2775, the
  archive directory 0555, every payload file 0444 and every payload directory 0555 (0 exceptions).
- `release.py verify-current` prints the id and exits 0; `99_verify.py` on the build directory exits 0 and leaves
  every path's mtime and size unchanged.
- `tests/run.sh core`: 19 pass, exit 0, 14 min 55 s wall (check 71's full copy of the build included);
  `tests/run.sh consumers`: 8 pass, 5 unsupported, exit 0. No bytecode under `src/`, `tests/`, `bin/`; `pubtest`
  empty afterwards.
- Sizes measured as sums of regular file sizes: exports `ucsc` 3,021,714,346, `ensembl` 2,926,266,953, `gencode`
  3,021,140,740 bytes (8 files each); registration 347,526,106; the 43-file payload 10,461,884,289; with the three
  identity files 10,461,923,990. The figure 10,461,962,113 carried since milestone 5 equals the payload plus 19
  directory entries of 4,096 bytes (`du -sb`); the per-namespace figures 3,021,713,838 / 2,926,268,559 /
  3,021,138,299 match neither measurement and are superseded.
- Provenance of the installed archive: builder sha `99bf646`, dirty `true` (the phase 7 work uncommitted), export
  writer peak 5,968,367,616 bytes (5,828,484 KiB) for stage 30, image evidence `/etc/cloud/build.info` with the
  container digest unavailable.
- Git: reflog head `99bf646`; nine checkouts under `.ref` clean; `git status` lists the implementer's files plus the
  orchestrator's three `docs/_internal/` edits. Public prose grep clean; no history chatter in comments.

## Deviations reported by the implementer

1. `docs/DECISIONS.md` entry 7 rewritten to publish both ids and the ledger key: the prompt's contract section asked
   for it (milestone 5 ruling M1) while the touch list allowed the two deferral sentences alone. The contract section
   binds; the touch list was the prompt's error. Accepted as delivered.
2. A directory renamed across parents needs write permission on itself (its `..` entry changes), so the build root
   receives 0555 after the rename, under the lock and before selection. POSIX semantics; accepted, and
   `docs/RELEASES.md` states it.
3. Export byte sums differ from the documented baseline. Ruled above: public documents carry the measured sums of
   regular file sizes with the measurement named; the fix restates `docs/RELEASES.md`, plan 17 and the session record.

## Codex review (`p7_codex.md`, verdict BLOCKING)

Codex reproduced both identities with its own encoder, matched all 43 inventory entries in both
roots, ran core (19 pass) and consumers (8 pass, 5 unsupported), and probed the publication
seam with tiny fixture builds. Its findings and my rulings:

- **B1 accepted (blocking).** The orchestrator reproduced the reading: `verify_build` recomputes
  the export roster from the running builder's `EXPORT_JOBS` and `EXPORT_CONTRACTS`
  (`src/lib/manifest.py:152-169`, `356-357`) and pins `taxonomy_rule_version` to the current
  constant (`347`). An archive built under an earlier roster therefore fails verification under a
  later builder, and `install --select` (`src/release.py:129`) rejects a healthy `current`. Ruling:
  the builder authors the declaration and the verifier judges an archive against its own
  declaration. Concretely, `verify_build` checks `identity.export_contracts` for well-formed
  entries (known keys; `export_path` of the shape `exports/<namespace>/<universe>/<variant>/<file>`
  whose components equal the entry's `namespace`, `universe_name`, `variant` and `format`;
  `feature_level` from the known set) and then requires `tables/exports.tsv` rows, the export
  files present, their row counts and their digests to equal that declaration. The authoring-time
  cross-check against `EXPORT_JOBS` stays in `identity_from_payload`. `taxonomy_rule_version` and
  the universe predicate grammar are accepted from tuples of published versions that only grow
  (`taxonomy_rule_v1`; predicate schema 1); `schema_version` keeps its single accepted value and a
  future manifest schema adds a verifier branch. Check 72 gains the genuine evolution case: build A
  under the current roster is installed and selected; build B carrying one added export (the
  fixture extends the job registry and the contract table, as the codex probe did) installs with
  `--select`, which re-verifies A and selects B; `select --build-id A` and `verify-current`
  succeed; the verifier rejects an archive whose `exports.tsv` roster differs from its own
  declaration and an archive declaring an unpublished taxonomy rule version.
- **B2 accepted;** it restates deviation 3 with the same measurements. Public figures become the
  sums of regular file sizes: `ucsc` 3,021,714,346, `ensembl` 2,926,266,953, `gencode`
  3,021,140,740, registration 347,526,106, 43-file payload 10,461,884,289; the
  `all_rmsk` record BED measures 332,554,184 / 316,524,255 / 332,461,688 bytes, replacing "318 MB
  per namespace". The fix restates `docs/RELEASES.md`, plan 17 lines 21 to 24 and session.md lines
  196 to 197, and names the measurement as file sizes; directory entries are stated separately
  where a total is given.
- **A1 accepted.** The filesystem is ext4 without reflinks, so check 71 copies 10.46 GB in 33 s
  for two corruption cases. Check 71 keeps the real-build verification with the size and mtime
  comparison and moves the flipped-byte and extra-file cases onto a tiny publication fixture
  build; the verifier path is identical.
- **A2 accepted narrowly.** In `install --select`, when the verified `current` archive is the
  install target itself (`existing_id == identifier`), the convergence branch reuses that
  verification under the held lock. Staging verification and every other verification stay.
- **A3 deferred to phase 8** (family-specific identity, parent validation), which is that phase's
  scope. The fix adds one sentence to the genome configuration prose stating that admitting a
  genome config requires its `SPECIES` entry.
- **A4 accepted.** `consumer_keys` declare tested readers; `14761 ATAC` has no consumer check and
  leaves `EXPORT_CONTRACTS["record.bed"]`, while `docs/OUTPUTS.md` keeps describing the ATAC route
  on the `all_rmsk` record BED. Each consumer parser check (10, 12, 13, 14, 16) asserts the key it
  exercised against the declared `consumer_keys` entry, so contract drift fails a test. This
  changes `export_contracts` and therefore `BUILD_ID`; the fix regenerates the build directory's
  manifest and republishes the scratch root, and the records carry the new ids.
- **A5 accepted.** Public prose states measured release properties without project history:
  "supplied retention baseline" and "phase 6 fix verification" leave `docs/RELEASES.md`;
  `docs/DECISIONS.md` entry 7 shrinks to four sentences and gains the verifier-against-its-own-
  declaration sentence from B1; README lines 46 to 48 and 152 to 153 describe the delivered
  state (manifest, identities, publication) with hg38 as the remaining deferral.
- **A6 accepted in part.** The concurrency cases gain a start barrier so the two publishers
  overlap; the changed-payload case stays as written since a changed byte is a changed build. The
  remaining consult cases (interrupted transfer, reader during swap, disk full, cross-filesystem
  staging, ACL access) are covered by construction (verification before install, one-filesystem
  rename, atomic selector replacement, readers holding the resolved archive) and are named as host
  qualification items in `docs/RELEASES.md`; failure injection for them waits for the host build.

Codex also confirmed the three implementer deviations as ruled above, the dangling-`current`
behaviour (selection aborts naming the missing archive and preserves the link), the lock wait
and continuation, and the POSIX basis of the cross-parent rename permission.

## Opus re-review (`p7_opus.md`, verdict FAIL)

Opus recomputed both identities and all 43 digests with its own encoder, drove 20 publication cases
against fixture builds, executed the pandas and R `data.table` reader settings, and confirmed the
verifier's purity on all 64 paths. The codex review landed after Opus started, so its agreement
table was skipped; the two reviews converge on the retention figures and the version-locked
verifier. Rulings:

- **B1 accepted;** identical to codex B2 and deviation 3. The `du -sb` figure for the whole build
  directory (10,462,001,814 bytes) is stated separately as the provisioning size.
- **A1 accepted;** identical to codex B1. With published-version tuples and verification against
  the archive's own declaration, `select`, `install --select` and `verify-current` accept earlier
  archives, so no manual re-selection step exists to document; `docs/RELEASES.md` states how the
  verifier treats versions (fix item 7).
- **A2 accepted as a contract amendment.** `CATALOG_ID` protects ledger continuity of the record
  catalog, and the record catalog is produced from `rmsk_out` alone: the UCSC rmsk table is a
  qualification cross-check, `chromAlias` feeds namespaces and `chrom.sizes` feeds bounds and the
  build-scope `contig_set_sha256`. `identity.catalog.sources` narrows to `rmsk_out`; the other
  three sources move to a sibling identity key `build_sources` with the same per-source shape, so
  `BUILD_ID` still binds all four and `CATALOG_ID` holds across an alias or table refresh with
  byte-identical canonical tables. Check 70 gains the mutation (a `build_sources` digest changes
  `BUILD_ID` alone). Both identities of the scratch build change; nothing published on the host
  depends on them yet. The owner may overturn this with the other `CATALOG_ID` rulings.
- **A3 accepted** together with codex A2: `select_locked` verifies the existing selection first and
  returns when it already names the candidate; the candidate is verified once otherwise.
- **A4 accepted.** `verify_current` reports archive faults under the selector:
  `current -> archive/<id>: <fault>`; check 72's dangling and corrupt-selector cases assert the
  prefix.
- **A5 accepted in its first half** (codex A4, `14761 ATAC` leaves). The second half is ruled the
  other way: `consumer_keys` state the reader's key column and grammar for a file, a fact of the
  file format that holds for every universe of that file, so the `all_rmsk` copy declaring IRescue
  and bedtools is truthful; tested routes per universe live in the OUTPUTS.md route table.
  `docs/RELEASES.md` states that reading of `consumer_keys` in one sentence.
- **A6 accepted.** 5,891,116 KiB is 6.03 GB, and this build's provenance records 5,968,367,616
  bytes; the public floor reads 6.0 GB resident with `provenance.peak_rss_bytes` as the per-build
  record, and the stage 35 figure leaves `docs/RELEASES.md` since only stage 30 is instrumented and
  the floor is the maximum. Plan 17 and the session record carry the KiB measurements with the
  corrected unit.
- **A7 accepted.** The host-build sentence names the recorded toolchain versions as the comparable
  evidence and states that the image identity is recorded when the container exposes one.
- **A8 accepted for the cheap cases:** check 72 gains `install --select` against a dangling
  `current`, a removed archive directory under `current`, `current` as a regular file and as an
  absolute symlink, staging outside `.staging`, a non-hex `--build-id` and a symlinked family root,
  each exiting 1 with its named message and preserving state. The cross-filesystem guard stays a
  host qualification item (codex A6). The genuine added-export case is codex B1's evolution case.

Opus additionally confirmed the `rmsk_out` pin against the ADR67 consult's independent hashes, the
`universes.json` byte profile, the export/table/source split (8,969,122,039 / 1,181,535,059 /
311,224,840 bytes) and the prose and comment conventions in every phase 7 hunk.

## Fix loop (`prompts/p7_fix.md`, unit `te-tracks-p7-fix`; `prompts/p7_fix2.md`, unit `te-tracks-p7-fix2`)

The fix unit implemented the twelve items, re-manifested the build directory and republished the
scratch root. New identities: `BUILD_ID`
`0e053139fea4fba3e819d333b4eec1f8998f1d79f34da82360a69311a4bb8c9a`, `CATALOG_ID`
`0c0a959dea69e397890b590b640162d5bd45e71a88f6468cadd4b7615022b4a4`; the 43 payload files are
byte-identical to the reviewed build. Its reported deviations and the rulings:

- **`du -sb` and per-build peak RSS moved.** After re-manifesting, `du -sb` reads 10,462,001,615
  bytes for the build directory and 10,462,001,625 for the published archive, against the
  10,462,001,814 the fix prompt stated; the republished build's `provenance.peak_rss_bytes` is
  5,498,744,832 against the 5,968,367,616 cited. Both literals vary with provenance bytes and with
  the run. Ruling: public prose carries the stable measured properties. `docs/RELEASES.md` states
  "about 10.46 GB by `du -sb`" beside the exact payload sum, and a resident floor "near 6.0 GB,
  measured between 5.5 GB and 6.0 GB across in-container builds" with `provenance.peak_rss_bytes`
  as the per-build record. Unit `te-tracks-p7-fix2` made that two-sentence edit; plan 17 records
  the individual measurements.
- **The prompt's `awk` sum printed scientific notation;** the unit confirmed the three namespace
  sums with integer arithmetic. The orchestrator's verification script sums with Python.
- **No touch-list deviation.** The concurrent changes the unit saw under `docs/_internal/` are the
  orchestrator's own records and prompts.

Check 72 now leaves four archives after the evolution case and six after the concurrency cases;
check 71's fixture cases run in about five seconds.

## Orchestrator verification of the fix (`_scratch/te-tracks-audit/p7_verify/verify_b.log`)

- Both identities recompute with an independent encoder in the build directory and in
  `pubroot/te_mm39/current`; identity sections equal; provenance differs in `built_at`,
  `invocation_argv`, `peak_rss_bytes`, `peak_rss_measurement`. Identity keys now include
  `build_sources` (`chromAlias`, `chrom_sizes`, `rmsk_table`) and `catalog.sources` holds
  `rmsk_out` alone; `record.bed` declares `IRescue` and `bedtools`.
- 43 on-disk payload files equal the inventory list; 0 digest or size mismatches; the
  `exports.tsv` path and digest columns are equal across both roots, so the payload is unchanged
  from the reviewed build.
- Installed archive: 0 files off 0444, 0 directories off 0555, `archive/` 2775, one archive,
  relative `current`, empty `.staging`; `verify-current` exit 0.
- Verifier independence (codex B1, Opus A1): a scratch copy of `src/` with
  `TAXONOMY_RULE_VERSION = "taxonomy_rule_v2"` and `record_extra.bed` added to the `all_rmsk` job
  verifies the real build (exit 0) and `verify-current` exits 0 against the published root.
- `99_verify.py` leaves the build directory byte- and mtime-identical.
- Public files carry no superseded figure or phrase; `docs/DECISIONS.md` entry 7 has four
  sentences; `verify_build` imports neither `EXPORT_JOBS` nor `EXPORT_CONTRACTS`.
- `tests/run.sh core` 19 pass in 12 min 28 s (check 71's fixture cases 2.0 s); `tests/run.sh
  consumers` 8 pass, 5 unsupported, exit 0.
- Git: HEAD `99bf646`, no git writes by any unit; the eleven consumer checkouts under `.ref` are
  clean (`14839-DM-cGAS` and `sene/` are plain directories whose counts are the umbrella's status).
- Leftovers: `pubtest` and publication `.staging` empty; the fix scratch removed; no `__pycache__`.

Committed as "Phase 7: identity and publication".
