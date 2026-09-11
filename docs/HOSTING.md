# Hosting & SaaS Deployment — how ClubSteward scales from laptop to product

Status: architecture notes. The hackathon submission is the local single-node version
(laptop, no cloud, ~€0.01/night) — everything below is the post-hackathon product path.

## The key insight: multi-tenancy is already the architecture

A "tenant" is a club folder. Every club (`clubs/<id>/`) owns:

- `policy.yaml` — its autonomy rules, fees, tone, signature
- `brand.yaml` — name, tagline, colors, locale
- `register.csv` — its member data
- `inbox/ outbox/ decisions/ processed/ sessions/` — its isolated runtime state
  (per-member LLM sessions live under `sessions/`)

No state is shared between clubs. The pipeline (`club run <id>`) is a pure function
over one club folder. That IS tenant isolation — by construction, not by a
multi-tenancy layer you have to bolt on later.

## Deployment stages (each is small)

### Stage 0 — today (hackathon): local, folder-based
- `uv run python -m clubsteward.club run <id>` per club
- cron/systemd timer for the nightly loop; a human runs `decide <id>` in the morning
- Zero infra, zero cost. This is what the demo video shows.

### Stage 0.5 — shared token (as soon as ports are published)

Set `CLUBSTEWARD_WEB_TOKEN=<random>` and every `/api/*` call must send
`X-API-Token: <same value>` (compared constant-time). The product page and the
console HTML stay public, but every API call fails with 401 without the header —
the console cannot read or act. Unset (default) = open local demo mode.
(The console UI does not send the header yet — token mode is for API
deployments/reverse proxies until Stage 1.)

### Stage 1 — single-box SaaS (weeks, not months)
One small server (VM or container), one FastAPI wrapper around the existing modules:

```
POST /clubs/{id}/run          → clubsteward.pipeline.run(club=id)
GET  /clubs/{id}/decisions    → reads decisions/*.json → JSON cards
POST /clubs/{id}/decisions/{did}/approve|deny|edit → decide.approve(...)
GET  /clubs/{id}/outbox       → drafts for review UI
```

- Scheduler: APScheduler/cron triggers `run` per club nightly (staggered)
- Auth: one login per club board (any IdP; JWT with club_id claim)
- Mail adapters: replace folder-drop with IMAP fetch + SMTP send-as-draft
  (the tools already write .eml — an SMTP adapter is ~50 lines)
- Web UI: decision cards (the decide CLI output maps 1:1 to a card component),
  outbox review, policy editor form (writes policy.yaml), brand/logo upload
- The SDK's interrupt/resume pattern is explicitly designed for stateless web
  frontends — our HITL flow already produces exactly the interrupt payloads a
  web card needs

### Stage 1.5 — tenant-native processing & club knowledge (roadmap, deliberately not scoped)

Where real deployments need data residency or club-specific knowledge, the
direction is "process in the tenant that owns the data" — each item only when a
specific club asks for it:

- **M365 / Graph ingestion**: fetch via Microsoft Graph application permissions
  scoped to the club's own shared mailbox (per-club admin consent), replies stay
  send-as-draft. Mail and drafts never touch our infrastructure; we only schedule.
- **AWS-native LLM option**: Bedrock (region-locked, tenant-owned) instead of a
  third-party endpoint; club documents stay in the club's own S3 bucket.
- **RAG-lite over club documents**: Satzung, fee rules, FAQ as a small local
  retrieval index so drafts quote the club's own rules — extends policy-as-data
  from "rules in YAML" to "rules + documents". Local-first by design (an
  embedded index keeps the keyless juror replay intact); enterprise RAG only on
  demand.

Post-competition priority, driven by real club demand: RAG-lite over club
documents first (cheap, local, no infra), tenant-native ingestion (M365/Bedrock)
second — heavier lift (permissions, consent flows), clear enterprise path.

### Stage 1.6 — Local-first model cascade (idea, decision pending)

Two-tier triage: a small LOCAL model (LM Studio / Ollama on a box in the
club's network, OpenAI-compatible endpoint) does the first-pass classification,
grounded in the club's own website/policy data (RAG-lite). Only when its
confidence is far too low does the mail escalate to the external LLM. Inbound
member mail for routine classification then never leaves the club network —
the strongest possible GDPR story for a Verein.

Why this is cheap for us: **Strands is already the framework and it is
model-agnostic.** The whole loop (triage/act agents, tools, HITL classifier,
per-member sessions) is strands-agents; the model enters only through
`make_model()` as a LiteLLM `openai/<model>` provider pointed at an
OpenAI-compatible base URL. A local endpoint is a config swap
(`ZAI_BASE_URL=http://lm-studio-lan:1234/v1`), not a rewrite. The cascade
re-uses policy-as-data at the model level: "below confidence X → escalate"
is the same axis as the existing `min_confidence` rule, just pointing at a
second model instead of a human. Triage agent → local model, act agent →
cloud model; tools/policy/HITL unchanged.

What would need deciding before relying on it:
- Small-model classification quality on OUR corpus — measurable today: the
  eval harness (`scripts/run_eval.sh`) points at any OpenAI-compatible
  endpoint and gates on accuracy; run it against the local model before
  trusting it. Our GLM structured-output quirks suggest small models will
  need the deterministic `safety_flag_check` backstop even more.
- Structured output reliability (TriageResult schema) on small models —
  the 1× triage retry already absorbs occasional parse failures.
- Hardware reality: a volunteer club has no server rack; the honest target
  is "the secretary's existing Mac or a €200 mini-PC runs LM Studio".
  Latency is irrelevant (nightly batch).
- Escalated mails still go external — document that, or redact names for
  the second hop (pipeline only needs intent/flags, not names).

Recommendation: keep it OUT of the hackathon submission (scope risk one day
before deadline; the keyless replay already demos without an API key) — but
it is the natural first post-competition feature, and the eval harness is
the honest way to prove it works.

### Stage 2 — multi-box (when it's actually needed)
- Worker queue (SQS/Redis) instead of in-process runs; one job per club per night
- Object storage (S3-compatible) replaces the folder per club — the Config layer
  is the only thing that touches paths, so it's one adapter
- Postgres instead of CSV register at scale (same schema, REGISTER_FIELDS)
- AgentCore as managed runtime if we want AWS-native (the $50 credits would go here)

## What NOT to build

- No shared database across clubs — folder-per-club keeps GDPR stories simple
  (delete club = delete folder) and lets a club export everything as a zip
- No realtime sockets for v1 — decisions are made in the morning, not chatted
- No per-club model keys — one platform key, metered per club (run_summary.json
  already tracks tokens per club per night)

## Data protection sketch (German Vereine will ask)

- Member data never leaves the club folder except anonymized classification calls
  (mail text → LLM API; no names required by the pipeline logic itself)
- Right to erasure: remove member row + session folder — done
- Export: zip the club folder — done
- If a club demands on-prem: Stage 0 already IS on-prem. Sell it as a feature.
