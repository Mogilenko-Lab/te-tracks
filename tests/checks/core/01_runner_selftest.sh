#!/usr/bin/env bash
# Exercise runner statuses and exits in an isolated check tree.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
scratch=$(mktemp -d -t te-tracks-runner-XXXXXXXX)
trap 'python3 -c "import shutil, sys; shutil.rmtree(sys.argv[1])" "$scratch"' EXIT
mkdir -p "$scratch/tests/checks/core" "$scratch/lib"
cp "$ROOT/tests/run.sh" "$scratch/tests/run.sh"
cp "$ROOT/lib/common.sh" "$scratch/lib/common.sh"
checks="$scratch/tests/checks/core"
printf 'exit 0\n' > "$checks/10_pass.sh"
printf 'exit 3\n' > "$checks/20_unsupported.sh"
printf 'exit 3\n' > "$checks/30_required.required.sh"
printf "printf 'probe failure\\n'\nexit 7\n" > "$checks/40_fail.sh"
ln -s missing-target "$checks/50_dangling.sh"

expect_exit() {
  local expected="$1" observed
  shift
  if bash "$scratch/tests/run.sh" "$@" > "$scratch/stdout" 2> "$scratch/stderr"; then
    observed=0
  else
    observed=$?
  fi
  if [ "$observed" -ne "$expected" ]; then
    printf 'runner self-test: expected exit %s, observed %s for %s\n' "$expected" "$observed" "$*" >&2
    cat "$scratch/stdout" "$scratch/stderr" >&2
    exit 1
  fi
}

expect_line() {
  local line
  while IFS= read -r line; do
    if [ "$line" = "$1" ]; then
      return 0
    fi
  done < "$scratch/${2:-stdout}"
  printf 'runner self-test: missing line: %s\n' "$1" >&2
  cat "$scratch/stdout" "$scratch/stderr" >&2
  exit 1
}

expect_exit 1 core --refroot "$scratch"
expect_line 'pass  10_pass.sh'
expect_line 'unsupported  20_unsupported.sh'
expect_line 'unsupported  30_required.required.sh'
expect_line 'fail  40_fail.sh'
expect_line 'fail  50_dangling.sh  dangling symlink'
expect_line 'checks=5 pass=1 fail=2 unsupported=2'
expect_line '  probe failure' stderr

rm "$checks/40_fail.sh" "$checks/50_dangling.sh"
expect_exit 1 core --refroot "$scratch"
expect_line 'unsupported  30_required.required.sh'
expect_line 'checks=3 pass=1 fail=0 unsupported=2'

rm "$checks/30_required.required.sh"
expect_exit 0 core --refroot "$scratch"
expect_line 'pass  10_pass.sh'
expect_line 'unsupported  20_unsupported.sh'
expect_line 'checks=2 pass=1 fail=0 unsupported=1'

expect_exit 2 acceptance --refroot "$scratch"
expect_line "runner error: missing check directory: $scratch/tests/checks/acceptance" stderr
mkdir "$scratch/tests/checks/acceptance"
expect_exit 2 acceptance --refroot "$scratch"
expect_line 'checks=0 pass=0 fail=0 unsupported=0'
expect_line 'no checks registered for mode acceptance'
expect_exit 2
expect_line 'usage: tests/run.sh <core|consumers|acceptance> [--refroot DIR]' stderr
python3 - "$scratch" <<'PY'
import json
import os
from pathlib import Path
import subprocess
import sys

root = Path(sys.argv[1])
checks = root / "tests/checks/consumers"
checks.mkdir()
(checks / "probe_module.py").write_text("value = 1\n")
(checks / "10_probe.py").write_text('''import json, os, time
from pathlib import Path
import probe_module
assert os.environ["PYTHONDONTWRITEBYTECODE"] == "1"
fixture = Path(os.environ["TE_TRACKS_CONSUMER_FIXTURES"])
fixture.mkdir(parents=True, exist_ok=True)
(fixture / "owner").write_text(os.environ["PROBE_NAME"])
probe = Path(os.environ["PROBE_ROOT"])
(probe / os.environ["PROBE_NAME"]).write_text(json.dumps(str(fixture)))
deadline = time.monotonic() + 30
while len(list(probe.iterdir())) < int(os.environ["PROBE_COUNT"]):
    assert time.monotonic() < deadline, "concurrent runner did not start"
    time.sleep(0.05)
assert (fixture / "owner").read_text() == os.environ["PROBE_NAME"]
''')
(checks / "20_reuse.py").write_text('''import os
from pathlib import Path
assert (Path(os.environ["TE_TRACKS_CONSUMER_FIXTURES"]) / "owner").read_text() == os.environ["PROBE_NAME"]
''')
probe = root / "probe"
probe.mkdir()
env = {key: value for key, value in os.environ.items()
       if key not in {"TE_TRACKS_CONSUMER_FIXTURES", "PYTHONDONTWRITEBYTECODE"}}
env.update(TMPDIR=str(root), PROBE_ROOT=str(probe), PROBE_COUNT="2")
command = ["bash", str(root / "tests/run.sh"), "consumers", "--refroot", str(root)]
runs = [subprocess.Popen(command, env={**env, "PROBE_NAME": name},
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        for name in ("first", "second")]
for run in runs:
    stdout, stderr = run.communicate(timeout=60)
    assert run.returncode == 0, stdout + stderr
paths = [Path(json.loads((probe / name).read_text())) for name in ("first", "second")]
assert paths[0] != paths[1] and paths[0].parent != paths[1].parent
assert all(not path.parent.parent.exists() for path in paths), paths
override = root / "retained/consumers"
result = subprocess.run(command, env={**env, "PROBE_NAME": "override", "PROBE_COUNT": "1",
    "TE_TRACKS_CONSUMER_FIXTURES": str(override)}, capture_output=True, text=True, timeout=60)
assert result.returncode == 0, result.stdout + result.stderr
assert (override / "owner").read_text() == "override"
assert not list(root.rglob("__pycache__"))
PY
printf '%s\n' 'runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass'
printf '%s\n' 'concurrent consumer runs isolate and reuse fixtures, clean private directories, retain overrides and suppress bytecode'
