"""Measure context scaling and compare legacy child payloads in an explicit scratch root."""

import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import resource
import shutil
import sys
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from gene_child import policy_bundle
from manifest import config_values, write_manifest
from transcript_context import write_context

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("mode", choices=("context", "baseline", "compare"))
parser.add_argument("--refroot", type=Path, required=True)
parser.add_argument("--gtf", type=Path)
parser.add_argument("--chrom")
parser.add_argument("--baseline-source", type=Path)
parser.add_argument("--baseline-config", type=Path)
args = parser.parse_args()
ref = args.refroot.resolve()
parent = ref / "te_mm39/build"
started = time.perf_counter()
if args.mode == "context":
    child = ref / ("context-" + (args.chrom or "mm39"))
    (child / "tables").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(parent / "tables/contig_aliases.tsv", child / "tables/contig_aliases.tsv")
    counts = write_context(parent, child, args.gtf, policy_bundle(config_values(ROOT / "config/mm39_gene.env")), args.chrom)
    print(json.dumps({"scope": args.chrom or "mm39", "pair_rows": counts[0], "record_rows": counts[1],
                      "wall_seconds": round(time.perf_counter() - started, 3),
                      "peak_rss_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024}), flush=True)
elif args.mode == "baseline":
    spec = importlib.util.spec_from_file_location("baseline_gene_child", args.baseline_source)
    baseline = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(baseline)
    child = ref / "baseline"
    (child / "tables").mkdir(parents=True, exist_ok=True)
    (child / "source").mkdir(exist_ok=True)
    shutil.copyfile(args.gtf, child / "source" / args.gtf.name)
    baseline.write_sources(child, parent, config_values(args.baseline_config))
    baseline.copy_parent_inputs(child, parent)
    baseline.build_child(parent, child, args.gtf)
    write_manifest(child, args.baseline_config, argv=["legacy payload qualification"], parent_dir=parent)
    print("baseline child payload complete", flush=True)
else:
    old, new = ref / "baseline", ref / "te_mm39_gene/build"
    count = 0
    identity_changes = {"BUILD_ID", "MANIFEST.json", "source/SOURCES.json"}
    changed = []
    for path in sorted(old.rglob("*")):
        if path.is_file():
            relative = path.relative_to(old)
            with path.open("rb") as stream:
                before = hashlib.file_digest(stream, "sha256").hexdigest()
            with (new / relative).open("rb") as stream:
                after = hashlib.file_digest(stream, "sha256").hexdigest()
            if str(relative) in identity_changes:
                assert before != after, relative
                changed.append(str(relative))
                continue
            if before != after:
                raise ValueError(f"legacy bytes differ: {relative}")
            count += 1
    assert count == 21, count
    print(f"legacy byte identity: {count} files, zero differences", flush=True)
    print("required identity metadata changes: " + ", ".join(changed), flush=True)
