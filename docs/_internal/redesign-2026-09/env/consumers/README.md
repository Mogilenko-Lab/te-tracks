# Consumer tools for the execution checks (prepared 2026-09-17)

The owner authorized a tool environment for the `tests/run.sh consumers` execution gates: a Python venv
without conda, reproducible from pinned sources, with the base venv used only where nothing conflicts.

- Root: `/workspaces/Meta-Aging/.venv/te-consumers` (the umbrella ignores `.venv/`). `venv/` holds the five
  Python tools at the exact commits of the `01_modules/.ref/` checkouts the parser fixtures were written
  against; `opt/` holds STAR 2.7.11b, subread 2.1.1 and cellranger 10.1.0 (extracted from the owner's tarball
  at `01_modules/cellranger-10.1.0.tar.gz`); `shims/` holds one symlink per tool executable.
- Only `shims/` goes on `PATH` (`source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh`), so `python3`
  stays the base interpreter the checks import pandas and pyarrow from. `duckdb` is a dependency-free wheel
  installed into the base venv with sudo, because check 30 imports it under the base interpreter. `gawk` is a
  system package installed with apt; both need a line in the devcontainer image to survive a rebuild.
- `bootstrap.sh` recreates everything and is idempotent; `requirements.txt` pins the git sources;
  `pip-freeze.txt`, `python-version.txt` and `MANIFEST.tsv` (versions, sources, sha256 of every downloaded
  archive) record what the run produced. `/tmp` is mounted noexec here, so the script sets `TMPDIR` under the
  root for pip's builds.
- First run of the suite with the shims on PATH (`consumers_run_20260917.log`): 13 checks, 11 pass, 1
  unsupported (the Stellarscope boundary defect), 1 fail: `20_irescue_exec.sh` observes 5.5 and 3.5 where the
  fixture expects 6 and 3, confirming the loci consult's reading of IRescue's EM. The owner ruled the
  allocation outside te-tracks' responsibility; phase 9 rewrites that check to assert identity joins and
  molecule conservation and to record the allocation.
- Canonical home of this recipe: `/workspaces/Meta-Aging/01_modules/te-consumers/env/` (owner ruling, fourth round).
- Phase 9 promotes this into the package (a tracked bootstrap and lock beside `tests/`, and the runner's
  documentation) through a codex unit; until then these files are the orchestrator's record.
