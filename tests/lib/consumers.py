"""Build deterministic consumer inputs and exercise local parser and executable contracts."""

import ast
from contextlib import contextmanager, redirect_stderr, redirect_stdout
import csv
import gzip
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import random
import re
import shutil
import shlex
import subprocess
import sys
import traceback

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
CHECKOUTS = ROOT.parent / ".ref"
CHECKOUT_PINS = {
    "irescue": ("https://github.com/bodegalab/irescue.git",
                 "26f36fb391bb031a156ae8f0a77f31c125bfbe15"),
    "stellarscope": ("https://github.com/nixonlab/stellarscope.git",
                 "0e0d594047212afe81e3754732119975a0d2aa6f"),
    "TEsingle": ("https://github.com/mhammell-laboratory/TEsingle.git",
                 "655f1274de0fe5f3241219afc2ecb1c2e0830ae9"),
    "TEtranscripts": ("https://github.com/mhammell-laboratory/TEtranscripts.git",
                 "e7f9b93f8c351b1b582cf0882aed49ffd1f0d1e9"),
    "TElocal": ("https://github.com/mhammell-laboratory/TElocal.git",
                 "1a168c299714fc55df7dd93359f553759b95c810"),
    "MATES": ("https://github.com/mcgilldinglab/MATES.git",
                 "87c1218603a26fc9cfa8ab36ef6f730d72d127af"),
}
FIXTURES = Path(os.environ.get("TE_TRACKS_CONSUMER_FIXTURES", str(Path(os.environ.get(
    "TE_TRACKS_REFROOT", "/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot"
)).resolve() / "fixtures/consumers")))
EXPECTED = json.loads((ROOT / "tests/fixtures/consumers/expected.json").read_text())
TOOLS = ("irescue", "featureCounts", "stellarscope", "TEsingle", "TEcount", "TElocal",
         "bedtools", "samtools", "STAR", "cellranger")
CONTIGS = {"chrA": 5000, "chrB": 3000}
CELL = "ACGTACGTACGTACGT-1"
ROSTER = [
    ("chrA", 1001, 1200, "+", "SubA", "LINE/L1", "1"),
    ("chrA", 2001, 2200, "-", "SubA", "LINE/L1", "2"),
    ("chrA", 3001, 3100, "+", "SubB", "LTR/ERV1", "7"),
    ("chrA", 3201, 3400, "+", "SubB-int", "LTR/ERV1", "7"),
    ("chrA", 3601, 3700, "+", "NoFam", "DNA", "8"),
    ("chrA", 3801, 3900, "+", "TwoLab", "DNA/hAT-Tip100", "9"),
    ("chrA", 4001, 4100, "-", "TwoLab", "DNA/hAT-Tip100", "10"),
    ("chrA", 4201, 4300, "+", "TwoLab", "DNA/hAT-Blackjack", "11"),
    ("chrB", 101, 110, "+", "Edge", "DNA/hAT", "12"),
    ("chrB", 1501, 1600, "+", "DupX", "LINE/L1", "13"),
    ("chrB", 1501, 1600, "+", "DupY", "LINE/L1", "14"),
]


class Unsupported(Exception):
    """Identify a missing runtime capability or a recognized consumer defect."""


def discover(tool):
    """Capture executable discovery and version diagnostics without changing installations."""
    path = shutil.which(tool)
    result = {"tool": tool, "path": path, "version": "absent"}
    if path:
        try:
            probe = subprocess.run([path, "--version"], capture_output=True, text=True,
                                   errors="replace", timeout=10)
            result.update(version_stdout=probe.stdout, version_stderr=probe.stderr,
                          version_exit=probe.returncode)
            lines = (probe.stdout + probe.stderr).strip().splitlines()
            if tool == "featureCounts" and probe.returncode:
                fallback = subprocess.run([path, "-v"], capture_output=True, text=True,
                                          errors="replace", timeout=10)
                lines = (fallback.stdout + fallback.stderr).strip().splitlines()
                result["fallback_version"] = lines
            result["version"] = next((line.strip() for line in lines if line.strip()),
                                     "version unavailable")
        except (OSError, subprocess.TimeoutExpired) as error:
            result["version"] = f"version unavailable ({error})"
    return result


def checkout_directory(checkout):
    """Require a pinned source clone and name its restoration command."""
    directory = CHECKOUTS / checkout
    if not directory.is_dir():
        url, commit = CHECKOUT_PINS[checkout]
        target = shlex.quote(str(directory))
        raise Unsupported(f"{checkout} checkout absent: {directory}; restore with "
                          f"git clone {url} {target} && git -C {target} checkout --detach {commit} "
                          "(setup requires network; docs/RUNBOOK.md#consumer-parser-sources)")
    return directory


def checkout_import(checkout, module, subpackage=None):
    """Import checkout code, optionally rooting imports at an isolated subpackage."""
    directory = checkout_directory(checkout)
    if subpackage:
        package_dir = directory.joinpath(*subpackage.split("."))
        private = "_te_tracks_" + subpackage.replace(".", "_")
        if private not in sys.modules:
            spec = importlib.util.spec_from_file_location(
                private, package_dir / "__init__.py",
                submodule_search_locations=[str(package_dir)])
            package = importlib.util.module_from_spec(spec)
            sys.modules[private] = package
            spec.loader.exec_module(package)
        loaded = importlib.import_module(f"{private}.{module}")
    else:
        sys.path.insert(0, str(directory))
        loaded = importlib.import_module(module)
    assert Path(loaded.__file__).resolve().is_relative_to(directory.resolve()), loaded.__file__
    return loaded


def checkout_version(checkout):
    """Read the declared parser version and checkout description without executing setup code."""
    directory = checkout_directory(checkout)
    description = command(["git", "-C", directory,
                           "describe", "--tags", "--always"]).strip()
    if checkout == "stellarscope":
        values = [command(["git", "-C", directory,
                           "describe", "--tags", "--abbrev=0"]).strip()]
    elif checkout == "irescue":
        _, tree = source_tree(checkout, "irescue/_version.py")
        values = [ast.literal_eval(node.value) for node in tree.body
                  if isinstance(node, ast.Assign)
                  and any(isinstance(target, ast.Name) and target.id == "__version__"
                          for target in node.targets)]
    else:
        _, tree = source_tree(checkout, "setup.py")
        values = [ast.literal_eval(keyword.value) for node in ast.walk(tree)
                  if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                  and node.func.id == "setup" for keyword in node.keywords
                  if keyword.arg == "version"]
    assert len(values) == 1 and isinstance(values[0], str), (checkout, values)
    return f"{values[0]} ({description})"


def absent_external_module(error):
    """Recognize absent external top-level modules while preserving internal import failures."""
    if not isinstance(error, ModuleNotFoundError) or not error.name:
        return None
    name = error.name.split(".")[0]
    roots = [ROOT, ROOT / "src/lib", ROOT / "tests/lib", *(CHECKOUTS / checkout for checkout in CHECKOUT_PINS)]
    if any((root / name).exists() or (root / f"{name}.py").exists() for root in roots):
        return None
    if name in sys.modules or importlib.util.find_spec(name) is not None:
        return None
    return name


def run_check(tool, version, check):
    """Print the runner's support line before captured parser diagnostics."""
    output, errors = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(output), redirect_stderr(errors):
            version = version() if callable(version) else version
            summary = check()
    except Unsupported as error:
        provenance = f"; {tool} {version}" if isinstance(version, str) else ""
        print(f"unsupported: {error}{provenance}")
        raise SystemExit(3)
    except BaseException as error:
        missing = absent_external_module(error)
        if missing:
            provenance = f"; {version}" if isinstance(version, str) else ""
            print(f"unsupported: {tool} python module {missing} absent{provenance}")
            raise SystemExit(3)
        print(f"failed {tool}: {error}")
        print(output.getvalue(), end="")
        print(errors.getvalue(), end="", file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)
    print(f"supported {tool} {version}" + (f"; {summary}" if summary else ""))
    print(output.getvalue(), end="")


def record_key(row):
    chrom, start, end, strand, name = row[:5]
    return f"{name}|{chrom}:{start}-{end}|{strand}"


def record_alias(row):
    chrom, start, end, strand, name = row[:5]
    return f"R|mm39|{name}|{chrom}|{start}|{end}|{strand}"


def expected_tuples(level):
    """Derive identity expectations from the authored roster and canonical rank oracle."""
    return {f"{record_alias(row) if level == 'record' else row[4]}:{row[4]}:"
            + ":".join(EXPECTED["taxonomy"][row[4]]) for row in ROSTER}


def assert_registered(keys, level, grammar):
    """Join the reader's complete feature set to exact roster records and full blocks."""
    expected = {}
    for row in ROSTER:
        name = row[4]
        family, cls = EXPECTED["taxonomy"][name]
        triple = f"{name}:{family}:{cls}"
        feature = {
            ("record", "rmsk_record_id"): record_key(row),
            ("record", "record_alias"): record_alias(row),
            ("record", "four_tuple"): f"{record_alias(row)}:{triple}",
            ("subfamily", "rmsk_name"): name,
            ("subfamily", "four_tuple"): f"{name}:{triple}",
            ("family", "family_bucket"): f"{cls}/{family}",
            ("taxonomy_triple", "taxonomy_triple"): triple,
            ("instance", "instance_alias"): f"I|mm39|{row[6]}",
        }[level, grammar]
        expected.setdefault(feature, []).append((record_key(row), row[1], row[2]))
    keys = set(keys)
    assert keys == set(expected), (level, grammar, keys, set(expected))
    joined = {key: [] for key in keys}
    with gzip.open(FIXTURES / "tables/export_feature_members.tsv.gz", "rt") as handle:
        for row in csv.DictReader(handle, delimiter="\t"):
            if (row["universe_name"], row["variant"], row["feature_level"], row["key_grammar"]) == (
                "interspersed", "full", level, grammar,
            ) and row["emitted_feature_id"] in keys:
                joined[row["emitted_feature_id"]].append((
                    row["rmsk_record_id"], int(row["block_start_1"]), int(row["block_end_1"])))
    assert {key: sorted(rows) for key, rows in joined.items()} == {
        key: sorted(rows) for key, rows in expected.items()
    }, (level, grammar, joined, expected)
    return {key: {row[0] for row in rows} for key, rows in joined.items()}


@contextmanager
def gzip_text(path):
    """Write UTF-8 gzip text with stable timestamp and filename headers."""
    with path.open("wb") as raw:
        with gzip.GzipFile(fileobj=raw, mode="wb", filename="", mtime=0) as compressed:
            with io.TextIOWrapper(compressed, encoding="utf-8", newline="\n") as handle:
                yield handle


def source_tree(checkout, relative):
    path = checkout_directory(checkout) / relative
    return path, ast.parse(path.read_text())


def execute_source_nodes(path, nodes, namespace):
    """Execute selected upstream statements in an explicit fixture namespace."""
    tree = ast.fix_missing_locations(ast.Module(body=nodes, type_ignores=[]))
    exec(compile(tree, str(path), "exec"), namespace)


def write_mates_pair(records, directory):
    """Write the optional eight-column MATES reference pair with stable numeric identities."""
    rows = [(r.chrom, r.start_1 - 1, r.end_1, r.rmsk_name, index, r.strand,
             r.rmsk_class_family, r.length_bp) for index, r in enumerate(records.itertuples())]
    for suffix, delimiter in (("csv", ","), ("bed", "\t")):
        with (directory / f"record_mates.{suffix}").open("w", newline="") as handle:
            csv.writer(handle, delimiter=delimiter, lineterminator="\n").writerows(rows)


def umi_sequences(count):
    """Keep synthetic molecule UMIs beyond the consumer's edit-distance correction radius."""
    rng = random.Random(271828)
    values = []
    while len(values) < count:
        candidate = "".join(rng.choices("ACGT", k=12))
        if len(set(candidate)) > 1 and all(
            sum(a != b for a, b in zip(candidate, other)) >= 4 for other in values
        ):
            values.append(candidate)
    return values


def molecule(name, umi, sites, copies=1, raw_copies=(), reverse=False, flag=0):
    return {"name": name, "umi": umi, "sites": sites, "copies": copies,
            "raw_copies": list(raw_copies), "reverse": reverse, "flag": flag}


def raw_umi(mol, copy):
    """Represent a one-base sequencing error on designated molecule copies."""
    umi = mol["umi"]
    return ("ACGT"[("ACGT".index(umi[0]) + 1) % 4] + umi[1:]
            if copy in mol["raw_copies"] else umi)


def write_bam(path, molecules, sequences, paired=False, tagged=True):
    """Write coordinate-sorted alignments with explicit molecule, copy, mate and NH accounting."""
    import pysam

    header = {"HD": {"VN": "1.6", "SO": "coordinate"},
              "SQ": [{"SN": name, "LN": length} for name, length in CONTIGS.items()]}
    unsorted = path.with_suffix(".unsorted.bam")
    with pysam.AlignmentFile(unsorted, "wb", header=header) as handle:
        for mol in molecules:
            for copy in range(mol["copies"]):
                for hit, (chrom, start, length) in enumerate(mol["sites"]):
                    for mate in range(2 if paired else 1):
                        read = pysam.AlignedSegment(handle.header)
                        read.query_name = f"{mol['name']}_copy{copy}"
                        read.reference_id = list(CONTIGS).index(chrom)
                        right_mate = paired and (mate == 0 if mol["reverse"] else mate == 1)
                        offset = length if right_mate and length > 1 else 0
                        read.reference_start = start + offset
                        primary_chrom, primary_start, primary_length = mol["sites"][0]
                        assert length == primary_length
                        sequence_start = primary_start + offset
                        read.query_sequence = sequences[primary_chrom][sequence_start:sequence_start + length]
                        read.query_qualities = pysam.qualitystring_to_array("I" * length)
                        orientation = ((83 if mate == 0 else 163) if mol["reverse"]
                                       else (99 if mate == 0 else 147))
                        read.flag = (orientation if paired else (16 if mol["reverse"] else 0))
                        read.flag |= (256 if hit else 0) | mol["flag"]
                        if read.is_reverse:
                            read.query_sequence = read.query_sequence.translate(
                                str.maketrans("ACGT", "TGCA"))[::-1]
                            read.query_qualities = pysam.qualitystring_to_array("I" * length)
                        read.mapping_quality = 60 if len(mol["sites"]) == 1 else 3
                        read.cigar = [(0, length)]
                        if paired:
                            read.next_reference_id = read.reference_id
                            read.next_reference_start = start if right_mate else start + (length if length > 1 else 0)
                            span = length * 2 if length > 1 else 1
                            read.template_length = -span if right_mate else span
                        read.set_tag("NH", len(mol["sites"]))
                        read.set_tag("HI", hit + 1)
                        if tagged:
                            for tag, value in (("CB", CELL), ("UB", mol["umi"]), ("UR", raw_umi(mol, copy))):
                                read.set_tag(tag, value)
                        handle.write(read)
    pysam.sort("--no-PG", "-o", str(path), str(unsorted))
    unsorted.unlink()
    pysam.index(str(path))
    return {"paired": paired, "tagged": tagged, "molecules": molecules,
            "intended_alignments": sum(m["copies"] * len(m["sites"]) * (2 if paired else 1)
                                       for m in molecules)}


def build_fixture():
    """Generate scratch tables through the production taxonomy resolver and exporter."""
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import pysam

    sys.path.insert(0, str(ROOT / "src/lib"))
    from build_exports import EXPORTS, build_exports
    from build_taxonomy import build_taxonomy
    from records_io import RECORD_SCHEMA, write_tsv
    from records import SCHEMA, read_tsv

    tables = FIXTURES / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    rows = []
    for ordinal, row in enumerate(ROSTER, 1):
        chrom, start, end, strand, name, raw, instance = row
        cls, family = raw.split("/") if "/" in raw else (raw, raw)
        length = end - start + 1
        rows.append(dict(
            rmsk_record_id=record_key(row), chrom=chrom, start_1=start, end_1=end,
            strand=strand, rmsk_name=name, rmsk_family=family, rmsk_class=cls,
            rmsk_instance_id=instance, sw_score=1000, divergence_pct=1.0,
            deletion_pct=0.0, insertion_pct=0.0, length_bp=length,
            consensus_start_1=1, consensus_end_1=length, consensus_left_bp=0,
            query_left_bp=CONTIGS[chrom] - end, rmsk_overlap_flag=False,
            rmsk_class_family=raw, ucsc_rep_start=0, ucsc_rep_end=length,
            ucsc_rep_left=0, source_row_number=ordinal))
    records = pd.DataFrame(rows, columns=RECORD_SCHEMA.names)
    assert (len(records), records.rmsk_name.nunique(), records.rmsk_instance_id.nunique()) == (
        EXPECTED["records"], EXPECTED["names"], EXPECTED["instances"])
    pq.write_table(pa.Table.from_pandas(records, schema=RECORD_SCHEMA, preserve_index=False),
                   tables / "rmsk_records.parquet")
    write_tsv(records, tables / "rmsk_records.tsv.gz")
    read_tsv(tables / "rmsk_records.tsv.gz", SCHEMA)
    write_tsv(records[["rmsk_instance_id", "rmsk_record_id"]].sort_values(
        ["rmsk_instance_id", "rmsk_record_id"]), tables / "rmsk_instance_members.tsv.gz")
    taxonomy = records.groupby(["rmsk_name", "rmsk_family", "rmsk_class"], sort=True).agg(
        record_count=("rmsk_record_id", "size"), instance_count=("rmsk_instance_id", "nunique"),
        record_length_sum_bp=("length_bp", "sum")).reset_index()
    write_tsv(taxonomy, tables / "rmsk_taxonomy.tsv")
    (FIXTURES / "universes.json").write_text(json.dumps({
        "schema_version": "1", "default_universe": "interspersed", "universes": [
            {"name": "interspersed", "description": "Synthetic consumer records.",
             "predicate": {}, "provisional_classes": []}]
    }, indent=2) + "\n")
    write_tsv(pd.DataFrame({"universe_name": "interspersed",
                           "rmsk_record_id": records.rmsk_record_id, "provisional": False}),
              tables / "universe_members.tsv.gz")
    build_taxonomy(FIXTURES)
    canonical = pd.read_csv(tables / "taxonomy_canonical.tsv", sep="\t", keep_default_na=False)
    assert {r.rmsk_name: [r.canonical_family, r.canonical_class]
            for r in canonical.itertuples()} == EXPECTED["taxonomy"]
    two = canonical.set_index("rmsk_name").loc["TwoLab"]
    assert (two.family_status, two.family_plurality_share, two.instance_count) == (
        "resolved_plurality", 0.667, 3)
    assert canonical.set_index("rmsk_name").loc["NoFam", "family_status"] == "unspecified"
    build_exports(FIXTURES, "mm39", jobs=(("interspersed", EXPORTS),))
    write_mates_pair(records, FIXTURES)

    rng = random.Random(1729)
    sequences = {name: "".join(rng.choices("ACGT", k=length)) for name, length in CONTIGS.items()}
    fasta = FIXTURES / "reference.fa"
    with fasta.open("w") as handle:
        for name, sequence in sequences.items():
            handle.write(f">{name}\n")
            handle.writelines(sequence[i:i + 80] + "\n" for i in range(0, len(sequence), 80))
    pysam.faidx(str(fasta))
    umis = umi_sequences(20)
    main = [molecule("unique_a", umis[0], [("chrA", 1030, 20)], raw_copies=(0,)),
            molecule("duplicate_b", umis[1], [("chrA", 2030, 20)], copies=2,
                     raw_copies=(1,), reverse=True),
            molecule("multi", umis[2], [("chrA", 1080, 20), ("chrA", 2080, 20)]),
            molecule("gap", umis[3], [("chrA", 3120, 20)])]
    main += [molecule(f"edge_{start}", umis[4 + i], [("chrB", start, 1)])
             for i, start in enumerate((99, 100, 109, 110))]
    main += [molecule("minus_twolab", umis[8], [("chrA", 4030, 20)], reverse=True),
             molecule("flag_duplicate", umis[9], [("chrA", 1040, 20)], flag=1024),
             molecule("flag_qcfail", umis[10], [("chrA", 1050, 20)], flag=512)]
    jobs = {"arc_3prime.bam": (main, False, True),
            "ocm_5prime_pe.bam": (main, True, True), "bulk_pe.bam": (main, True, False)}
    for layout, paired in (("arc", False), ("ocm", True)):
        jobs[f"irescue_simple_{layout}.bam"] = ([main[i] for i in (0, 1, 3)], paired, True)
        for left, right in ((4, 2), (3, 3)):
            alloc = [molecule(f"unique_A_{i}", umis[i], [("chrA", 1030 + i, 20)])
                     for i in range(left)]
            alloc += [molecule(f"unique_B_{i}", umis[left + i], [("chrA", 2030 + i, 20)], reverse=True)
                      for i in range(right)]
            alloc += [molecule(f"shared_{i}", umis[6 + i],
                               [("chrA", 1080 + i, 20), ("chrA", 2080 + i, 20)])
                      for i in range(3)]
            jobs[f"allocation_{left}_{right}_{layout}.bam"] = (alloc, paired, True)
    jobs["featurecounts_pe.bam"] = ([main[0], molecule("unique_b", umis[1],
                                                    [("chrA", 2030, 20)], reverse=True), main[3]], True, False)
    jobs["featurecounts_onebase.bam"] = ([main[5]], False, False)
    manifest = {}
    for name, (molecules, paired, tagged) in jobs.items():
        manifest[name] = write_bam(FIXTURES / name, molecules, sequences, paired, tagged)
        assert manifest[name]["intended_alignments"] == EXPECTED["bams"][name]["alignments"]
    (FIXTURES / "bam_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    (FIXTURES / "onebase.saf").write_text("GeneID\tChr\tStart\tEnd\tStrand\nOneBase\tchrB\t101\t101\t+\n")
    return FIXTURES


def export_path(name):
    return FIXTURES / "exports/ucsc/interspersed/full" / name


def declared_key(export, consumer):
    """Read the export writer's declared key column or grammar for a consumer."""
    sys.path.insert(0, str(ROOT / "src/lib"))
    from build_exports import EXPORT_CONTRACTS

    return EXPORT_CONTRACTS[export]["consumer_keys"][consumer]


def command(args, **kwargs):
    """Retain complete command diagnostics on a failed executable check."""
    result = subprocess.run([str(arg) for arg in args], capture_output=True, text=True, **kwargs)
    assert result.returncode == 0, (args, result.returncode, result.stdout, result.stderr)
    return result.stdout


def bedtools_check():
    build_fixture()
    query = FIXTURES / "query.bed"
    duplicate_ids = {record_key(row) for row in ROSTER if row[4] in {"DupX", "DupY"}}
    for start, end, strand, option, expected in (
        (1500, 1501, "+", None, duplicate_ids), (1600, 1601, "+", None, set()),
        (1500, 1501, "+", "-s", duplicate_ids), (1500, 1501, "+", "-S", set()),
        (1500, 1501, "-", "-s", set()), (1500, 1501, "-", "-S", duplicate_ids),
        (110, 111, "+", None, set()),
    ):
        query.write_text(f"chrB\t{start}\t{end}\tquery\t0\t{strand}\n")
        args = ["bedtools", "intersect", "-wa", "-wb", "-a", query, "-b", export_path("record.bed")]
        rows = [line.split("\t") for line in command(args + ([option] if option else [])).splitlines()]
        assert all(len(row) == 12 for row in rows), rows
        observed = [row[9] for row in rows]
        assert set(observed) == expected and len(observed) == len(expected), (args, observed, expected)
    return "duplicate names, half-open boundaries and -s/-S pass"


def samtools_check():
    import pysam

    build_fixture()
    manifest = json.loads((FIXTURES / "bam_manifest.json").read_text())
    assert set(manifest) == set(EXPECTED["bams"])
    for name, expected in EXPECTED["bams"].items():
        path, spec = FIXTURES / name, manifest[name]
        command(["samtools", "quickcheck", path])
        command(["samtools", "index", path])
        observed = int(command(["samtools", "view", "-c", path]).strip())
        assert observed == expected["alignments"] == spec["intended_alignments"], (name, observed, expected)
        with pysam.AlignmentFile(path) as bam:
            assert bam.has_index() and dict(zip(bam.references, bam.lengths)) == CONTIGS
            reads = list(bam.fetch(until_eof=True))
        assert len({r.query_name for r in reads}) == expected["templates"], name
        assert len(spec["molecules"]) == expected["molecules"], name
        for tag in ("UB", "UR"):
            molecules = len({(r.get_tag("CB"), r.get_tag(tag)) for r in reads}) if spec["tagged"] else None
            assert molecules == expected["molecules_by_tag"][tag], (name, tag, molecules)
        for flag, predicate in (("duplicate", lambda r: r.is_duplicate), ("qcfail", lambda r: r.is_qcfail)):
            assert sorted({r.query_name for r in reads if predicate(r)}) == expected["flagged_reads"][flag], name
        coordinates = [(r.reference_id, r.reference_start) for r in reads]
        assert coordinates == sorted(coordinates), name
        intended = {}
        for mol in spec["molecules"]:
            for copy in range(mol["copies"]):
                intended[f"{mol['name']}_copy{copy}"] = mol
        for query_name, mol in intended.items():
            alignments = [r for r in reads if r.query_name == query_name]
            mates = 2 if spec["paired"] else 1
            assert len(alignments) == len(mol["sites"]) * mates, (name, query_name)
            assert sum(not r.is_secondary for r in alignments) == mates
            for mate in ({True, False} if spec["paired"] else {False}):
                assert len({r.query_sequence for r in alignments if r.is_read1 == mate}) == 1
            for read in alignments:
                assert read.get_tag("NH") == len(mol["sites"])
                assert read.is_paired == spec["paired"]
                assert read.is_duplicate == bool(mol["flag"] & 1024)
                assert read.is_qcfail == bool(mol["flag"] & 512)
                assert read.is_reverse == (mol["reverse"] != (spec["paired"] and read.is_read2))
                if spec["paired"]:
                    assert read.is_proper_pair and read.is_read1 != read.is_read2
                    partner = next(r for r in alignments if r.is_read1 != read.is_read1
                                   and r.get_tag("HI") == read.get_tag("HI"))
                    assert read.next_reference_start == partner.reference_start
                    assert read.template_length == -partner.template_length
                assert read.has_tag("CB") == read.has_tag("UB") == read.has_tag("UR") == spec["tagged"]
                if spec["tagged"]:
                    assert (read.get_tag("CB"), read.get_tag("UB")) == (CELL, mol["umi"])
                    copy = int(query_name.rsplit("_copy", 1)[1])
                    assert read.get_tag("UR") == raw_umi(mol, copy)
                    assert sum(a != b for a, b in zip(read.get_tag("UR"), read.get_tag("UB"))) == (
                        copy in mol["raw_copies"])
                site = mol["sites"][read.get_tag("HI") - 1]
                right_mate = spec["paired"] and (read.is_read1 if mol["reverse"] else read.is_read2)
                offset = site[2] if right_mate and site[2] > 1 else 0
                assert read.reference_name == site[0]
                assert read.get_blocks() == [(site[1] + offset, site[1] + offset + site[2])]
        if spec["tagged"]:
            assert len({(r.get_tag("CB"), r.get_tag("UB")) for r in reads}) == expected["molecules"]
    with pysam.AlignmentFile(FIXTURES / "arc_3prime.bam") as bam:
        reads = list(bam.fetch(until_eof=True))
    for chrom, start, end, strand, *_ in ROSTER:
        if strand == "-":
            assert any(r.is_reverse and r.reference_name == chrom and start - 1 <= r.reference_start < end
                       for r in reads), (chrom, start, end)
    return (f"{len(manifest)} sorted, indexed BAMs; ARC=13 OCM=26 bulk=26 alignments, "
            "11 molecules each; tagged main UB=11 UR=12; reverse strands and duplicate/QC-fail flags pass")


def featurecounts_check():
    build_fixture()
    for annotation, bam, options, feature, expected in (
        (export_path("subfamily.saf"), "featurecounts_pe.bam", ["-p", "--countReadPairs"], "SubA", 2),
        (export_path("taxonomy_triple.saf"), "featurecounts_pe.bam", ["-p", "--countReadPairs"], "SubA:L1:LINE", 2),
        (FIXTURES / "onebase.saf", "featurecounts_onebase.bam", [], "OneBase", 1),
    ):
        output = FIXTURES / f"{annotation.stem}.{bam}.counts.tsv"
        command(["featureCounts", "-F", "SAF", "-a", annotation, "-o", output,
                 "-s", "0", *options, FIXTURES / bam])
        with output.open() as handle:
            rows = list(csv.DictReader((line for line in handle if not line.startswith("#")), delimiter="\t"))
        counts = {row["Geneid"]: float(list(row.values())[-1]) for row in rows}
        assert counts[feature] == expected and sum(counts.values()) == expected, counts
    return "-s 0; two fragments per subfamily and triple SAF feature; inclusive one-base overlap"


def refused_case(check, message):
    """Require a replay to fail with its named discrepancy."""
    try:
        check()
    except AssertionError as error:
        assert message in str(error), str(error)
    else:
        raise AssertionError(f"accepted corrupt replay: {message}")
    return message


def irescue_counts(counts_dir, expected_total):
    """Bind matrix dimensions, feature identities and mass before reducing counts."""
    import numpy as np
    from scipy.io import mmread

    with gzip.open(counts_dir / "features.tsv.gz", "rt") as handle:
        features = [line.rstrip().split("\t") for line in handle]
    assert all(row[0] == row[1] for row in features), features
    with gzip.open(counts_dir / "barcodes.tsv.gz", "rt") as handle:
        barcodes = handle.read().splitlines()
    matrix = mmread(counts_dir / "matrix.mtx.gz")
    assert matrix.shape == (len(features), len(barcodes)), "IRescue matrix dimensions differ from rosters"
    assert len({row[0] for row in features}) == len(features), "IRescue duplicate feature name"
    assert np.isclose(matrix.sum(), expected_total), "IRescue matrix molecule total differs from fixture"
    assert barcodes == [CELL]
    counts = np.asarray(matrix.sum(axis=1)).ravel()
    return dict(zip((row[0] for row in features), counts))


def irescue_check():
    import numpy as np
    from scipy.io import mmread, mmwrite
    from scipy.sparse import csr_matrix, vstack

    build_fixture()
    manifest = json.loads((FIXTURES / "bam_manifest.json").read_text())

    def molecule_total(bam, bed):
        intervals = [line.split("\t")[:3] for line in export_path(bed).read_text().splitlines()]
        return len({mol["umi"] for mol in manifest[bam]["molecules"]
                    if any(chrom == site[0] and int(start) < site[1] + site[2] and site[1] < int(end)
                           for site in mol["sites"] for chrom, start, end in intervals)})

    def quantify(bam, bed, label):
        output = FIXTURES / label
        command(["irescue", "-b", FIXTURES / bam, "-r", export_path(bed), "-o", output,
                 "-u", "UB", "-p", "1", "--locus-level", "disabled", "--strandedness", "unstranded"])
        return irescue_counts(output / "counts", molecule_total(bam, bed))

    allocation = {}
    registered = assert_registered({record_key(row) for row in ROSTER}, "record", "rmsk_record_id")
    registered_names = assert_registered({row[4] for row in ROSTER}, "subfamily", "rmsk_name")
    for layout in ("arc", "ocm"):
        subfamily = quantify(f"irescue_simple_{layout}.bam", "subfamily.bed", f"irescue_{layout}_subfamily")
        records = quantify(f"irescue_simple_{layout}.bam", "record.bed", f"irescue_{layout}_record")
        assert subfamily == {"SubA": 2}, subfamily
        assert set(subfamily) <= set(registered_names) and set(records) <= set(registered)
        keys = [record_key(row) for row in ROSTER if row[4] == "SubA"]
        assert records == dict.fromkeys(keys, 1), records
        for left, right in ((4, 2), (3, 3)):
            counts = quantify(f"allocation_{left}_{right}_{layout}.bam", "record.bed",
                              f"irescue_{layout}_allocation_{left}_{right}")
            assert set(counts) == set(keys) and set(counts) <= set(registered), counts
            x = float(counts[keys[0]] - left)
            assert -1e-6 <= x <= 3 + 1e-6, counts
            assert np.isclose(counts[keys[1]], right + (3 - x)) and np.isclose(sum(counts.values()), 9), counts
            assert all(floor - 1e-6 <= counts[key] <= floor + 3 + 1e-6
                       for key, floor in zip(keys, (left, right))), counts
            allocation[f"{layout}_{left}_{right}"] = {"A": float(counts[keys[0]]),
                                                       "B": float(counts[keys[1]]), "EM_x": x}
    (FIXTURES / "irescue_allocation.json").write_text(json.dumps(allocation, indent=2) + "\n")
    source = FIXTURES / "irescue_arc_allocation_4_2/counts"
    refusals = []
    for label, message in (("extra_row", "IRescue matrix dimensions differ from rosters"),
                            ("duplicate_feature", "IRescue duplicate feature name")):
        replay = FIXTURES / ("irescue_replay_" + label)
        if replay.exists():
            shutil.rmtree(replay)
        shutil.copytree(source, replay)
        matrix = mmread(replay / "matrix.mtx.gz")
        added = csr_matrix([[100]])
        matrix = vstack([added, matrix] if label == "duplicate_feature" else [matrix, added])
        with gzip.open(replay / "matrix.mtx.gz", "wb") as stream:
            mmwrite(stream, matrix)
        if label == "duplicate_feature":
            with gzip.open(replay / "features.tsv.gz", "rt") as stream:
                lines = stream.readlines()
            with gzip.open(replay / "features.tsv.gz", "wt") as stream:
                stream.writelines([lines[0], *lines])
        refusals.append(refused_case(lambda: irescue_counts(
            replay, molecule_total("allocation_4_2_arc.bam", "record.bed")), message))
    return "SubA=2, records=1+1; refused: " + "; ".join(refusals) + "; " + json.dumps(allocation, sort_keys=True)


STARSOLO_ATTRIBUTES = ["gene_id", "transcript_id", "gene_name", "gene_type", "locus", "rmsk_name",
                       "family_id", "class_id", "rmsk_family", "rmsk_class", "instance_id", "rmsk_record_id"]


def gtf_rows(path):
    """Parse nine-column GTF rows with ordered, completely consumed attributes."""
    opener = gzip.open if str(path).endswith(".gz") else open
    with opener(path, "rt") as stream:
        for line in stream:
            if line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            assert len(fields) == 9, (path, fields)
            pairs = re.findall(r'(\w+) "([^"\n]*)";', fields[8])
            assert " ".join(f'{key} "{value}";' for key, value in pairs) == fields[8], path
            assert len(dict(pairs)) == len(pairs), path
            yield fields, dict(pairs)


def combined_gtf_preflight(host, te):
    """Require distinct host and TE identities and reserve record-alias prefixes."""
    te_rows = list(gtf_rows(te))
    genes = {a["gene_id"] for _, a in te_rows}
    transcripts = {a["transcript_id"] for _, a in te_rows}
    assert len(genes) == len(transcripts) == len(te_rows)
    transcript_genes = {}
    for _, attributes in gtf_rows(host):
        for key, values in (("gene_id", genes), ("transcript_id", transcripts)):
            value = attributes[key]
            if value in values:
                raise ValueError(f"host {key} collides with TE alias: {value}")
            if value.startswith("R|mm39|"):
                raise ValueError(f"host {key} uses reserved R|mm39| prefix: {value}")
        transcript, gene = attributes["transcript_id"], attributes["gene_id"]
        if transcript in transcript_genes and transcript_genes[transcript] != gene:
            raise ValueError(f"host transcript maps to several genes: {transcript}")
        transcript_genes[transcript] = gene


def starsolo_profile_check():
    build_fixture()
    from contigs import rename_export
    path = export_path("record_starsolo.gtf")
    assert declared_key(path.name, "STARsolo") == declared_key(path.name, "cellranger") == "gene_id"
    observed = list(gtf_rows(path))
    assert len(observed) == len(ROSTER)
    expected = {record_alias(row): row for row in ROSTER}
    for fields, attributes in observed:
        assert list(attributes) == STARSOLO_ATTRIBUTES
        gene = attributes["gene_id"]
        row = expected[gene]
        assert gene == attributes["transcript_id"] == attributes["locus"]
        assert attributes["gene_name"] == attributes["rmsk_name"] == row[4]
        assert attributes["gene_type"] == "transposable_element"
        assert attributes["rmsk_record_id"] == record_key(row)
        assert (fields[0], int(fields[3]), int(fields[4]), fields[6]) == row[:4]
    assert_registered([a["gene_id"] for _, a in observed], "record", "record_alias")
    suba = [a for _, a in observed if a["gene_name"] == "SubA"]
    assert len(suba) == len({a["gene_id"] for a in suba}) == 2
    edge = next(fields for fields, a in observed if a["gene_name"] == "Edge")
    left, right = int(edge[3]) - 1, int(edge[4])
    assert [int(left <= p < right) for p in (99, 100, 109, 110)] == [0, 1, 1, 0]
    onebase = FIXTURES / "starsolo_onebase.gtf"
    onebase.write_text((ROOT / "tests/fixtures/exports/expected/record_starsolo.gtf").read_text().splitlines()[0] + "\n")
    for namespace, mapping in (("ensembl", {"chrA": "A", "chrB": "B"}),
                               ("gencode", {"chrA": "CM_A.1", "chrB": "CM_B.1"})):
        target = FIXTURES / f"starsolo_{namespace}.gtf"
        rename_export(path, target, mapping)
        renamed = {a["gene_id"]: (f, a) for f, a in gtf_rows(target)}
        for original, a in observed:
            fields, attributes = renamed[a["gene_id"]]
            assert fields == [mapping[original[0]], *original[1:]] and attributes == a
        rename_export(onebase, target, {"chr10": "10" if namespace == "ensembl" else "chr10"})
        fields, _ = next(gtf_rows(target))
        assert fields[3:5] == ["1", "1"]
    fixtures = ROOT / "tests/fixtures/consumers"
    combined_gtf_preflight(fixtures / "starsolo_host.gtf", path)
    for filename, message in (("starsolo_collision.gtf", "host gene_id collides with TE alias"),
                               ("starsolo_reserved.gtf", "host gene_id uses reserved R|mm39| prefix")):
        try:
            combined_gtf_preflight(fixtures / filename, path)
        except ValueError as error:
            assert message in str(error), str(error)
        else:
            raise AssertionError(f"accepted collision fixture: {filename}")
    return "12 ordered attributes; 11 record genes; same-name separation, registration, namespaces, one-base endpoints and host collisions pass"


def combined_fixture():
    build_fixture()
    host = ROOT / "tests/fixtures/consumers/starsolo_host.gtf"
    te = export_path("record_starsolo.gtf")
    combined_gtf_preflight(host, te)
    combined = FIXTURES / "starsolo_combined.gtf"
    combined.write_bytes(host.read_bytes() + te.read_bytes())
    return combined


def starsolo_support(raw, selected, combined, feature):
    """Conserve fixture molecules within their supported genes for each counting mode."""
    import numpy as np
    from scipy.io import mmread

    intervals = {}
    for fields, attrs in gtf_rows(combined):
        intervals.setdefault((attrs["gene_id"], fields[0]), []).append((int(fields[3]) - 1, int(fields[4])))
    if feature == "GeneFull":
        intervals = {key: [(min(a for a, _ in spans), max(b for _, b in spans))]
                     for key, spans in intervals.items()}
    supports = [{gene for (gene, chrom), spans in intervals.items() if chrom == mol["chrom"]
                 and any(start < int(mol["start_0"]) + int(mol["read_length"]) and int(mol["start_0"]) < end
                         for start, end in spans)} for mol in selected]
    allowed = set().union(*supports)
    features = [line.split("\t")[0] for line in (raw / "features.tsv").read_text().splitlines()]
    for filename, total in (("matrix.mtx", sum(len(s) == 1 for s in supports)),
                             ("UniqueAndMult-EM.mtx", sum(bool(s) for s in supports))):
        matrix = mmread(raw / filename)
        assert matrix.shape[0] == len(features), "STARsolo matrix rows differ from features"
        values = np.asarray(matrix.sum(axis=1)).ravel()
        assert np.isfinite(values).all() and (values >= 0).all()
        active = {gene for gene, value in zip(features, values) if value != 0}
        assert active <= allowed, f"STARsolo support outside fixture genes: {feature} {filename}: {sorted(active - allowed)}"
        assert np.isclose(sum(value for gene, value in zip(features, values) if gene in allowed), total), (
            f"STARsolo supported molecule total differs from fixture: {feature} {filename}")


def starsolo_check():
    import numpy as np
    import pysam
    from scipy.io import mmread, mmwrite

    combined = combined_fixture()
    with (ROOT / "tests/fixtures/consumers/starsolo_molecules.tsv").open() as stream:
        molecules = list(csv.DictReader(stream, delimiter="\t"))
    lengths = {int(m["read_length"]) for m in molecules}
    assert len(lengths) == 1
    read_length = lengths.pop()
    index = FIXTURES / "starsolo_index"
    if index.exists():
        shutil.rmtree(index)
    index.mkdir()
    command(["STAR", "--runMode", "genomeGenerate", "--runThreadN", "1", "--genomeDir", index,
             "--genomeFastaFiles", FIXTURES / "reference.fa", "--sjdbGTFfile", combined,
             "--genomeSAindexNbases", "4", "--sjdbOverhang", str(read_length - 1),
             "--outFileNamePrefix", str(index) + "/"])
    expected = {record_alias(row): row[4] for row in ROSTER}
    observations = {}
    with pysam.FastaFile(str(FIXTURES / "reference.fa")) as fasta:
        for case in dict.fromkeys(m["case"] for m in molecules):
            directory = FIXTURES / ("starsolo_" + case)
            if directory.exists():
                shutil.rmtree(directory)
            directory.mkdir()
            first, second = directory / "read1.fastq", directory / "read2.fastq"
            selected = [m for m in molecules if m["case"] == case]
            with first.open("w") as r1, second.open("w") as r2:
                for mol, umi in zip(selected, umi_sequences(len(selected))):
                    start = int(mol["start_0"])
                    cdna = fasta.fetch(mol["chrom"], start, start + read_length)
                    if mol["reverse"] == "true":
                        cdna = cdna.translate(str.maketrans("ACGT", "TGCA"))[::-1]
                    for stream, sequence in ((r1, mol["barcode"] + umi), (r2, cdna)):
                        stream.write(f"@{mol['molecule']}\n{sequence}\n+\n{'I' * len(sequence)}\n")
            command(["STAR", "--runThreadN", "1", "--genomeDir", index,
                     "--readFilesIn", second, first, "--outFileNamePrefix", str(directory) + "/",
                     "--soloType", "CB_UMI_Simple", "--soloCBstart", "1", "--soloCBlen", "16",
                     "--soloUMIstart", "17", "--soloUMIlen", "12", "--soloCBwhitelist", "None",
                     "--soloFeatures", "Gene", "GeneFull", "--soloMultiMappers", "EM",
                     "--soloStrand", "Unstranded", "--soloCellFilter", "None", "--outSAMtype", "None"])
            observations[case] = {}
            for feature in ("Gene", "GeneFull"):
                raw = directory / "Solo.out" / feature / "raw"
                starsolo_support(raw, selected, combined, feature)
                features = [line.split("\t") for line in (raw / "features.tsv").read_text().splitlines()]
                assert len(features) == len(expected) + 1 and len({r[0] for r in features}) == len(features)
                te_features = {r[0]: r[1] for r in features if r[0] in expected}
                assert te_features == expected
                assert all(r[2] == "Gene Expression" for r in features)
                assert_registered(te_features, "record", "record_alias")
                unique = np.asarray(mmread(raw / "matrix.mtx").sum(axis=1)).ravel()
                em = np.asarray(mmread(raw / "UniqueAndMult-EM.mtx").sum(axis=1)).ravel()
                assert len(unique) == len(em) == len(features)
                u, e = [dict(zip((r[0] for r in features), values)) for values in (unique, em)]
                assert np.isfinite(em).all() and (em >= 0).all() and (unique >= 0).all()
                observations[case][feature] = {"unique": {k: float(v) for k, v in u.items() if v},
                                               "EM": {k: float(v) for k, v in e.items() if v}}
                if case == "same_name":
                    keys = [record_alias(row) for row in ROSTER if row[4] == "SubA"]
                    assert all(u[k] == e[k] == 1 for k in keys) and sum(u.values()) == sum(e.values()) == 2
                elif case == "gap":
                    assert sum(u[k] for k in expected) == sum(e[k] for k in expected) == 0
                elif case == "overlap":
                    te = next(k for k, name in expected.items() if name == "SubB")
                    floor = 1 if feature == "Gene" else 0
                    assert u["HostGene"] == 1 and u[te] == floor and sum(u.values()) == 1 + floor, observations[case]
                    assert 1 <= e["HostGene"] <= 3 - floor and floor <= e[te] <= 2
                elif case == "intronic" and feature == "Gene":
                    te = next(k for k, name in expected.items() if name == "SubB-int")
                    assert u[te] == 1 and sum(u.values()) == 1
    (FIXTURES / "starsolo_allocation.json").write_text(json.dumps(observations, indent=2) + "\n")
    for feature in ("Gene", "GeneFull"):
        counts = observations["overlap"][feature]["EM"]
        unique_total = sum(observations["overlap"][feature]["unique"].values())
        if np.isclose(sum(counts.values()), unique_total):
            raise Unsupported("STAR multi-annotation molecule omitted from EM; " + json.dumps(observations, sort_keys=True))
        assert np.isclose(sum(counts.values()), 3), observations
        te = next(k for k, name in expected.items() if name == "SubB")
        floor = 1 if feature == "Gene" else 0
        assert 1 < counts["HostGene"] < 3 - floor and floor < counts[te] < 2, observations
    refusals = []
    selected = [mol for mol in molecules if mol["case"] == "overlap"]
    for feature in ("Gene", "GeneFull"):
        source = FIXTURES / "starsolo_overlap/Solo.out" / feature / "raw"
        for filename in ("matrix.mtx", "UniqueAndMult-EM.mtx"):
            replay = FIXTURES / ("starsolo_replay_" + feature + "_" + filename)
            if replay.exists():
                shutil.rmtree(replay)
            shutil.copytree(source, replay)
            genes = [line.split("\t")[0] for line in (replay / "features.tsv").read_text().splitlines()]
            matrix = mmread(replay / filename).astype(float).tolil()
            edge = next(k for k, name in expected.items() if name == "Edge")
            matrix[genes.index("HostGene"), 0] -= 0.3
            matrix[genes.index(edge), 0] += 0.3
            mmwrite(replay / filename, matrix)
            refusals.append(refused_case(lambda: starsolo_support(replay, selected, combined, feature),
                                         "STARsolo support outside fixture genes"))
    return ("record gene identities and molecule conservation pass; four replays refused: " + refusals[0]
            + "; " + json.dumps(observations, sort_keys=True))


def cellranger_check():
    combined = combined_fixture()
    work = FIXTURES / "cellranger_reference"
    if work.exists():
        shutil.rmtree(work)
    work.mkdir()
    filtered = work / "filtered.gtf"
    command(["cellranger", "mkgtf", combined, filtered,
             "--attribute=gene_type:transposable_element", "--attribute=gene_type:protein_coding"])
    expected = {record_alias(row) for row in ROSTER}
    for path in (filtered,):
        observed = {a["gene_id"] for _, a in gtf_rows(path)}
        assert observed == expected | {"HostGene"}
    args = ["cellranger", "mkref", "--genome=tiny", f"--fasta={FIXTURES / 'reference.fa'}",
            f"--genes={filtered}", "--nthreads=1", "--memgb=3"]
    result = subprocess.run(args, cwd=work, capture_output=True, text=True)
    (work / "mkref.log").write_text(result.stdout + result.stderr)
    assert result.returncode == 0, (args, result.returncode, result.stdout, result.stderr)
    reference = work / "tiny"
    genes = reference / "genes/genes.gtf"
    if not genes.exists():
        genes = genes.with_suffix(".gtf.gz")
    observed = {a["gene_id"] for _, a in gtf_rows(genes)}
    assert observed == expected | {"HostGene"}, observed
    assert_registered(observed & expected, "record", "record_alias")
    assert (reference / "star").is_dir() and (reference / "star/Genome").is_file()
    return "mkgtf retains TE and host biotypes; mkref pins 3 GB and keeps 11 alias genes and its STAR index"


def executable_check(tool):
    info = discover(tool)
    if not info["path"]:
        print(f"unsupported: {tool} absent")
        raise SystemExit(3)
    checks = {"irescue": irescue_check, "featureCounts": featurecounts_check,
              "bedtools": bedtools_check, "samtools": samtools_check,
              "STAR": starsolo_check, "cellranger": cellranger_check}
    run_check(tool, info["version"].removeprefix(f"{tool} "), checks[tool])


if __name__ == "__main__":
    executable_check(sys.argv[1])
