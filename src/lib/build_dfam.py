"""Project pinned Dfam metadata into name, model, lineage and clade tables."""

import argparse
from collections import Counter
import gzip
import json
from pathlib import Path
import re
import sys

import pandas as pd
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from build_universes import evaluate_predicate
from records_io import write_tsv


PART_ROLES = ("5end", "orf2", "3end")
RANKS = ("class", "subclass", "order", "superfamily", "family")
COLUMNS = [
    "rmsk_name", "rmsk_class", "rmsk_family", "canonical_class", "canonical_family",
    "record_count", "match_status", "dfam_accessions", "dfam_model_names",
    "dfam_model_versions", "dfam_model_lengths_bp", "available_part_count",
    "part_roles_present", "model_length_sum_bp", "classification_path", "classification_leaf",
    "clades", "clade_count", "clade_leaves", "clade_compatibility", "dfam_release", "wicker_code",
    "wicker_code_uncertain", *[field for rank in RANKS
                              for field in (f"wicker_{rank}", f"wicker_{rank}_status")],
    "subfamily", "subfamily_status", "dfam_repeat_type", "dfam_repeat_subtype",
]
MODEL_COLUMNS = ["rmsk_name", "role", "accession", "model_name", "model_version",
                 "model_length_bp", "classification_path", "clades", "repeat_type", "repeat_subtype"]
NODE_COLUMNS = ["full_path", "parent_path", "name", "depth", "wicker_code",
                "repeatmasker_type", "repeatmasker_subtype", "family_count"]
CLADE_COLUMNS = ["accession", "clade_path", "clade_leaf"]
ORDERS = {"R": {"I": "LINE", "L": "LTR", "S": "SINE", "P": "PLE", "Y": "DIRS"},
          "D": {"T": "TIR", "Y": "Crypton", "H": "Helitron", "M": "Maverick"}}
SUPERFAMILIES = {
    "TIR": {"T": "Tc1-Mariner", "A": "hAT", "M": "Mutator", "E": "Merlin", "R": "Transib",
            "P": "P element", "B": "PiggyBac", "H": "PIF-Harbinger", "C": "CACTA"},
    "LINE": {"R": "R2", "T": "RTE", "J": "Jockey", "L": "L1", "I": "I"},
    "LTR": {"C": "Copia", "G": "Gypsy", "B": "Bel-Pao", "R": "Retrovirus", "E": "ERV"},
    "SINE": {"T": "tRNA", "L": "7SL", "S": "5S"}, "PLE": {"P": "Penelope"},
    "DIRS": {"D": "DIRS", "N": "Ngaro", "V": "Viper"}, "Crypton": {"C": "Crypton"},
    "Helitron": {"H": "Helitron"}, "Maverick": {"M": "Maverick"},
}


def lineage_nodes(tree):
    """Flatten every classification node with its immediate parent and root-zero depth."""
    rows = []

    def visit(node, parent="", depth=0):
        path = node["full_name"]
        if parent and path != parent + ";" + node["name"]:
            raise ValueError(f"Dfam lineage parent differs: {path}")
        rows.append(dict(zip(NODE_COLUMNS, [path, parent, node["name"], depth,
            (node.get("wicker_equiv") or "").strip(), node.get("repeatmasker_type") or "",
            node.get("repeatmasker_subtype") or "", node.get("count", "")])))
        for child in node.get("children", []):
            visit(child, path, depth + 1)

    visit(tree)
    if len({row["full_path"] for row in rows}) != len(rows):
        raise ValueError("Dfam lineage requires unique paths")
    return sorted(rows, key=lambda row: row["full_path"])


def match_models(name, snapshot):
    """Select an exact summary name or strict part suffixes in the declared role order."""
    hits = snapshot["summaries"].get(name, [])
    exact = [hit for hit in hits if hit["name"] == name]
    selected = []
    for role, label in ([("whole", name)] if exact else [(r, name + "_" + r) for r in PART_ROLES]):
        matches = [hit for hit in hits if hit["name"] == label]
        if len(matches) > 1:
            raise ValueError(f"Dfam duplicate model role: {name} {role}")
        if matches:
            hit = matches[0]
            accession = hit["accession"]
            if accession not in snapshot["records"]:
                raise ValueError(f"Dfam full record missing: {name} {accession}")
            model = snapshot["records"][accession]
            if any(model[key] != hit[key] for key in ("accession", "name", "version", "length", "classification")):
                raise ValueError(f"Dfam summary and full record differ: {name} {accession}")
            selected.append((role, model))
    status = "exact" if exact else "part_model_set" if selected else "missing"
    if len({model["classification"] for _, model in selected}) > 1:
        raise ValueError(f"Dfam part classification disagreement: {name}")
    return status, selected


def derive_ranks(name, path, nodes, match_status):
    """Derive Wicker ranks from the nearest coded ancestor with explicit rank statuses."""
    result = {field: value for rank in RANKS for field, value in (
        (f"wicker_{rank}", ""), (f"wicker_{rank}_status", "missing"))}
    result.update(wicker_code="", wicker_code_uncertain=False,
                  subfamily=name, subfamily_status="mapped")
    if match_status == "missing":
        return result
    if path not in nodes:
        raise ValueError(f"Dfam classification path missing from tree: {name}: {path}")
    ancestor = path
    while ancestor and not nodes[ancestor]["wicker_code"]:
        ancestor = nodes[ancestor]["parent_path"]
    if not ancestor:
        return result
    code = nodes[ancestor]["wicker_code"]
    result.update(wicker_code=code, wicker_code_uncertain=code.endswith("?"))
    status = ("part_model_set" if match_status == "part_model_set" else
              "mapped" if ancestor == path else "inherited")
    tokens = code.rstrip("? ").split("/")
    parsed = [re.fullmatch(r"([RD])", tokens[0])]
    parsed += [re.fullmatch(r"([A-Z])(?:\s*\(([^()]+)\))?\s*", token) for token in tokens[1:]]
    if len(tokens) > 3 or not all(parsed):
        raise ValueError(f"Dfam invalid Wicker code: {code}")

    def assign(rank, value, rank_status=status):
        result[f"wicker_{rank}"] = value
        result[f"wicker_{rank}_status"] = rank_status

    cls = parsed[0][1]
    assign("class", "Class I (retrotransposons)" if cls == "R" else "Class II (DNA transposons)")
    if cls == "R":
        assign("subclass", "", "inapplicable")
    if len(parsed) >= 2:
        letter, label = parsed[1].groups()
        order = label or ORDERS[cls][letter]
        assign("order", order)
        if cls == "D":
            assign("subclass", "subclass 1" if order in ("TIR", "Crypton") else "subclass 2")
        if len(parsed) == 3:
            letter, label = parsed[2].groups()
            if not label and letter not in SUPERFAMILIES.get(order, {}):
                raise ValueError(f"Dfam unknown Wicker superfamily letter: {order}/{letter}")
            assign("superfamily", label or SUPERFAMILIES[order][letter])
    assign("family", nodes[path]["name"], "part_model_set" if match_status == "part_model_set" else "mapped")
    return result


def clade_status(models):
    """Prioritize a Primates branch over multiple curated clades."""
    if not models:
        return "missing"
    if any("Primates" in path.split(";") for _, model in models for path in model["clades"]):
        return "primate_branch"
    return "multi_clade" if any(len(model["clades"]) > 1 for _, model in models) else "compatible"


def unique_join(values):
    return ";".join(dict.fromkeys(values))


def project_name(name, snapshot, nodes):
    """Preserve all selected model metadata and every curated clade path."""
    status, models = match_models(name, snapshot)
    path = models[0][1]["classification"] if models else ""
    model_rows = [dict(zip(MODEL_COLUMNS, [name, role, model["accession"], model["name"],
        model["version"], model["length"], model["classification"], ";".join(model["clades"]),
        model.get("repeat_type_name") or "", model.get("repeat_subtype_name") or ""]))
        for role, model in models]
    clades = list(dict.fromkeys(path for _, model in models for path in model["clades"]))
    result = {"match_status": status, "classification_path": path,
              "classification_leaf": path.rsplit(";", 1)[-1] if path else "",
              "available_part_count": len(models) if status == "part_model_set" else 0,
              "part_roles_present": ";".join(role for role, _ in models if role != "whole"),
              "model_length_sum_bp": sum(model["length"] for _, model in models),
              "clades": ";".join(clades), "clade_count": len(clades),
              "clade_leaves": unique_join(p.rsplit(";", 1)[-1] for p in clades),
              "clade_compatibility": clade_status(models), "dfam_release": snapshot["version"]["dfam_version"],
              **derive_ranks(name, path, nodes, status)}
    for target, source in (("dfam_accessions", "accession"), ("dfam_model_names", "name"),
                           ("dfam_model_versions", "version"), ("dfam_model_lengths_bp", "length")):
        result[target] = ";".join(str(model[source]) for _, model in models)
    for rank in ("type", "subtype"):
        result["dfam_repeat_" + rank] = unique_join(model.get("repeat_" + rank + "_name") or ""
                                                   for _, model in models)
    return result, model_rows, [(model["accession"], path, path.rsplit(";", 1)[-1])
                               for _, model in models for path in model["clades"]]


def build_dfam(build_dir, snapshot_path, universe="interspersed"):
    tables = Path(build_dir) / "tables"
    with gzip.open(snapshot_path, "rt") as stream:
        snapshot = json.load(stream)
    nodes = lineage_nodes(snapshot["classes"])
    node_index = {row["full_path"]: row for row in nodes}
    definitions = json.loads((Path(build_dir) / "universes.json").read_text())
    predicate = next(row["predicate"] for row in definitions["universes"] if row["name"] == universe)
    counts = Counter()
    for batch in pq.ParquetFile(tables / "rmsk_records.parquet").iter_batches(
            columns=["rmsk_name", "rmsk_class", "rmsk_family"], batch_size=200_000):
        frame = batch.to_pandas()
        counts.update(frame.loc[evaluate_predicate(frame, predicate), "rmsk_name"].value_counts().to_dict())
    canonical = pd.read_csv(tables / "taxonomy_canonical.tsv", sep="\t", dtype=str,
                            keep_default_na=False).set_index("rmsk_name")
    raw = pd.read_csv(tables / "rmsk_taxonomy.tsv", sep="\t", keep_default_na=False)
    rows, model_rows, clades = [], [], set()
    for name in sorted(counts):
        labels = canonical.loc[name]
        choices = raw.loc[raw.rmsk_name.eq(name)]
        for rank in ("class", "family"):
            value = labels["canonical_" + rank]
            compatible = choices.loc[choices["rmsk_" + rank].str.removesuffix("?").eq(value)]
            if not compatible.empty:
                choices = compatible
        chosen = choices.sort_values(["instance_count", "rmsk_class", "rmsk_family"],
                                      ascending=[False, True, True]).iloc[0]
        metadata, models, paths = project_name(name, snapshot, node_index)
        rows.append({"rmsk_name": name, "rmsk_class": chosen.rmsk_class,
                     "rmsk_family": chosen.rmsk_family, "record_count": counts[name],
                     "canonical_class": labels.canonical_class, "canonical_family": labels.canonical_family,
                     **metadata})
        model_rows.extend(models)
        clades.update(paths)
    for filename, values, columns in (("taxonomy_dfam.tsv", rows, COLUMNS),
            ("taxonomy_dfam_models.tsv", model_rows, MODEL_COLUMNS),
            ("dfam_lineage_nodes.tsv", nodes, NODE_COLUMNS),
            ("dfam_model_clades.tsv", sorted(clades), CLADE_COLUMNS)):
        write_tsv(pd.DataFrame(values, columns=columns), tables / filename)
    print(f"Dfam {snapshot['version']['dfam_version']}: names={len(rows)} models={len(model_rows)} "
          f"nodes={len(nodes)} clades={len(clades)} matches={dict(Counter(row['match_status'] for row in rows))}",
          flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build-dir", required=True, type=Path)
    parser.add_argument("--snapshot", required=True, type=Path)
    args = parser.parse_args()
    try:
        build_dfam(args.build_dir, args.snapshot)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"build_dfam: {error}\n")


if __name__ == "__main__":
    main()
