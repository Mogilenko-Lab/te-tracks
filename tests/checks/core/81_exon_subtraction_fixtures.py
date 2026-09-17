#!/usr/bin/env python3
"""Compare production child writers with hand-authored interval and coverage answers."""

from contextlib import redirect_stdout
import gzip
import io
import json
import os
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "src/lib"))
from build_taxonomy import build_taxonomy
from build_universes import DEFINITIONS
from gene_child import CHILD_UNIVERSES, annotation_mask, build_child
from records_io import RECORD_KEY, RECORD_SCHEMA, write_tsv

if not (Path(os.environ["TE_TRACKS_REFROOT"]) / "te_mm39_gene/build").is_dir():
    print("gene child build is absent")
    raise SystemExit(3)
FIXTURE = ROOT / "tests/fixtures/gene"
SCRATCH = Path(os.environ["TE_TRACKS_REFROOT"]) / "pubtest"
SCRATCH.mkdir(parents=True, exist_ok=True)
answers = json.loads((FIXTURE / "geometry.json").read_text())
with TemporaryDirectory(prefix="geometry-", dir=SCRATCH) as temporary:
    parent, child = Path(temporary) / "parent", Path(temporary) / "child"
    for path in (parent / "tables", child / "tables", child / "source"):
        path.mkdir(parents=True)
    (parent / "universes.json").write_text(json.dumps(DEFINITIONS))
    shutil.copyfile(parent / "universes.json", child / "universes.json")
    shutil.copyfile(FIXTURE / "contig_aliases.tsv", child / "tables/contig_aliases.tsv")
    records = []
    for number, answer in enumerate(answers):
        row = {field.name: ("" if pa.types.is_string(field.type) else False
                           if pa.types.is_boolean(field.type) else 0) for field in RECORD_SCHEMA}
        row.update(rmsk_record_id=f"{answer['name']}|{answer['chrom']}:{answer['start']}-{answer['end']}|{answer['strand']}",
                   rmsk_name=answer["name"], chrom=answer["chrom"], start_1=answer["start"], end_1=answer["end"],
                   strand=answer["strand"], length_bp=100, rmsk_family="L1", rmsk_class="LINE",
                   rmsk_instance_id=str(number + 1), sw_score=100)
        records.append(row)
    frame = pd.DataFrame(records).sort_values(RECORD_KEY)
    pq.write_table(pa.Table.from_pandas(frame, schema=RECORD_SCHEMA, preserve_index=False),
                   parent / "tables/rmsk_records.parquet")
    write_tsv(frame[["rmsk_name", "rmsk_family", "rmsk_class"]].assign(
        record_count=1, instance_count=1, record_length_sum_bp=100), parent / "tables/rmsk_taxonomy.tsv")
    gtf = child / "source/fixture.gtf.gz"
    gtf.write_bytes(gzip.compress((FIXTURE / "annotation.gtf").read_bytes(), mtime=0))
    with redirect_stdout(io.StringIO()):
        build_taxonomy(parent)
        build_child(parent, child, gtf)
    assert (child / "tables/gene_annotation_coverage.tsv").read_bytes() == (FIXTURE / "coverage.tsv").read_bytes()
    status = pd.read_csv(child / "tables/exon_subtraction_status.tsv", sep="\t").set_index("rmsk_record_id")
    members = pd.read_csv(child / "tables/export_feature_members.tsv.gz", sep="\t", keep_default_na=False)
    assert not members.duplicated().any()
    assert len(members) == 96
    aliases = pd.read_csv(FIXTURE / "contig_aliases.tsv", sep="\t", dtype=str).set_index("chrom_ucsc")
    for answer, record in zip(answers, records):
        key = record["rmsk_record_id"]
        row = status.loc[key]
        assert row.tolist() == [answer["status"], len(answer["blocks"]), answer["retained"], answer["removed"]], answer
        for universe in CHILD_UNIVERSES:
            for level, grammar in (("subfamily", "rmsk_name"), ("taxonomy_triple", "taxonomy_triple")):
                feature = answer["name"] if level == "subfamily" else answer["name"] + ":L1:LINE"
                subset = members.loc[(members.rmsk_record_id == key) & (members.universe_name == universe)
                                     & (members.feature_level == level)]
                assert subset[["block_start_1", "block_end_1"]].values.tolist() == answer["blocks"]
                assert subset.emitted_feature_id.eq(feature).all() and subset.key_grammar.eq(grammar).all()
                assert subset.variant.eq("exon_subtracted").all()
    for namespace in ("ucsc", "ensembl", "gencode"):
        for universe in CHILD_UNIVERSES:
            for level in ("subfamily", "taxonomy_triple"):
                expected = []
                for answer in answers:
                    feature = answer["name"] if level == "subfamily" else answer["name"] + ":L1:LINE"
                    chrom = answer["chrom"] if namespace == "ucsc" else aliases.loc[answer["chrom"], "chrom_" + namespace]
                    expected.extend((feature, chrom, a, b, answer["strand"]) for a, b in answer["blocks"])
                expected.sort(key=lambda row: (row[1], row[2], row[3], row[4], row[0]))
                path = child / f"exports/{namespace}/{universe}/exon_subtracted/{level}.saf"
                actual = pd.read_csv(path, sep="\t")
                assert list(actual.itertuples(index=False, name=None)) == expected, path
    baseline = {path.relative_to(child): path.read_bytes() for path in child.rglob("*") if path.is_file()}
    lines = (FIXTURE / "annotation.gtf").read_text().splitlines(keepends=True)
    gtf.write_bytes(gzip.compress("".join(dict.fromkeys(lines)).encode(), mtime=0))
    with redirect_stdout(io.StringIO()):
        build_child(parent, child, gtf)
    for relative, content in baseline.items():
        if relative.parts[0] == "exports" or relative.name in ("export_feature_members.tsv.gz", "exon_subtraction_status.tsv"):
            assert (child / relative).read_bytes() == content, relative
    mask, _ = annotation_mask(gtf, child / "tables/contig_aliases.tsv")
    assert [1541, 1560] in mask["chr1"].tolist()
    for bad in (b'unknown\tfixture\texon\t1\t2\t.\t+\t.\tgene_id "x";\n',):
        gtf.write_bytes(gzip.compress(bad, mtime=0))
        try:
            build_child(parent, child, gtf)
        except ValueError as error:
            assert "unmapped GTF contig: unknown" in str(error)
        else:
            raise AssertionError("unknown GTF contig accepted")
    try:
        build_child(parent, child, gtf, universes=("all_rmsk",))
    except ValueError as error:
        assert "outside CHILD_UNIVERSES" in str(error)
    else:
        raise AssertionError("unsupported universe accepted")
print("15 geometry cases, 12 SAFs, 96 registrations, annotation coverage, duplicate invariance and named refusals pass")
