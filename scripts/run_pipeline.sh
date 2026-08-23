#!/usr/bin/env bash
# Run the ClubKeeper batch pipeline (loads Z.ai key from sops)
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(sops -d ~/.secrets/zai.env | grep -v '^#' | sed 's/^/export /')"
exec uv run python -m clubkeeper.pipeline "$@"
