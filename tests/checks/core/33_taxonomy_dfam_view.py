#!/usr/bin/env python3
"""Compare Dfam tables with pinned metadata, catalog weights and the authored census."""

from collections import Counter
import csv
import gzip
import json
from pathlib import Path
import re
import sys
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import (BUILD, require, DFAM_COLUMNS, DFAM_MODEL_COLUMNS, DFAM_NODE_COLUMNS, DFAM_CLADE_COLUMNS)

FILES = ("taxonomy_dfam.tsv", "taxonomy_dfam_models.tsv", "dfam_lineage_nodes.tsv", "dfam_model_clades.tsv")
require(*(f"tables/{name}" for name in FILES))


def read(path):
    with path.open() as stream:
        return list(csv.DictReader(stream, delimiter="\t"))


RANKS = ("class", "subclass", "order", "superfamily", "family")
ORDERS = {"R": dict(I="LINE", L="LTR", S="SINE", P="PLE", Y="DIRS"),
          "D": dict(T="TIR", Y="Crypton", H="Helitron", M="Maverick")}
SUPERFAMILIES = {
    "TIR": dict(T="Tc1-Mariner", A="hAT", M="Mutator", E="Merlin", R="Transib",
                P="P element", B="PiggyBac", H="PIF-Harbinger", C="CACTA"),
    "LINE": dict(R="R2", T="RTE", J="Jockey", L="L1", I="I"),
    "LTR": dict(C="Copia", G="Gypsy", B="Bel-Pao", R="Retrovirus", E="ERV"),
    "SINE": dict(T="tRNA", L="7SL", S="5S"), "PLE": dict(P="Penelope"),
    "DIRS": dict(D="DIRS", N="Ngaro", V="Viper"), "Crypton": dict(C="Crypton"),
    "Helitron": dict(H="Helitron"), "Maverick": dict(M="Maverick"),
}


def check_rank_cells(table, nodes):
    """Reconstruct every rank cell from the published code and lineage tree."""
    for row in table:
        path, code = row["classification_path"], row["wicker_code"]
        values = dict.fromkeys(RANKS, "")
        statuses = dict.fromkeys(RANKS, "missing")
        if code:
            ancestor = path
            while not nodes[ancestor]["wicker_code"]:
                ancestor = nodes[ancestor]["parent_path"]
            assert nodes[ancestor]["wicker_code"] == code
            status = ("part_model_set" if row["match_status"] == "part_model_set" else
                      "mapped" if ancestor == path else "inherited")
            tokens = code.rstrip("? ").split("/")
            cls = tokens[0]
            assert cls in ORDERS and len(tokens) <= 3
            values["class"] = {"R": "Class I (retrotransposons)", "D": "Class II (DNA transposons)"}[cls]
            statuses["class"] = status
            if cls == "R":
                statuses["subclass"] = "inapplicable"
            if len(tokens) > 1:
                letter, label = re.fullmatch(r"([A-Z])(?:\s*\(([^()]+)\))?\s*", tokens[1]).groups()
                values["order"] = label or ORDERS[cls][letter]
                statuses["order"] = status
                if cls == "D":
                    values["subclass"] = "subclass 1" if values["order"] in ("TIR", "Crypton") else "subclass 2"
                    statuses["subclass"] = status
            if len(tokens) == 3:
                letter, label = re.fullmatch(r"([A-Z])(?:\s*\(([^()]+)\))?\s*", tokens[2]).groups()
                values["superfamily"] = label or SUPERFAMILIES[values["order"]][letter]
                statuses["superfamily"] = status
            values["family"] = nodes[path]["name"]
            statuses["family"] = "part_model_set" if row["match_status"] == "part_model_set" else "mapped"
        for rank in RANKS:
            for column, expected in (("wicker_" + rank, values[rank]),
                                     ("wicker_" + rank + "_status", statuses[rank])):
                assert row[column] == expected, f"Dfam rank cell differs: {row['rmsk_name']}: {column}"


rows, models, nodes, clades = [read(BUILD / "tables" / name) for name in FILES]
for table, columns in zip((rows, models, nodes, clades),
                          (DFAM_COLUMNS, DFAM_MODEL_COLUMNS, DFAM_NODE_COLUMNS, DFAM_CLADE_COLUMNS)):
    assert list(table[0]) == columns
expected = {r["metric"]: int(r["value"]) for r in read(ROOT / "tests/expectations/mm39/dfam_census.tsv")}
canonical = {r["rmsk_name"]: r for r in read(BUILD / "tables/taxonomy_canonical.tsv")}
with gzip.open(BUILD / "source/dfam_interspersed_mm39_snapshot.json.gz", "rt") as stream:
    snapshot = json.load(stream)
raw_nodes = {}


def walk(node):
    raw_nodes[node["full_name"]] = node
    for child in node.get("children", []):
        walk(child)


walk(snapshot["classes"])
assert {r["full_path"] for r in nodes} == set(raw_nodes)
assert len(nodes) == len(raw_nodes)
assert [r["full_path"] for r in nodes] == sorted(raw_nodes)
model_order = [(m["rmsk_name"], ("whole", "5end", "orf2", "3end").index(m["role"])) for m in models]
assert model_order == sorted(set(model_order))
clade_order = [(c["accession"], c["clade_path"]) for c in clades]
assert clade_order == sorted(set(clade_order))
for row in nodes:
    raw = raw_nodes[row["full_path"]]
    assert row["name"] == raw["name"]
    assert row["parent_path"] == row["full_path"].rsplit(";", 1)[0] if ";" in row["full_path"] else row["parent_path"] == ""
    assert int(row["depth"]) == row["full_path"].count(";")
    for out, field in (("wicker_code", "wicker_equiv"), ("repeatmasker_type", "repeatmasker_type"),
                        ("repeatmasker_subtype", "repeatmasker_subtype"), ("family_count", "count")):
        assert row[out] == str(raw.get(field) or "").strip(), (row["full_path"], out)
names = [row["rmsk_name"] for row in rows]
assert names == sorted(set(names)) == sorted(snapshot["summaries"])
node_index = {row["full_path"]: row for row in nodes}
check_rank_cells(rows, node_index)
counts = Counter()
classes = {"SINE", "LTR", "LINE", "DNA", "RC", "Retroposon", "Unknown", "Unspecified", "DNA?"}
for batch in pq.ParquetFile(BUILD / "tables/rmsk_records.parquet").iter_batches(
        columns=["rmsk_name", "rmsk_class"], batch_size=200_000):
    frame = batch.to_pandas()
    counts.update(frame.loc[frame.rmsk_class.isin(classes), "rmsk_name"].value_counts().to_dict())
assert set(counts) == set(names)
raw_labels = read(BUILD / "tables/rmsk_taxonomy.tsv")
by_name = {}
for model in models:
    by_name.setdefault(model["rmsk_name"], []).append(model)
assert len({(m["rmsk_name"], m["role"]) for m in models}) == len(models)
expected_clades = set()
census = Counter(names=len(rows), records=sum(counts.values()), model_rows=len(models),
                 lineage_nodes=len(nodes), coded_nodes=sum(bool(n["wicker_code"]) for n in nodes))
l2 = []
for row in rows:
    name = row["rmsk_name"]
    assert int(row["record_count"]) == counts[name]
    for field in ("canonical_class", "canonical_family"):
        assert row[field] == canonical[name][field], (name, field)
    labels = [r for r in raw_labels if r["rmsk_name"] == name]
    for rank in ("class", "family"):
        matching = [r for r in labels if r["rmsk_" + rank].removesuffix("?") == canonical[name]["canonical_" + rank]]
        if matching:
            labels = matching
    raw = sorted(labels, key=lambda r: (-int(r["instance_count"]), r["rmsk_class"], r["rmsk_family"]))[0]
    assert (row["rmsk_class"], row["rmsk_family"]) == (raw["rmsk_class"], raw["rmsk_family"])
    hits = snapshot["summaries"][name]
    chosen = [("whole", h) for h in hits if h["name"] == name]
    if not chosen:
        chosen = [(role, h) for role in ("5end", "orf2", "3end") for h in hits if h["name"] == name + "_" + role]
    status = "exact" if chosen and chosen[0][0] == "whole" else "part_model_set" if chosen else "missing"
    assert row["match_status"] == status
    census[status + "_names"] += 1
    census[status + "_records"] += counts[name]
    selected = by_name.get(name, [])
    assert [(m["role"], m["accession"]) for m in selected] == [(role, h["accession"]) for role, h in chosen]
    for target, source in (("dfam_accessions", "accession"), ("dfam_model_names", "model_name"),
                           ("dfam_model_versions", "model_version"), ("dfam_model_lengths_bp", "model_length_bp")):
        assert row[target] == ";".join(m[source] for m in selected), (name, target)
    assert int(row["model_length_sum_bp"]) == sum(int(m["model_length_bp"]) for m in selected)
    parts = [m["role"] for m in selected if m["role"] != "whole"]
    assert int(row["available_part_count"]) == len(parts)
    assert row["part_roles_present"] == ";".join(parts)
    all_clades = []
    paths = set()
    for model in selected:
        raw = snapshot["records"][model["accession"]]
        for out, field in (("model_name", "name"), ("model_version", "version"), ("model_length_bp", "length"),
                            ("classification_path", "classification"), ("repeat_type", "repeat_type_name"),
                            ("repeat_subtype", "repeat_subtype_name")):
            assert model[out] == str(raw.get(field) or ""), (name, out)
        assert model["clades"] == ";".join(raw["clades"])
        paths.add(model["classification_path"])
        assert model["classification_path"] in raw_nodes
        census["multi_clade_models"] += len(raw["clades"]) > 1
        census["primate_branch_models"] += any("Primates" in p.split(";") for p in raw["clades"])
        expected_clades.update((model["accession"], p, p.split(";")[-1]) for p in raw["clades"])
        all_clades.extend(raw["clades"])
    assert len(paths) <= 1
    assert row["classification_path"] == next(iter(paths), "")
    assert row["classification_leaf"] == row["classification_path"].split(";")[-1]
    assert row["clades"] == ";".join(dict.fromkeys(all_clades))
    assert int(row["clade_count"]) == len(set(all_clades)), (name, "clade_count")
    assert row["clade_leaves"] == ";".join(dict.fromkeys(p.split(";")[-1] for p in all_clades))
    compatibility = ("missing" if not selected else "primate_branch" if any("Primates" in p.split(";") for p in all_clades)
                     else "multi_clade" if any(len(snapshot["records"][m["accession"]]["clades"]) > 1 for m in selected)
                     else "compatible")
    assert row["clade_compatibility"] == compatibility
    census["primate_branch_names"] += compatibility == "primate_branch"
    if parts:
        census[f"part_sets_{len(parts)}"] += 1
        if row["rmsk_family"] in ("L2", "CR1"):
            l2.append(name)
    if status == "exact":
        census["exact_wicker_" + row["wicker_class_status"]] += 1
    ancestor = row["classification_path"]
    while ancestor and not raw_nodes[ancestor].get("wicker_equiv"):
        ancestor = ancestor.rsplit(";", 1)[0] if ";" in ancestor else ""
    code = raw_nodes[ancestor]["wicker_equiv"].strip() if ancestor else ""
    assert row["wicker_code"] == code
    assert row["wicker_code_uncertain"] == str(code.endswith("?")).lower()
    if not code:
        for rank in RANKS:
            assert row["wicker_" + rank] == "", f"Dfam rank cell differs: {name}: wicker_{rank}"
            assert row["wicker_" + rank + "_status"] == "missing", f"Dfam rank cell differs: {name}: wicker_{rank}_status"
    assert row["subfamily"] == name and row["subfamily_status"] == "mapped"
    for field, model_field in (("dfam_repeat_type", "repeat_type"), ("dfam_repeat_subtype", "repeat_subtype")):
        assert row[field] == ";".join(dict.fromkeys(m[model_field] for m in selected))
    assert row["dfam_release"] == snapshot["version"]["dfam_version"]
assert sorted(l2) == ["L2a", "L2b", "L2c", "L2d", "L2d2", "L3b"]
census["l2_cr1_part_sets"] = len(l2)
assert len(clades) == len(expected_clades)
assert {(r["accession"], r["clade_path"], r["clade_leaf"]) for r in clades} == expected_clades
assert {m["accession"] for m in models} == {r["accession"] for r in clades}
assert dict(census) == expected, (dict(census), expected)
refusals = []
with TemporaryDirectory(prefix="dfam-rank-mutations-") as directory:
    path = Path(directory) / "taxonomy_dfam.tsv"
    for rank in RANKS:
        for column in ("wicker_" + rank, "wicker_" + rank + "_status"):
            mutated = [dict(row) for row in rows]
            mutated[0][column] = "CORRUPT"
            with path.open("w") as stream:
                writer = csv.DictWriter(stream, fieldnames=DFAM_COLUMNS, delimiter="\t", lineterminator="\n")
                writer.writeheader()
                writer.writerows(mutated)
            message = f"Dfam rank cell differs: {rows[0]['rmsk_name']}: {column}"
            try:
                check_rank_cells(read(path), node_index)
            except AssertionError as error:
                assert str(error) == message, str(error)
                refusals.append(message)
            else:
                raise AssertionError(f"accepted rank mutation: {column}")
print("Dfam census and catalog joins pass; " + json.dumps(dict(census), sort_keys=True)
      + "; refused: " + "; ".join(refusals))
