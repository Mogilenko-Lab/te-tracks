# Phase 5 rulings (orchestrator, 2026-09-16, implementer tree over `3837814`)

Inputs: `p5_codex.md` and `p5_opus.md` (appended when they land). Orchestrator verification before the
reviews: `consumers` 6 pass, 5 unsupported, exit 0; `core` 13 pass; pysam molecule and alignment counts equal
`expected.json` for all eleven fixture BAMs; the four boundary reads sit at 0-based `[99,100)`, `[100,101)`,
`[109,110)`, `[110,111)`; every BAM coordinate-sorted and indexed; the six checkouts under `.ref` untouched, no
bytecode written there; git untouched; public prose clean.

## Orchestrator finding

- **Stellarscope parser test reports unsupported on `setuptools_scm`.** The failing import is the top-level
  `stellarscope/__init__.py`; the `annotation` subpackage and `intervaltree` import cleanly here. Ruling: the
  check loads `stellarscope/annotation/__init__.py` as a package through `importlib.util.spec_from_file_location`
  with `submodule_search_locations`, registers it in `sys.modules`, and imports `utils` and `_intervaltree`
  beneath it; `unsupported` then names an absent `intervaltree` only. The plan calls the parser-level tests
  always supported, and this makes the boundary gate run here. The MATES adapter stays unsupported on `pyranges`
  (optional adapter, recorded).
  Measured by the orchestrator with that loading: 11 loci by `locus`, 10 by `instance_id`, the attribute regex
  accepts every GTF line, and the boundary gate observes `0,1,1,1` against expected `0,1,1,0`. The check therefore
  exits 3 with the documented right-boundary defect message for Stellarscope 1.5 once it runs, which is the plan's
  intended disposition (`15_phase5_consumer_fixtures.md`: keep the assertion, label the consumer version
  unsupported until fixed upstream).

## Codex (BLOCKING; B1 to B3, A1, A2)

- **B1 Stellarscope and MATES parser checks report unsupported.** Accept, and it extends the orchestrator's
  finding to MATES: codex executed MATES's `split_count_10X_data` with its source helpers and loaded
  `calculate_MU.py` directly, and the whole adapter check passed. Both checks load their source in isolation;
  `unsupported` is reserved for an absent third-party module the source itself needs. The contract and README
  rows state the exercised statuses.
- **B2 IRescue `chrcat` never exercised.** Accept: the check runs the checkout's real `chrcat` on synthetic
  intersection rows and asserts the emitted record and subfamily identities before reading them back.
- **B3 every `ImportError` becomes unsupported.** Accept: `run_check` classifies a `ModuleNotFoundError` whose
  missing name is a third-party module outside the checkout as unsupported, naming it; any other import failure
  (a missing symbol, a checkout-internal error) exits 1.
- **A1 fixture nondeterminism.** Accept: the fixture `.tsv.gz` writers use deterministic gzip headers (mtime 0,
  empty name, as `records_io.tsv_stream` does); the `.locInd` pickles embed the GTF path by TElocal's design, so
  the check compares them semantically and the contract says so.
- **A2 literal parser versions.** Accept: versions are read from each checkout (`setup.py`, `pyproject.toml` or
  the package's version attribute) when the parser loads, and the reported line carries what was read.

## Opus (FAIL; B1 to B5, A1 to A8)

- **B1** as codex B1 and the orchestrator's finding; reproduced with a scratch shim, boundary `0,1,1,1`.
- **B2 record-grain identity has no oracle in the IRescue check.** Accept: the check asserts the record-grain name
  set equals the roster's record keys and the coordinates equal the roster, so wrong identities fail.
- **B3** as codex B3, with four false-unsupported classes shown; fixed as ruled.
- **B4 `chrcat` needs `gawk`, absent here.** Accept: the IRescue parser check splits in two. `10_irescue_parser.py`
  always runs (`index_features`, `parse_maps`, record and subfamily identity, the comma hazard);
  `15_irescue_chrcat.py` runs the checkout's real `chrcat` and reports `unsupported: irescue system tool gawk absent`
  where `gawk` is missing. Plan 15 amended: a parser-level test whose checkout code path needs a system tool names
  that tool as its dependency.
- **B5 MATES blocks on `pkg_resources`, and `pyranges` is untouched by the adapter path.** Accept: the check loads
  only the two functions it exercises from source; where the exercised path imports `pkg_resources`, the check
  supplies a minimal in-test stand-in limited to the attribute used and says so in its docstring; the contract and
  README rows name `pkg_resources` (setuptools below 82) as the installed package's dependency and drop `pyranges`.
- **A1 nondeterminism sits in the checks.** Accept: the five IRescue `.tsv.gz` writes use deterministic gzip
  headers; the `.locInd` pickles are compared semantically and the contract says why.
- **A2 versions.** Accept: `setup.py` for TEsingle, TEtranscripts, TElocal, MATES; `irescue/_version.py`; Stellarscope
  from `git -C <checkout> describe --tags --always` (a read).
- **A3 `UB` equals `UR` on every read.** Accept: a designated subset of molecules carries a raw `UR` one base away
  from its corrected `UB`; `expected.json` states molecule counts by `UB` and by `UR`; the TEsingle cutoff path
  uses `UR`. Expected values are authored from the roster and the builder's intent.
- **A4 no reverse-strand, duplicate or QC-fail reads.** Accept: the builder adds reverse-strand reads on the two
  minus-strand records, one duplicate-flagged and one QC-fail-flagged read; checks that reach TEsingle's read filter
  assert they are skipped; the featureCounts execution check records its strand option for when it runs.
- **A5 MATES writes into the fixture root.** Accept: the MATES check works in its own scratch directory under
  `$TE_TRACKS_REFROOT/fixtures/consumers_scratch/` and removes it.
- **A6 tool inventory has no oracle.** Reporting-only by contract; OUTPUTS says so.
- **A7 contract contradiction.** Plan 15 acceptance amended: every parser test passes, or reports the documented
  upstream defect or a named system dependency; the runner exits 0 in both cases.
- **A8 scope.** The phase 6 to 9 planning and prompt changes are the orchestrator's alignment edits.

## Orchestrator verification of the fix (`te-tracks-p5-fix`)

- `tests/run.sh consumers`: 7 pass, 5 unsupported (Stellarscope right-boundary defect observed `0,1,1,1`; `gawk`;
  `irescue`; `featureCounts`; `duckdb`), exit 0. `tests/run.sh core`: 13 pass.
- Independent pysam recount (orchestrator code, importing nothing from `tests/`) over all eleven fixture BAMs
  reproduces every `alignments`, `templates`, `molecules_by_tag` and `flagged_reads` entry in `expected.json`;
  `UR` differs from `UB` on exactly `unique_a_copy0` and `duplicate_b_copy1`; both minus-strand roster records carry
  reverse reads; the four `Edge` reads cover `[99,100)`, `[100,101)`, `[109,110)`, `[110,111)`.
- Two fixture builds into fresh roots through `tests/run.sh consumers --refroot`: 51 of 53 files byte-identical; the
  two TElocal `.locInd` pickles are identical after swapping the embedded GTF path.
- Six checkouts under `.ref` clean at their clone commits; te-tracks reflog unchanged at `3837814`; nothing under
  `src/` touched. One stale `__pycache__` under the Stellarscope checkout, written by the first round's imports
  before `sys.dont_write_bytecode`, removed by the orchestrator.
- Notes for the next fix round, below the fix threshold on their own: `14_mates_parser.py` creates its scratch
  directory without `exist_ok`, so an interrupted run leaves a directory the next run trips on; check 12 writes the
  two flagged molecules as the literal `- 2` where `expected.json` names them.
