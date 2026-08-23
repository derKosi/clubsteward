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
- Phase 1: three concepts + scoring matrix + `DECISION.md` ← done this session, see below

## Session 2026-08-23 — Phase 1: Concept Decision

**Done**
- Originality research (web): subscription-audit agents and generic nonprofit triage agents already exist in OSS; volunteer-club secretary agent = open niche.
- Three concepts worked out (all on shared architecture: local inbox → batch agent → decision queue → outbox + ledger):
  - A) Deadline Guardian (Everyday) — contract renewal/cancellation deadlines
  - B) Concept Cashflow Chaser (Professional) — freelancer dunning
  - C) **ClubKeeper (Good Neighbor) — RECOMMENDED**: club secretary inbox agent with policy-as-data decision layer
- Scoring matrix (demo, feasibility, impact, originality, Strands depth): A 19 · B 21.5 · C 24.5
- `DECISION.md` written with full reasoning + fallback (B shares the architecture)

**Learned**
- The shared substrate makes the concept switchable until ~Sep 1 at near-zero cost.
- HITL custom-classifier + policy-as-data is both the creative centerpiece AND Strands-depth showcase.

**Blocked / decisions needed**
- Kosi's veto on concept C (default: we build C). Veto window: while Phase 2 < 3 days old (until ~Aug 26, 12:00).

**Next**
- Phase 2 build kickoff (architecture skeleton, demo corpus, pipeline skeleton) — started same day, see below

## Session 2026-08-23 — Phase 2 kickoff: ClubKeeper v0.1 end-to-end

**Done**
- Package `clubkeeper/`: models (MailItem, TriageResult, Decision), policy-as-data loader (YAML), config, 5 structured tools (register lookup/update/add, save_draft, log_activity), triage agent (structured output), act agent (tool loop), batch pipeline, human decision CLI.
- Demo corpus: 8 synthetic English club emails covering all intents (signup, address change, hardship, cancellation, question, complaint, spam) + register.csv (6 members) + policy.yaml (Riverside Juniors FC).
- `scripts/reset_demo.py` — restores pristine sandbox from `demo/corpus/`.
- End-to-end verified (real LLM, glm-5-turbo): 8 mails → 5 auto-processed, 3 queued (hardship, cancellation, complaint), spam correctly REJECTED. Then `decide y` approved all 3 → executed, outbox 7 drafts, register updated, activity log written.
- Quality highlights: agent caught that "brother Tomas" is NOT in the register and asked instead of inventing; hardship reply offered concrete options (50% reduction / instalments) with warm tone.

**Learned**
- Z.ai emits `reasoningContent` warnings on multi-turn Chat Completions — harmless noise; filter in logs.
- `Agent.structured_output(PydanticModel, prompt)` works reliably with GLM via LiteLLM `openai/` prefix.
- Decision JSONs + policy_reason give a clean audit trail (judges love this).

**Blocked / decisions needed**
- none (concept C in build; veto window closed)

**Next**
- demo/run_demo.sh (<3 min end-to-end), README with architecture + GIF, tests (unit for policy/tools), Strands depth upgrades: HumanInTheLoop intervention w/ custom classifier replacing manual policy eval, session persistence, multi-agent orchestration polish.

