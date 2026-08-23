# agents-for-humans (working title)

Entry for the [Agents for Humans Hackathon](https://agentsforhumans.devpost.com/) (AWS × Devpost, 2026).
Built with the [Strands Agents SDK](https://strandsagents.com/) and GLM (Z.ai) via LiteLLM.

> Status: Phase 2 — **ClubKeeper v0.1 runs end-to-end** (triage → policy → act → human decisions).
> Concept & reasoning: see [DECISION.md](DECISION.md). Progress log: [PROGRESS.md](PROGRESS.md).

## What it does

ClubKeeper runs a volunteer sports club''s secretary inbox overnight:
it classifies member emails, updates the member register, drafts warm replies,
and queues **only real judgment calls** (hardship waivers, mid-season cancellations,
complaints) for a human — governed by a policy file the club edits, not code.

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
