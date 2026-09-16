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
  (`99_verify.py` against `/data2/users/shared/refcache/te_mm39/current`) and records the
  `BUILD_ID`s in `docs/_internal/_project/session.md`.
- README truth table updated to delivered and tested; `AGENTS.md` final; `docs/OUTPUTS.md`,
  `docs/PROVENANCE.md`, `docs/RELEASES.md` accurate to the bytes.
- Parking handoff in `docs/_internal/_project/session.md`: what is published, what is tested, what
  is unsupported (tool executables), what is deferred (hg38, transcript context, ERV units, age
  tiers), and the next gates.

Milestone 2 rulings landing here: the `compat_tetranscripts_mm39` membership count equals the row count
of the published legacy `te_subfamily.saf` (H1); published table digests, `CATALOG_ID` and `BUILD_ID`
equal the in-container `_scratch` build (H6); the runbook seeds the host `TE_TRACKS_SOURCE_CACHE` from
the container's retained source copy, and a checksum mismatch stops for a re-pin decision (L4).

Milestone 5 rulings landing here: the runbook states a measured floor per consumer, projected from a 50,000-row
head of `record.gtf` through Stellarscope's `IntervalTreeAnnotation` and TElocal's `TEindex`, beside the producer's
5.7 GB (H3); the runbook pins consumer installs to the vendored checkout commits or records the divergence (M4); the
handoff names the barcode-threshold audit as the consumer's (M6); the acceptance record names the oracles the builder
did not produce: the UCSC `rmsk` table (phase 1 qualification), the pinned Dfam snapshot (check 31) and the host
legacy release for the compat count (L4, with H1 corrected: the in-container legacy directories were audit
experiments, moved to `_scratch/te-tracks-audit/legacy_release_experiments/`).

Final review: codex and Opus on the whole release plus a `divergent` pass on the handoff.
Then the umbrella pin bumps and D2 and D3 resume.
