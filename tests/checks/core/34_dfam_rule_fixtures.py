#!/usr/bin/env python3
"""Exercise Wicker ranks, strict part matches and clade precedence with authored cases."""

import csv
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from build_dfam import derive_ranks, lineage_nodes, project_name

with (ROOT / "tests/fixtures/taxonomy/dfam_rank_cases.tsv").open() as stream:
    cases = list(csv.DictReader(stream, delimiter="\t"))
for case in cases:
    root = {"full_name": "root", "name": "root"}
    parent = {"full_name": "root;Order", "name": "Order"}
    leaf = {"full_name": "root;Order;Leaf", "name": "Leaf"}
    root["children"], parent["children"] = [parent], [leaf]
    (parent if case["code_at"] == "parent" else leaf)["wicker_equiv"] = case["code"]
    nodes = {row["full_path"]: row for row in lineage_nodes(root)}
    roles = case["roles"].split(";") if case["roles"] else []
    models = [{"accession": f"DF{i}", "name": "Example" + ("_" + role if role != "whole" else ""),
               "version": 1, "length": 100 + i, "classification": leaf["full_name"],
               "clades": json.loads(case["clades"]), "repeat_type_name": "LINE", "repeat_subtype_name": "L1"}
              for i, role in enumerate(roles)]
    if case["error"]:
        models[-1]["classification"] = parent["full_name"]
    snapshot = {"version": {"dfam_version": "4.0"}, "summaries": {"Example": models},
                "records": {model["accession"]: model for model in models}}
    try:
        observed, selected, clades = project_name("Example", snapshot, nodes)
    except ValueError as error:
        assert case["error"] and case["error"] in str(error), (case["case"], str(error))
    else:
        assert not case["error"], case["case"]
        for field, value in json.loads(case["expected"]).items():
            assert observed[field] == value, (case["case"], field, observed[field], value)
        assert observed["subfamily"] == "Example" and observed["subfamily_status"] == "mapped"
        assert observed["model_length_sum_bp"] == sum(100 + i for i in range(len(roles)))
        assert observed["available_part_count"] == len([r for r in roles if r != "whole"])
        assert [model["role"] for model in selected] == roles
        assert len(clades) == len(models) * len(json.loads(case["clades"]))
refusals = []
for code, message in (("R/I/L/X", "Dfam invalid Wicker code: R/I/L/X"),
                       ("D/T (TIR)/Z", "Dfam unknown Wicker superfamily letter: TIR/Z")):
    nodes = {"root": {"name": "root", "parent_path": "", "wicker_code": code}}
    try:
        derive_ranks("Example", "root", nodes, "exact")
    except ValueError as error:
        assert str(error) == message, str(error)
        refusals.append(message)
    else:
        raise AssertionError(f"accepted invalid code: {code}")
print(f"{len(cases)} authored Dfam cases: codes, inherited ranks, uncertainty, subclasses, parts, clades and named disagreement pass; "
      "refused: " + "; ".join(refusals))
