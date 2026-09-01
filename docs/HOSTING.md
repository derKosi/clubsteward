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
