# Phase 9: acceptance and parking

Deliverables
- `tests/run.sh acceptance` against a full in-container build into `_scratch`: every number in
  phases 1 to 8 re-measured and compared to `tests/expectations/mm39/<universe>/`; fixture tables
  independently authored, never copied from the build under test.
- Host runbook `docs/RUNBOOK.md`: prerequisites and versions, writable host root versus the
  read-only container mount, source cache, `build.sh` invocation for `te_mm39` then
  `te_mm39_gene`, verification, publication, transfer to the CRI root, interruption recovery,
  resolving `current` once per consumer operation.
- Owner runs the host build; the orchestrator verifies the published bytes in-container
  (`release.py verify-current --root /data2/users/shared/refcache --family te_mm39`, which resolves `current`
  once and verifies that archive; `99_verify.py` takes the resolved `archive/<BUILD_ID>` path and refuses the
  selector symlink itself, milestone 7 codex A3) and records the
  `BUILD_ID`s in `docs/_internal/_project/session.md`.
- README truth table updated to delivered and tested; `AGENTS.md` final; `docs/OUTPUTS.md`,
  `docs/PROVENANCE.md`, `docs/RELEASES.md` accurate to the bytes.
- Parking handoff in `docs/_internal/_project/session.md`: what is published, what is tested, what
  is unsupported (tool executables), what is deferred (hg38, transcript context, ERV units, age
  tiers), and the next gates.

Milestone 2 rulings landing here: the `compat_tetranscripts_mm39` membership count equals the 3,799,629 data
lines of the packaged `GRCm39_Ensembl_rmsk_TE.gtf.gz` (md5 `1d6770be131fc1b47402a633f4401cbd`) in the refcache, the
oracle `docs/PROVENANCE.md` joins 1:1 on coordinates (H1; milestone 7 divergent H4 found no legacy SAF on disk); published table digests, `CATALOG_ID` and `BUILD_ID`
equal the in-container `_scratch` build (H6); the runbook seeds the host `TE_TRACKS_SOURCE_CACHE` from
the container's retained source copy, and a checksum mismatch stops for a re-pin decision (L4).

Milestone 5 rulings landing here: the runbook states a measured floor per consumer, projected from a 50,000-row
head of `record.gtf` through Stellarscope's `IntervalTreeAnnotation` and TElocal's `TEindex`, beside the producer's
floor near 6.0 GB resident, measured 5.5 to 6.0 GB across builds (H3); the runbook pins consumer installs to the vendored checkout commits or records the divergence (M4); the
handoff names the barcode-threshold audit as the consumer's (M6); the acceptance record names the oracles the builder
did not produce: the UCSC `rmsk` table (phase 1 qualification), the pinned Dfam snapshot (check 31) and the host
legacy release for the compat count (L4, with H1 corrected: the in-container legacy directories were audit
experiments, moved to `_scratch/te-tracks-audit/legacy_release_experiments/`).

Final review: codex and Opus on the whole release plus a `divergent` pass on the handoff.
Then the umbrella pin bumps and D2 and D3 resume.

Milestone 7 rulings landing here (`reviews/m7_rulings.md`): the runbook verifies the published root with
`release.py verify-current` (codex A3); after host publication the family root and `archive/` are tightened to
owner-only write or the group write is stated as the publisher policy, with the host backup named (divergent M1);
host publication requires `builder_git_dirty` false and a fresh complete `--root` build (M2); when the host build's
ids differ from the in-container build's, a `CATALOG_ID` difference stops for investigation and a `BUILD_ID`
difference with equal `CATALOG_ID` publishes the host build with the in-container build recorded as its content
witness (M5); the handoff names the 14761 ledger's adoption of `te_catalog_id` and `te_build_id` as a consumer gate
(M4); `tests/checks/acceptance/` gains its checks, and the runner exits 2 for a mode without checks (L3).
