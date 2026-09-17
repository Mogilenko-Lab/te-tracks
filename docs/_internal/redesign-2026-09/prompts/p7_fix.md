# te-tracks phase 7 fix (unit `te-tracks-p7-fix`)

Working directory: `/workspaces/Meta-Aging/01_modules/te-tracks` (branch `redesign-2026-09`, HEAD `99bf646`; the phase 7
implementer's tree sits uncommitted on top and is your starting point). You implement the rulings in
`docs/_internal/redesign-2026-09/reviews/p7_rulings.md`; the reviews they answer are `reviews/p7_codex.md` and
`reviews/p7_opus.md`.

## Read first
1. `docs/_internal/redesign-2026-09/reviews/p7_rulings.md` (every item below is a ruling there).
2. `docs/_internal/redesign-2026-09/prompts/p7_impl.md` sections "Manifest contract", "Verifier contract" and
   "Release contract" (the contract you are refining).
3. `docs/_internal/redesign-2026-09/reviews/p7_codex.md` B1, B2, A1 to A6; `reviews/p7_opus.md` where present.
4. `/workspaces/Meta-Aging/AGENTS.md` sections "Prose" and "Comments".
5. The files in the touch list, in full, before editing them.

## Environment and rules
- `export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
  TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1`. The
  build under `$TE_TRACKS_REFROOT/te_mm39/build` is yours to re-manifest (`src/90_manifest.py`); every payload table
  and export there stays byte-identical. The published root `$TE_TRACKS_REFROOT/pubroot` is yours to reset and
  republish (item 10). Scratch under `/workspaces/Meta-Aging/_scratch/te-tracks-audit/p7fix/`, removed with Python
  `shutil` when you finish (`/tmp` is noexec).
- No git writes anywhere (the checkouts under `/workspaces/Meta-Aging/01_modules/.ref/` are git repositories too), no
  installs, no network, no edits outside the touch list.
- Never weaken or delete a test beyond what an item below rules. Report a blocking test by name. Every numeric
  target below is measured; when an observation differs, report the deviation instead of editing an artifact or an
  expectation to match.
- Public prose (README, docs, docstrings, comments, check messages) is affirmative and brief; comments state intent in
  one line; no history, provenance or review chatter in package files.

## Items

1. **The verifier judges an archive against its own declaration** (`src/lib/manifest.py`, ruling B1). Split the
   present `export_contracts` into two functions. The authoring function keeps its name and body: it derives the
   contracts from `EXPORT_JOBS` and `EXPORT_CONTRACTS`, cross-checks `tables/exports.tsv` and the export files, and is
   called from `identity_from_payload` alone. A verification function (`verify_export_contracts(build_dir, identity,
   entries, lines)`) takes `identity["export_contracts"]` as the declaration and requires: each entry has exactly the
   keys `export_path`, `namespace`, `universe_name`, `variant`, `format`, `feature_level`, `feature_identity`,
   `attribute_sources`, `consumer_keys`, `selectable_levels`, `coordinate_convention`; `export_path` has the shape
   `exports/<namespace>/<universe>/<variant>/<file>` and its four components equal the entry's `namespace`,
   `universe_name`, `variant` and the file's extension equals `format`; `format` is one of `bed`, `gtf`, `saf`;
   `feature_level` and every value of `selectable_levels` come from the feature levels the exporter knows (`record`,
   `subfamily`, `family`, `taxonomy_triple`, `instance`; define the tuple once beside `EXPORT_CONTRACTS` and import
   it); `universe_name` is declared in `identity["universes"]`; declared paths are unique and sorted. It then
   requires `tables/exports.tsv` rows to equal the declared roster (paths, and per row `namespace`, `universe_name`,
   `variant`, `feature_level`, `format`), the export files present under `exports/` to equal the declared roster,
   and each file's row count and sha256 to match its `exports.tsv` row and the inventory. `verify_build` calls the
   verification function and drops the equality against the running exporter. `EXPORT_JOBS` and
   `EXPORT_CONTRACTS` are imported only where authoring happens.
2. **Published versions** (`src/lib/manifest.py`, ruling B1). Define `PUBLISHED_TAXONOMY_RULE_VERSIONS =
   ("taxonomy_rule_v1",)` and `PUBLISHED_PREDICATE_SCHEMAS = (1,)` beside `SCHEMA_VERSION`; the verifier accepts a
   declared `taxonomy_rule_version` and `universes.schema_version` from those tuples (messages `unsupported
   taxonomy_rule_version` and `universes.json: unsupported predicate grammar version` stay). The authoring path
   requires `TAXONOMY_RULE_VERSION` to be a member of the tuple, so a rule bump extends the tuple in the same change.
   The predicate key set for schema 1 (`class_in`, `family_prefix_excluded`) stays as written. `schema_version` keeps
   its single accepted value; the docstring of `verify_build` states that a future manifest schema adds a verifier
   branch and that archives declaring published versions stay verifiable.
3. **Check 72 gains the roster evolution case** (`tests/checks/core/72_publication_cases.py`,
   `tests/fixtures/publication/build_fixture.py`, ruling B1). `make_build` gains `added_export=False`; when true it
   builds under an extended roster: the `all_rmsk` job also emits `record_extra.bed` at level `record`, with a
   contract entry equal to `record.bed`'s, in all three namespaces (extend the exporter's job registry and contract
   table for the duration of that build inside the fixture process and restore them afterwards; a context manager
   does this). The case: build A under the current roster is installed and selected; build B with `added_export=True`
   installs with `--select`, which re-verifies A and selects B (`current` points at B, both archives present); `select
   --build-id <A>` succeeds; `verify-current` succeeds; B's `MANIFEST.json` declares 27 export contracts and A's 24;
   A and B share `CATALOG_ID`. Place the case after the existing changed-payload case and before the corrupt-archive
   cases so the later archive counts stay as asserted, adjusting those counts by exactly the archives this case adds.
   Success message names the evolution case. `tests/fixtures/publication/README.md` gains one sentence on the extended
   roster.
4. **Check 71 verifies the real build and corrupts a fixture** (`tests/checks/core/71_verify_build.py`, ruling A1).
   Keep the real-build verification and the size/mtime comparison. Replace the `cp -a` copy with a tiny fixture build
   (`make_build` into a temporary family under `$TE_TRACKS_REFROOT/pubtest/`): a flipped byte in
   `source/mm39.chrom.sizes` fails naming that path; an extra `unexpected.txt` fails naming it; a rewritten
   `MANIFEST.json` declaring `taxonomy_rule_version` `taxonomy_rule_v9` with `BUILD_ID` recomputed by the check's own
   encoder (the same encoder as check 70) fails with `unsupported taxonomy_rule_version`; an `exports.tsv` with one
   roster row removed fails with `export roster differs`. Restore write permission on the fixture before removal
   (check 72's `writable` helper shows the pattern). Success message updated. Budget for the check: under ten seconds
   beyond the real-build verification.
5. **One verification per archive per command** (`src/release.py`, codex A2, Opus A3, Opus A4). In `install`, when the
   target exists and `existing_id == identifier`, the verification of `current` already covered the target directory
   under the held lock; skip the second `verify_archive` of the target and proceed to `discard_staging` and
   `converged`. In `select_locked`, verify the existing selection first when `current` exists and return `selected`
   when it already names the candidate; otherwise verify the candidate once and replace the selector. Every other
   path verifies as today. `verify_current` reports archive faults under the selector as
   `current -> archive/<id>: <fault>` (wrap the `verify_archive` error). One-line comments state intent.
6. **Consumer keys declare tested readers** (`src/lib/build_exports.py`, `tests/checks/consumers/*`, ruling A4).
   Remove `"14761 ATAC": "name"` from `EXPORT_CONTRACTS["record.bed"]["consumer_keys"]`; `docs/OUTPUTS.md` keeps
   describing the ATAC route on the `all_rmsk` record BED. Consumer checks 10 (IRescue), 12 (TEsingle), 13
   (TEtranscripts, TElocal), 16 (bedtools on `family.bed`, SAF column reader) import `EXPORT_CONTRACTS` and assert that
   the key each reader exercised equals the declared `consumer_keys` entry for that consumer on that export (a
   helper in `tests/lib/consumers.py`, `declared_key(export, consumer)`, keeps the lookups in one place). Check 11
   (Stellarscope) asserts the same before it reports unsupported. Check 14 (MATES) has no declared entry and stays as
   written.
7. **`docs/RELEASES.md` retention and prose** (rulings B2, A5, A6). The retention paragraph states the measured sums
   of regular file sizes: `ucsc` 3,021,714,346 bytes, `ensembl` 2,926,266,953, `gencode` 3,021,140,740; registration
   347,526,106; the 43-file payload 10,461,884,289 bytes; the `all_rmsk` record BED 332,554,184 / 316,524,255 /
   332,461,688 bytes per namespace; the whole build directory measures 10,462,001,814 bytes by `du -sb`, the provisioning size. The words "supplied",
   "baseline" and "phase 6 fix verification" go. The resident floor reads: the export writer peaks at 6.0 GB resident
   (`provenance.peak_rss_bytes` records each build's own measurement; this build 5,968,367,616 bytes); the stage 35
   figure goes. The host-build sentence states that the recorded Python, pandas, pyarrow and zlib versions are the
   evidence a host build compares against, and that the image identity is recorded when the container exposes one.
   The manifest section states in one sentence that `consumer_keys` names each reader's key column and grammar for
   a file, a fact of the file format that holds for every universe of that file, while tested routes per universe
   live in the OUTPUTS.md route table. The transfer section gains
   one sentence naming host qualification items that the publication checks leave to the host build: interrupted
   transfer into staging, readers during selector replacement, disk exhaustion during rename, staging on another
   filesystem, and ACL access for consumers. The verification section gains one sentence stating that the verifier
   judges an archive against its own manifest and the published schema, taxonomy-rule and predicate-grammar versions,
   and describes `catalog.sources` and `build_sources` per item 11.
8. **`docs/DECISIONS.md` entry 7** (rulings A5, B1, Opus A2): exactly four affirmative sentences covering `BUILD_ID` and
   `CATALOG_ID` (bound to the RepeatMasker source, run identity, instance scope and the four canonical table
   digests) with the ledger key; provenance outside both hashes; staging, single install, atomic selection and
   retention with consumer pins; the verifier judging an archive against its own declaration and the published
   versions so earlier archives stay verifiable and selectable.
9. **README** (rulings A3, A5). Lines 46 to 48 describe the delivered layout (`source/`, `tables/`, `universes.json`,
   `exports/`, `MANIFEST.json`, `BUILD_ID`, `CATALOG_ID`) and the publication layout under `archive/<BUILD_ID>/`
   with `current`; lines 152 to 153 state that mm39 builds and publishes through `build.sh --root`, that admitting a
   genome config requires its `SPECIES` entry in `src/lib/manifest.py`, and that hg38 is deferred with its named
   prerequisites. The truth table rows stay.
10. **Re-manifest and republish** (consequence of items 6 and 11). Run `src/90_manifest.py` on the build directory
    and report the new `BUILD_ID` and `CATALOG_ID`; the inventory stays 43 entries and the payload bytes stay
    unchanged. Reset `$TE_TRACKS_REFROOT/pubroot` (restore write modes first; the snippet
    in the acceptance block does both) and publish once with `./build.sh --genome mm39 --root
    "$TE_TRACKS_REFROOT/pubroot"` (about 11.5 minutes); `current` then carries the same `BUILD_ID` as the build
    directory.

11. **`CATALOG_ID` binds the record-producing source** (`src/lib/manifest.py`, `tests/checks/core/70_manifest_identity.py`,
    Opus A2). `identity.catalog.sources` holds `rmsk_out` alone; a sibling identity key `build_sources` holds
    `rmsk_table`, `chromAlias` and `chrom_sizes` with the same `{url, md5, sha256, bytes}` shape; `contig_set_sha256`
    stays. The authoring path and `catalog_from_payload` follow; the verifier requires `build_sources` in the identity
    key set and recomputes it from `source/SOURCES.json` and the inventory exactly as it does the catalog sources.
    Check 70 adds the mutation: changing `build_sources.chromAlias.sha256` changes `BUILD_ID` and leaves `CATALOG_ID`;
    its existing `rmsk_out` mutation stays. `docs/RELEASES.md` lines 4 and the manifest section, and README line 26,
    describe `CATALOG_ID` in these terms.
12. **Check 72 selector and root cases** (`tests/checks/core/72_publication_cases.py`, Opus A8), each exit 1 with its
    named message and state preserved: `install --select` against a dangling `current`; `select` and `verify-current`
    after the selected archive directory is removed (restore write modes, remove, assert the `current ->` prefix, then
    re-select a surviving archive); `current` as a regular file and as an absolute symlink to a valid archive;
    `install --staging` naming a directory outside `.staging`; `select --build-id` with a non-hex value; a family root
    that is a symlink. Success message names the selector cases.

## Touch list (exact)
`src/lib/manifest.py`, `src/lib/build_exports.py` (the `consumer_keys` entry and the feature-level tuple only),
`src/release.py`, `tests/checks/core/71_verify_build.py`, `tests/checks/core/72_publication_cases.py`,
`tests/checks/core/70_manifest_identity.py`, `tests/fixtures/publication/build_fixture.py`,
`tests/fixtures/publication/README.md`, `tests/lib/consumers.py`
(one helper), `tests/checks/consumers/10_irescue_parser.required.py`, `11_stellarscope_parser.py`,
`12_tesingle_parser.required.py`, `13_tetranscripts_telocal_parser.required.py`,
`16_family_triple_readers.required.py`, `docs/RELEASES.md`, `docs/DECISIONS.md`, `README.md`.

## Acceptance (run these yourself; paste outputs verbatim)
```
cd /workspaces/Meta-Aging/01_modules/te-tracks
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source PYTHONDONTWRITEBYTECODE=1
B=$TE_TRACKS_REFROOT/te_mm39/build
for f in build.sh lib/common.sh src/*.sh tests/run.sh; do bash -n "$f" && echo "syntax ok $f"; done
for f in src/*.py src/lib/*.py tests/checks/core/7*.py tests/fixtures/publication/build_fixture.py tests/lib/consumers.py; do python3 -m py_compile "$f" && echo "compiles $f"; done
python3 -c "import sys; sys.path.insert(0,'src/lib'); import manifest, inspect; src=inspect.getsource(manifest.verify_build); print('EXPORT_JOBS' in src, 'verify_export_contracts' in src)"   # False True
python3 src/90_manifest.py "$B" config/mm39.env && cat "$B/BUILD_ID" "$B/CATALOG_ID"
python3 -c "import json;m=json.load(open('$B/MANIFEST.json'));i=m['identity'];print(len(i['inventory']), len(i['export_contracts']), sorted(i['export_contracts'][0]['consumer_keys']), sorted(i['catalog']['sources']), sorted(i['build_sources']))"   # 43 24 ['IRescue', 'bedtools'] ['rmsk_out'] ['chromAlias', 'chrom_sizes', 'rmsk_table']
python3 src/99_verify.py "$B" | tail -3; echo "exit=${PIPESTATUS[0]}"
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
for ns in ucsc ensembl gencode; do printf "%s " $ns; find "$B/exports/$ns" -type f -printf '%s\n' | awk '{s+=$1} END{print s}'; done   # 3021714346 2926266953 3021140740
time tests/run.sh core; echo "exit=$?"          # 19 pass
tests/run.sh consumers; echo "exit=$?"     # 8 pass, 5 unsupported, exit 0
ls "$TE_TRACKS_REFROOT/pubtest"; ls "$TE_TRACKS_REFROOT/pubroot/te_mm39/.staging"   # both empty
git status --short
```

## Final message
Every file created or changed; acceptance outputs verbatim including the new `BUILD_ID` and `CATALOG_ID`; the archive count after
the evolution case in check 72; any deviation from a stated number or from the touch list, named.
