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
    catalog = pd.read_parquet(BUILD / "tables/rmsk_records.parquet",
                              columns=["rmsk_record_id", "chrom", "start_1", "end_1", "strand", "sw_score"])
    catalog_index = pd.Index(catalog["rmsk_record_id"])
    assert catalog_index.is_unique and len(catalog) == 5_320_771
    all_counts = np.zeros(len(catalog), dtype=np.uint32)
    aliases = pd.read_csv(BUILD / "tables/contig_aliases.tsv", sep="\t", keep_default_na=False)
    rows = all_rows = 0
    for chunk in pd.read_csv(
        BUILD / "tables/export_feature_members.tsv.gz", sep="\t", quoting=3, keep_default_na=False,
        dtype={column: "int64" if column.startswith("block_") else str for column in columns},
        chunksize=250_000,
    ):
        assert chunk["universe_name"].isin(["interspersed", "all_rmsk"]).all()
        assert chunk["variant"].eq("full").all()
        complete = chunk.loc[chunk["universe_name"].eq("all_rmsk")]
        if not complete.empty:
            assert rows + chunk["universe_name"].eq("interspersed").sum() == 30_119_592
            assert complete["feature_level"].eq("record").all()
            assert complete["key_grammar"].eq("rmsk_record_id").all()
            shape.equal(complete["emitted_feature_id"], complete["rmsk_record_id"], "catalog IDs")
            indices = catalog_index.get_indexer(complete["rmsk_record_id"])
            assert (indices >= 0).all()
            expected = catalog.iloc[indices]
            shape.equal(complete["block_start_1"], expected["start_1"], "catalog block starts")
            shape.equal(complete["block_end_1"], expected["end_1"], "catalog block ends")
            np.add.at(all_counts, indices, 1)
            all_rows += len(complete)
        chunk = chunk.loc[chunk["universe_name"].eq("interspersed")]
        if chunk.empty:
            continue
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
    assert all_rows == 5_320_771 and (all_counts == 1).all(), "one block per complete catalog record"
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
    assert actual_paths == {
        f"exports/{namespace}/interspersed/full/{name}"
        for namespace in ("ucsc", "ensembl", "gencode") for name in shape.FILES
    } | {f"exports/{namespace}/all_rmsk/full/record.bed" for namespace in ("ucsc", "ensembl", "gencode")}
    assert len(inventory) == 24
    assert inventory.export_path.tolist() == sorted(actual_paths)
    for row in inventory.itertuples(index=False):
        path = BUILD / row.export_path
        level = path.stem
        assert row.namespace in {"ucsc", "ensembl", "gencode"}
        assert row.universe_name in {"interspersed", "all_rmsk"}
        assert row.export_path == f"exports/{row.namespace}/{row.universe_name}/full/{path.name}"
        assert (row.variant, row.feature_level, row.format) == ("full", level, path.suffix[1:])
        to_ucsc = dict(zip(aliases[f"chrom_{row.namespace}"], aliases["chrom_ucsc"]))
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
        count = len(catalog) if row.universe_name == "all_rmsk" else len(records)
        assert lines - (path.suffix == ".saf") == row.rows == count, path
        if row.universe_name == "all_rmsk":
            assert level == "record" and path.suffix == ".bed" and row.distinct_features == len(catalog)
            seen = np.zeros(len(catalog), dtype=np.uint8)
            for chunk in pd.read_csv(path, sep="\t", header=None, keep_default_na=False,
                                     dtype={0: str, 1: "int64", 2: "int64", 3: str, 4: "int64", 5: str},
                                     chunksize=100_000):
                indices = catalog_index.get_indexer(chunk[3])
                assert (indices >= 0).all()
                expected = catalog.iloc[indices]
                for observed, wanted in ((chunk[0].map(to_ucsc), expected.chrom),
                                         (chunk[1], expected.start_1 - 1), (chunk[2], expected.end_1),
                                         (chunk[4], expected.sw_score.clip(upper=1000)),
                                         (chunk[5], expected.strand)):
                    shape.equal(observed, wanted, (path, "catalog BED"))
                np.add.at(seen, indices, 1)
            assert (seen == 1).all(), path
            continue
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
                        attributes["gene_id"] + "|" + chunk[0].map(to_ucsc) + ":" + chunk[3] + "-" + chunk[4] + "|" + chunk[6])
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
    print(f"registrations: interspersed={rows} all_rmsk={all_rows}; eight interspersed ID spellings; instances={instance_count}; "
          "24 inventory hashes, feature sets and GTF tuple/instance joins pass; "
          "three record grammars; count 7 stays 7 at record, subfamily and family levels")


if __name__ == "__main__":
    main()
