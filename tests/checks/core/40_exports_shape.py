#!/usr/bin/env python3
"""Check every exported interval and identifier against the canonical tables."""

import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import BUILD, KEY, require


DIRECTORY = "exports/ucsc/interspersed/full"
FILES = ["record.bed", "subfamily.bed", "family.bed", "record.gtf", "subfamily.gtf",
         "subfamily.saf", "taxonomy_triple.saf"]
ALPHABET = r"[A-Za-z0-9_.+?()|:/-]+"
ATTRIBUTES = ["gene_id", "transcript_id", "locus", "family_id", "class_id",
              "rmsk_family", "rmsk_class"]


def reference_records():
    """Read membership independently and attach each name's canonical labels."""
    selected = []
    for chunk in pd.read_csv(BUILD / "tables/universe_members.tsv.gz", sep="\t",
                             dtype=str, keep_default_na=False, quoting=3, chunksize=500_000):
        selected.extend(chunk.loc[chunk["universe_name"].eq("interspersed"), "rmsk_record_id"])
    assert len(selected) == len(set(selected)) == 3_764_949
    records = pd.read_parquet(BUILD / "tables/rmsk_records.parquet", columns=[
        "rmsk_record_id", *KEY, "rmsk_family", "rmsk_class", "sw_score", "rmsk_instance_id",
    ])
    records = records.loc[records["rmsk_record_id"].isin(selected)].sort_values(
        KEY, ignore_index=True)
    assert len(records) == len(selected)
    taxonomy = pd.read_csv(BUILD / "tables/taxonomy_canonical.tsv", sep="\t",
                           dtype=str, keep_default_na=False, quoting=3).set_index("rmsk_name")
    for rank in ("class", "family"):
        canonical = taxonomy[f"canonical_{rank}"].copy()
        unresolved = taxonomy[f"{rank}_status"].eq("unresolved")
        assert unresolved.equals(canonical.eq(""))
        canonical.loc[unresolved] = "unresolved_" + rank + "_" + canonical.index[unresolved]
        records[rank] = records["rmsk_name"].map(canonical)
        assert records[rank].notna().all()
    records["family_feature"] = records["class"] + "/" + records["family"]
    records["triple"] = records["rmsk_name"] + ":" + records["family"] + ":" + records["class"]
    records["alias"] = ("R|mm39|" + records["rmsk_name"] + "|" + records["chrom"] + "|"
                        + records["start_1"].astype(str) + "|" + records["end_1"].astype(str)
                        + "|" + records["strand"])
    return records


def equal(observed, expected, context):
    assert np.array_equal(np.asarray(observed), np.asarray(expected)), context


def main():
    require(*(f"{DIRECTORY}/{filename}" for filename in FILES))
    records = reference_records()
    sample = set(np.linspace(0, len(records) - 1, 1000, dtype=int))
    features = {}
    for filename in FILES:
        path = BUILD / DIRECTORY / filename
        ordered = (records.sort_values([*KEY[:-1], "family_feature"], kind="stable", ignore_index=True)
                   if filename == "family.bed" else records)
        offset = 0
        distinct = set()
        if path.suffix == ".bed":
            columns = ["chrom", "start_0", "end_1", "feature", "score", "strand"]
            integers = ["start_0", "end_1", "score"]
        elif path.suffix == ".gtf":
            columns = ["chrom", "source", "type", "start_1", "end_1", "score", "strand",
                       "frame", "attributes"]
            integers = ["start_1", "end_1", "score"]
        else:
            columns = ["feature", "chrom", "start_1", "end_1", "strand"]
            integers = ["start_1", "end_1"]
            with path.open() as stream:
                assert stream.readline() == "GeneID\tChr\tStart\tEnd\tStrand\n", filename
        for chunk in pd.read_csv(
            path, sep="\t", header=None, names=columns, quoting=3, keep_default_na=False,
            skiprows=1 if path.suffix == ".saf" else 0, chunksize=100_000,
            dtype={column: "int64" if column in integers else str for column in columns},
        ):
            expected = ordered.iloc[offset:offset + len(chunk)].reset_index(drop=True)
            chunk = chunk.reset_index(drop=True)
            for column in ("chrom", "end_1", "strand"):
                equal(chunk[column], expected[column], (filename, column, offset))
            start = "start_0" if path.suffix == ".bed" else "start_1"
            equal(chunk[start], expected["start_1"] - (path.suffix == ".bed"),
                  (filename, start, offset))
            if path.suffix == ".bed":
                equal(chunk["score"], expected["sw_score"].clip(upper=1000), filename)
                identity = {"record.bed": "rmsk_record_id", "subfamily.bed": "rmsk_name",
                            "family.bed": "family_feature"}[filename]
                equal(chunk["feature"], expected[identity], filename)
            elif path.suffix == ".saf":
                identity = "triple" if filename == "taxonomy_triple.saf" else "rmsk_name"
                equal(chunk["feature"], expected[identity], filename)
            else:
                assert chunk["source"].eq("te-tracks").all(), filename
                assert chunk["type"].eq("exon").all() and chunk["frame"].eq(".").all(), filename
                equal(chunk["score"], expected["sw_score"], filename)
                keys = ATTRIBUTES + (["instance_id", "rmsk_record_id"]
                                     if filename == "record.gtf" else [])
                pattern = " ".join(f'{key} "({ALPHABET})";' for key in keys)
                values = chunk["attributes"].str.extract("^" + pattern + "$", expand=True)
                assert values.notna().all().all(), (filename, "attribute grammar", offset)
                values.columns = keys
                identity = "alias" if filename == "record.gtf" else "rmsk_name"
                for attribute, column in (("gene_id", "rmsk_name"), ("transcript_id", identity),
                                          ("locus", identity), ("family_id", "family"),
                                          ("class_id", "class"), ("rmsk_family", "rmsk_family"),
                                          ("rmsk_class", "rmsk_class")):
                    equal(values[attribute], expected[column], (filename, attribute, offset))
                if filename == "record.gtf":
                    equal(values["rmsk_record_id"], expected["rmsk_record_id"], filename)
                    equal(values["instance_id"], "I|mm39|" + expected["rmsk_instance_id"], filename)
                else:
                    equal(values["transcript_id"], values["gene_id"], filename)
                for position in sorted(sample.intersection(range(offset, offset + len(chunk)))):
                    attributes = chunk.at[position - offset, "attributes"]
                    parsed = re.findall(r'(\w+) "([^"]*)";', attributes)
                    assert [key for key, _ in parsed] == keys, (filename, position)
                    assert " ".join(f'{key} "{value}";' for key, value in parsed) == attributes
                chunk["feature"] = values["locus"]
            assert chunk["feature"].str.fullmatch(ALPHABET).all(), filename
            if not filename.startswith("record."):
                distinct.update(chunk["feature"])
            offset += len(chunk)
        assert offset == 3_764_949, (filename, offset)
        features[filename] = len(distinct)
    assert features["subfamily.bed"] == features["subfamily.gtf"] == features["subfamily.saf"] == 1220
    assert features["taxonomy_triple.saf"] == 1220
    assert features["family.bed"] == records["family_feature"].nunique()
    print(f"seven exports: 3764949 rows each; subfamilies=1220 "
          f"families={features['family.bed']} taxonomy_triples=1220; coordinates and identifiers pass")


if __name__ == "__main__":
    main()
