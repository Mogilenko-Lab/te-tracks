#!/usr/bin/env python3
"""Measure complete subtraction conservation and independently inspect registered geometry."""

from collections import Counter
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

import numpy as np
import pandas as pd
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from build_universes import evaluate_predicate

REF = Path(os.environ["TE_TRACKS_REFROOT"])
CHILD, PARENT = REF / "te_mm39_gene/build", REF / "te_mm39/build"
if not CHILD.is_dir():
    print("gene child build is absent")
    raise SystemExit(3)
assert (CHILD / "tables/exon_subtraction_summary.tsv").read_bytes() == (
    ROOT / "tests/expectations/mm39/exon_subtraction_summary.tsv").read_bytes(), "exon_subtraction_summary census differs"
records = pq.read_table(PARENT / "tables/rmsk_records.parquet", columns=[
    "rmsk_record_id", "chrom", "start_1", "end_1", "strand", "length_bp", "rmsk_class", "rmsk_family",
]).to_pandas()
ids = pd.Index(records.rmsk_record_id)
assert ids.is_unique and len(records) == 5_320_771
statuses = pd.read_csv(CHILD / "tables/exon_subtraction_status.tsv", sep="\t")
assert statuses.rmsk_record_id.equals(records.rmsk_record_id)
assert (statuses.retained_bp + statuses.removed_bp).equals(records.length_bp)
assert (statuses[["n_blocks", "retained_bp", "removed_bp"]] >= 0).all().all()
expected_status = np.where(statuses.n_blocks == 0, "fully_subtracted", np.where(statuses.removed_bp == 0,
                  "unchanged", np.where(statuses.n_blocks > 1, "split", "trimmed")))
assert (statuses.status == expected_status).all()
assert statuses.retained_bp.eq(0).equals(statuses.n_blocks.eq(0))
identity = json.loads((CHILD / "MANIFEST.json").read_text())["identity"]
gtf = CHILD / "source" / identity["gene_annotation"]["url"].rsplit("/", 1)[1]
aliases = pd.read_csv(CHILD / "tables/contig_aliases.tsv", sep="\t", dtype=str, keep_default_na=False)
gtf_chroms = dict(zip(aliases.chrom_gencode, aliases.chrom_ucsc))
gtf_lengths = dict(zip(aliases.chrom_ucsc, aliases.length_bp.astype(int)))
annotation_counts = {chrom: Counter() for chrom in aliases.chrom_ucsc}
exons = {chrom: [] for chrom in aliases.chrom_ucsc}
annotated = set()
with gzip.open(gtf, "rt") as stream:
    for line in stream:
        if line.startswith("#"):
            continue
        fields = line.rstrip("\n").split("\t")
        assert len(fields) == 9 and fields[0] in gtf_chroms
        chrom = gtf_chroms[fields[0]]
        start, end = int(fields[3]), int(fields[4])
        assert 1 <= start <= end <= gtf_lengths[chrom]
        annotated.add(chrom)
        annotation_counts[chrom][fields[2]] += 1
        if fields[2] == "exon":
            exons[chrom].append((start, end))
mask, coverage_rows = {}, []
for chrom in sorted(exons):
    merged = []
    left, right = None, None
    for start, end in sorted(exons.pop(chrom)):
        if left is None:
            left, right = start, end
        elif start > right + 1:
            merged.append((left, right))
            left, right = start, end
        elif end > right:
            right = end
    if left is not None:
        merged.append((left, right))
    mask[chrom] = np.array(merged, dtype=np.int64).reshape(-1, 2)
    coverage_rows.append([chrom, *(annotation_counts[chrom][kind] for kind in ("gene", "transcript", "exon")),
                          sum(end - start + 1 for start, end in merged), chrom in annotated])
expected_coverage = pd.DataFrame(coverage_rows, columns=[
    "chrom_ucsc", "gene_rows", "transcript_rows", "exon_rows", "exon_union_bp", "annotated"])
coverage = pd.read_csv(CHILD / "tables/gene_annotation_coverage.tsv", sep="\t")
assert coverage.equals(expected_coverage)
assert coverage.annotated.sum() == 38 and (~coverage.annotated).sum() == 23
assert coverage[["gene_rows", "transcript_rows", "exon_rows", "exon_union_bp"]].sum().tolist() == [78317,278369,1298921,160549642]
unannotated = set(coverage.loc[~coverage.annotated, "chrom_ucsc"])
assert records.chrom.isin(unannotated).sum() == 2638
predicates = {row["name"]: row["predicate"] for row in identity["universes"]["universes"]}
universes = identity["child_universes"]
selected = {universe: evaluate_predicate(records, predicates[universe]).to_numpy() for universe in universes}
eligible = np.flatnonzero(np.logical_or.reduce(list(selected.values())))
sampled = np.zeros(len(records), dtype=bool)
sampled[eligible[np.linspace(0, len(eligible) - 1, 200_000, dtype=np.int64)]] = True
assert sampled.sum() == 200_000
starts, ends = records.start_1.to_numpy(), records.end_1.to_numpy()
chroms = records.chrom.to_numpy()
strands = records.strand.to_numpy()
counts = {u: np.zeros(len(records), dtype=np.int32) for u in universes}
lengths = {u: np.zeros(len(records), dtype=np.int64) for u in universes}
last = {(u, level): (-1, 0) for u in universes for level in ("subfamily", "taxonomy_triple")}
groups, names = Counter(), {key: set() for key in last}
row_digests = Counter()
digest_modulus = 1 << 128
for chunk in pd.read_csv(CHILD / "tables/export_feature_members.tsv.gz", sep="\t", keep_default_na=False,
                         quoting=3, chunksize=200_000):
    assert chunk.variant.eq("exon_subtracted").all()
    assert not chunk.duplicated().any()
    for (universe, level), group in chunk.groupby(["universe_name", "feature_level"], sort=False):
        assert (universe, level) in last
        grammar = "rmsk_name" if level == "subfamily" else "taxonomy_triple"
        assert group.key_grammar.eq(grammar).all()
        positions = ids.get_indexer(group.rmsk_record_id)
        assert (positions >= 0).all() and selected[universe][positions].all()
        left, right = group.block_start_1.to_numpy(), group.block_end_1.to_numpy()
        assert ((left >= starts[positions]) & (right <= ends[positions]) & (left <= right)).all()
        previous_position, previous_end = last[(universe, level)]
        p = np.r_[previous_position, positions[:-1]]
        e = np.r_[previous_end, right[:-1]]
        assert (positions >= p).all() and ((positions != p) | (left > e)).all(), "block order or disjointness differs"
        last[(universe, level)] = (positions[-1], right[-1])
        if level == "subfamily":
            np.add.at(counts[universe], positions, 1)
            np.add.at(lengths[universe], positions, right - left + 1)
        groups[(universe, level)] += len(group)
        names[(universe, level)].update(group.emitted_feature_id.unique())
        for feature, chrom, start, end, strand in zip(group.emitted_feature_id, chroms[positions],
                                                     left, right, strands[positions]):
            payload = f"{feature}\t{chrom}\t{start}\t{end}\t{strand}".encode()
            row_digests[(universe, level)] += int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(), "big")
        row_digests[(universe, level)] %= digest_modulus
        sample = sampled[positions]
        for chrom in np.unique(chroms[positions[sample]]):
            use = sample & (chroms[positions] == chrom)
            intervals = mask[chrom]
            if len(intervals):
                lo = np.searchsorted(intervals[:, 1], left[use])
                hi = np.searchsorted(intervals[:, 0], right[use], side="right")
                assert (lo == hi).all(), "residual exon overlap"
for universe in universes:
    assert (counts[universe][selected[universe]] == statuses.n_blocks.to_numpy()[selected[universe]]).all()
    assert (lengths[universe][selected[universe]] == statuses.retained_bp.to_numpy()[selected[universe]]).all()
assert groups == {("interspersed", "subfamily"):3684934, ("interspersed", "taxonomy_triple"):3684934,
                  ("compat_tetranscripts_mm39", "subfamily"):3717740,
                  ("compat_tetranscripts_mm39", "taxonomy_triple"):3717740}
exports = pd.read_csv(CHILD / "tables/exports.tsv", sep="\t")
assert len(exports) == 12
for row in exports.itertuples():
    chrom_ucsc = {source.encode(): target.encode() for source, target in
                 zip(aliases["chrom_" + row.namespace], aliases.chrom_ucsc)}
    with (CHILD / row.export_path).open("rb") as stream:
        assert stream.readline() == b"GeneID\tChr\tStart\tEnd\tStrand\n"
        count, digest, distinct, previous = 0, 0, set(), None
        for line in stream:
            fields = line.rstrip(b"\n").split(b"\t")
            assert len(fields) == 5, row.export_path
            feature, chrom, start, end, strand = fields
            order = (chrom, int(start), int(end), strand, feature)
            assert previous is None or previous <= order, "SAF order differs: " + row.export_path
            previous = order
            payload = b"\t".join((feature, chrom_ucsc[chrom], start, end, strand))
            digest = (digest + int.from_bytes(hashlib.blake2b(payload, digest_size=16).digest(), "big")) % digest_modulus
            count += 1
            distinct.add(feature.decode())
    assert count == row.rows == groups[(row.universe_name, row.feature_level)]
    assert digest == row_digests[(row.universe_name, row.feature_level)], "SAF rows differ from registration: " + row.export_path
    assert distinct == names[(row.universe_name, row.feature_level)] and len(distinct) == row.distinct_features
print("5320771 records conserve bases; registered blocks ordered, disjoint and contained; 200000-record sample exon-disjoint; "
      "summary census, 14805348 registrations, 12 SAF row multisets and sort orders, independent GTF coverage 38/61 "
      "with 2638 unannotated records pass")
