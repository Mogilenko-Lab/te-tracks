#!/usr/bin/env python3
"""Check all source aliases, measured FASTA names and complete contig coverage."""

import hashlib
from pathlib import Path
import sys

import pandas as pd

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/lib"))
from records import BUILD, require

require("tables/contig_aliases.tsv", "tables/contig_coverage.tsv")
aliases = pd.read_csv(BUILD / "tables/contig_aliases.tsv", sep="\t", keep_default_na=False)
columns = ["chrom_ucsc", "chrom_ensembl", "chrom_gencode", "chrom_genbank", "chrom_refseq", "length_bp"]
assert list(aliases) == columns and len(aliases) == 61
assert aliases.chrom_ucsc.tolist() == sorted(aliases.chrom_ucsc)
for column in columns[:-1]:
    assert aliases[column].is_unique and aliases[column].ne("").all(), column
indexed = aliases.set_index("chrom_ucsc")
assert tuple(indexed.loc["chr1_GL456210v1_random", ["chrom_ensembl", "chrom_gencode"]]) == (
    "GL456210.1", "GL456210.1")
assert tuple(indexed.loc["chrM", ["chrom_ensembl", "chrom_gencode"]]) == ("MT", "chrM")
fixture = ROOT / "tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv"
assert hashlib.sha256(fixture.read_bytes()).hexdigest() == (
    "69070f846f5407f046ece7dcf38538ba2feb271bb6df32080e7906e2e7360a62")
fasta = dict((name, int(length)) for name, length in (line.split() for line in fixture.read_text().splitlines()))
assert len(fasta) == 61
assert aliases.set_index("chrom_gencode").length_bp.to_dict() == fasta
source_sizes = dict((name, int(length)) for name, length in (
    line.split() for line in (BUILD / "source/mm39.chrom.sizes").read_text().splitlines()))
assert indexed.length_bp.to_dict() == source_sizes
source_aliases = pd.read_csv(BUILD / "source/mm39.chromAlias.txt", sep="\t").rename(columns={"# ucsc": "ucsc"})
assert set(indexed.index) == set(source_aliases.ucsc)
for column in ("ensembl", "genbank", "refseq"):
    assert indexed[f"chrom_{column}"].to_dict() == source_aliases.set_index("ucsc")[column].to_dict()
assert aliases.chrom_gencode.tolist() == [row.chrom_genbank if "_" in row.chrom_ucsc else row.chrom_ucsc
                                         for row in aliases.itertuples()]
records = pd.read_parquet(BUILD / "tables/rmsk_records.parquet", columns=["chrom", "end_1", "query_left_bp"])
assert set(records.chrom) <= set(indexed.index)
assert (records.end_1 + records.query_left_bp).eq(records.chrom.map(source_sizes)).all()
coverage = pd.read_csv(BUILD / "tables/contig_coverage.tsv", sep="\t", keep_default_na=False)
assert list(coverage) == ["chrom_ucsc", "length_bp", "records_all", "records_interspersed",
                          "has_ensembl", "has_gencode", "length_agrees"]
assert coverage.chrom_ucsc.tolist() == aliases.chrom_ucsc.tolist()
assert coverage.length_bp.tolist() == aliases.length_bp.tolist()
assert coverage[["has_ensembl", "has_gencode", "length_agrees"]].all().all()
all_counts = records.chrom.value_counts()
assert coverage.set_index("chrom_ucsc").records_all.to_dict() == {
    chrom: int(all_counts.get(chrom, 0)) for chrom in indexed.index}
interspersed = {}
for chunk in pd.read_csv(BUILD / "tables/universe_members.tsv.gz", sep="\t", dtype=str,
                         keep_default_na=False, chunksize=500_000):
    keys = chunk.loc[chunk.universe_name.eq("interspersed"), "rmsk_record_id"]
    for chrom, count in keys.str.split("|", regex=False).str[1].str.split(":").str[0].value_counts().items():
        interspersed[chrom] = interspersed.get(chrom, 0) + count
assert coverage.set_index("chrom_ucsc").records_interspersed.to_dict() == {
    chrom: interspersed.get(chrom, 0) for chrom in indexed.index}
assert set(coverage.loc[coverage.records_interspersed.eq(0), "chrom_ucsc"]) == {
    "chr4_JH584295v1_random", "chrM"}
assert coverage.records_all.ge(1).all()
assert coverage.set_index("chrom_ucsc").loc[["chr4_JH584295v1_random", "chrM"], "records_all"].to_dict() == {
    "chr4_JH584295v1_random": 2, "chrM": 4}
assert coverage.records_all.sum() == 5_320_771
assert coverage.records_interspersed.sum() == 3_764_949
print("61 injective aliases and FASTA names/lengths; catalog=5320771 interspersed=3764949; "
      "all contigs carry catalog records; chr4_JH584295v1_random and chrM carry 2 and 4 catalog records, "
      "zero interspersed records")
