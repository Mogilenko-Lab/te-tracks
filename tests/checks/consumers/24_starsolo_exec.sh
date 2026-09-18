#!/usr/bin/env bash
# Qualify record genes and molecule allocation through STARsolo.
set -euo pipefail
export PYTHONDONTWRITEBYTECODE=1
exec python3 "$(dirname "${BASH_SOURCE[0]}")/../../lib/consumers.py" STAR
