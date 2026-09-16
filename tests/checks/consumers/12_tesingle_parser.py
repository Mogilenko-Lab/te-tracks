#!/usr/bin/env python3
"""Verify both TEsingle feature grains and its distinct-UR cutoff."""

import ast
from collections import Counter
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (CELL, EXPECTED, FIXTURES, build_fixture, checkout_import, checkout_version,
                       expected_tuples, export_path, run_check, source_tree)


def check_alignment_filter(alignment, index, counters, cutoff):
    """Use real BAM UR tags to exercise read filtering and the barcode cutoff."""
    import pysam

    genes = SimpleNamespace(Gene_annotation=lambda intervals: [])
    bam_path = FIXTURES / "arc_3prime.bam"
    cells = alignment.read_in_alignment(str(bam_path), genes, index, "yes")
    with pysam.AlignmentFile(bam_path) as bam:
        header = bam.header.to_dict()
        reads = list(bam.fetch(until_eof=True))
    usable = [read for read in reads if not (read.is_duplicate or read.is_qcfail)]
    assert set(cells) == {CELL}
    assert set(cells[CELL]) == {read.get_tag("UR") for read in usable}
    assert len(cells[CELL]) == EXPECTED["bams"]["arc_3prime.bam"]["molecules_by_tag"]["UR"] - 2
    parsed_names = {name for molecules in cells.values() for names in molecules.values() for name in names}
    assert parsed_names == {read.query_name for read in usable}, parsed_names
    flagged = EXPECTED["bams"]["arc_3prime.bam"]["flagged_reads"]
    assert parsed_names.isdisjoint(flagged["duplicate"] + flagged["qcfail"])
    for name in ("duplicate_b_copy0", "duplicate_b_copy1", "minus_twolab_copy0"):
        assert any(hit[1] for names in cells[CELL].values() for hit in names.get(name, [])), name

    scratch = FIXTURES.parent / "consumers_scratch"
    scratch.mkdir(exist_ok=True)
    with TemporaryDirectory(prefix="tesingle_", dir=scratch) as directory:
        path = Path(directory) / "cutoff.bam"
        header["HD"]["SO"] = "unsorted"
        with pysam.AlignmentFile(path, "wb", header=header) as bam:
            for cell, count in (("below", 999), ("at", 1000)):
                for number in range(count):
                    read = pysam.AlignedSegment.fromstring(usable[0].to_string(), bam.header)
                    read.query_name = f"{cell}_{number}"
                    read.set_tag("CB", cell)
                    read.set_tag("UB", "A" * 12)
                    read.set_tag("UR", "".join("ACGT"[(number >> (2 * pos)) & 3] for pos in range(12)))
                    bam.write(read)
        raw_cells = alignment.read_in_alignment(str(path), genes, index, "no")
    assert {cell: len(umis) for cell, umis in raw_cells.items()} == {"below": 999, "at": 1000}
    filtered, initial, retained = counters.basic_filtering(raw_cells, cutoff)
    assert (initial, retained, set(filtered)) == (2, 1, {"at"}), filtered.keys()


def check():
    teindex = checkout_import("TEsingle", "TEtools.TEindex")
    counters = checkout_import("TEsingle", "TEtools.Counters")
    alignment = checkout_import("TEsingle", "TEtools.AlignmentIO")
    build_fixture()
    for level, number in (("record", EXPECTED["records"]), ("subfamily", EXPECTED["names"])):
        index = teindex.TEfeatures()
        index.build(str(export_path(f"{level}.gtf")))
        observed = index.getElements()
        assert len(observed) == number and set(observed) == expected_tuples(level), observed
        two = [label for label in observed if label.split(":")[1] == "TwoLab"]
        assert len(two) == (3 if level == "record" else 1)
        assert all(label.endswith(":TwoLab:hAT-Tip100:DNA") for label in two), two
        lines = [line for line in export_path(f"{level}.gtf").read_text().splitlines()
                 if 'gene_id "TwoLab";' in line]
        assert Counter("hAT-Blackjack" if 'rmsk_family "hAT-Blackjack";' in line
                       else "hAT-Tip100" for line in lines) == {"hAT-Tip100": 2, "hAT-Blackjack": 1}

    path, tree = source_tree("TEsingle", "TEsingle")
    options = [node for node in ast.walk(tree) if isinstance(node, ast.Call)
               and isinstance(node.func, ast.Attribute) and node.func.attr == "add_argument"
               and any(isinstance(arg, ast.Constant) and arg.value == "--cutoff" for arg in node.args)]
    assert len(options) == 1
    default = next(ast.literal_eval(keyword.value) for keyword in options[0].keywords if keyword.arg == "default")
    assert default == 1000
    _, tree = source_tree("TEsingle", "TEtools/Counters.py")
    filtering = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                     and node.name == "basic_filtering")
    comparison = [node for node in ast.walk(filtering) if isinstance(node, ast.Compare)]
    assert len(comparison) == 1 and ast.unparse(comparison[0]) == "len(bcumi_dict[cbc]) < cutoff"
    check_alignment_filter(alignment, index, counters, default)
    return "record=11, subfamily=8; 999 distinct UR dropped, 1000 kept; duplicate/QC-fail reads skipped"


run_check("TEsingle", lambda: f"{checkout_version('TEsingle')} checkout parser", check)
