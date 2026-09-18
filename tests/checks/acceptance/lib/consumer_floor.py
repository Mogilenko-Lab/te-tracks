"""Reproduce the reviewed 50,000-row annotation-load measurements."""

import argparse
import itertools
import json
from pathlib import Path
import resource
import shutil
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[4]
SCRATCH = Path("/workspaces/Meta-Aging/_scratch/te-tracks-audit/p9b")
ANCHORS = {"Stellarscope": (134418432, 1.79), "TElocal": (51904512, 12.21)}


def measure(reader, gtf):
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
    print(json.dumps(dict(reader=reader, version=version, rows=count, peak_resident_bytes=peak,
        before_resident_bytes=before, annotation_resident_bytes=resident,
        seconds=round(seconds, 3), bytes_per_row=round(resident / count, 3),
        milliseconds_per_row=round(seconds * 1000 / count, 5),
        projected_bytes=round(resident / count * 3764949),
        projected_minutes=round(seconds / count * 3764949 / 60, 3),
        anchor_resident_bytes=anchor_bytes, anchor_seconds=anchor_seconds,
        resident_deviation_bytes=resident - anchor_bytes, seconds_deviation=round(seconds - anchor_seconds, 3)), sort_keys=True))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gtf", type=Path)
    parser.add_argument("--reader", choices=ANCHORS)
    args = parser.parse_args()
    if args.reader:
        measure(args.reader, args.gtf)
        return
    SCRATCH.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="consumer-floor-", dir=SCRATCH))
    try:
        head = temporary / "record.50000.gtf"
        with args.gtf.open() as incoming, head.open("w") as outgoing:
            count = 0
            for line in itertools.islice(incoming, 50000):
                outgoing.write(line)
                count += 1
        assert count == 50000
        for reader in ANCHORS:
            subprocess.run([sys.executable, str(Path(__file__).resolve()), str(head), "--reader", reader], check=True)
    finally:
        shutil.rmtree(temporary)


if __name__ == "__main__":
    main()
