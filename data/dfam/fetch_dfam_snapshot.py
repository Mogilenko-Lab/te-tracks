"""Fetch offline Dfam metadata from canonical names selected by a published universe.

Run with --taxonomy BUILD/tables/taxonomy_canonical.tsv --universe interspersed
--census CENSUS.tsv --output-dir data/dfam. Review the resulting provenance and pin
the snapshot and provenance for builds.
"""

import argparse
import csv
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import sys
import time
import urllib.parse
import urllib.request

API = "https://dfam.org/api"
DROP = {"consensus_sequence", "model_mask", "hmm_general_threshold", "search_stages", "buffer_stages"}


def get(path, params=None, tries=4):
    url = API + path + ("?" + urllib.parse.urlencode(params) if params else "")
    for attempt in range(tries):
        try:
            with urllib.request.urlopen(url, timeout=90) as response:
                return json.load(response)
        except (OSError, ValueError):
            if attempt == tries - 1:
                raise
            time.sleep(2 * (attempt + 1))


def selected_names(taxonomy, universe):
    import pyarrow.parquet as pq

    sys.dont_write_bytecode = True
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src/lib"))
    from build_universes import evaluate_predicate

    definitions = json.loads((taxonomy.parent.parent / "universes.json").read_text())
    predicate = next(row["predicate"] for row in definitions["universes"] if row["name"] == universe)
    names = set()
    for batch in pq.ParquetFile(taxonomy.with_name("rmsk_records.parquet")).iter_batches(
            columns=["rmsk_name", "rmsk_class", "rmsk_family"], batch_size=200_000):
        frame = batch.to_pandas()
        names.update(frame.loc[evaluate_predicate(frame, predicate), "rmsk_name"])
    with taxonomy.open() as stream:
        canonical = [row["rmsk_name"] for row in csv.DictReader(stream, delimiter="\t")]
    if len(canonical) != len(set(canonical)) or not names <= set(canonical):
        raise ValueError("canonical names and universe membership differ")
    return sorted(names)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--taxonomy", type=Path, required=True)
    parser.add_argument("--census", type=Path, required=True, help="query census TSV with an rmsk_name column")
    parser.add_argument("--universe", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    genome = json.loads((args.taxonomy.parent.parent / "source/SOURCES.json").read_text())["genome"]
    names = selected_names(args.taxonomy, args.universe)
    with args.census.open() as stream:
        census_names = [row["rmsk_name"] for row in csv.DictReader(stream, delimiter="\t")]
    if sorted(census_names) != names:
        raise ValueError("census names and universe membership differ")
    started = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    version, classes = get("/version"), get("/classes")
    summaries, records, errors = {}, {}, []
    for index, name in enumerate(names, 1):
        try:
            data = get("/families", {"name": name, "format": "summary"})
        except (OSError, ValueError) as error:
            errors.append({"name": name, "stage": "summary", "error": str(error)})
            continue
        results = data.get("results", [])
        summaries[name] = results
        wanted = ([row for row in results if row["name"] == name] or
                  [row for row in results if row["name"].startswith(name + "_")])
        for row in wanted:
            accession = row["accession"]
            if accession in records:
                continue
            try:
                full = get("/families/" + accession)
            except (OSError, ValueError) as error:
                errors.append({"name": name, "accession": accession, "stage": "record", "error": str(error)})
                continue
            records[accession] = {key: value for key, value in full.items() if key not in DROP}
        if index % 100 == 0:
            print(f"{index} names, {len(records)} records, {len(errors)} errors", flush=True)
    finished = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    snapshot = {"version": version, "classes": classes, "summaries": summaries, "records": records}
    payload = json.dumps(snapshot, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    target = args.output_dir / f"dfam_{args.universe}_{genome}_snapshot.json.gz"
    with gzip.GzipFile(target, "wb", mtime=0) as stream:
        stream.write(payload)
    provenance = {
        "endpoint": API, "dfam_version": version, "fetch_started": started, "fetch_finished": finished,
        "names_queried": len(names), "names_with_results": sum(bool(rows) for rows in summaries.values()),
        "records_fetched": len(records), "errors": errors, "dropped_record_fields": sorted(DROP),
        "payload_sha256": hashlib.sha256(payload).hexdigest(), "payload_bytes": len(payload),
        "file_sha256": hashlib.sha256(target.read_bytes()).hexdigest(), "file_bytes": target.stat().st_size,
        "taxonomy_sha256": hashlib.sha256(args.taxonomy.read_bytes()).hexdigest(), "universe": args.universe,
        "census_sha256": hashlib.sha256(args.census.read_bytes()).hexdigest(),
    }
    target.with_suffix("").with_suffix(".provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n")
    print(json.dumps(provenance, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
