#!/usr/bin/env bash
# Load Z.ai key from sops (never plaintext on disk) and run the smoke test.
set -euo pipefail
cd "$(dirname "$0")/.."
eval "$(sops -d ~/.secrets/zai.env | grep -v '^#' | sed 's/^/export /')"
exec uv run python scripts/smoke_test.py
