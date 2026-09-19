"""Measure annotation-load memory and time on 50,000 rows."""

import argparse
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
from common import SCRATCH
ANCHORS = {"Stellarscope": (134418432, 1.79), "TElocal": (51904512, 12.21)}


def measure(reader, gtf, total_rows):
    sys.path.insert(0, str(ROOT / "tests/lib"))
    from consumers import checkout_import, checkout_version
    if reader == "Stellarscope":
        module = checkout_import("stellarscope", "_intervaltree", subpackage="stellarscope.annotation")
        version = checkout_version("stellarscope")
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        started = time.perf_counter()
        annotation = module.IntervalTreeAnnotation(str(gtf), "locus", "exon")
        seconds = time.perf_counter() - started
        count = len(annotation.loci)
    else:
        module = checkout_import("TElocal", "TElocal_Toolkit.TEindex")
        version = checkout_version("TElocal")
        annotation = module.TEfeatures()
        before = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
        started = time.perf_counter()
        annotation.build(str(gtf))
        seconds = time.perf_counter() - started
        count = len(annotation.getElements())
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024
    resident = peak - before
    assert count == 50000, (reader, count)
    anchor_bytes, anchor_seconds = ANCHORS[reader]
    print(json.dumps(dict(reader=reader, version=version, rows=count, total_rows=total_rows, peak_resident_bytes=peak,
        before_resident_bytes=before, annotation_resident_bytes=resident,
        seconds=round(seconds, 3), bytes_per_row=round(resident / count, 3),
        milliseconds_per_row=round(seconds * 1000 / count, 5),
        projected_bytes=round(resident / count * total_rows),
        projected_minutes=round(seconds / count * total_rows / 60, 3),
        anchor_resident_bytes=anchor_bytes, anchor_seconds=anchor_seconds,
        resident_deviation_bytes=resident - anchor_bytes, seconds_deviation=round(seconds - anchor_seconds, 3)), sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gtf", type=Path)
    parser.add_argument("--reader", choices=ANCHORS)
    parser.add_argument("--total-rows", type=int, help="source row count for an isolated head reader")
    args = parser.parse_args()
    if args.reader:
        total_rows = args.total_rows
        if total_rows is None:
            with args.gtf.open() as stream:
                total_rows = sum(bool(line.strip()) and not line.startswith("#") for line in stream)
        assert total_rows >= 50000, "the annotation-load probe requires at least 50000 data rows"
        measure(args.reader, args.gtf, total_rows)
        return
    if args.total_rows is not None:
        parser.error("--total-rows accompanies --reader")
    SCRATCH.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="consumer-floor-", dir=SCRATCH))
    try:
        head = temporary / "record.50000.gtf"
        with args.gtf.open() as incoming, head.open("w") as outgoing:
            total_rows = 0
            for line in incoming:
                if not line.strip() or line.startswith("#"):
                    continue
                if total_rows < 50000:
                    outgoing.write(line)
                total_rows += 1
        assert total_rows >= 50000, "the annotation-load probe requires at least 50000 data rows"
        print(f"annotation source: {args.gtf}; total_rows={total_rows}; head_rows=50000; scratch={temporary}", flush=True)
        for reader in ANCHORS:
            subprocess.run([sys.executable, str(Path(__file__).resolve()), str(head), "--reader", reader,
                            "--total-rows", str(total_rows)], check=True)
    finally:
        shutil.rmtree(temporary)


if __name__ == "__main__":
    main()
