#!/usr/bin/env bash
# End-to-end demo: reset → overnight pipeline → human decisions → show results.
# Runs the REAL agent with a REAL LLM call (needs ZAI_API_KEY, see .env.example).
# Runtime: ~2–4 minutes. No cloud, no accounts, everything stays in demo/data/.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== ClubKeeper demo — reset sandbox =="
uv run python scripts/reset_demo.py

echo
echo "== Nightly batch run (triage → policy → act | queue) =="
uv run python -m clubkeeper.pipeline

echo
echo "== Human decisions (auto-approve mode for scripted demo) =="
if [ "${1:-}" = "--interactive" ]; then
    uv run python -m clubkeeper.decide
else
    uv run python -m clubkeeper.decide y
fi

echo
echo "== Morning report =="
echo "--- outbox drafts ---"
ls demo/data/outbox/*.eml 2>/dev/null | sed 's/^/  /' || echo "  (none)"
echo "--- register (updated) ---"
column -t -s, demo/data/register.csv 2>/dev/null || cat demo/data/register.csv
echo "--- activity log ---"
cat demo/data/activity.log 2>/dev/null | sed 's/^/  /'
echo
echo "Demo complete. Drafts are in demo/data/outbox — review before 'sending'."
