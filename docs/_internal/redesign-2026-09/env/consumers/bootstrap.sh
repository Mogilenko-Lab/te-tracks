#!/usr/bin/env bash
# Recreates the consumer-tool environment that the te-tracks execution checks run against, from pinned sources.
# Idempotent: every step is skipped when its product exists. Only tool shims go on PATH; python3 stays the base one.
set -euo pipefail
ROOT=${TE_CONSUMERS_ROOT:-/workspaces/Meta-Aging/.venv/te-consumers}
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
BASE_PY=${BASE_PY:-/opt/venvs/base/bin/python3}
CELLRANGER_TARBALL=${CELLRANGER_TARBALL:-/workspaces/Meta-Aging/01_modules/cellranger-10.1.0.tar.gz}
STAR_VERSION=2.7.11b
STAR_URL="https://github.com/alexdobin/STAR/releases/download/${STAR_VERSION}/STAR_${STAR_VERSION}.zip"
SUBREAD_VERSION=2.1.1
SUBREAD_URL="https://sourceforge.net/projects/subread/files/subread-${SUBREAD_VERSION}/subread-${SUBREAD_VERSION}-Linux-x86_64.tar.gz/download"
DUCKDB_VERSION=1.5.5
log(){ printf '[%s] %s\n' "$(date -u +%H:%M:%S)" "$*"; }
sha(){ sha256sum "$1" | cut -d' ' -f1; }
mkdir -p "$ROOT"/{downloads,opt,shims,tmp}
# /tmp is mounted noexec in this container, so builds and their compiled extensions need an executable temp dir.
export TMPDIR="$ROOT/tmp"

log "python venv from $BASE_PY"
[ -x "$ROOT/venv/bin/python3" ] || "$BASE_PY" -m venv "$ROOT/venv"
"$ROOT/venv/bin/pip" install -q --upgrade pip setuptools wheel
export SETUPTOOLS_SCM_PRETEND_VERSION_FOR_STELLARSCOPE=1.5
log "pip install from $HERE/requirements.txt"
"$ROOT/venv/bin/pip" install -q -r "$HERE/requirements.txt"

log "STAR $STAR_VERSION"
if [ ! -x "$ROOT/opt/STAR_${STAR_VERSION}/STAR" ]; then
  [ -s "$ROOT/downloads/STAR_${STAR_VERSION}.zip" ] || curl -sSL --retry 3 -o "$ROOT/downloads/STAR_${STAR_VERSION}.zip" "$STAR_URL"
  mkdir -p "$ROOT/opt/STAR_${STAR_VERSION}"
  "$BASE_PY" - "$ROOT/downloads/STAR_${STAR_VERSION}.zip" "$ROOT/opt/STAR_${STAR_VERSION}" <<'PY'
import os, sys, zipfile
archive, out_dir = sys.argv[1], sys.argv[2]
with zipfile.ZipFile(archive) as z:
    wanted = [n for n in z.namelist() if n.endswith("Linux_x86_64_static/STAR") or n.endswith("Linux_x86_64_static/STARlong")]
    for name in wanted:
        target = os.path.join(out_dir, os.path.basename(name))
        with open(target, "wb") as handle:
            handle.write(z.read(name))
        os.chmod(target, 0o755)
print("extracted", wanted)
PY
fi

log "subread $SUBREAD_VERSION"
if [ ! -x "$ROOT/opt/subread-${SUBREAD_VERSION}-Linux-x86_64/bin/featureCounts" ]; then
  [ -s "$ROOT/downloads/subread-${SUBREAD_VERSION}-Linux-x86_64.tar.gz" ] || curl -sSL --retry 3 -o "$ROOT/downloads/subread-${SUBREAD_VERSION}-Linux-x86_64.tar.gz" "$SUBREAD_URL"
  tar -xzf "$ROOT/downloads/subread-${SUBREAD_VERSION}-Linux-x86_64.tar.gz" -C "$ROOT/opt"
fi

log "gawk (system package)"
if ! command -v gawk >/dev/null 2>&1; then
  sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gawk >/dev/null 2>&1 \
    || { sudo -n apt-get update -qq >/dev/null; sudo -n env DEBIAN_FRONTEND=noninteractive apt-get install -y -qq gawk >/dev/null; }
fi

log "cellranger from $CELLRANGER_TARBALL"
if [ ! -x "$ROOT/opt/cellranger-10.1.0/cellranger" ]; then
  [ -s "$CELLRANGER_TARBALL" ] && tar -xzf "$CELLRANGER_TARBALL" -C "$ROOT/opt" || log "cellranger tarball absent; skipped"
fi

log "duckdb $DUCKDB_VERSION into the base venv (dependency-free wheel)"
"$BASE_PY" -c "import duckdb" >/dev/null 2>&1 || sudo -n "$BASE_PY" -m pip install -q "duckdb==${DUCKDB_VERSION}"

log "shims"
for t in irescue stellarscope TEsingle TEcount TEtranscripts TElocal; do
  if [ -x "$ROOT/venv/bin/$t" ]; then ln -sfn "$ROOT/venv/bin/$t" "$ROOT/shims/$t"; else log "no console script for $t"; fi
done
ln -sfn "$ROOT/opt/STAR_${STAR_VERSION}/STAR" "$ROOT/shims/STAR"
ln -sfn "$ROOT/opt/subread-${SUBREAD_VERSION}-Linux-x86_64/bin/featureCounts" "$ROOT/shims/featureCounts"
[ -x "$ROOT/opt/cellranger-10.1.0/cellranger" ] && ln -sfn "$ROOT/opt/cellranger-10.1.0/cellranger" "$ROOT/shims/cellranger"
printf 'export PATH="%s/shims:$PATH"\n' "$ROOT" > "$ROOT/activate.sh"

log "manifest"
probe(){ "$@" 2>&1 | grep -v '^$' | head -1 || true; }
{
  printf 'tool\tversion\tsource\tsha256\n'
  printf 'STAR\t%s\t%s\t%s\n' "$(probe "$ROOT/shims/STAR" --version)" "$STAR_URL" "$(sha "$ROOT/downloads/STAR_${STAR_VERSION}.zip")"
  printf 'featureCounts\t%s\t%s\t%s\n' "$(probe "$ROOT/shims/featureCounts" -v)" "$SUBREAD_URL" "$(sha "$ROOT/downloads/subread-${SUBREAD_VERSION}-Linux-x86_64.tar.gz")"
  printf 'gawk\t%s\t%s\t%s\n' "$(probe gawk --version)" "apt (system package; add to the devcontainer image)" "-"
  if [ -x "$ROOT/shims/cellranger" ]; then printf 'cellranger\t%s\t%s\t%s\n' "$(probe "$ROOT/shims/cellranger" --version)" "$CELLRANGER_TARBALL" "$(sha "$CELLRANGER_TARBALL")"; fi
  for t in irescue stellarscope TEsingle TEcount TEtranscripts TElocal; do
    [ -x "$ROOT/shims/$t" ] && printf '%s\t%s\t%s\t%s\n' "$t" "$(probe "$ROOT/shims/$t" --version)" "$(grep -i "^$t " "$HERE/requirements.txt" | cut -d' ' -f3)" "-"
  done
  printf 'duckdb (base venv module)\t%s\t%s\t%s\n' "$("$BASE_PY" -c 'import duckdb; print(duckdb.__version__)')" "pypi duckdb==${DUCKDB_VERSION}" "-"
} > "$ROOT/MANIFEST.tsv"
"$ROOT/venv/bin/pip" freeze > "$ROOT/pip-freeze.txt"
"$ROOT/venv/bin/python3" --version > "$ROOT/python-version.txt"
log "done: $ROOT"
"$BASE_PY" -c "import sys,csv; rows=list(csv.reader(open(sys.argv[1]),delimiter=chr(9))); w=[max(len(r[i]) for r in rows if len(r)>i) for i in range(2)]; [print(r[0].ljust(w[0]),r[1].ljust(min(w[1],60))[:60],r[2][:70]) for r in rows]" "$ROOT/MANIFEST.tsv"
