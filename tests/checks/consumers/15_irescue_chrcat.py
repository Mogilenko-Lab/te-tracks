#!/usr/bin/env python3
"""Verify feature identities emitted by the checkout's intersection concatenation."""

import gzip
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (FIXTURES, ROSTER, Unsupported, build_fixture, checkout_import,
                       checkout_version, export_path, gzip_text, record_key, run_check)


def check():
    if shutil.which("gawk") is None:
        raise Unsupported("irescue system tool gawk absent")
    mapping = checkout_import("irescue", "irescue.map")
    counting = checkout_import("irescue", "irescue.count")
    build_fixture()
    scratch = FIXTURES.parent / "consumers_scratch"
    scratch.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="irescue_chrcat_", dir=scratch) as directory:
        for level in ("record", "subfamily"):
            work = Path(directory) / level
            work.mkdir()
            intersection = work / "intersection.tsv.gz"
            names = [line.split("\t")[3] for line in export_path(f"{level}.bed").read_text().splitlines()]
            expected = {record_key(row) if level == "record" else row[4] for row in ROSTER}
            with gzip_text(intersection) as handle:
                handle.writelines(f"cell\tUMI{i:02d}\tread{i:02d}\t{name}\n" for i, name in enumerate(names))
            maps, barcodes, features = mapping.chrcat([str(intersection)], 1, str(work), str(work))
            with gzip.open(features, "rt") as handle:
                emitted = [line.rstrip().split("\t") for line in handle]
            assert {row[0] for row in emitted} == expected and len(emitted) == len(expected), emitted
            assert all(row == [row[0], row[0], "Gene Expression"] for row in emitted), emitted
            with gzip.open(barcodes, "rt") as handle:
                assert handle.read().splitlines() == ["cell"]
            with gzip.open(maps, "rt") as handle:
                mapped = [line.rstrip().split("\t") for line in handle]
            assert sorted(mapped) == sorted(
                ["cell", f"UMI{i:02d}", name, "1"] for i, name in enumerate(names)), mapped
            index = counting.index_features(features)
            cells = list(counting.parse_maps(maps, index))
            assert len(cells) == 1 and len(cells[0][1]) == len(ROSTER), cells
            assert {next(iter(eq.features)) for eq in cells[0][1]} == set(index.values())
    return "chrcat emitted record=11, subfamily=8 identities; mappings and feature index agree"


run_check("irescue", lambda: f"{checkout_version('irescue')} checkout chrcat", check)
