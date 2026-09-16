#!/usr/bin/env python3
"""Verify custom BED feature identity and the comma-delimited mapping hazard."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (EXPECTED, FIXTURES, ROSTER, build_fixture, checkout_import,
                       checkout_version, export_path, gzip_text, record_key, run_check)


def check():
    mapping = checkout_import("irescue", "irescue.map")
    counting = checkout_import("irescue", "irescue.count")
    build_fixture()
    for level, number in (("record", EXPECTED["records"]), ("subfamily", EXPECTED["names"])):
        bed = export_path(f"{level}.bed")
        loaded = mapping.makeRmsk(str(bed), None, {}, str(FIXTURES), locus="instance")
        assert loaded == str(bed)
        rows = [row.split("\t") for row in Path(loaded).read_text().splitlines()]
        names = {row[3] for row in rows}
        assert len(names) == number, names
        assert names == {record_key(row) if level == "record" else row[4] for row in ROSTER}, names
        observed = [(r[0], int(r[1]), int(r[2]), r[3], r[5]) for r in rows]
        expected = [(r[0], r[1] - 1, r[2], record_key(r) if level == "record" else r[4], r[3])
                    for r in ROSTER]
        assert sorted(observed) == sorted(expected), (level, observed, expected)
        feature_file = FIXTURES / f"irescue_{level}_features.tsv.gz"
        with gzip_text(feature_file) as handle:
            handle.writelines(f"{name}\t{name}\tGene Expression\n" for name in sorted(names))
        feature_index = counting.index_features(str(feature_file))
        assert len(feature_index) == number
        maps = FIXTURES / f"irescue_{level}_maps.tsv.gz"
        with gzip_text(maps) as handle:
            handle.writelines(f"cell\tACGTACGT\t{name}\t1\n" for name in sorted(names))
        cells = list(counting.parse_maps(str(maps), feature_index))
        assert len(cells) == 1 and len(cells[0][1]) == number
        assert {next(iter(eq.features)) for eq in cells[0][1]} == set(feature_index.values())

    maps = FIXTURES / "irescue_comma_maps.tsv.gz"
    with gzip_text(maps) as handle:
        handle.write("cell\tACGTACGT\tleft,right\t1\n")
    cells = list(counting.parse_maps(str(maps), {b"left": 1, b"right": 2, b"left,right": 3}))
    assert cells[0][1][0].features == {1, 2}, cells
    from build_exports import COMPONENT, IDENTIFIER, validate
    for pattern in (COMPONENT, IDENTIFIER):
        try:
            validate("left,right", pattern, export_path("record.bed"))
        except ValueError as error:
            assert "left,right" in str(error) and "record.bed" in str(error)
        else:
            raise AssertionError("exporter accepted comma-containing feature")
    return "record=11, subfamily=8; comma splits one name and exporter rejects it"


run_check("irescue", lambda: f"{checkout_version('irescue')} checkout parser", check)
