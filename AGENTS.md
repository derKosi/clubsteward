# AGENTS.md — ClubSteward

Entry for the Agents for Humans Hackathon (AWS × Devpost 2026), track "Good Neighbor Agents".
**Submission deadline: 2026-09-12** (hard limit 14.09., 17:00 PT). Agent-side work is done;
remaining items are video, blog post and Devpost submission — see `docs/TODO.md`.

## What it is

Overnight email agent for volunteer clubs: triages the inbox, maintains the member
register (CSV), drafts replies into an outbox (nothing is ever sent automatically),
and queues only real judgment calls for a human. Built with the Strands Agents SDK,
powered by GLM (Z.ai) via LiteLLM. Club rules live in `demo/corpus/policy.yaml` —
policy is data, not code.

## Repo layout

- `clubsteward/` — Python package: pipeline, agents, policy, interventions (HITL), web (FastAPI)
- `demo/` — demo corpus: inbox/outbox, member register, `policy.yaml`
- `scripts/` — entry points (`run_pipeline.sh`, `run_decide.sh`, `run_eval.sh`, `run_smoke.sh`, …)
- `docs/` — English docs: TODO, storyboard, voiceover, Devpost drafts, eval reports
- `tests/` — pytest suite
- `PROGRESS.md` / `REQUIREMENTS.md` — session log / hackathon checklist

## Commands

```bash
uv sync                                   # install deps (Python 3.12)
uv run pytest                             # tests
uv run ruff check .                       # lint (see pyproject.toml rule set)
uv run python scripts/run_smoke.sh        # smoke test
uv run python scripts/reset_demo.py       # reset demo inbox
uv run python -m clubsteward.pipeline     # nightly run (needs Z.ai key)
uv run python -m clubsteward.decide       # HITL decision queue
```

## Conventions

- Docs in this repo are English; converse with the user in German.
- `PROGRESS.md`: one section per session with **Done / Learned / Blocked / Next**.
- Conventional commits (`feat:`, `fix:`, `docs:`, `chore:`).
- Python 3.12, ruff rules from `pyproject.toml` — keep code passing `ruff check` and `pytest`.

## Critical rules

- **Never send email automatically.** The agent only writes drafts to the outbox; sending is always a human action.
- **Secrets**: Z.ai API key lives in `~/.secrets/zai.env` (sops-encrypted). Never commit keys or paste them into docs/tests/demos.
- **This repo is public** (github.com/derKosi/clubsteward). Assume anything committed is visible to the jury and the world.
- Demo data must stay synthetic — no real personal data of club members.
