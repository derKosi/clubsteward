#!/usr/bin/env bash
# End-to-end demo: reset → overnight pipeline → human decisions → morning report.
#
# With ZAI_API_KEY set: runs the REAL agent with REAL LLM calls (~2–4 min).
# Without a key:       falls back to the recorded session replay (clearly labeled).
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== ClubSteward demo =="
uv run python scripts/reset_demo.py

if [ -n "${ZAI_API_KEY:-}" ] || [ -n "${GLM_API_KEY:-}" ]; then
    echo
    echo "== Nightly batch run (live LLM: triage → policy → act | queue) =="
    uv run python -m clubsteward.pipeline

    echo
    echo "== Human decisions =="
    if [ "${1:-}" = "--interactive" ]; then
        uv run python -m clubsteward.decide
    else
        echo "(auto-approve mode for scripted demo — use --interactive for the real experience)"
        uv run python -m clubsteward.decide y
    fi
else
    echo
    echo "== No ZAI_API_KEY set → replaying recorded session (labeled, no LLM calls) =="
    uv run python -m clubsteward.replay
fi

echo
echo "== Morning report =="
echo "--- outbox drafts ---"
ls demo/data/outbox/*.eml 2>/dev/null | sed 's/^/  /' || echo "  (none)"
echo "--- register (updated) ---"
column -t -s, demo/data/register.csv 2>/dev/null || cat demo/data/register.csv
echo "--- activity log ---"
sed 's/^/  /' demo/data/activity.log 2>/dev/null || true
echo
echo "Demo complete. Drafts are in demo/data/outbox — review before 'sending'."
