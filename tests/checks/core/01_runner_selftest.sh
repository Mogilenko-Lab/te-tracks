#!/usr/bin/env bash
# Exercise runner statuses and exits in an isolated check tree.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
scratch=$(mktemp -d -t te-tracks-runner-XXXXXXXX)
trap 'rm -rf -- "$scratch"' EXIT
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
printf '%s\n' 'runner statuses, required checks, diagnostics, dangling symlinks and usage exits pass'
