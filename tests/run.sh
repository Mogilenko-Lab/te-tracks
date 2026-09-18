#!/usr/bin/env bash
source "$(dirname "${BASH_SOURCE[0]}")/../lib/common.sh"

usage() {
  printf '%s\n' \
    'usage: tests/run.sh <core|consumers|acceptance> [--refroot DIR]' \
    'checks: tests/checks/<mode>/*.sh and tests/checks/<mode>/*.py, sorted by name' \
    'consumer environment: source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh' \
    'consumer suite: tests/run.sh consumers' \
    'execution: bash for .sh; python3 for .py; all file modes included' >&2
}

mode="${1:-}"
case "$mode" in
  core|consumers|acceptance) shift ;;
  *) usage; exit 2 ;;
esac

refroot=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
case "$#" in
  0) ;;
  2)
    if [ "$1" != --refroot ] || [ -z "$2" ]; then
      usage
      exit 2
    fi
    refroot="$2"
    ;;
  *) usage; exit 2 ;;
esac
refroot=$(realpath -m -- "$refroot")
export TE_TRACKS_REFROOT="$refroot"

cd "$REPO_ROOT"
check_dir="$REPO_ROOT/tests/checks/$mode"
if [ ! -d "$check_dir" ]; then
  printf 'runner error: missing check directory: %s\n' "$check_dir" >&2
  exit 2
fi
checks=()
for check in "$check_dir"/*; do
  if [[ ( -f "$check" || ( -L "$check" && ! -e "$check" ) ) && ( "$check" == *.sh || "$check" == *.py ) ]]; then
    checks+=("$check")
  fi
done

pass=0
fail=0
unsupported=0
runner_exit=0
for check in "${checks[@]}"; do
  if [[ -L "$check" && ! -e "$check" ]]; then
    printf 'fail  %s  dangling symlink\n' "${check#"$check_dir/"}"
    fail=$((fail + 1))
    runner_exit=1
    continue
  fi
  case "$check" in
    *.sh) check_command=(bash "$check") ;;
    *.py) check_command=(python3 "$check") ;;
  esac
  # Preserve check diagnostics, including trailing blank lines.
  if check_stdout=$(
    "${check_command[@]}"
    check_exit=$?
    printf '.'
    exit "$check_exit"
  ); then
    check_exit=0
  else
    check_exit=$?
  fi
  check_stdout="${check_stdout%.}"
  case "$check_exit" in
    0)
      status=pass
      pass=$((pass + 1))
      ;;
    3)
      status=unsupported
      unsupported=$((unsupported + 1))
      case "$check" in
        *.required.sh|*.required.py) runner_exit=1 ;;
      esac
      ;;
    *)
      status=fail
      fail=$((fail + 1))
      runner_exit=1
      ;;
  esac
  first_line="${check_stdout%%$'\n'*}"
  printf '%s  %s' "$status" "${check#"$check_dir/"}"
  if [ "$status" != fail ] && [ -n "$first_line" ]; then
    printf '  %s' "$first_line"
  fi
  printf '\n'
  if [ "$status" = fail ]; then
    while IFS= read -r line || [ -n "$line" ]; do
      printf '  %s\n' "$line" >&2
    done < <(printf '%s' "$check_stdout")
  fi
done

printf 'checks=%s pass=%s fail=%s unsupported=%s\n' "${#checks[@]}" "$pass" "$fail" "$unsupported"
if [ "${#checks[@]}" -eq 0 ]; then
  printf 'no checks registered for mode %s\n' "$mode"
  exit 2
fi
exit "$runner_exit"
