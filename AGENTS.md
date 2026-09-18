# te-tracks

This package owns a reference projection of RepeatMasker for one assembly: canonical tables,
universes, exports and fixtures. Quantification, biological interpretation and knowledge of
downstream assays belong to consuming projects and sit outside this package's scope.

## Execution

`/data2/users/shared/refcache` is read-only inside the container. Production builds, publication,
directory/ACL policy, backup and CRI transfer run on the host in the qualified devcontainer image
with writable destination mounts. [RUNBOOK.md](docs/RUNBOOK.md) defines those steps.
Tests and acceptance builds run in-container against a scratch reference root.

```bash
tests/run.sh core
tests/run.sh consumers
tests/run.sh acceptance
tests/run.sh acceptance --build
tests/run.sh core --refroot /workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
```

The four test modes are `core` (contracts and fixtures), `consumers` (parser and executable
qualification), `acceptance` (both complete acceptance archives), and `acceptance --build`
(fresh core and child publication followed by acceptance). Activate the consuming environment
with `source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh` before consumer qualification.
Offline consumer qualification sets `TENX_DISABLE_TELEMETRY=1`.

The default `TE_TRACKS_REFROOT` is `/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`;
`--refroot DIR` selects another scratch root for any mode and is exported as an absolute path.
`--build` applies to acceptance and passes `TE_TRACKS_ACCEPTANCE_BUILD=1` to its first check.
That check verifies cached source pins, requires an empty `$TE_TRACKS_REFROOT/acceptance/`,
and builds `te_mm39` followed by `te_mm39_gene` there. Existing development archives remain
retained. Missing acceptance builds report `unsupported: run tests/run.sh acceptance --build`.
All eleven acceptance checks are required, so acceptance exits 1 when no archive is available.
A selected archive missing `BUILD_ID`, `CATALOG_ID` or `MANIFEST.json` fails.
Checks are `tests/checks/<mode>/*.sh` and `*.py`, run in name order through `bash` or `python3`
regardless of file mode. A check exit of 0 is pass, 3 is unsupported and any other exit is fail.
A failing check makes the runner exit 1, as does an unsupported check whose name ends in
`.required.sh` or `.required.py`. Bad usage, a missing check directory and a mode with no checks exit 2.

Export `PYTHONDONTWRITEBYTECODE=1` in every shell. Acceptance and the consumer floor probe use
`${TMPDIR:-$TE_TRACKS_REFROOT/tmp}/te-tracks-<root-hash>/acceptance`, where `root-hash` is the
first twelve SHA-256 digits of the absolute reference-root path. The runner prints this path;
`tempfile.mkdtemp` isolates each task and Python `shutil.rmtree` removes its directory.
Core publication fixtures also honor `TMPDIR`.
Source refresh is an explicit re-pin decision. Acceptance expectations retain reviewed oracle
values and prior-output reproduction pins; report deviations for investigation. Sequence mutation reviews and suite runs,
and capture complete output with exit status. Give concurrent consumer runs separate
`TE_TRACKS_CONSUMER_FIXTURES` directories.

## Review

Follow the [review protocol](docs/_internal/_project/plans/2026-09-16_te-tracks-redesign/02_orchestration.md).
Git writes require the owner's explicit authorization. Commit messages describe the change;
AI attribution and co-authorship trailers are excluded.

## Writing

Public prose is affirmative and brief: state what a thing is. Omit contrastive negation.
Comments state intent only, briefly and affirmatively, in one line.
