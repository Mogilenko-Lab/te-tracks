#!/usr/bin/env python3
"""Join bedtools family buckets and SAF taxonomy triples to their exact record support."""

from collections import Counter
import csv
from pathlib import Path
import shutil
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (EXPECTED, ROSTER, Unsupported, assert_registered, build_fixture,
                       command, discover, export_path, record_key, run_check)


def check():
    build_fixture()
    if shutil.which("bedtools") is None:
        raise Unsupported("family reader system tool bedtools absent")
    output = command(["bedtools", "intersect", "-wa", "-wb",
                      "-a", export_path("record.bed"), "-b", export_path("family.bed")])
    rows = [line.split("\t") for line in output.splitlines()]
    assert all(len(row) == 12 for row in rows), rows
    assert {row[3] for row in rows} == {record_key(row) for row in ROSTER}
    for record in ROSTER:
        family, cls = EXPECTED["taxonomy"][record[4]]
        buckets = [row[9] for row in rows if row[3] == record_key(record)]
        assert buckets == [f"{cls}/{family}"] * (2 if record[4] in {"DupX", "DupY"} else 1), buckets
        if record[4] == "TwoLab":
            assert buckets == ["DNA/hAT-Tip100"], buckets
        elif record[4] in {"DupX", "DupY"}:
            assert buckets == ["LINE/L1", "LINE/L1"], buckets
    assert_registered({row[9] for row in rows}, "family", "family_bucket")

    with export_path("taxonomy_triple.saf").open() as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        assert reader.fieldnames == ["GeneID", "Chr", "Start", "End", "Strand"]
        triples = list(reader)
    expected_rows = [(name + ":" + ":".join(EXPECTED["taxonomy"][name]), chrom, start, end, strand)
                     for chrom, start, end, strand, name, *_ in ROSTER]
    assert [(row["GeneID"], row["Chr"], int(row["Start"]), int(row["End"]), row["Strand"])
            for row in triples] == expected_rows
    grouped = Counter(row["GeneID"] for row in triples)
    assert len(grouped) == 8 and sum(grouped.values()) == 11, grouped
    assert grouped["TwoLab:hAT-Tip100:DNA"] == 3, grouped
    assert {key for key in grouped if key.startswith("TwoLab:")} == {"TwoLab:hAT-Tip100:DNA"}
    assert_registered(grouped, "taxonomy_triple", "taxonomy_triple")
    return "family buckets and 8 SAF GeneIDs registered; three TwoLab rows share one triple"


run_check("family/triple readers", lambda: f"{discover('bedtools')['version']}; Python SAF column reader", check)
