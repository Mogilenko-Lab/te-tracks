"""Compare published geometry with bedtools and the packaged legacy annotation."""

from collections import Counter
from contextlib import ExitStack
import csv
import gzip
import json
from pathlib import Path
import shutil
import subprocess

from .common import EXPECT, digest, rows, scratch


def gene_child_oracle(core, child):
    bedtools = shutil.which("bedtools")
    if bedtools is None:
        print("unsupported: bedtools is absent; install it in the qualification image")
        raise SystemExit(3)
    contigs = ("chr18", "chr19", "chr1_MU069434v1_random")
    aliases = {r["chrom_gencode"]: r["chrom_ucsc"] for r in rows(child / "tables/contig_aliases.tsv")}
    identity = json.loads((child / "MANIFEST.json").read_text())["identity"]
    gtf = child / "source" / identity["gene_annotation"]["url"].rsplit("/", 1)[-1]
    measured = {chrom: Counter() for chrom in contigs}
    expected_blocks = {chrom: Counter() for chrom in contigs}
    observed_blocks = {chrom: Counter() for chrom in contigs}
    with scratch("bedtools-oracle-") as temporary, ExitStack() as stack:
        exon_files = {chrom: stack.enter_context((temporary / (chrom + ".exons.bed")).open("w")) for chrom in contigs}
        record_files = {chrom: stack.enter_context((temporary / (chrom + ".records.bed")).open("w")) for chrom in contigs}
        with gzip.open(gtf, "rt") as stream:
            for line in stream:
                if line.startswith("#"):
                    continue
                fields = line.rstrip("\n").split("\t")
                chrom = aliases[fields[0]]
                if chrom in measured:
                    measured[chrom]["annotation_rows"] += 1
                    if fields[2] == "exon":
                        measured[chrom]["exon_rows"] += 1
                        exon_files[chrom].write(f"{chrom}\t{int(fields[3]) - 1}\t{fields[4]}\n")
        with (core / "exports/ucsc/interspersed/full/record.bed").open() as stream:
            for line in stream:
                fields = line.rstrip("\n").split("\t")
                chrom = fields[0]
                if chrom in measured:
                    measured[chrom]["input_records"] += 1
                    fields[3] = fields[3].split("|", 1)[0]
                    record_files[chrom].write("\t".join(fields) + "\n")
        for stream in [*exon_files.values(), *record_files.values()]:
            stream.close()
        for chrom in contigs:
            assert measured[chrom]["input_records"] > 0, (chrom, "record-bearing contig required")
            sorted_exons = temporary / (chrom + ".sorted.bed")
            union = temporary / (chrom + ".union.bed")
            blocks = temporary / (chrom + ".blocks.bed")
            with sorted_exons.open("w") as outgoing:
                subprocess.run(["sort", "-k1,1", "-k2,2n", "-k3,3n", "-T", str(temporary),
                                str(temporary / (chrom + ".exons.bed"))], stdout=outgoing, check=True)
            with union.open("w") as outgoing:
                subprocess.run([bedtools, "merge", "-i", str(sorted_exons)], stdout=outgoing, check=True)
            with union.open() as stream:
                for line in stream:
                    fields = line.split()
                    measured[chrom]["union_intervals"] += 1
                    measured[chrom]["union_bp"] += int(fields[2]) - int(fields[1])
            with blocks.open("w") as outgoing:
                subprocess.run([bedtools, "subtract", "-a", str(temporary / (chrom + ".records.bed")),
                                "-b", str(union)], stdout=outgoing, check=True)
            with blocks.open() as stream:
                for line in stream:
                    _, start, end, name, _, strand = line.rstrip("\n").split("\t")
                    expected_blocks[chrom][int(start), int(end), strand, name] += 1
                    measured[chrom]["blocks"] += 1
                    measured[chrom]["retained_bp"] += int(end) - int(start)
        with (child / "exports/ucsc/interspersed/exon_subtracted/subfamily.saf").open() as stream:
            for row in csv.DictReader(stream, delimiter="\t"):
                if row["Chr"] in observed_blocks:
                    observed_blocks[row["Chr"]][int(row["Start"]) - 1, int(row["End"]), row["Strand"], row["GeneID"]] += 1
        for chrom in contigs:
            missing = expected_blocks[chrom] - observed_blocks[chrom]
            extra = observed_blocks[chrom] - expected_blocks[chrom]
            assert not missing and not extra, (chrom, "bedtools/SAF multiset differs", list(missing.items())[:10], list(extra.items())[:10])
        assert measured[contigs[2]]["annotation_rows"] == 0, "oracle contig requires absent annotation"
        for row in rows(EXPECT / "gene_oracle.tsv"):
            assert measured[row["contig"]][row["metric"]] == int(row["value"]), (row, measured[row["contig"]])
    print("bedtools merge/subtract multiset equality; " + "; ".join(
        chrom + " " + ",".join(f"{key}={measured[chrom][key]}" for key in
                                ("input_records", "exon_rows", "union_intervals", "union_bp", "blocks", "retained_bp"))
        for chrom in contigs))


def legacy_reconciliation(core, child):
    legacy = Path("/data2/users/shared/refcache/mm39/mm39_20260911/GRCm39_Ensembl_rmsk_TE.gtf.gz")
    if not legacy.is_file():
        print(f"unsupported: packaged legacy GTF absent: {legacy}")
        raise SystemExit(3)
    assert digest(legacy, "md5") == "1d6770be131fc1b47402a633f4401cbd", f"legacy md5 differs: {legacy}"
    aliases = rows(core / "tables/contig_aliases.tsv")
    mapping = {row[column]: row["chrom_ucsc"] for row in aliases for column in
               ("chrom_ucsc", "chrom_ensembl", "chrom_gencode", "chrom_genbank", "chrom_refseq")}
    counts = Counter()
    with scratch("legacy-oracle-") as temporary:
        members_path, legacy_path = temporary / "members.tsv", temporary / "legacy.tsv"
        with gzip.open(core / "tables/universe_members.tsv.gz", "rt") as incoming, members_path.open("w") as outgoing:
            for row in csv.DictReader(incoming, delimiter="\t"):
                if row["universe_name"] == "compat_tetranscripts_mm39":
                    _, location, strand = row["rmsk_record_id"].split("|")
                    chrom, interval = location.split(":")
                    start, end = interval.split("-")
                    outgoing.write(f"{chrom}\t{start}\t{end}\t{strand}\n")
                    counts["membership"] += 1
        with gzip.open(legacy, "rt") as incoming, legacy_path.open("w") as outgoing:
            for line in incoming:
                if not line.strip() or line.startswith("#"):
                    continue
                fields = line.rstrip("\n").split("\t")
                assert len(fields) == 9 and fields[0] in mapping, fields[:1]
                outgoing.write(f"{mapping[fields[0]]}\t{int(fields[3])}\t{int(fields[4])}\t{fields[6]}\n")
                counts["legacy"] += 1
        sorted_paths = []
        for path in (members_path, legacy_path):
            target = path.with_suffix(".sorted.tsv")
            with target.open("w") as outgoing:
                subprocess.run(["sort", "--buffer-size=256M", "-T", str(temporary), str(path)], stdout=outgoing, check=True)
            sorted_paths.append(target)
        differences, samples = Counter(), {"compat_only": [], "legacy_only": []}
        with sorted_paths[0].open() as left, sorted_paths[1].open() as right:
            a, b = next(left, None), next(right, None)
            while a is not None or b is not None:
                if a == b:
                    a, b = next(left, None), next(right, None)
                    continue
                side = "compat_only" if b is None or (a is not None and a < b) else "legacy_only"
                value = a if side == "compat_only" else b
                differences[side] += 1
                if len(samples[side]) < 20:
                    samples[side].append(value.rstrip("\n"))
                if side == "compat_only":
                    a = next(left, None)
                else:
                    b = next(right, None)
        report = (f"legacy md5=1d6770be131fc1b47402a633f4401cbd; compat membership={counts['membership']} "
                  f"packaged GTF={counts['legacy']}; interval multiset difference compat_only={differences['compat_only']} "
                  f"legacy_only={differences['legacy_only']}")
        print(report)
        if differences:
            print("interval difference examples: " + json.dumps(samples, sort_keys=True))
        assert counts["membership"] == counts["legacy"] == 3799629 and not differences, report
