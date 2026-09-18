#!/usr/bin/env bash
# Exercise preflight exit codes against measured and synthetic sequence dictionaries.
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
export PYTHONDONTWRITEBYTECODE=1
python3 - "$ROOT" <<'PY'
import csv
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from tempfile import TemporaryDirectory

import pysam

root = Path(sys.argv[1])
build = Path(os.environ.get("TE_TRACKS_REFROOT", "/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot")) / "te_mm39/build"
command = root / "bin/te-tracks-preflight"
fixture = root / "tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv"
alias_table = build / "tables/contig_aliases.tsv"
if not alias_table.is_file():
    print("unsupported: run stage 35 first")
    raise SystemExit(3)
with alias_table.open() as stream:
    aliases = list(csv.DictReader(stream, delimiter="\t"))
lengths = {row[column]: int(row["length_bp"]) for row in aliases
           for column in row if column.startswith("chrom_")}
errors = []
cases = 0


def export_names(path):
    """Read the exact contig set from the export's declared format."""
    column = 1 if path.suffix == ".saf" else 0
    with path.open() as stream:
        if column:
            assert stream.readline() == "GeneID\tChr\tStart\tEnd\tStrand\n"
        return {line.split("\t", column + 1)[column] for line in stream}


def run(export, names, reference, reference_lengths, code, table=alias_table,
        exported_lengths=lengths, unreadable=False, stderr=False, error_line=None):
    """Compare exact ordered reports and exit codes with independent set arithmetic."""
    global cases
    cases += 1
    result = subprocess.run([command, export, reference], capture_output=True, text=True)
    shared = names & reference_lengths.keys()
    expected = {
        "only_in_reference": sorted(reference_lengths.keys() - names),
        "only_in_export": sorted(names - reference_lengths.keys()),
        "length_disagreements": [
            {"contig": name, "reference_length": reference_lengths[name],
             "export_length": exported_lengths[name]}
            for name in sorted(shared) if reference_lengths[name] != exported_lengths[name]],
        "alias_table": str(table.absolute()),
    }
    expected_stdout = "" if unreadable else "".join(
        f"{label}\t{json.dumps(value, separators=(',', ':'))}\n" for label, value in expected.items())
    try:
        observed = dict((label, json.loads(value)) for label, value in (
            line.split("\t", 1) for line in result.stdout.splitlines()))
    except ValueError:
        observed = result.stdout
    if (result.returncode != code or result.stdout != expected_stdout
            or observed != ({} if unreadable else expected) or (stderr and not result.stderr.strip())
            or (error_line is not None and result.stderr != f"te-tracks-preflight: {error_line}\n")):
        errors.append(f"{export} vs {reference.name}: expected exit={code}, report={expected}; "
                      f"observed exit={result.returncode}, report={observed}; stderr={result.stderr!r}")


def write_reference(path, dictionary):
    if path.suffix == ".bam":
        with pysam.AlignmentFile(str(path), "wb", header={"HD": {"VN": "1.6"},
                "SQ": [{"SN": name, "LN": length} for name, length in dictionary.items()]}):
            pass
    else:
        suffix = "\t0\t60\t61" if path.suffix == ".fai" else ""
        path.write_text("".join(f"{name}\t{length}{suffix}\n" for name, length in dictionary.items()))


fasta = {name: int(length) for name, length in (line.split() for line in fixture.read_text().splitlines())}
assert len(fasta) == 61
assert sum("_" in row["chrom_ucsc"] for row in aliases) == 39
assert sum("_" not in row["chrom_ucsc"] for row in aliases) == 22
with TemporaryDirectory(prefix="te-tracks-preflight-") as directory:
    scratch = Path(directory)
    full_index, full_bam = scratch / "reference.fai", scratch / "reference.bam"
    write_reference(full_index, fasta)
    write_reference(full_bam, fasta)
    primary_lengths = {row["chrom_ucsc"]: int(row["length_bp"]) for row in aliases
                       if re.fullmatch(r"chr([0-9]+|X|Y)", row["chrom_ucsc"])}
    assert len(primary_lengths) == 21
    primary = scratch / "primary.sizes"
    write_reference(primary, primary_lengths)
    wrong = scratch / "wrong.bam"
    write_reference(wrong, {"chr1": 1})
    for universe in ("interspersed", "all_rmsk"):
        files = ("record.bed", "record.gtf", "record_starsolo.gtf", "subfamily.saf") if universe == "interspersed" else ("record.bed",)
        expected_sizes = ({"gencode": (2, 0), "ucsc": (40, 38), "ensembl": (23, 21)}
                          if universe == "interspersed" else
                          {"gencode": (0, 0), "ucsc": (39, 39), "ensembl": (22, 22)})
        for namespace in ("gencode", "ucsc", "ensembl"):
            for filename in files:
                export = build / f"exports/{namespace}/{universe}/full/{filename}"
                names = export_names(export)
                assert len(names) == (59 if universe == "interspersed" else 61)
                assert (len(fasta.keys() - names), len(names - fasta.keys())) == expected_sizes[namespace]
                for reference in (fixture, full_index, full_bam):
                    run(export, names, reference, fasta, 0 if namespace == "gencode" else 2)
                run(export, names, primary, primary_lengths, 1 if namespace == "ensembl" else 2,
                    stderr=namespace == "ensembl")
                if namespace != "ensembl":
                    assert len(names - primary_lengths.keys()) == (38 if universe == "interspersed" else 40)
                exact_lengths = {name: lengths[name] for name in sorted(names)}
                for extension in ("sizes", "fai"):
                    exact = scratch / f"covered.{extension}"
                    write_reference(exact, exact_lengths)
                    run(export, names, exact, exact_lengths, 0)
                if namespace == "ucsc":
                    assert names & {"chr1"} == {"chr1"} and lengths["chr1"] != 1
                    run(export, names, wrong, {"chr1": 1}, 1)
    export = build / "exports/gencode/interspersed/full/record.bed"
    names = export_names(export)
    empty = scratch / "empty.sizes"
    empty.touch()
    run(export, names, empty, {}, 1, stderr=True)
    run(export, names, scratch / "missing.sizes", {}, 1, unreadable=True, stderr=True)
    run(export.with_name("missing.bed"), set(), fixture, fasta, 1, unreadable=True, stderr=True)
    linked = scratch / "linked"
    (linked / "tables").mkdir(parents=True)
    (linked / "MANIFEST.json").write_text("{}\n")
    local_aliases = linked / "tables/contig_aliases.tsv"
    local_aliases.write_bytes(alias_table.read_bytes())
    (linked / "exports").symlink_to(build / "exports", target_is_directory=True)
    run(linked / "exports/gencode/interspersed/full/record.bed", names, fixture, fasta, 0,
        table=local_aliases)
    nested = linked / "nested"
    (nested / "tables").mkdir(parents=True)
    (nested / "record.bed").symlink_to(export)
    run(nested / "record.bed", names, fixture, fasta, 0, table=local_aliases)
    (nested / "MANIFEST.json").write_text("{}\n")
    enclosing_error = "export requires an enclosing build with MANIFEST.json and tables/contig_aliases.tsv"
    run(nested / "record.bed", names, fixture, fasta, 1, unreadable=True, error_line=enclosing_error)
    nearest = nested / "tables/contig_aliases.tsv"
    changed = [{**row, "length_bp": str(int(row["length_bp"]) + (row["chrom_ucsc"] == "chr1"))}
               for row in aliases]
    with nearest.open("w") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(aliases[0]), delimiter="\t", lineterminator="\n")
        writer.writeheader()
        writer.writerows(changed)
    run(nested / "record.bed", names, fixture, fasta, 1, table=nearest,
        exported_lengths={**lengths, "chr1": lengths["chr1"] + 1})
    unbound = scratch / "unbound"
    (unbound / "tables").mkdir(parents=True)
    (unbound / "tables/contig_aliases.tsv").write_bytes(alias_table.read_bytes())
    detached = unbound / "nested/record.bed"
    detached.parent.mkdir()
    detached.write_text("chr1\t0\t1\tprobe\t0\t+\n")
    run(detached, {"chr1"}, fixture, fasta, 1, unreadable=True, error_line=enclosing_error)
    nearest.write_text("\t".join(aliases[0]) + "\nchr1\n")
    run(nested / "record.bed", names, fixture, fasta, 1, unreadable=True,
        error_line="int() argument must be a string, a bytes-like object or a real number, not 'NoneType'")
if errors:
    print("preflight contract deviations:")
    print("\n".join(errors))
    raise SystemExit(1)
print(f"{cases} preflight cases; both universes, three namespaces, BED/GTF/SAF and sizes/FAI/BAM; "
      "covered=0, export-only=2, empty/shared-length/input errors=1; exact reports and enclosing build aliases pass")
PY
