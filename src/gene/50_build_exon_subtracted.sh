#!/usr/bin/env bash
# Publish every retained block with its parent identity and annotation coverage.
SCRIPT_NAME=50_exon_subtracted
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common.sh"
[ "$#" -eq 3 ] || die "usage: 50_build_exon_subtracted.sh <build-dir> <config.env> <parent-dir>"
python3 "$REPO_ROOT/src/lib/gene_child.py" build --build-dir "$1" --config "$2" --parent-dir "$3"
