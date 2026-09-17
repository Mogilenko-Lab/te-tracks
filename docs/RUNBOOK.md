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
