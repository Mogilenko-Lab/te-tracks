#!/usr/bin/env bash
# Qualify record gene identities through cellranger reference construction.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
exec python3 "$(dirname "${BASH_SOURCE[0]}")/../../lib/consumers.py" cellranger
