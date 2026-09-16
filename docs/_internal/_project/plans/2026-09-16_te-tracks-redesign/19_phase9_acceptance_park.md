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

Final review: codex and Opus on the whole release plus a `divergent` pass on the handoff.
Then the umbrella pin bumps and D2 and D3 resume.
