# Runbook

## Gene child build

Use a writable reference root containing a verified core archive. Host builds publish to the
shared reference root; container builds and tests use the scratch root below.

```bash
export TE_TRACKS_REFROOT=/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
export PYTHONDONTWRITEBYTECODE=1
ROOT="$TE_TRACKS_REFROOT/pubroot"
PARENT_ID=$(python3 src/release.py verify-current --root "$ROOT" --family te_mm39) || exit
./build.sh --genome mm39 --family gene --root "$ROOT" --parent-build-id "$PARENT_ID"
python3 src/release.py verify-current --root "$ROOT" --family te_mm39_gene
```

The child config pins GENCODE vM37 by MD5. Place
`gencode.vM37.primary_assembly.annotation.gtf.gz` in `TE_TRACKS_SOURCE_CACHE` to reuse verified
source bytes. The builder retains its own copy, verifies the parent archive and publishes
under `te_mm39_gene/archive/<BUILD_ID>/`. Add `--no-select` to keep the existing child selection.

A scratch child takes an explicit verified core directory:

```bash
C="$TE_TRACKS_REFROOT/te_mm39_gene/build"
P="$TE_TRACKS_REFROOT/te_mm39/build"
./build.sh --genome mm39 --family gene --build-dir "$C" --parent-dir "$P"
python3 src/99_verify.py "$C" --parent-dir "$P"
tests/run.sh core --refroot "$TE_TRACKS_REFROOT"
```

For a transferred child, install and verify its parent archive at the destination first.
Resolve dependencies under that root with `python3 src/99_verify.py <child-dir> --root <root>`.
[RELEASES.md](RELEASES.md#transfer-and-recovery) specifies immutable transfer, verification,
selection and recovery. Consumers pin the child and parent IDs, annotation digest, universe,
namespace, feature grouping and export digest. Use `bin/te-tracks-preflight <export> <bam|fai|sizes>`
to check the counting reference's contigs and lengths.

## Consumer environment

The consuming module owns the environment recipe at
`/workspaces/Meta-Aging/01_modules/te-consumers/env/bootstrap.sh`. Its adjacent
`requirements.txt`, `MANIFEST.tsv`, `pip-freeze.txt` and `python-version.txt`
record the five pinned Python-tool commits, executable archive versions, installed versions and Python.
The recipe installs the five pinned tool commits and records the installed versions;
`pip-freeze.txt` describes the qualified installation. Pinning packaging-tool upgrades,
consuming the dependency freeze and enforcing download hashes remain the consuming module's work.
The installed environment lives at `/workspaces/Meta-Aging/.venv/te-consumers`.

```bash
export PYTHONDONTWRITEBYTECODE=1
export TENX_DISABLE_TELEMETRY=1
source /workspaces/Meta-Aging/.venv/te-consumers/activate.sh
tests/run.sh consumers
```

Offline qualification sets `TENX_DISABLE_TELEMETRY=1`. Activation adds executable shims to PATH.
The suite qualifies STAR 2.7.11b,
cellranger 10.1.0, IRescue and featureCounts alongside the checkout parser tests.
With activation, 16 checks report 15 pass and one unsupported: Stellarscope's
right-boundary overlap defect. Without activation, 11 pass and five are
unsupported: that boundary gate plus absent `irescue`, `featureCounts`, `STAR`
and `cellranger` binaries. Parser checks and the installed bedtools, samtools,
gawk and DuckDB capabilities run in both environments.

STARsolo fixtures record Gene/GeneFull EM allocations while asserting identities,
unique support and molecule conservation. Cellranger qualification runs `mkgtf`
with TE and host biotypes followed by `mkref --memgb=3` on the tiny genome.
The `cellranger count` recipe, chemistry, FASTQs and retained-cell policy belong
to `/workspaces/Meta-Aging/01_modules/te-consumers/recipes/`.

TEsingle's mate selection, UMI graph and hard ties remain consuming-toolkit
qualification gates. Stellarscope's parser exposes its right-boundary defect,
and its per-alignment maximum-overlap selection precedes EM. IRescue initializes
ambiguous-molecule EM evenly and adds unique support separately; the fixture
records that allocation alongside identity and conservation checks.


## Consumer parser sources

Parser qualification reads six pinned clones in the ignored sibling directory
`/workspaces/Meta-Aging/01_modules/.ref/`. Clone setup requires network access.
The pinned commit is the source that qualification measures. Run the commands below once
before consumer qualification; the consuming environment bootstrap supplies the installed tools.

| Checkout | Upstream origin | Destination | Pinned commit |
|---|---|---|---|
| irescue | `https://github.com/bodegalab/irescue.git` | `/workspaces/Meta-Aging/01_modules/.ref/irescue` | `26f36fb391bb031a156ae8f0a77f31c125bfbe15` |
| stellarscope | `https://github.com/nixonlab/stellarscope.git` | `/workspaces/Meta-Aging/01_modules/.ref/stellarscope` | `0e0d594047212afe81e3754732119975a0d2aa6f` |
| TEsingle | `https://github.com/mhammell-laboratory/TEsingle.git` | `/workspaces/Meta-Aging/01_modules/.ref/TEsingle` | `655f1274de0fe5f3241219afc2ecb1c2e0830ae9` |
| TEtranscripts | `https://github.com/mhammell-laboratory/TEtranscripts.git` | `/workspaces/Meta-Aging/01_modules/.ref/TEtranscripts` | `e7f9b93f8c351b1b582cf0882aed49ffd1f0d1e9` |
| TElocal | `https://github.com/mhammell-laboratory/TElocal.git` | `/workspaces/Meta-Aging/01_modules/.ref/TElocal` | `1a168c299714fc55df7dd93359f553759b95c810` |
| MATES | `https://github.com/mcgilldinglab/MATES.git` | `/workspaces/Meta-Aging/01_modules/.ref/MATES` | `87c1218603a26fc9cfa8ab36ef6f730d72d127af` |

```bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
mkdir -p /workspaces/Meta-Aging/01_modules/.ref
git clone https://github.com/bodegalab/irescue.git /workspaces/Meta-Aging/01_modules/.ref/irescue
git -C /workspaces/Meta-Aging/01_modules/.ref/irescue checkout --detach 26f36fb391bb031a156ae8f0a77f31c125bfbe15
git clone https://github.com/nixonlab/stellarscope.git /workspaces/Meta-Aging/01_modules/.ref/stellarscope
git -C /workspaces/Meta-Aging/01_modules/.ref/stellarscope checkout --detach 0e0d594047212afe81e3754732119975a0d2aa6f
git clone https://github.com/mhammell-laboratory/TEsingle.git /workspaces/Meta-Aging/01_modules/.ref/TEsingle
git -C /workspaces/Meta-Aging/01_modules/.ref/TEsingle checkout --detach 655f1274de0fe5f3241219afc2ecb1c2e0830ae9
git clone https://github.com/mhammell-laboratory/TEtranscripts.git /workspaces/Meta-Aging/01_modules/.ref/TEtranscripts
git -C /workspaces/Meta-Aging/01_modules/.ref/TEtranscripts checkout --detach e7f9b93f8c351b1b582cf0882aed49ffd1f0d1e9
git clone https://github.com/mhammell-laboratory/TElocal.git /workspaces/Meta-Aging/01_modules/.ref/TElocal
git -C /workspaces/Meta-Aging/01_modules/.ref/TElocal checkout --detach 1a168c299714fc55df7dd93359f553759b95c810
git clone https://github.com/mcgilldinglab/MATES.git /workspaces/Meta-Aging/01_modules/.ref/MATES
git -C /workspaces/Meta-Aging/01_modules/.ref/MATES checkout --detach 87c1218603a26fc9cfa8ab36ef6f730d72d127af
```

## Acceptance verification

```bash
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/workspaces/Meta-Aging/_scratch/te-tracks-audit/source
tests/run.sh acceptance --build
tests/run.sh acceptance
```

Use `--build` with an empty acceptance root; use `--refroot DIR` to isolate another pair.
An absent pair reports `unsupported: run tests/run.sh acceptance --build` and exits 1.
A selected archive missing an identity file fails. The untouched reference-root replay took
**54 minutes 33 seconds**, with 11 of 11 checks passing, as recorded in the
[phase 9b Opus review](_internal/redesign-2026-09/reviews/p9b_opus.md#closing-verification).

## Host build and publication

Run the producer on the host inside the same devcontainer image, with
`/data2/users/shared/refcache` mounted writable. The development container mounts that path
read-only; acceptance publishes into
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot/acceptance/`.
The workspace Compose service `dev-core` declares `scdock-r-dev:v0.5.15`.
The container exposes Ubuntu 22.04.5 LTS and image build serial `20260627`; its image digest is
available from the host Docker daemon. Record that digest with the publication log and use the
running devcontainer's image ID for the producer.

From the host's Meta-Aging checkout, identify the running `dev-core` container and launch its
image with the workspace and writable reference mount:

```bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
TE_TRACKS_CONTAINER=$(docker compose -f .devcontainer/docker-compose.yml ps -q dev-core)
TE_TRACKS_IMAGE=$(docker inspect --format '{{.Image}}' "$TE_TRACKS_CONTAINER")
printf '%s\n' "$TE_TRACKS_IMAGE"
docker run --rm -it --user "$(id -u):$(id -g)" \
  --mount "type=bind,source=$PWD,target=/workspaces/Meta-Aging" \
  --mount type=bind,source=/data2/users/shared/refcache,target=/data2/users/shared/refcache \
  --workdir /workspaces/Meta-Aging/01_modules/te-tracks \
  --env PYTHONDONTWRITEBYTECODE=1 "$TE_TRACKS_IMAGE" bash -leuo pipefail
```

The following versions were read from this container. The producer uses
`/opt/venvs/base/bin/python3`. Verify the same versions in the host container before building;
retain the version output beside its image ID.

| Prerequisite | Qualified version |
|---|---|
| python3 | 3.11.15 |
| pyarrow | 25.0.0 |
| pandas | 2.2.3 |
| numpy | 1.26.4 |
| pysam | 0.24.0 |
| zlib, compile and runtime | 1.2.11 |
| bash | 5.1.16(1)-release, x86_64-pc-linux-gnu |
| GNU coreutils | 8.32 |
| bedtools | 2.31.1 |

```bash
export PYTHONDONTWRITEBYTECODE=1
export PATH="/opt/venvs/base/bin:$PATH"
python3 - <<'VERSIONS'
import platform, pyarrow, pandas, numpy, pysam, zlib
print("python3", platform.python_version())
for module in (pyarrow, pandas, numpy, pysam):
    print(module.__name__, module.__version__)
print("zlib", zlib.ZLIB_VERSION, zlib.ZLIB_RUNTIME_VERSION)
VERSIONS
bash --version
sort --version
bedtools --version
```

Seed the host source cache from the retained container copy. Validate every pin before copying;
a checksum mismatch stops publication for an explicit re-pin decision. The tracked `data/dfam/`
snapshot, provenance and fetch script travel with the package; the build reads those local inputs.

```bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_SOURCE_CACHE=/data2/users/shared/refcache/te-tracks-source
python3 - <<'SEED'
import csv, hashlib, os, shutil
from pathlib import Path
retained = Path("/workspaces/Meta-Aging/_scratch/te-tracks-audit/source")
cache = Path(os.environ["TE_TRACKS_SOURCE_CACHE"])
with open("tests/expectations/mm39/source_pins.tsv") as stream:
    pins = list(csv.DictReader(stream, delimiter="\t"))
for pin in pins:
    path = Path(pin["path"]) if pin["location"] == "package" else retained / pin["path"]
    with path.open("rb") as stream:
        observed = hashlib.file_digest(stream, pin["algorithm"]).hexdigest()
    if observed != pin["digest"]:
        raise SystemExit(f"checksum mismatch: {path}; stop for a re-pin decision")
cache.mkdir(parents=True, exist_ok=True)
for pin in pins:
    if pin["location"] == "cache":
        target = cache / pin["path"]
        if target.exists():
            with target.open("rb") as stream:
                if hashlib.file_digest(stream, pin["algorithm"]).hexdigest() != pin["digest"]:
                    raise SystemExit(f"checksum mismatch: {target}; stop for a re-pin decision")
        else:
            shutil.copy2(retained / pin["path"], target)
SEED
```

Use a clean committed package tree and fresh private staging directories for publication.
The CLI selects configs through `--genome` and `--family`. `--require-clean` enforces clean
builder provenance at installation and selection; the owner omits it for deliberate dirty-tree
scratch qualification. Run these blocks in the fail-fast host shell above.

```bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
export TE_TRACKS_REFROOT=/data2/users/shared/refcache
export GIT_OPTIONAL_LOCKS=0
test -z "$(git status --porcelain)"
mkdir -p "$TE_TRACKS_REFROOT/te_mm39/.staging"
CORE_STAGING=$(mktemp -d "$TE_TRACKS_REFROOT/te_mm39/.staging/build.XXXXXXXX")
./build.sh --genome mm39 --build-dir "$CORE_STAGING"
PARENT_ID=$(cat "$CORE_STAGING/BUILD_ID")
python3 src/release.py install --root "$TE_TRACKS_REFROOT" --family te_mm39 \
  --staging "$CORE_STAGING" --require-clean
```

Compare all `tables/` file digests and both IDs with the acceptance core before selection.
Equal IDs qualify the same-image reproduction. A `CATALOG_ID` difference stops for investigation.
For a `BUILD_ID` difference with an equal `CATALOG_ID`, inspect the toolchain and payload
changes, publish the host build, and record the in-container build as its content witness.
Keep that comparison in the publication log. Convergence retains the first installed manifest;
`--require-clean` checks that retained provenance too.

```bash
set -euo pipefail
python3 src/release.py select --root "$TE_TRACKS_REFROOT" --family te_mm39 \
  --build-id "$PARENT_ID" --require-clean
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT" --family te_mm39
mkdir -p "$TE_TRACKS_REFROOT/te_mm39_gene/.staging"
CHILD_STAGING=$(mktemp -d "$TE_TRACKS_REFROOT/te_mm39_gene/.staging/build.XXXXXXXX")
./build.sh --genome mm39 --family gene --build-dir "$CHILD_STAGING" \
  --parent-dir "$TE_TRACKS_REFROOT/te_mm39/archive/$PARENT_ID"
CHILD_ID=$(cat "$CHILD_STAGING/BUILD_ID")
python3 src/release.py install --root "$TE_TRACKS_REFROOT" --family te_mm39_gene \
  --staging "$CHILD_STAGING" --require-clean
```

Apply the same identity comparison to the child and its acceptance witness, then select and verify it:

```bash
set -euo pipefail
python3 src/release.py select --root "$TE_TRACKS_REFROOT" --family te_mm39_gene \
  --build-id "$CHILD_ID" --require-clean
python3 src/release.py verify-current --root "$TE_TRACKS_REFROOT" --family te_mm39_gene
chmod 0755 "$TE_TRACKS_REFROOT/te_mm39" "$TE_TRACKS_REFROOT/te_mm39_gene"
chmod 2755 "$TE_TRACKS_REFROOT/te_mm39/archive" "$TE_TRACKS_REFROOT/te_mm39_gene/archive"
```

This runbook chooses owner-only write on family and archive directories. Payload files remain
0444 and build directories 0555. Check effective ACLs on the host so they agree with that policy.
Every build a consumer pins, together with its parent dependency, stays retained beside `current`.
The named backup copy for this publication is the verified CRI archive mirror at
`/gpfs/data/rathmell-lab/data/refdata/{te_mm39,te_mm39_gene}/archive/`.
Completing and verifying that second copy is a host publication gate; its availability is checked
on the destination host.

## Transfer, recovery and consumer pins

Transfer the parent before the child. For each family, resolve source `current` once with
`release.py verify-current`, record the ID and raw manifest SHA-256, and create a fresh directory
under the destination family's `.staging/`. Copy the resolved `archive/<ID>/` contents into that
staging directory using the site's host-to-CRI transfer channel. On the CRI host, with this same
producer image and package checkout available, run:

```bash
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
CRI_ROOT=/gpfs/data/rathmell-lab/data/refdata
python3 src/99_verify.py "$STAGING" --root "$CRI_ROOT"
python3 src/release.py install --root "$CRI_ROOT" --family "$FAMILY" --staging "$STAGING" --require-clean
python3 src/release.py select --root "$CRI_ROOT" --family "$FAMILY" --build-id "$TRANSFER_ID" --require-clean
python3 src/release.py verify-current --root "$CRI_ROOT" --family "$FAMILY"
```

Here `FAMILY` is `te_mm39` and then `te_mm39_gene`; `STAGING` is the fresh direct child of that
family's `.staging/`, and `TRANSFER_ID` is the source pin. Compare the copied manifest's raw
SHA-256 before `install` and the installed manifest's SHA-256 before `select`. Convergence
retains the first installed manifest. Apply the owner-only directory policy to both CRI families.
[RELEASES.md](RELEASES.md#transfer-and-recovery) defines the transfer integrity contract.

After interruption, confirm the builder or transfer process has exited. Preserve its log for
diagnosis, remove its abandoned private staging directory with `shutil.rmtree`, and start a fresh
complete build or transfer. A complete unselected archive can be verified and selected by ID.
An invalid `current` target requires owner investigation with the damaged archive preserved.
Check concurrent selection, interrupted copy, disk exhaustion, cross-filesystem refusal and
consumer ACL access on the host filesystem before pilot adoption.

Resolve `current` once per consumer operation:

```bash
ROOT=/data2/users/shared/refcache
CORE_ID=$(python3 src/release.py verify-current --root "$ROOT" --family te_mm39) || exit
CORE="$ROOT/te_mm39/archive/$CORE_ID"
CHILD_ID=$(python3 src/release.py verify-current --root "$ROOT" --family te_mm39_gene) || exit
CHILD="$ROOT/te_mm39_gene/archive/$CHILD_ID"
```

Read every input from those resolved paths. A child operation uses its declared
`parent_build_id` at `$ROOT/te_mm39/archive/<parent_build_id>/`; `verify-current` for the child
also verifies that dependency. When combining the two selected families, require that parent
ID to equal `CORE_ID`; a selection mismatch is resolved by using the child's retained parent.
Pin `BUILD_ID`, `CATALOG_ID`, annotation and export SHA-256 digests, namespace, universe,
variant, feature level and key grammar. The 14761 ledger adopts `te_catalog_id` and `te_build_id`.
The bulk featureCounts route reads the child's exon-subtracted SAF. EM routes read unmasked
record exports and pin the full gene annotation used by their counting reference. For the
exon-subtracted route, match the gene annotation digest to the child; the current child's
GENCODE vM37 pin identifies its geometry.

## Resource floors and consumer pins

A core payload occupies 15,301,538,537 bytes, about 15.3 GB; the child adds 2,157,717,760 bytes,
about 2.16 GB. The pair retains 17,459,256,297 payload bytes. Reserve one complete staging
copy per new build, sort workspace and the verified CRI backup in addition.

| Producer stage | Acceptance peak resident bytes | Interpretation |
|---|---:|---|
| Core export writer, stage 30 | 4,936,556,544 | 4.94 GB in the final fresh build; retained in the core manifest’s `provenance.peak_rss_bytes`. |
| Child exon subtraction, stage 50 | 881,565,696 | 0.882 GB; 154.376 seconds for subtraction and child export writing, retained in the child manifest’s stage metrics. |

The initial producer measurements are recorded in the
[milestone 9 rulings](_internal/redesign-2026-09/reviews/m9_rulings.md#observations-that-lost-their-carrier).
The [phase 9a review prompt](_internal/redesign-2026-09/prompts/p9a_review.md)
records the earlier complete-build peak near 9 GB,
so stage-only floors describe their own work. Reserve at least 16 GB resident for a single producer
and measure the host run's complete peak beside these per-stage figures.

The reviewed 50,000-row head measurements provide the following annotation-load planning floor.
Projections scale the measured cost to all 3,764,949 rows of `record.gtf`.
The anchors are recorded in the [phase 9a rulings](_internal/redesign-2026-09/reviews/p9a_rulings.md#consumer-annotation-floors-orchestrator-for-the-milestone-5-ruling-h3-anchor);
the reproduction command below measures the file supplied to it.

| Reader | Resident bytes, 50,000 rows | Seconds | Per row | Full-profile projection |
|---|---:|---:|---|---|
| Stellarscope `IntervalTreeAnnotation(gtf, 'locus', 'exon')` | 134,418,432 | 1.79 | 2,688 bytes; 0.036 ms | 10.1 GB; 2.2 min |
| TElocal `TEfeatures.build` through `TEindex` | 51,904,512 | 12.21 | 1,038 bytes; 0.244 ms | 3.9 GB; 15.3 min |

A consumer loading the whole record profile needs about 10 GB resident for Stellarscope.
Counting also retains alignments, molecules, workers and matrices; reserve their working memory
separately. These linear projections describe annotation loading on this image.
Reproduce the measurement with isolated parser processes:

```bash
export PYTHONDONTWRITEBYTECODE=1
python3 tests/checks/acceptance/lib/consumer_floor.py "$CORE/exports/ucsc/interspersed/full/record.gtf"
```

The probe reports peak RSS before and after loading, their increase, elapsed load time, per-row
cost and projection. It reads the export's total data-row count and loads its first 50,000 data rows
in each isolated reader. The two anchors above use the resident increase across annotation loading.
Process peaks include the interpreter and import baseline.

Acceptance and the floor probe use `${TMPDIR:-$TE_TRACKS_REFROOT/tmp}/te-tracks-<root-hash>/acceptance`
for temporary directories, where `root-hash` is the first twelve SHA-256 digits of the absolute
reference-root path. The default reference root is
`/workspaces/Meta-Aging/_scratch/te-tracks-audit/refroot`. Set `TMPDIR` to a writable executable
scratch filesystem; each run creates a private directory and removes it with `shutil.rmtree`.
The acceptance runner prints the derived path.

Consumer installations pin the following clone commits in the ignored sibling directory. The consuming module's
`env/MANIFEST.tsv` and the installed `direct_url.json` metadata record the same five Python-tool commits. An alternate installation
records its exact commit and fixture divergence before adoption; MATES qualification covers its
isolated adapter. The table is the output of `git describe --tags --always` beside the full commit.

| Consumer | git describe | Commit |
|---|---|---|
| IRescue | `v1.2.0-20-g26f36fb` | `26f36fb391bb031a156ae8f0a77f31c125bfbe15` |
| Stellarscope | `1.5` | `0e0d594047212afe81e3754732119975a0d2aa6f` |
| TEsingle | `1.0-8-g655f127` | `655f1274de0fe5f3241219afc2ecb1c2e0830ae9` |
| TEtranscripts | `2.2.4-13-ge7f9b93` | `e7f9b93f8c351b1b582cf0882aed49ffd1f0d1e9` |
| TElocal | `1.1.3-4-g1a168c2` | `1a168c299714fc55df7dd93359f553759b95c810` |
| MATES adapter | `v0.1.8-9-g87c1218` | `87c1218603a26fc9cfa8ab36ef6f730d72d127af` |

The barcode-threshold audit belongs to the consumer: whitelist admission, empty-cell behavior,
per-barcode thresholds, paired-mate handling and UMI policy require the three single-cell and
single-nucleus datasets' pilot evidence. Bulk qualification records its counting unit and strand
policy. [OUTPUTS.md](OUTPUTS.md#consumer-map) binds each counting question to its artifact.
