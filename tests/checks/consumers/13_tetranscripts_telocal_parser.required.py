#!/usr/bin/env python3
"""Round-trip TElocal's own index through its loader and verify TEtranscripts grouping."""

import ast
from pathlib import Path
import pickle
import sys
from types import SimpleNamespace

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (EXPECTED, FIXTURES, build_fixture, checkout_import,
                       assert_registered, checkout_version, execute_source_nodes, expected_tuples, export_path,
                       run_check, source_tree)


def load_telocal(path):
    """Run the checkout's locInd branch through its actual open and pickle.load statements."""
    source, tree = source_tree("TElocal", "TElocal")
    branches = [node for node in ast.walk(tree) if isinstance(node, ast.If)
                and isinstance(node.test, ast.Compare)
                and ast.unparse(node.test) == "args.tefile[-7:] == '.locInd'"]
    assert len(branches) == 1
    namespace = {"args": SimpleNamespace(tefile=str(path)), "pickle": pickle, "sys": sys,
                 "info": lambda *args: None, "error": lambda *args: None}
    execute_source_nodes(source, branches, namespace)
    return namespace["teIdx"]


def check():
    transcripts = checkout_import("TEtranscripts", "TEToolkit.TEindex")
    local = checkout_import("TElocal", "TElocal_Toolkit.TEindex")
    build_fixture()
    triples = {name + ":" + ":".join(ranks) for name, ranks in EXPECTED["taxonomy"].items()}
    for level, number in (("record", EXPECTED["records"]), ("subfamily", EXPECTED["names"])):
        gtf = str(export_path(f"{level}.gtf"))
        transcript_index = transcripts.TEfeatures()
        transcript_index.build(gtf)
        observed = transcript_index.getElements()
        assert len(observed) == EXPECTED["names"] and set(observed) == triples, observed
        assert_registered(observed, "taxonomy_triple", "taxonomy_triple")
        grouped = transcript_index.groupByEle([1] * EXPECTED["records"])
        assert grouped["TwoLab:hAT-Tip100:DNA"] == 3 and sum(grouped.values()) == 11, grouped
        local_index = local.TEfeatures()
        local_index.build(gtf)
        path = FIXTURES / f"{level}.locInd"
        with path.open("wb") as handle:
            pickle.dump(local_index, handle, protocol=pickle.HIGHEST_PROTOCOL)
        restored = load_telocal(path)
        assert type(restored) is local.TEfeatures
        assert sorted(tuple(name.split(":")) for name in restored.getNames()) == sorted(
            tuple(name.split(":")) for name in local_index.getNames())
        assert len(restored.getElements()) == number
        assert set(restored.getElements()) == expected_tuples(level)
        assert_registered(restored.getElements(), level, "four_tuple")
        assert restored.TE_annotation([("chrA", 1031, 1050, "+")]) == [0]
        assert restored.TE_annotation([("chrA", 3121, 3140, "+")]) == []
    return "TEtranscripts=8 groups; TElocal locInd record=11, subfamily=8"


run_check("TEtranscripts/TElocal", lambda: (
    f"{checkout_version('TEtranscripts')}/{checkout_version('TElocal')} checkout parsers"), check)
