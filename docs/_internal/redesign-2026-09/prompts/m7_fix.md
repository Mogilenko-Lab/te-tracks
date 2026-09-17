# te-tracks milestone 7 fix (unit `te-tracks-m7-fix`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, HEAD `9d16506`, clean apart
from orchestrator records under `docs/_internal/`). You implement the rulings in
`docs/_internal/redesign-2026-09/reviews/m7_rulings.md`; the reviews they answer are `reviews/m7_codex.md`,
`reviews/m7_divergent.md` and `reviews/m7_opus.md`.

## Read first
1. `docs/_internal/redesign-2026-09/reviews/m7_rulings.md` (every item below is a ruling there).
2. `reviews/m7_divergent.md` H1, H2, H3, M2, M3, L1 to L4; `reviews/m7_opus.md` where cited below.
3. `docs/RELEASES.md` "Manifest and identities" and "Consumer pins and retention"; `docs/DECISIONS.md` entry 7.
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The files in the touch list, in full, before editing them.

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
  TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1`. The build
  under `$TE_TRACKS_REFROOT/te_mm39/build` is yours to re-manifest; every payload file there stays byte-identical. The
  published root `$TE_TRACKS_REFROOT/pubroot` is yours to reset and republish (item 12). Scratch under
  `/workspaces/Meta-Aging/_scratch/te-tracks-audit/m7fix/`, removed with Python `shutil` when you finish (`/tmp` is noexec).
- No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too), no
  installs, no network, no edits outside the touch list.
- Never weaken or delete a test beyond what an item below rules. Report a blocking test by name. Every numeric target
  below is measured; when an observation differs, report the deviation instead of editing an artifact or an expectation
  to match.
- Public prose (README, docs, docstrings, comments, check messages) is affirmative and brief; comments state intent in
  one line; no history, provenance or review chatter in package files.

## Items

1. **Species admission by name and taxon** (`src/lib/manifest.py`, divergent H1). The verifier requires the declared
   `identity.species` to carry `name` and `taxon_id` equal to the admitted `SPECIES[genome]` values and ignores further
   keys on either side; authoring writes the admitted entry as today. Message stays `identity family or species differs`.
2. **Export contract fields are a required set a declaration may extend** (`src/lib/manifest.py`, divergent H1). In
   `verify_export_contracts`, `required_keys <= set(contract)` replaces equality; unknown extra keys pass. The docstring of
   `verify_build` states the two gates that stay single-valued by design: `schema_version` (a new schema adds a verifier
   branch) and the feature-level tuple (levels only grow; renaming one is a contract break).
3. **Reader labels leave the identity** (`src/lib/manifest.py`, `tests/checks/core/70_manifest_identity.py`,
   `docs/RELEASES.md`, divergent H2). The authoring function builds each manifest contract from `EXPORT_CONTRACTS` without
   `consumer_keys`; the verifier's required key set drops `consumer_keys`. `EXPORT_CONTRACTS` in `src/lib/build_exports.py`
   keeps `consumer_keys` for the consumer checks and stays untouched. Check 70 asserts every manifest contract carries
   exactly the ten identity fields and no `consumer_keys`. `docs/RELEASES.md` replaces its `consumer_keys` sentence with:
   reader key columns and grammars are documented in OUTPUTS.md and asserted by the consumer checks against the exporter's
   contract table; the identity binds what bytes and semantics depend on.
4. **`CATALOG_ID` binds table content** (`src/lib/manifest.py`, check 70, docs, divergent H3). `catalog.tables` becomes
   a mapping from logical table name to the SHA-256 of its decompressed bytes: `rmsk_records.tsv` (from
   `tables/rmsk_records.tsv.gz`), `rmsk_instance_members.tsv` (from `tables/rmsk_instance_members.tsv.gz`) and
   `rmsk_taxonomy.tsv` (plain). `rmsk_records.parquet` leaves the catalog and stays in the inventory. `catalog_from_payload`
   and the verifier stream-decompress to hash (about 310 MB of text; report the added verifier time). Check 70 adds two
   mutations: changing the inventory digest of `tables/rmsk_records.parquet` changes `BUILD_ID` alone; changing
   `catalog.tables["rmsk_records.tsv"]` changes both. `docs/RELEASES.md` (identities section and the `CATALOG_ID` encoding
   sentence), `docs/DECISIONS.md` entry 7 (four sentences stay four) and `README.md` line 26 describe `CATALOG_ID` as bound
   to the RepeatMasker source, run identity, instance scope and the decompressed canonical text tables, so a serializer
   or compressor change moves `BUILD_ID` alone.
5. **Core payload roster at authoring** (`src/lib/manifest.py`, `tests/checks/core/71_verify_build.py`, divergent M2).
   `identity_from_payload` requires the non-export inventory paths to equal exactly these nineteen:
   `source/SOURCES.json`, `source/mm39.chrom.sizes`, `source/mm39.chromAlias.txt`, `source/mm39.fa.out.gz`,
   `source/qualification.md`, `source/rmsk.txt.gz`, `tables/contig_aliases.tsv`, `tables/contig_coverage.tsv`,
   `tables/export_feature_members.tsv.gz`, `tables/exports.tsv`, `tables/rmsk_instance_members.tsv.gz`,
   `tables/rmsk_records.parquet`, `tables/rmsk_records.tsv.gz`, `tables/rmsk_taxonomy.tsv`, `tables/taxonomy_canonical.tsv`,
   `tables/taxonomy_resolution_report.tsv`, `tables/universe_members.tsv.gz`, `tables/universe_summary.tsv`,
   `universes.json` (derive the source file names from the config rather than literals where the code already knows them;
   the fixture's sources carry the same names). The failure message names the differing paths (`payload roster differs`).
   Check 71 adds a case: a fixture build with a stray `tables/stray.tmp` fails `src/90_manifest.py` with that message.
   `docs/RELEASES.md` "Transfer and recovery" gains one sentence: publication proceeds from a fresh complete `--root`
   build; a staging directory left by an interruption is for inspection and is removed before republication.
6. **Consumer pins** (`docs/RELEASES.md`, divergent M3). The consumer pin sentence lists `BUILD_ID`, `CATALOG_ID`, relative
   export paths and their digests, universe, feature level and required parent ids; the raw `MANIFEST.json` SHA-256 is
   named in the transfer section alone as the transfer-integrity check.
7. **Preflight binds the alias table to the export's build** (`bin/te-tracks-preflight`, `tests/checks/core/62_preflight.sh`,
   `docs/OUTPUTS.md`, divergent L1, L2). `export_lengths` walks up from the export path to the nearest parent directory
   that contains `MANIFEST.json` and reads that directory's `tables/contig_aliases.tsv`; an export with no such parent, or
   a parent without the table, fails with `export requires an enclosing build with MANIFEST.json and tables/contig_aliases.tsv`.
   The handler adds `TypeError`. Check 62: scratch trees used as roots carry a `MANIFEST.json` marker; a new case places
   an export under a tree whose alias table sits above a `MANIFEST.json`-free directory and asserts the refusal; a new case
   with a short alias row asserts exit 1 and a one-line message. The `alias_table` report line stays. `docs/OUTPUTS.md`
   preflight paragraph states the rule.
8. **Runner exit for an empty mode** (`tests/run.sh`, `tests/checks/core/01_runner_selftest.sh`, `AGENTS.md`, divergent L3).
   A mode with no registered checks prints its line and exits 2; check 01 asserts it with an empty mode directory;
   `AGENTS.md` "Execution" sentence reads "Bad usage, a missing check directory and a mode with no checks exit 2".
9. **Predicate keys per schema** (`src/lib/manifest.py`, divergent L4). `PUBLISHED_PREDICATE_KEYS = {1: {"class_in",
   "family_prefix_excluded"}}` replaces the tuple and the literal set; the verifier selects the key set by the archive's
   declared `universes.schema_version` and refuses an unpublished version as today.
10. **Docs for the verifier's gates** (`docs/RELEASES.md`). The verification section states which declarations are
    judged against published sets (taxonomy rule versions, predicate schemas and their keys, contract fields as a required
    core) and which stay single-valued by design (manifest schema version; feature levels only grow).
11. **README suite sentence and the featureCounts declared key** (`README.md`, `tests/checks/consumers/16_family_triple_readers.required.py`,
    Opus A1, A2). README's core-suite sentence names contigs (60 to 62) and identity and publication (70 to 72) after
    exports (40 to 42). Check 16 asserts `declared_key("subfamily.saf", "featureCounts") == "GeneID"` and the same for
    `taxonomy_triple.saf`, beside its SAF column reader assertion.
12. **Re-manifest and republish** (consequence of items 3 and 4). Run `src/90_manifest.py` on the build directory and
    report both new ids; the inventory stays 43 entries and every payload byte stays. Reset `$TE_TRACKS_REFROOT/pubroot`
    (the acceptance snippet restores write modes first) and publish once with `./build.sh --genome mm39 --root
    "$TE_TRACKS_REFROOT/pubroot"` (about 11.5 minutes); `current` then carries the same `BUILD_ID` as the build directory.

## Touch list (exact)
`src/lib/manifest.py`, `bin/te-tracks-preflight`, `tests/run.sh`, `tests/checks/core/01_runner_selftest.sh`,
`tests/checks/core/62_preflight.sh`, `tests/checks/core/70_manifest_identity.py`, `tests/checks/core/71_verify_build.py`,
`docs/RELEASES.md`, `docs/DECISIONS.md`, `docs/OUTPUTS.md`, `README.md`, `AGENTS.md`, `tests/checks/consumers/16_family_triple_readers.required.py`.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1
B=$TE_TRACKS_REFROOT/te_mm39/build
for f in build.sh lib/common.sh src/*.sh tests/run.sh tests/checks/core/*.sh; do bash -n "$f" && echo "syntax ok $f"; done
for f in src/*.py src/lib/*.py bin/te-tracks-preflight tests/checks/core/7*.py; do python3 -m py_compile "$f" && echo "compiles $f"; done
time python3 src/90_manifest.py "$B" config/mm39.env && cat "$B/BUILD_ID" "$B/CATALOG_ID"
python3 -c "import json;m=json.load(open('$B/MANIFEST.json'));i=m['identity'];c=i['export_contracts'][0];print(len(i['inventory']), len(i['export_contracts']), sorted(c), sorted(i['catalog']['tables']), sorted(i['species']))"
# 43 24 [10 fields, no consumer_keys] ['rmsk_instance_members.tsv', 'rmsk_records.tsv', 'rmsk_taxonomy.tsv'] ['name', 'taxon_id']
python3 -c "import gzip,hashlib,json;m=json.load(open('$B/MANIFEST.json'));t=m['identity']['catalog']['tables'];print(t['rmsk_records.tsv']==hashlib.sha256(gzip.open('$B/tables/rmsk_records.tsv.gz','rb').read()).hexdigest())"   # True
time python3 src/99_verify.py "$B" | tail -2; echo "exit=${PIPESTATUS[0]}"
tests/run.sh acceptance; echo "exit=$? (expect 2)"
bin/te-tracks-preflight "$B/exports/gencode/interspersed/full/record.bed" tests/fixtures/contigs/gencode_grcm39_fasta_contigs.tsv | cut -c1-90; echo "exit=${PIPESTATUS[0]} (expect 0)"
python3 - <<'PY'
import os, shutil
from pathlib import Path
root = Path(os.environ["TE_TRACKS_REFROOT"]) / "pubroot"
for directory, _, files in os.walk(root):
    Path(directory).chmod(0o775)
    for name in files:
        path = Path(directory) / name
        if not path.is_symlink():
            path.chmod(0o664)
shutil.rmtree(root, ignore_errors=True)
print("pubroot reset", not root.exists())
PY
time ./build.sh --genome mm39 --root "$TE_TRACKS_REFROOT/pubroot"; echo "exit=$?"
ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/archive/" | wc -l; readlink "$TE_TRACKS_REFROOT/pubroot/te_mm39/current"
diff "$B/BUILD_ID" "$TE_TRACKS_REFROOT/pubroot/te_mm39/current/BUILD_ID" && echo "same id from both modes"
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT/pubroot" --family te_mm39; echo "exit=$?"
time tests/run.sh core; echo "exit=$?"          # 19 pass
tests/run.sh consumers; echo "exit=$?"     # 8 pass, 5 unsupported, exit 0
ls "$TE_TRACKS_REFROOT/pubtest"; ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/.staging"   # both empty
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim including both new ids and the verifier's added time for
the decompressed digests; any deviation from a stated number or from the touch list, named.
