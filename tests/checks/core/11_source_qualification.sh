#!/usr/bin/env bash
# Check the retained full-source qualification evidence.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)"
report="$TE_TRACKS_REFROOT/te_mm39/build/source/qualification.md"
if [ ! -f "$report" ]; then
  printf '%s\n' 'unsupported: run build.sh first'
  exit 3
fi

python3 - "$report" <<'PY'
import sys
from pathlib import Path

text = Path(sys.argv[1]).read_text()
values = {}
for line in text.splitlines():
    cells = [cell.strip() for cell in line.strip("|").split("|")]
    if len(cells) == 2 and cells[1].replace(",", "").isdigit():
        assert cells[0] not in values, f"duplicate report metric: {cells[0]}"
        values[cells[0]] = int(cells[1].replace(",", ""))
assert "Status: PASS." in text, "qualification status must be PASS"
for key in ("out_rows", "table_rows", "matched_rows"):
    assert values.get(key) == 5320771, (key, values.get(key))
for key in ("unmatched_out_rows", "unmatched_table_rows", "field_disagreements",
            "ids_spanning_contigs", "starred_rows",
            "swScore", "milliDiv", "milliDel", "milliIns", "genoLeft", "repClass",
            "repFamily", "repStart", "repEnd", "repLeft"):
    assert values.get(key) == 0, (key, values.get(key))
for key, expected in {
    "distinct_ids": 4696900,
    "id_min": 1,
    "id_max": 4696900,
    "ids_contiguous": 1,
    "coordinate_collision_pairs": 3,
}.items():
    assert values.get(key) == expected, (key, values.get(key), expected)
PY

cmp "$report" "$ROOT/docs/_internal/redesign-2026-09/audit/source_qualification_mm39.md"

source "$ROOT/config/mm39.env"
python3 - "$(dirname "$report")/SOURCES.json" \
  "$RMSK_OUT_MD5" "$RMSK_TABLE_MD5" "$CHROMALIAS_MD5" "$CHROM_SIZES_MD5" <<'PY'
import json
import sys
from pathlib import Path

sources = json.loads(Path(sys.argv[1]).read_text())["sources"]
for key, pin in zip(("rmsk_out", "rmsk_table", "chromAlias", "chrom_sizes"), sys.argv[2:]):
    observed = sources[key]["md5"]
    assert observed == pin, (key, observed, pin)
PY
printf '%s\n' '13 summary metrics and 10 field disagreements verified; reports identical; four source md5s match config pins'
