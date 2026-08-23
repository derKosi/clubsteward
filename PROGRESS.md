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

## Session 2026-08-23 (2) — Strands HITL integration + tests + demo script

**Done**
- Read the SDK's actual `strands.vended_interventions.hitl` implementation; integrated it properly:
  - `clubkeeper/interventions.py`: custom `policy_classifier` (HumanInTheLoopClassifier contract) — read tools free; write tools free only under policy `auto` or human `auto_preapproved`; fail-closed otherwise. `ask="stdio"` for interactive mode; trust enabled.
  - Pipeline sets case context (`clubkeeper:case`) in agent state per mail; decide CLI marks approved cases `auto_preapproved` (decision id in audit trail).
  - Act agent now constructed with `interventions=[make_hitl(...)]` — the club YAML literally drives the SDK approval gate.
- Unit tests `tests/test_core.py`: 12 tests, all green (policy loading, evaluate_policy, classifier matrix incl. fail-closed, .eml parsing). No LLM needed.
- `demo/run_demo.sh` — one-command end-to-end (reset → pipeline → decide → morning report), `--interactive` flag for live HITL prompts.
- Full E2E re-run with new architecture: 5 auto / 3 queued / spam rejected → decide approved all 3 → 7 drafts, 7 log entries. EXIT 0.
- Fresh-clone gate: clone → uv sync → 12 tests pass → reset → run_demo syntax OK.
- README rewritten: problem, what it does, policy-as-data, mermaid architecture, quickstart, decisions table, design decisions.

**Learned**
- SDK HITL: `allowed_tools` + `classifier` + `ask="stdio"` + `enable_trust` — classifier contract `(event) -> ClassifierResult`; precedence: negated > trusted > wildcard > allowed > classifier > default-ask.
- Pyright strictness on protocol params: accept `**kwargs` in classifier signature.

**Blocked / decisions needed**
- none

**Next**
- Session persistence (strands session_manager) for multi-day runs, multi-agent polish (agents-as-tools triage→act as true sub-agents), observability/traces, GIF for README, Phase 3 assets (video script, builder.aws draft posts).

## Session 2026-08-23 (3) — Sessions, metrics, Phase-3 assets

**Done**
- Member memory: `act_agent_for()` gives every member a persistent Strands `FileSessionManager` session (demo/data/sessions/). Proven with corpus mail 09 (Miriam's follow-up): agent referenced the earlier instalment plan and handled brother Yaw consistently. Sessions carry across nightly runs.
- Run metrics: `clubkeeper/metrics.py` — run_summary.json with per-mail route, triage/act tokens, tool calls, latency; cost estimate printed at end of pipeline (~€0.009 for 9 mails / 29.6k tokens on GLM). SDK detail: usage lives on `agent.event_loop_metrics.accumulated_usage` (dict), AgentResult carries `.metrics`.
- TriageTokenTracker for per-mail deltas from the cumulative counter.
- Investigated GraphBuilder orchestration; rejected with reasoning (structured triage data would have to round-trip through string node results — the plain two-agent pipeline + policy gate expresses the same topology more honestly). Documented as design decision.
- Architecture diagram: docs/architecture.svg (mermaid-cli, no-emoji variant — renderer chokes on emojis/variation selectors) + architecture.mmd source. Content verified (all nodes/labels/arrows present).
- Phase-3 assets drafted: docs/video-storyboard.md (4 min, problem→demo→memory beat→close), docs/builder-posts-drafts.md (3 angles), docs/devpost-credits-helper.md (copy-paste text for Kosi's registration + $50 credits form, Good Neighbor track).
- REQUIREMENTS.md: architecture diagram + README checked off.
- Fresh-clone gate: 14 tests pass, reset works, docs present.

**Learned**
- mermaid-cli on this VM needs `-p puppeteer-config.json` with `--no-sandbox`; run it from the repo dir (background cwd quirk wrote the first SVG into /tmp/afh-clone).
- Emoji in mermaid labels break rendering here — use plain text labels.

**Blocked / decisions needed**
- none

**Next**
- Decide CLI polish for video (colored decision cards), demo GIF for README, optional: replay mode without API key (judges without Z.ai key), then Phase 3 video recording prep.

