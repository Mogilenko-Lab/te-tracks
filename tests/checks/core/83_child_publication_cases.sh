#!/usr/bin/env bash
# Exercise immutable child publication with its required sibling parent archive.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
if [ ! -d "$TE_TRACKS_REFROOT/te_mm39_gene/build" ]; then
  echo 'gene child build is absent'
  exit 3
fi
python3 "$ROOT/tests/fixtures/gene/publication_cases.py"
