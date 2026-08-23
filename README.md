# agents-for-humans (working title)

Entry for the [Agents for Humans Hackathon](https://agentsforhumans.devpost.com/) (AWS × Devpost, 2026).
Built with the [Strands Agents SDK](https://strandsagents.com/) and GLM (Z.ai) via LiteLLM.

> Status: Phase 0 — setup & smoke test complete. Concept decision in `DECISION.md` (coming).

## Quickstart

```bash
uv sync
cp .env.example .env   # add your Z.ai API key (https://z.ai)
uv run python scripts/smoke_test.py
```

Smoke test output should end with `tool_called=True`.

## Layout

- `scripts/` — smoke tests and helpers
- `REQUIREMENTS.md` — submission checklist derived from official rules
- `DECISION.md` — concept decision (after Phase 1)
- `PROGRESS.md` — running log

## License

MIT — see [LICENSE](LICENSE).
