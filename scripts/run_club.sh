#!/usr/bin/env bash
# Run the ClubSteward pipeline for a specific club (loads Z.ai key from sops)
# Usage: bash scripts/run_club.sh <club-id> [decide]
set -euo pipefail
cd "$(dirname "$0")/.."
CLUB="${1:?usage: run_club.sh <club-id> [decide]}"
eval "$(sops -d ~/.secrets/zai.env | grep -v '^#' | sed 's/^/export /')"
if [ "${2:-}" = "decide" ]; then
    exec uv run python -m clubsteward.club decide "$CLUB" --assume y
fi
exec uv run python -m clubsteward.club run "$CLUB"
