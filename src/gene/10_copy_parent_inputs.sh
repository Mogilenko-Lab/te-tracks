#!/usr/bin/env bash
# Keep the parent's universe and contig declarations local to the child.
SCRIPT_NAME=10_copy_parent
source "$(dirname "${BASH_SOURCE[0]}")/../../lib/common.sh"
[ "$#" -eq 3 ] || die "usage: 10_copy_parent_inputs.sh <build-dir> <config.env> <parent-dir>"
python3 "$REPO_ROOT/src/lib/gene_child.py" copy --build-dir "$1" --config "$2" --parent-dir "$3"
