#!/usr/bin/env bash
# Record a full session (loads Z.ai key from sops)
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(sops -d ~/.secrets/zai.env | grep -v '^#' | sed 's/^/export /')"
exec uv run python scripts/record_session.py "$@"
