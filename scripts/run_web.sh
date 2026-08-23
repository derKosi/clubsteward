#!/usr/bin/env bash
# Start the ClubKeeper web console (loads Z.ai key from sops)
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(sops -d ~/.secrets/zai.env | grep -v '^#' | sed 's/^/export /')"
exec uv run uvicorn clubkeeper.web:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8765}"
