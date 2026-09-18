#!/usr/bin/env python3
"""Verify every renamed payload, file order and invariant feature registration."""

from collections import Counter
import csv
import hashlib
import os
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

import pandas as pd

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import BUILD, require


FILES = ("record.bed", "subfamily.bed", "family.bed", "record.gtf", "record_starsolo.gtf", "subfamily.gtf",
         "subfamily.saf", "taxonomy_triple.saf")
NAMESPACES = ("ucsc", "ensembl", "gencode")
require("tables/contig_aliases.tsv", "tables/exports.tsv", "tables/export_feature_members.tsv.gz",
        *(f"exports/{ns}/interspersed/full/{name}" for ns in NAMESPACES for name in FILES),
        *(f"exports/{ns}/all_rmsk/full/record.bed" for ns in NAMESPACES))
aliases = pd.read_csv(BUILD / "tables/contig_aliases.tsv", sep="\t", keep_default_na=False)
with (BUILD / "tables/exports.tsv").open() as stream:
    inventory = list(csv.DictReader(stream, delimiter="\t"))
assert len(inventory) == 27
assert [row["export_path"] for row in inventory] == sorted({row["export_path"] for row in inventory})
by_path = {row["export_path"]: row for row in inventory}


SORT_KEYS = {".bed": ["-k1,1", "-k2,2n", "-k3,3n", "-k6,6", "-k4,4"],
             ".gtf": ["-k1,1", "-k4,4n", "-k5,5n", "-k7,7", "-k9,9"],
             ".saf": ["-k2,2", "-k3,3n", "-k4,4n", "-k5,5", "-k1,1"]}
ENVIRONMENT = {**os.environ, "LC_ALL": "C"}


def scan(path, expected_rows):
    """Check every row's order, complete file digest and inventory row count."""
    saf = path.suffix == ".saf"
    with path.open("rb", buffering=0) as stream:
        if saf:
            assert stream.readline() == b"GeneID\tChr\tStart\tEnd\tStrand\n", path
        order = subprocess.run(["sort", "--check", "--stable", "-t", "\t", *SORT_KEYS[path.suffix]],
                               stdin=stream, capture_output=True, env=ENVIRONMENT)
    assert order.returncode == 0, (path, "sort order", order.stderr)
    digest = hashlib.sha256()
    count = 0
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
            count += block.count(b"\n")
    count -= saf
    assert count == expected_rows, (path, count)
    entry = by_path[path.relative_to(BUILD).as_posix()]
    assert int(entry["rows"]) == count and entry["sha256"] == digest.hexdigest(), path
    return digest.hexdigest()


def regenerate(source, target, namespace):
    """Map each source contig and sort the complete renamed file independently."""
    saf = source.suffix == ".saf"
    alias_column = list(aliases).index(f"chrom_{namespace}") + 1
    program = (
        'BEGIN { FS=OFS="\\t" } '
        'NR==FNR { if (FNR>1) names[$1]=$alias_column; next } '
        'FNR==1 && saf { next } '
        '{ if (!($contig_column in names)) exit 1; '
        '$contig_column=names[$contig_column]; print }'
    )
    with target.open("wb") as outgoing:
        if saf:
            outgoing.write(b"GeneID\tChr\tStart\tEnd\tStrand\n")
            outgoing.flush()
        with subprocess.Popen(
            ["awk", "-v", f"alias_column={alias_column}", "-v", f"contig_column={2 if saf else 1}",
             "-v", f"saf={int(saf)}", program, BUILD / "tables/contig_aliases.tsv", source],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=ENVIRONMENT,
        ) as renamed:
            result = subprocess.run(
                ["sort", "--stable", "--buffer-size=512M", "--parallel=2", "-T", str(target.parent),
                 "-t", "\t", *SORT_KEYS[source.suffix]], stdin=renamed.stdout, stdout=outgoing,
                stderr=subprocess.PIPE, env=ENVIRONMENT,
            )
            renamed.stdout.close()
            error = renamed.stderr.read()
            assert renamed.wait() == 0, (source, "rename", error)
            assert result.returncode == 0, (source, "sort", result.stderr)
    with target.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


with TemporaryDirectory(prefix="te-tracks-namespaces-") as directory:
    scratch = Path(directory)
    for universe, files, count in (("interspersed", FILES, 3_764_949),
                                    ("all_rmsk", ("record.bed",), 5_320_771)):
        for filename in files:
            source = BUILD / f"exports/ucsc/{universe}/full/{filename}"
            scan(source, count)
            for namespace in ("ensembl", "gencode"):
                target = BUILD / f"exports/{namespace}/{universe}/full/{filename}"
                observed = scan(target, count)
                regenerated = scratch / filename
                expected = regenerate(source, regenerated, namespace)
                assert observed == expected, (target, "complete renamed payload")
                assert by_path[target.relative_to(BUILD).as_posix()]["sha256"] == expected
                assert by_path[target.relative_to(BUILD).as_posix()]["distinct_features"] == (
                    by_path[source.relative_to(BUILD).as_posix()]["distinct_features"])
                regenerated.unlink()
levels = Counter()
for chunk in pd.read_csv(BUILD / "tables/export_feature_members.tsv.gz", sep="\t", dtype=str,
                         keep_default_na=False, usecols=["universe_name", "feature_level", "key_grammar"],
                         chunksize=500_000):
    levels.update(chunk.value_counts().to_dict())
assert levels == Counter({
    ("interspersed", "record", "rmsk_record_id"): 3_764_949,
    ("interspersed", "record", "record_alias"): 3_764_949,
    ("interspersed", "record", "four_tuple"): 3_764_949,
    ("interspersed", "subfamily", "rmsk_name"): 3_764_949,
    ("interspersed", "subfamily", "four_tuple"): 3_764_949,
    ("interspersed", "family", "family_bucket"): 3_764_949,
    ("interspersed", "taxonomy_triple", "taxonomy_triple"): 3_764_949,
    ("interspersed", "instance", "instance_alias"): 3_764_949,
    ("all_rmsk", "record", "rmsk_record_id"): 5_320_771,
}), levels
print("27 sorted exports and SHA-256 digests; 18 complete renamed files regenerated; interspersed=3764949 all_rmsk=5320771 per namespace; registrations=30119592+5320771")
