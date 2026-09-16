#!/usr/bin/env python3
"""Exercise isolated MATES functions with a resource_filename-only pkg_resources stand-in."""

import ast
from contextlib import chdir
import os
from pathlib import Path
import pickle
import shutil
import sys
from types import ModuleType
from unittest.mock import patch

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "lib"))
from consumers import (CHECKOUTS, FIXTURES, build_fixture, checkout_version,
                       execute_source_nodes, run_check, source_tree)


def load_functions(relative, names, namespace):
    """Execute the selected upstream functions with explicit dependencies."""
    source, tree = source_tree("MATES", relative)
    nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name in names]
    assert {node.name for node in nodes} == set(names), (relative, names)
    execute_source_nodes(source, nodes, namespace)


def resource_filename(package, relative):
    """Resolve package resources inside the read-only MATES checkout."""
    assert package == "MATES"
    root = CHECKOUTS / "MATES/MATES"
    path = (root / relative).resolve()
    assert path.is_relative_to(root.resolve())
    return str(path)


def check():
    build_fixture()
    import pandas as pd

    namespace = {"os": os, "pd": pd, "pickle": pickle, "Path": Path}
    resources = ModuleType("pkg_resources")
    resources.resource_filename = resource_filename
    source, tree = source_tree("MATES", "MATES/bam_processor.py")
    imports = [node for node in tree.body if isinstance(node, ast.Import)
               and any(alias.name == "pkg_resources" for alias in node.names)]
    assert len(imports) == 1
    with patch.dict(sys.modules, {"pkg_resources": resources}):
        execute_source_nodes(source, imports, namespace)
    load_functions("MATES/scripts/helper_function.py",
                   ("check_file_exists", "create_directory", "read_file_lines"), namespace)
    load_functions("MATES/bam_processor.py", ("split_count_10X_data",), namespace)
    load_functions("MATES/scripts/calculate_MU.py", ("calculate_MU",), namespace)
    csv_rows = pd.read_csv(FIXTURES / "record_mates.csv", header=None)
    bed_rows = pd.read_csv(FIXTURES / "record_mates.bed", sep="\t", header=None)
    pd.testing.assert_frame_equal(csv_rows, bed_rows)
    assert csv_rows.shape == (11, 8)
    assert list(csv_rows[4]) == list(range(11)) and csv_rows[3].nunique() == 8
    assert (csv_rows[7] == csv_rows[2] - csv_rows[1]).all()
    scratch = FIXTURES.parent / "consumers_scratch/mates"
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True, exist_ok=True)
    try:
        with chdir(scratch):
            exercise(namespace, csv_rows, pd, scratch)
    finally:
        shutil.rmtree(scratch)
    return "eight-column pair; underscore stem; ?/Unknown model groups dropped"


def exercise(namespace, csv_rows, pd, scratch):
    """Keep adapter inputs and outputs within its disposable working directory."""
    for suffix in ("csv", "bed"):
        shutil.copyfile(FIXTURES / f"record_mates.{suffix}", f"record_mates.{suffix}")
    for filename in ("samples.txt", "bam_paths.txt", "barcodes_paths.txt"):
        Path(filename).write_text("")
    namespace["split_count_10X_data"]("inclusive", "samples.txt", "bam_paths.txt",
                                      "barcodes_paths.txt", ref_path="record_mates.csv")
    Path("record.mates.csv").write_bytes(Path("record_mates.csv").read_bytes())
    Path("record.mates.bed").write_bytes(Path("record_mates.bed").read_bytes())
    try:
        namespace["split_count_10X_data"]("inclusive", "samples.txt", "bam_paths.txt",
                                          "barcodes_paths.txt", ref_path="record.mates.csv")
    except FileNotFoundError as error:
        assert str(scratch / "record.bed") in str(error), error
    else:
        raise AssertionError("MATES accepted a dotted stem with only its same-stem companion")
    Path("barcodes.txt").write_text("cell\n")
    stats = Path("MU_Stats/fixture")
    stats.mkdir(parents=True, exist_ok=True)
    vectors = {name: {"cell": [0, 1, 2]} for name in ("L1", "hAT?", "?", "Unknown")}

    def coverage(sample, reference, barcodes, bin_size, proportion):
        assert list(reference.columns) == ["chromosome", "start", "end", "TE_Name",
                                           "index", "strand", "TE_fam", "length"]
        pd.testing.assert_frame_equal(reference.reset_index(drop=True).set_axis(range(8), axis=1), csv_rows)
        assert barcodes == ["cell"]
        return vectors, 4, 4

    namespace["calculate_M_U_10X"] = coverage
    namespace["calculate_MU"]("10X", "fixture", 10, 80, "record_mates.csv",
                              cut_off=0, barcodes_file="barcodes.txt")
    with (stats / "M&U_10_80%.pkl").open("rb") as handle:
        selected = pickle.load(handle)
    assert selected == {"cell": {"L1": [0, 1, 2]}}, selected
    counts = pd.read_csv(stats / "10_80_stat.csv", index_col=0)
    assert list(counts.index) == ["L1"]


run_check("MATES", lambda: f"{checkout_version('MATES')} checkout adapter", check)
