"""Bind complete payloads to catalog and build identities and verify them in place."""

import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import stat
import subprocess
import sys
from urllib.parse import urlsplit
import zlib

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

sys.dont_write_bytecode = True
from build_exports import FEATURE_LEVELS
from build_records import load_sizes
from records_io import RECORD_SCHEMA


SCHEMA_VERSION = "te-tracks-manifest-1"
PUBLISHED_TAXONOMY_RULE_VERSIONS = ("taxonomy_rule_v1",)
PUBLISHED_PREDICATE_SCHEMAS = (1,)
EXCLUDED = {"MANIFEST.json", "BUILD_ID", "CATALOG_ID"}
CATALOG_TABLES = (
    "tables/rmsk_records.parquet", "tables/rmsk_records.tsv.gz",
    "tables/rmsk_instance_members.tsv.gz", "tables/rmsk_taxonomy.tsv",
)
RUN_KEYS = ("rm_version", "rm_library", "rm_run_evidence", "rmsk_out_profile")
SOURCE_CONFIG = {"rmsk_out": "RMSK_OUT", "rmsk_table": "RMSK_TABLE",
                 "chromAlias": "CHROMALIAS", "chrom_sizes": "CHROM_SIZES"}
SPECIES = {"mm39": {"name": "Mus musculus", "taxon_id": 10090}}


def canonical_bytes(value):
    """Encode hashed objects as sorted, compact UTF-8 JSON."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
                      allow_nan=False).encode("utf-8")


def build_id(identity):
    return hashlib.sha256(b"te-tracks-build-v1\n" + canonical_bytes(identity)).hexdigest()


def catalog_id(catalog):
    return hashlib.sha256(b"te-tracks-catalog-v1\n" + canonical_bytes(catalog)).hexdigest()


def require(condition, message):
    if not condition:
        raise ValueError(message)


def relative_path(value):
    """Accept canonical relative paths confined to the build."""
    require(isinstance(value, str) and value, f"invalid inventory path: {value!r}")
    path = PurePosixPath(value)
    require(not path.is_absolute() and all(part not in ("", ".", "..") for part in value.split("/"))
            and "\\" not in value and "\x00" not in value,
            f"invalid inventory path: {value!r}")
    return value


def read_json(path):
    """Reject duplicate keys and nonfinite numbers in identity documents."""
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"{path}: duplicate JSON key {key!r}")
            result[key] = value
        return result

    def constant(value):
        raise ValueError(f"{path}: invalid JSON number {value}")

    with Path(path).open(encoding="utf-8") as stream:
        return json.load(stream, object_pairs_hook=pairs, parse_constant=constant)


def digest_file(path, algorithm="sha256"):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()


def inventory(build_dir):
    """Hash every regular payload file and count export lines during the same read."""
    build_dir = Path(build_dir)
    require(build_dir.is_dir() and not build_dir.is_symlink(), f"invalid build directory: {build_dir}")
    entries, lines = [], {}

    def walk_error(error):
        raise error

    for directory, directories, files in os.walk(build_dir, followlinks=False, onerror=walk_error):
        for name in sorted(directories + files):
            path = Path(directory) / name
            relative = relative_path(path.relative_to(build_dir).as_posix())
            mode = path.lstat().st_mode
            require(not stat.S_ISLNK(mode), f"symlink inside build: {relative}")
            if stat.S_ISDIR(mode):
                require(relative not in EXCLUDED, f"expected regular file: {relative}")
                continue
            require(stat.S_ISREG(mode), f"nonregular file inside build: {relative}")
            if relative in EXCLUDED:
                continue
            digest, size, count, last = hashlib.sha256(), 0, 0, b""
            with path.open("rb") as stream:
                while block := stream.read(4 * 1024 * 1024):
                    digest.update(block)
                    size += len(block)
                    if relative.startswith("exports/"):
                        count += block.count(b"\n")
                        last = block[-1:]
            entries.append({"path": relative, "bytes": size, "sha256": digest.hexdigest()})
            if relative.startswith("exports/"):
                require(not size or last == b"\n", f"export requires final LF: {relative}")
                lines[relative] = count
    return sorted(entries, key=lambda item: item["path"]), lines


def read_tsv(path):
    with Path(path).open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream, delimiter="\t", quoting=csv.QUOTE_NONE))


def source_path(source):
    return relative_path("source/" + PurePosixPath(urlsplit(source["url"]).path).name)


def sources_from_payload(build_dir, sources, entries, roles):
    """Bind declared source roles to their observed bytes and digests."""
    by_path = {entry["path"]: entry for entry in entries}
    observed = {}
    require(set(sources["sources"]) == set(SOURCE_CONFIG), "source/SOURCES.json: source roles differ")
    for role in roles:
        source = sources["sources"][role]
        path = source_path(source)
        item = by_path[path]
        md5 = digest_file(build_dir / path, "md5")
        require(md5 == source["md5"], f"{path}: source md5 mismatch")
        require(item["bytes"] == source["bytes"], f"{path}: source byte count mismatch")
        observed[role] = {"url": source["url"], "md5": md5,
                          "sha256": item["sha256"], "bytes": item["bytes"]}
    return observed


def catalog_from_payload(build_dir, sources, entries):
    """Bind the record-producing source, run identity and canonical table digests."""
    by_path = {entry["path"]: entry for entry in entries}
    observed = sources_from_payload(build_dir, sources, entries, ("rmsk_out",))
    return {"sources": observed, "run_identity": {key: sources[key] for key in RUN_KEYS},
            "instance_id_scope": "source_run",
            "tables": {path: by_path[path]["sha256"] for path in CATALOG_TABLES}}


def export_contracts(build_dir, entries, lines):
    """Cross-check the authored contracts, export roster, observed rows and digests."""
    from build_exports import EXPORT_CONTRACTS, EXPORT_JOBS

    by_path = {entry["path"]: entry for entry in entries}
    expected = {}
    for namespace in ("ucsc", "ensembl", "gencode"):
        for universe, jobs in EXPORT_JOBS:
            for filename, level in jobs:
                path = f"exports/{namespace}/{universe}/full/{filename}"
                expected[path] = {"export_path": path, "namespace": namespace,
                                  "universe_name": universe, "variant": "full",
                                  "format": filename.rsplit(".", 1)[1],
                                  **EXPORT_CONTRACTS[filename]}
                require(expected[path]["feature_level"] == level, f"export job level differs: {path}")
    rows = read_tsv(build_dir / "tables/exports.tsv")
    paths = [relative_path(row["export_path"]) for row in rows]
    require(len(paths) == len(set(paths)), "tables/exports.tsv: duplicate export path")
    require(set(paths) == set(expected),
            f"tables/exports.tsv: export roster differs: {sorted(set(paths) ^ set(expected))}")
    require(set(lines) == set(expected),
            f"export files differ: {sorted(set(lines) ^ set(expected))}")
    for row in rows:
        path = row["export_path"]
        contract = expected[path]
        for key in ("namespace", "universe_name", "variant", "feature_level", "format"):
            require(row[key] == contract[key], f"tables/exports.tsv: {path}: {key} differs")
        count = lines[path] - (1 if contract["format"] == "saf" else 0)
        require(count == int(row["rows"]), f"tables/exports.tsv: {path}: rows {count} != {row['rows']}")
        require(row["sha256"] == by_path[path]["sha256"], f"tables/exports.tsv: {path}: sha256 mismatch")
    return [expected[path] for path in sorted(expected)]


def verify_export_contracts(build_dir, identity, entries, lines):
    """Verify declared export contracts against the archive's roster, rows and digests."""
    contracts = identity["export_contracts"]
    require(isinstance(contracts, list), "identity.export_contracts requires a list")
    keys = {"export_path", "namespace", "universe_name", "variant", "format", "feature_level",
            "feature_identity", "attribute_sources", "consumer_keys", "selectable_levels",
            "coordinate_convention"}
    universes = {universe["name"] for universe in identity["universes"]["universes"]}
    paths = []
    for contract in contracts:
        require(isinstance(contract, dict) and set(contract) == keys, "export contract fields differ")
        path = relative_path(contract["export_path"])
        parts = path.split("/")
        require(len(parts) == 5 and parts[0] == "exports", f"invalid export path: {path}")
        require(parts[1:4] == [contract[key] for key in ("namespace", "universe_name", "variant")],
                f"export path components differ: {path}")
        require(contract["format"] in ("bed", "gtf", "saf")
                and PurePosixPath(path).suffix == "." + contract["format"],
                f"export format differs: {path}")
        require(contract["feature_level"] in FEATURE_LEVELS, f"unsupported export feature_level: {path}")
        require(isinstance(contract["selectable_levels"], dict)
                and all(level in FEATURE_LEVELS for level in contract["selectable_levels"].values()),
                f"unsupported export selectable_levels: {path}")
        require(contract["universe_name"] in universes, f"undeclared export universe: {path}")
        paths.append(path)
    require(paths == sorted(set(paths)), "export contract paths require unique sorted order")
    declared = dict(zip(paths, contracts))
    rows = read_tsv(build_dir / "tables/exports.tsv")
    row_paths = [relative_path(row["export_path"]) for row in rows]
    require(len(row_paths) == len(set(row_paths)), "tables/exports.tsv: duplicate export path")
    require(set(row_paths) == set(declared),
            f"tables/exports.tsv: export roster differs: {sorted(set(row_paths) ^ set(declared))}")
    require(set(lines) == set(declared), f"export files differ: {sorted(set(lines) ^ set(declared))}")
    by_path = {entry["path"]: entry for entry in entries}
    for row in rows:
        path = row["export_path"]
        contract = declared[path]
        for key in ("namespace", "universe_name", "variant", "feature_level", "format"):
            require(row[key] == contract[key], f"tables/exports.tsv: {path}: {key} differs")
        count = lines[path] - (1 if contract["format"] == "saf" else 0)
        require(count == int(row["rows"]), f"tables/exports.tsv: {path}: rows {count} != {row['rows']}")
        require(row["sha256"] == by_path[path]["sha256"], f"tables/exports.tsv: {path}: sha256 mismatch")
    return contracts


def config_values(path):
    keys = ["GENOME", "ASSEMBLY", "GENOME_FA_URL", "GENOME_FA_MD5",
            *(key.upper() for key in RUN_KEYS),
            *(prefix + suffix for prefix in SOURCE_CONFIG.values() for suffix in ("_URL", "_MD5"))]
    command = 'source "$1"; shift; for key in "$@"; do printf "%s\\0" "${!key}"; done'
    result = subprocess.run(["bash", "-eu", "-c", command, "manifest-config", str(Path(path).resolve()),
                             *keys], check=True, stdout=subprocess.PIPE)
    values = result.stdout.decode().split("\0")[:-1]
    require(len(keys) == len(values), f"invalid config: {path}")
    return dict(zip(keys, values))


def identity_from_payload(build_dir, config, entries, lines):
    from build_taxonomy import TAXONOMY_RULE_VERSION

    require(TAXONOMY_RULE_VERSION in PUBLISHED_TAXONOMY_RULE_VERSIONS,
            "unsupported taxonomy_rule_version")
    sources = read_json(build_dir / "source/SOURCES.json")
    genome = config["GENOME"]
    require(genome in SPECIES, f"species admission required for {genome}")
    require(sources["genome"] == genome and sources["assembly"] == config["ASSEMBLY"],
            "source/SOURCES.json: configured assembly differs")
    for key in RUN_KEYS:
        require(sources[key] == config[key.upper()], f"source/SOURCES.json: configured {key} differs")
    for role, prefix in SOURCE_CONFIG.items():
        for field in ("url", "md5"):
            require(sources["sources"][role][field] == config[prefix + "_" + field.upper()],
                    f"source/SOURCES.json: configured {role} {field} differs")
    declared = {"genome_fa_url": config["GENOME_FA_URL"],
                "genome_fa_md5": config["GENOME_FA_MD5"], "status": "declared"}
    require(sources["declared_assembly"] == declared, "source/SOURCES.json: declared assembly differs")
    catalog = catalog_from_payload(build_dir, sources, entries)
    build_sources = sources_from_payload(build_dir, sources, entries,
                                         ("rmsk_table", "chromAlias", "chrom_sizes"))
    return {
        "schema_version": SCHEMA_VERSION, "family": f"te_{genome}", "species": SPECIES[genome],
        "assembly": {"ucsc": genome, "name": config["ASSEMBLY"]}, "declared_assembly": declared,
        "contig_set_sha256": build_sources["chrom_sizes"]["sha256"], "catalog": catalog,
        "build_sources": build_sources,
        "universes": read_json(build_dir / "universes.json"),
        "taxonomy_rule_version": TAXONOMY_RULE_VERSION,
        "export_contracts": export_contracts(build_dir, entries, lines),
        "parent_build_id": None, "parent_catalog_id": None, "inventory": entries,
    }


def image_identity():
    """Record exposed image evidence and the extent of its identification."""
    candidates = ["/etc/devcontainer-release", "/etc/devcontainer.json", "/etc/image-labels.json",
                  "/etc/container-image", "/usr/local/share/dev-container-features/metadata.json",
                  "/usr/local/etc/vscode-dev-containers/meta.env", "/etc/cloud/build.info"]
    labels = {path: Path(path).read_text(encoding="utf-8")
              for path in candidates if Path(path).is_file()}
    return {"os_release": Path("/etc/os-release").read_text(encoding="utf-8"),
            "image_label_files": labels, "checked_paths": candidates,
            "status": "exposed local files; container image digest unavailable"}


def provenance(sources, argv):
    repo = Path(__file__).resolve().parents[2]
    env = {**os.environ, "GIT_OPTIONAL_LOCKS": "0"}
    sha = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"],
                         capture_output=True, text=True, env=env)
    dirty = subprocess.run(["git", "-C", str(repo), "status", "--porcelain", "--untracked-files=normal"],
                           capture_output=True, text=True, env=env)
    acquisitions = {}
    for role, source in sources.items():
        cache = os.environ.get("TE_TRACKS_SOURCE_CACHE")
        candidate = Path(cache) / Path(source_path(source)).name if cache else None
        acquisitions[role] = (str(candidate.resolve()) if candidate and candidate.is_file()
                              and digest_file(candidate, "md5") == source["md5"] else source["url"])
    peak = os.environ.get("TE_TRACKS_EXPORT_PEAK_RSS_BYTES")
    return {
        "builder_git_sha": sha.stdout.strip() if sha.returncode == 0 else None,
        "builder_git_dirty": bool(dirty.stdout) if dirty.returncode == 0 else None,
        "invocation_argv": argv, "python": platform.python_version(), "pyarrow": pa.__version__,
        "pandas": pd.__version__, "zlib": zlib.ZLIB_RUNTIME_VERSION,
        "devcontainer_image": image_identity(),
        "built_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "source_acquisition": acquisitions,
        "source_acquisition_evidence": "checksum-matching configured cache, otherwise declared URL",
        "validation": {"status": "pending"},
        "peak_rss_bytes": int(peak) if peak else None,
        "peak_rss_measurement": "stage 30 child maximum RSS" if peak else "unavailable for this invocation",
    }


def verify_records(build_dir, identity, emit):
    path = build_dir / "tables/rmsk_records.parquet"
    parquet = pq.ParquetFile(path)
    require(parquet.schema_arrow.equals(RECORD_SCHEMA, check_metadata=False),
            "tables/rmsk_records.parquet: required record schema differs")
    emit("ok records schema: 24 required typed columns")
    sizes_path = source_path(identity["build_sources"]["chrom_sizes"])
    sizes = load_sizes(build_dir / sizes_path)
    seen, count = set(), 0
    for batch in parquet.iter_batches(batch_size=100_000):
        require(all(column.null_count == 0 for column in batch.columns),
                "tables/rmsk_records.parquet: null value")
        frame = batch.select(["rmsk_record_id", "rmsk_name", "chrom", "start_1", "end_1",
                              "strand", "length_bp", "rmsk_instance_id"]).to_pandas()
        ids = frame["rmsk_record_id"]
        require(ids.is_unique and not any(key in seen for key in ids),
                "tables/rmsk_records.parquet: duplicate rmsk_record_id")
        seen.update(ids)
        expected = (frame["rmsk_name"] + "|" + frame["chrom"] + ":" + frame["start_1"].astype(str)
                    + "-" + frame["end_1"].astype(str) + "|" + frame["strand"])
        require(expected.equals(ids), "tables/rmsk_records.parquet: record key differs from components")
        limits = frame["chrom"].map(sizes)
        valid = (limits.notna() & frame["start_1"].ge(1) & frame["end_1"].ge(frame["start_1"])
                 & frame["end_1"].le(limits) & frame["strand"].isin(["+", "-"])
                 & frame["length_bp"].eq(frame["end_1"] - frame["start_1"] + 1))
        require(valid.all(), f"tables/rmsk_records.parquet: bounds or strand differ against {sizes_path}")
        require(frame["rmsk_instance_id"].str.fullmatch(r"[0-9]+").all(),
                "tables/rmsk_records.parquet: invalid text instance id")
        count += len(frame)
    emit(f"ok record identities: {count} unique keys and text instance ids")
    emit(f"ok record bounds: {sizes_path}")
    summaries = read_tsv(build_dir / "tables/universe_summary.tsv")
    all_rows = [row for row in summaries if row["universe_name"] == "all_rmsk"]
    require(len(all_rows) == 1 and int(all_rows[0]["records"]) == count,
            f"tables/universe_summary.tsv: all_rmsk records differ from {count}")
    emit(f"ok universe_summary all_rmsk: {count} records")


def verify_build(build_dir, emit=print):
    """Verify bytes, identities and record/export invariants in place with read-only access.

    A future manifest schema adds a verifier branch; archives declaring published versions stay verifiable.
    """
    build_dir = Path(build_dir)
    entries, lines = inventory(build_dir)
    emit("ok build paths: regular files and directories")
    manifest = read_json(build_dir / "MANIFEST.json")
    require(set(manifest) == {"identity", "provenance"}, "MANIFEST.json: expected identity and provenance")
    identity = manifest["identity"]
    require(identity["schema_version"] == SCHEMA_VERSION, "MANIFEST.json: unsupported schema_version")
    required = {"schema_version", "family", "species", "assembly", "declared_assembly",
                "contig_set_sha256", "catalog", "build_sources", "universes", "taxonomy_rule_version",
                "export_contracts", "parent_build_id", "parent_catalog_id", "inventory"}
    require(set(identity) == required, "MANIFEST.json: identity fields differ")
    expected = identity["inventory"]
    for item in expected:
        relative_path(item["path"])
        require(set(item) == {"path", "bytes", "sha256"}, f"inventory fields differ: {item['path']}")
    paths = [item["path"] for item in expected]
    require(paths == sorted(set(paths)), "MANIFEST.json: inventory paths require unique sorted order")
    expected_by_path = {item["path"]: item for item in expected}
    observed_by_path = {item["path"]: item for item in entries}
    for path in sorted(set(expected_by_path) | set(observed_by_path)):
        require(path in expected_by_path, f"inventory extra file: {path}")
        require(path in observed_by_path, f"inventory missing file: {path}")
        require(expected_by_path[path] == observed_by_path[path], f"inventory bytes or sha256 mismatch: {path}")
    emit(f"ok inventory: {len(entries)} files, exact paths, bytes and sha256")
    identifier = build_id(identity)
    require((build_dir / "BUILD_ID").read_bytes() == (identifier + "\n").encode(),
            f"BUILD_ID mismatch: recomputed {identifier}")
    emit(f"ok BUILD_ID: {identifier}")
    catalog_identifier = catalog_id(identity["catalog"])
    require((build_dir / "CATALOG_ID").read_bytes() == (catalog_identifier + "\n").encode(),
            f"CATALOG_ID mismatch: recomputed {catalog_identifier}")
    emit(f"ok CATALOG_ID: {catalog_identifier}")
    sources = read_json(build_dir / "source/SOURCES.json")
    require(identity["catalog"] == catalog_from_payload(build_dir, sources, entries),
            "identity.catalog differs from source/SOURCES.json or canonical table digests")
    require(identity["build_sources"] == sources_from_payload(
        build_dir, sources, entries, ("rmsk_table", "chromAlias", "chrom_sizes")),
        "identity.build_sources differs from source/SOURCES.json or inventory")
    require(identity["assembly"] == {"ucsc": sources["genome"], "name": sources["assembly"]},
            "identity.assembly differs from source/SOURCES.json")
    require(identity["family"] == "te_" + sources["genome"] and
            identity["species"] == SPECIES.get(sources["genome"]), "identity family or species differs")
    require(identity["parent_build_id"] is None and identity["parent_catalog_id"] is None,
            "core identity requires null parent ids")
    require(identity["declared_assembly"] == sources["declared_assembly"], "declared_assembly differs")
    require(identity["contig_set_sha256"] == identity["build_sources"]["chrom_sizes"]["sha256"],
            "contig_set_sha256 differs from source chrom.sizes")
    require(identity["taxonomy_rule_version"] in PUBLISHED_TAXONOMY_RULE_VERSIONS,
            "unsupported taxonomy_rule_version")
    emit("ok catalog, source_run scope, assembly, contig digest and taxonomy rule")
    universes = read_json(build_dir / "universes.json")
    require(identity["universes"] == universes, "universes.json differs from identity.universes")
    require(universes["schema_version"] in PUBLISHED_PREDICATE_SCHEMAS,
            "universes.json: unsupported predicate grammar version")
    for universe in universes["universes"]:
        require(set(universe["predicate"]) <= {"class_in", "family_prefix_excluded"},
                f"universes.json: unsupported predicate in {universe['name']}")
    emit("ok universe definitions and predicate grammar")
    contracts = verify_export_contracts(build_dir, identity, entries, lines)
    emit(f"ok export contracts: {len(contracts)} namespace paths")
    for contract in contracts:
        emit(f"ok export rows and sha256: {contract['export_path']}")
    verify_records(build_dir, identity, emit)
    emit(f"verified {identifier}")
    return identifier


def write_manifest(build_dir, config_path, argv=None):
    """Write both identities and retain a successful read-only verifier summary."""
    build_dir = Path(build_dir)
    entries, lines = inventory(build_dir)
    identity = identity_from_payload(build_dir, config_values(config_path), entries, lines)
    invocation = argv if argv is not None else json.loads(os.environ.get("TE_TRACKS_INVOCATION", "null"))
    sources = {**identity["catalog"]["sources"], **identity["build_sources"]}
    manifest = {"identity": identity, "provenance": provenance(sources, invocation or sys.argv)}
    path = build_dir / "MANIFEST.json"

    def save():
        path.write_text(json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False,
                                   allow_nan=False) + "\n", encoding="utf-8")

    save()
    identifier, catalog_identifier = build_id(identity), catalog_id(identity["catalog"])
    (build_dir / "BUILD_ID").write_text(identifier + "\n", encoding="ascii")
    (build_dir / "CATALOG_ID").write_text(catalog_identifier + "\n", encoding="ascii")
    assertions = []
    verify_build(build_dir, emit=assertions.append)
    manifest["provenance"]["validation"] = {"status": "verified", "summary": assertions}
    save()
    return identifier, catalog_identifier
