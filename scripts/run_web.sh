#!/usr/bin/env bash
# Start the ClubSteward web console (loads Z.ai key from sops)
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(sops -d ~/.secrets/zai.env | grep -v '^#' | sed 's/^/export /')"
exec uv run uvicorn clubsteward.web:app --host "${HOST:-127.0.0.1}" --port "${PORT:-8765}"
