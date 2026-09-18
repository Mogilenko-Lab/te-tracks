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
  "$RMSK_OUT_MD5" "$RMSK_TABLE_MD5" "$CHROMALIAS_MD5" "$CHROM_SIZES_MD5" \
  "$GENOME_FA_URL" "$GENOME_FA_MD5" <<'PY'
import json
import sys
from pathlib import Path

metadata = json.loads(Path(sys.argv[1]).read_text())
sources = metadata["sources"]
for key, pin in zip(("rmsk_out", "rmsk_table", "chromAlias", "chrom_sizes"), sys.argv[2:6]):
    observed = sources[key]["md5"]
    assert observed == pin, (key, observed, pin)
declared = metadata["declared_assembly"]
for key, pin in zip(("genome_fa_url", "genome_fa_md5"), sys.argv[6:8]):
    assert declared[key] == pin, (key, declared[key], pin)
assert declared["status"] == "declared", declared
PY

fetch_pins=$(python3 - "$ROOT" "$DFAM_SNAPSHOT_PATH" "$DFAM_SNAPSHOT_SHA256" "$DFAM_PROVENANCE_SHA256" \
  "$RMSK_OUT_URL" "$RMSK_TABLE_URL" "$CHROMALIAS_URL" "$CHROM_SIZES_URL" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
from urllib.parse import urlsplit

root, tracked, snapshot_pin, provenance_pin, *urls = sys.argv[1:]
root = Path(root)
with TemporaryDirectory(prefix="source-pins-") as directory:
    scratch = Path(directory)
    cache = scratch / "cache"
    cache.mkdir()
    snapshot = scratch / Path(tracked).name
    provenance = snapshot.with_suffix("").with_suffix(".provenance.json")
    shutil.copy2(root / tracked, snapshot)
    shutil.copy2((root / tracked).with_suffix("").with_suffix(".provenance.json"), provenance)
    overrides = [f"DFAM_SNAPSHOT_PATH={shlex.quote(str(snapshot))}"]
    for prefix, url in zip(("RMSK_OUT", "RMSK_TABLE", "CHROMALIAS", "CHROM_SIZES"), urls):
        data = (prefix + "\n").encode()
        (cache / Path(urlsplit(url).path).name).write_bytes(data)
        overrides.append(f"{prefix}_MD5={hashlib.md5(data).hexdigest()}")
    config = scratch / "pins.env"
    config.write_text((root / "config/mm39.env").read_text() + "\n" + "\n".join(overrides) + "\n")
    env = {**os.environ, "TE_TRACKS_SOURCE_CACHE": str(cache)}

    def fetch(case):
        build = scratch / case
        result = subprocess.run(["bash", str(root / "src/00_fetch_sources.sh"), str(build), str(config)],
                                env=env, capture_output=True, text=True)
        return build, result

    build, result = fetch("valid")
    assert result.returncode == 0, result.stdout + result.stderr
    sources = json.loads((build / "source/SOURCES.json").read_text())["sources"]
    assert sources["dfam_snapshot"] == {"path": str(snapshot), "sha256": snapshot_pin,
                                        "bytes": snapshot.stat().st_size}
    assert (build / "source" / provenance.name).read_bytes() == provenance.read_bytes()
    refusals = []
    for role, path, pin in (("dfam_snapshot", snapshot, snapshot_pin),
                            ("dfam_provenance", provenance, provenance_pin)):
        original = path.read_bytes()
        if role == "dfam_provenance":
            edited = json.loads(original)
            edited["fetch_finished"] = "1999-01-01T00:00:00.000000Z"
            path.write_text(json.dumps(edited) + "\n")
        else:
            path.write_bytes(original + b"\n")
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        message = f"{role} sha256 mismatch: {path}: {observed} != {pin}"
        build, result = fetch(role)
        assert result.returncode != 0 and message in result.stderr, result.stdout + result.stderr
        assert not (build / "source/SOURCES.json").exists(), "source metadata written after pin refusal"
        refusals.append(f"{role} sha256 mismatch")
        path.write_bytes(original)
    print("offline fetch pins pass; refused: " + "; ".join(refusals))
PY
)
printf '%s; %s\n' '13 summary metrics and 10 field disagreements verified; reports identical; four source md5s and declared assembly match config pins' "$fetch_pins"
