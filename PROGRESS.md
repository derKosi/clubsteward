# PROGRESS

## Session 2026-08-23 — Phase 0: Setup & Recon

**Done**
- Repo `~/derKosi/AgentForHumans` initialized (git, uv, Python 3.12, strands-agents 1.53.0 + litellm extra)
- Z.ai access verified: key stored encrypted (sops, `~/.secrets/zai.env`), models endpoint lists glm-4.5 … glm-5.3
- Raw chat smoke test: `glm-5-turbo` answers "SMOKE_OK" (119 tokens)
- Strands smoke test: minimal agent + custom `word_count` tool → agent calls the tool and reports result. `tool_called=True`, exit 0.
  - Gotcha: tool results in `agent.messages` use `{"toolUse": {...}}` content blocks (no `type` field).
  - Gotcha: Z.ai warns `reasoningContent is not supported in multi-turn conversations` — harmless with Chat Completions API.
- Hackathon rules/main/FAQ read; binary checklist in `REQUIREMENTS.md`
- Strands docs recon: HITL intervention (`HumanInTheLoop` with LLM risk classifier + trust memory), Interventions framework, LiteLLM model provider, multi-agent patterns (agents-as-tools, swarm, graph, workflow), GoalLoop plugin, observability (metrics/traces/logs), Evals SDK.
  - Note: SDK is being rebranded "Strands Harness" (monorepo `strands-agents/harness-sdk`); PyPI package `strands-agents` unchanged.

**Learned**
- HITL is a first-class SDK feature (vended intervention) — great fit for the hackathon theme; can be extended with a custom policy layer.
- LiteLLM path for custom OpenAI-compatible providers: `LiteLLMModel(client_args={api_key, api_base}, model_id="openai/<model>")`.

**Blocked / decisions needed**
- none

**Next**
- Phase 1: three concepts + scoring matrix + `DECISION.md`
