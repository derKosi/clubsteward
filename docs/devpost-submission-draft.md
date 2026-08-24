# Devpost Submission Text (draft — Kosi pastes at submission, Phase 4)

## Inspiration

Community clubs run on burned-out volunteers. The club secretary of every sports club,
PTA, scout troop and neighborhood league spends 5–10 hours a week on member email:
sign-ups, address changes, fixture questions — and, once a month, a letter that needs a
human heart, like a single parent asking for a fee waiver. We wanted an agent that takes
the repetitive 80% off that plate without ever touching the 20% that deserves human
judgment.

## What it does

ClubKeeper runs the club's inbox overnight, unattended:

- **Triages** every inbound member email (structured extraction: intent, facts, confidence)
- **Updates the member register** (CSV) — sign-ups, address/email changes, team moves
- **Drafts warm, on-brand replies** into an outbox folder (nothing is ever sent automatically)
- **Queues only real judgment calls** for the secretary: hardship waivers, mid-season
  cancellations, complaints — each presented as a decision card with the original mail,
  extracted facts, and the exact policy rule that triggered the escalation
- **Escalates on conditions, not just intents**: a plain sign-up runs automatically,
  but the same sign-up mentioning an asthma inhaler gets flagged (`medical`) and
  escalated by the club's own `ask_if` policy rule — autonomy tuning is pure data
- **Discards spam** silently
- **Remembers members**: persistent per-member sessions mean the agent recalls last
  week's instalment plan when a family writes again
- **Reports itself**: every run writes an audit log and a summary (mails, routes, tokens,
  tool calls, ~€0.01–0.03 per night)

## How we built it

- **Strands Agents SDK** (Python): two specialized agents — a Triage agent using
  `structured_output` (Pydantic), and an Act agent with five custom tools
  (register lookup/update/add, draft, log) running inside the SDK's
  **HumanInTheLoop intervention** with a custom classifier.
- **Policy as data**: the club's rules live in a 30-line YAML file. The same file drives
  routing (auto/ask/reject) AND the runtime approval classifier — volunteers edit YAML,
  not code, and the agent's autonomy changes accordingly.
- **Fail-closed design**: unknown intents are queued, unknown tools require approval,
  lookups happen before writes, drafts never send.
- **GLM (Z.ai)** via LiteLLM's OpenAI-compatible provider — no cloud, no AWS bill;
  runs on any laptop.
- **Eval harness**: a labeled 9-mail corpus regression-tests triage accuracy (caught a
  real bug: hardship follow-ups misread as questions — prompt fix took it to 100%).
- **Replay mode**: judges without an API key can replay a recorded real session,
  clearly labeled as recorded.

## Challenges we ran into

- Making "only ask a human when it matters" an engineered property rather than a vibe:
  we solved it with a three-layer autonomy model (policy route → tool-category gating →
  per-case context), all inspectable.
- Triage edge cases: polite follow-up emails that mention fee relief read like questions;
  our eval harness caught this and the fix is regression-tested.

## Accomplishments we're proud of

- The agent refuses to invent: it flagged a "brother already in the club" claim it
  couldn't verify instead of granting a sibling discount.
- Decision cards that show *why* the human is asked (the exact policy line) —
  transparency as a feature.
- A complete product loop in a terminal: overnight run → morning decision cards →
  updated register + outbox, for about a cent per night.

## What we learned

Autonomy is a spectrum you can data-drive. For volunteer organizations, the policy file
IS the product: governance that a non-programmer can read, edit, and trust.

## What's next for ClubKeeper

- IMAP/SMTP adapters for real mailboxes (same pipeline, folder-based boundaries stay)
- Multi-club hosting with per-club policy files
- Optional AgentCore deployment for clubs that want a managed runtime

## Built with

python, strands-agents-sdk, litellm, glm-5-turbo (z.ai), pydantic, uv, asciinema

---

## Submission form fields (quick reference)

- Track: **Good Neighbor Agents**
- Repo: <public GitHub URL — set at submission>
- Video: <YouTube link — recorded per docs/video-storyboard.md>
- License: MIT (LICENSE file present; Kosi pins it in repo About section)
