#!/usr/bin/env python3
"""Verify complete feature membership, measured inventory and count conservation."""

import gzip
import hashlib
import importlib
import sys

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
shape = importlib.import_module("40_exports_shape")
from records import BUILD, require


def conservation_fixture():
    """Load shared measured counts, supporting records and hand-computed target expectations."""
    fixtures = shape.ROOT / "tests/fixtures/exports"
    membership = pd.read_csv(fixtures / "conservation_members.tsv", sep="\t",
                             dtype=str, keep_default_na=False)
    counts = pd.read_csv(fixtures / "conservation_counts.tsv", sep="\t",
                         dtype={"emitted_feature_id": str, "count": "int64"})
    targets = membership.melt(id_vars=["emitted_feature_id", "rmsk_record_id"],
                              value_vars=["record", "subfamily", "family"],
                              var_name="feature_level", value_name="target")
    totals = pd.read_csv(fixtures / "conservation_totals.tsv", sep="\t",
                         dtype={"feature_level": str, "target": str, "count": "int64"})
    return membership[["emitted_feature_id", "rmsk_record_id"]], counts, targets, totals


def conservation(registration):
    """Assert registered targets and count each measured feature once per target and level."""
    membership, counts, targets, totals = conservation_fixture()
    assert set(registration.loc[registration["feature_level"].eq("record"), "key_grammar"]) == {
        "rmsk_record_id", "record_alias", "four_tuple",
    }
    selected = registration.loc[
        ((registration["feature_level"].eq("record") & registration["key_grammar"].eq("rmsk_record_id"))
         | (registration["feature_level"].eq("subfamily") & registration["key_grammar"].eq("rmsk_name"))
         | (registration["feature_level"].eq("family") & registration["key_grammar"].eq("family_bucket"))),
        ["rmsk_record_id", "feature_level", "emitted_feature_id"],
    ].rename(columns={"emitted_feature_id": "target"})
    edges = membership.merge(selected, on="rmsk_record_id", validate="one_to_many")
    assert sorted(edges.itertuples(index=False, name=None)) == sorted(
        targets.itertuples(index=False, name=None)), "conservation targets per measured feature"
    rolled_up = edges[["feature_level", "target", "emitted_feature_id"]].drop_duplicates().merge(
        counts, on="emitted_feature_id", validate="many_to_one",
    ).groupby(["feature_level", "target"])["count"].sum()
    assert rolled_up.to_dict() == totals.set_index(["feature_level", "target"])["count"].to_dict()
    for level in ("record", "subfamily", "family"):
        selected = edges.loc[edges["feature_level"].eq(level), ["emitted_feature_id"]].drop_duplicates()
        total = selected.merge(counts, on="emitted_feature_id", validate="one_to_one")["count"].sum()
        assert total == 7, (level, total)
    assert edges.merge(counts, on="emitted_feature_id").groupby("feature_level")["count"].sum().eq(21).all()


def main():
    require(*(f"{shape.DIRECTORY}/{name}" for name in shape.FILES),
            "tables/export_feature_members.tsv.gz", "tables/exports.tsv")
    records = shape.reference_records()
    record_index = pd.Index(records["rmsk_record_id"])
    assert record_index.is_unique
    identities = [value.to_numpy() for value in (
        records["rmsk_record_id"], records["alias"], records["alias"] + ":" + records["triple"],
        records["rmsk_name"], records["rmsk_name"] + ":" + records["triple"],
        records["family_feature"], records["triple"], "I|mm39|" + records["rmsk_instance_id"],
    )]
    slot_index = pd.MultiIndex.from_tuples([
        ("record", "rmsk_record_id"), ("record", "record_alias"), ("record", "four_tuple"),
        ("subfamily", "rmsk_name"), ("subfamily", "four_tuple"), ("family", "family_bucket"),
        ("taxonomy_triple", "taxonomy_triple"), ("instance", "instance_alias"),
    ])
    counts = np.zeros((8, len(records)), dtype=np.uint32)
    instances = set()
    conservation_members, _, _, _ = conservation_fixture()
    conservation_rows = []
    columns = ["universe_name", "variant", "feature_level", "key_grammar", "emitted_feature_id",
               "rmsk_record_id", "block_start_1", "block_end_1"]
    with gzip.open(BUILD / "tables/export_feature_members.tsv.gz", "rt") as stream:
        assert stream.readline().rstrip("\n").split("\t") == columns
    rows = 0
    for chunk in pd.read_csv(
        BUILD / "tables/export_feature_members.tsv.gz", sep="\t", quoting=3, keep_default_na=False,
        dtype={column: "int64" if column.startswith("block_") else str for column in columns},
        chunksize=250_000,
    ):
        assert chunk["universe_name"].eq("interspersed").all() and chunk["variant"].eq("full").all()
        conservation_rows.append(chunk.loc[
            chunk["rmsk_record_id"].isin(conservation_members["rmsk_record_id"])])
        indices = record_index.get_indexer(chunk["rmsk_record_id"])
        assert (indices >= 0).all(), "registration contains a record outside the universe"
        expected = records.iloc[indices]
        shape.equal(chunk["block_start_1"], expected["start_1"], "block starts")
        shape.equal(chunk["block_end_1"], expected["end_1"], "block ends")
        slots = slot_index.get_indexer(pd.MultiIndex.from_frame(chunk[["feature_level", "key_grammar"]]))
        assert (slots >= 0).all(), "registration feature levels and grammars"
        positions = np.arange(rows, rows + len(chunk))
        shape.equal(slots, positions % 8, "registration spelling order")
        shape.equal(indices, positions // 8, "registration record order")
        emitted = chunk["emitted_feature_id"].to_numpy()
        instances.update(emitted[slots == 7])
        for slot in range(8):
            mask = slots == slot
            shape.equal(emitted[mask], identities[slot][indices[mask]], ("registered ID", slot))
            np.add.at(counts[slot], indices[mask], 1)
        rows += len(chunk)
    assert rows == 8 * len(records) and (counts == 1).all(), "one row per record and ID spelling"
    instance_count = len(instances)
    assert instance_count == records["rmsk_instance_id"].nunique(), "registered instance count"
    del instances
    inventory = pd.read_csv(BUILD / "tables/exports.tsv", sep="\t", keep_default_na=False,
                            dtype={"rows": "int64", "distinct_features": "int64"})
    assert list(inventory) == ["export_path", "namespace", "universe_name", "variant", "feature_level",
                               "format", "rows", "distinct_features", "sha256"]
    actual_paths = {path.relative_to(BUILD).as_posix() for path in (BUILD / "exports").rglob("*")
                    if path.is_file()}
    assert inventory["export_path"].is_unique
    assert set(inventory["export_path"]) == actual_paths
    assert actual_paths == {f"{shape.DIRECTORY}/{name}" for name in shape.FILES}
    for row in inventory.itertuples(index=False):
        path = BUILD / row.export_path
        level = path.stem
        assert (row.namespace, row.universe_name, row.variant, row.feature_level, row.format) == (
            "ucsc", "interspersed", "full", level, path.suffix[1:])
        digest = hashlib.sha256()
        lines = 0
        last = b""
        with path.open("rb") as stream:
            while block := stream.read(1024 * 1024):
                digest.update(block)
                lines += block.count(b"\n")
                assert b"\r" not in block, path
                last = block[-1:]
        assert last == b"\n", path
        assert digest.hexdigest() == row.sha256, path
        assert lines - (path.suffix == ".saf") == row.rows == len(records), path
        slot = (1 if path.suffix == ".gtf" else 0) if level == "record" else {
            "subfamily": 3, "family": 5, "taxonomy_triple": 6,
        }[level]
        registered = pd.Index(identities[slot]).drop_duplicates()
        seen = np.zeros(len(registered), dtype=bool)
        column = {".bed": 3, ".gtf": 8, ".saf": 0}[path.suffix]
        usecols = [0, 3, 4, 6, 8] if path.suffix == ".gtf" else [column]
        for chunk in pd.read_csv(path, sep="\t", header=None, usecols=usecols, dtype=str,
                                 keep_default_na=False, quoting=3, chunksize=100_000,
                                 skiprows=1 if path.suffix == ".saf" else 0):
            features = chunk[column]
            if path.suffix == ".gtf":
                attributes = {key: features.str.extract(
                    rf'(?:^|; ){key} "([^"]+)";', expand=False)
                    for key in ("transcript_id", "gene_id", "family_id", "class_id", "locus",
                                *(["rmsk_record_id", "instance_id"] if level == "record" else []))}
                assert all(value.notna().all() for value in attributes.values()), path
                keys = (attributes["rmsk_record_id"] if level == "record" else
                        attributes["gene_id"] + "|" + chunk[0] + ":" + chunk[3] + "-" + chunk[4] + "|" + chunk[6])
                members = record_index.get_indexer(keys)
                assert (members >= 0).all(), (path, "GTF record membership")
                composed = (attributes["transcript_id"] + ":" + attributes["gene_id"] + ":"
                            + attributes["family_id"] + ":" + attributes["class_id"])
                tuple_slot = slot_index.get_loc((level, "four_tuple"))
                shape.equal(composed, identities[tuple_slot][members], (path, "registered four-tuple"))
                assert (counts[tuple_slot, members] == 1).all(), path
                if level == "record":
                    shape.equal(attributes["instance_id"], identities[7][members],
                                (path, "registered instance"))
                    assert (counts[7, members] == 1).all(), path
                features = attributes["locus"]
            indices = registered.get_indexer(features)
            assert (indices >= 0).all(), (path, "unregistered emitted feature")
            seen[indices] = True
        assert seen.all() and seen.sum() == row.distinct_features, path
    conservation(pd.concat(conservation_rows, ignore_index=True))
    print(f"registrations={rows}; eight ID spellings cover every record once; instances={instance_count}; "
          "seven inventory hashes, feature sets and GTF tuple/instance joins pass; "
          "three record grammars; count 7 stays 7 at record, subfamily and family levels")


if __name__ == "__main__":
    main()
