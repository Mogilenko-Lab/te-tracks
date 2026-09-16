#!/usr/bin/env python3
"""Gate Stellarscope grouping, attribute parsing and endpoint behavior."""

from pathlib import Path
import sys

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (EXPECTED, FIXTURES, ROSTER, Unsupported, build_fixture,
                       assert_registered, checkout_import, checkout_version, export_path,
                       record_alias, record_key, run_check)


def check():
    intervaltree = checkout_import("stellarscope", "_intervaltree", subpackage="stellarscope.annotation")
    utils = checkout_import("stellarscope", "utils", subpackage="stellarscope.annotation")
    import pysam

    build_fixture()
    gtf = export_path("record.gtf")
    features = [utils.GTFFeature(line) for line in gtf.read_text().splitlines()]
    required = {"gene_id", "transcript_id", "locus", "family_id", "class_id",
                "rmsk_family", "rmsk_class", "instance_id", "rmsk_record_id"}
    assert len(features) == EXPECTED["records"]
    for feature, row in zip(features, ROSTER):
        assert set(feature.attributes) == required, feature.attributes
        assert all(feature.attributes.values())
        assert feature.attributes["locus"] == record_alias(row)
        assert feature.attributes["gene_id"] == row[4]
        assert feature.attributes["instance_id"] == f"I|mm39|{row[6]}"
        assert "__no_feature" not in feature.attributes.values()
    records = intervaltree.IntervalTreeAnnotation(str(gtf), "locus", "exon")
    instances = intervaltree.IntervalTreeAnnotation(str(gtf), "instance_id", "exon")
    assert len(records.loci) == EXPECTED["records"]
    assert len(instances.loci) == EXPECTED["instances"]
    assert_registered(records.loci, "record", "record_alias")
    registered_instances = assert_registered(instances.loci, "instance", "instance_alias")
    assert registered_instances["I|mm39|7"] == {
        record_key(row) for row in ROSTER if row[4] in {"SubB", "SubB-int"}
    }
    assert {f.attributes["gene_id"] for f in instances.loci["I|mm39|7"]} == {"SubB", "SubB-int"}
    assert len([iv for iv in instances.itree["chrA"] if iv.data == "I|mm39|7"]) == 2
    subfamilies = intervaltree.IntervalTreeAnnotation(str(export_path("subfamily.gtf")), "locus", "exon")
    assert_registered(subfamilies.loci, "subfamily", "rmsk_name")
    edge = record_alias(next(row for row in ROSTER if row[4] == "Edge"))
    with pysam.AlignmentFile(FIXTURES / "arc_3prime.bam") as bam:
        reads = {r.query_name: r for r in bam.fetch(until_eof=True)}
    assert instances.intersect_blocks("chrA", reads["gap_copy0"].get_blocks()) == {}
    observed = [int(bool(records.intersect_blocks("chrB", reads[f"edge_{start}_copy0"].get_blocks()).get(edge)))
                for start in (99, 100, 109, 110)]
    if observed == [0, 1, 1, 1]:
        raise Unsupported("stellarscope right-boundary overlap defect, "
                          "observed 0,1,1,1 expected 0,1,1,0")
    assert observed == EXPECTED["boundary"], (observed, EXPECTED["boundary"])
    return "locus=11, instance_id=10, boundary=0,1,1,0"


run_check("stellarscope", lambda: f"{checkout_version('stellarscope')} checkout parser", check)
