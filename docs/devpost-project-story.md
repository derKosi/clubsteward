## Inspiration

Community clubs run on burned-out volunteers. The club secretary of every sports club, PTA, scout troop and neighborhood league spends 5–10 hours a week on member email: sign-ups, address changes, fixture questions — and, once a month, a letter that needs a human heart, like a single parent asking for a fee waiver.

We wanted an agent that takes the repetitive 80% off that plate — **without ever touching the 20% that deserves human judgment.** Not "AI does everything", but an agent that knows exactly where to stop.

## What it does

ClubSteward runs the club's inbox overnight, unattended. It triages every mail (structured extraction: intent, facts, confidence), updates the member register, drafts warm on-brand replies — and queues **only real judgment calls** for the secretary: hardship waivers, mid-season cancellations, complaints. Each becomes a decision card: the original mail, what the agent understood, what it proposes, and the exact policy line that escalated it (*"Warum du?"* — in the club's own language). Spam is discarded silently.

It escalates on **conditions, not just intents**: a plain sign-up runs automatically, but the same sign-up mentioning an asthma inhaler is flagged `medical` and stopped by the club's own `ask_if` policy rule. Six demo clubs ship in three languages (German, English, Spanish) — replies always arrive in the member's language, signed by the club.

The **web console** is the secretary's morning: step through mails live (mail left, agent analysis right), approve with one instruction, review every draft side-by-side with the mail it answers. Nothing is ever sent automatically. A full night costs about one cent.

## How we built it

- **Strands Agents SDK** (Python): two specialized agents — a Triage agent using `structured_output` (Pydantic) and an Act agent with five custom tools — running inside the SDK's **HumanInTheLoop intervention** with a custom, policy-driven approval classifier. Read tools run free, writes need policy or a human, unknown tools fail closed.
- **Policy as data**: the club's entire governance lives in a 30-line YAML file that drives routing (auto/ask/reject), the runtime approval classifier, and reply tone. Volunteers edit YAML, not code.
- **Web console**: FastAPI + vanilla JS, no build step — the same pipeline a judge can drive live with **Reset data → Process next mail → Approve + instruct → Run night/Stop**.
- **GLM (Z.ai)** via LiteLLM's OpenAI-compatible provider. No cloud, no accounts — runs on a laptop.
- **Eval harness**: a labeled 10-mail corpus regression-tests triage accuracy on every change.
- **Replay mode**: judges without an API key replay a recorded real session, clearly labeled as recorded.

## Challenges we ran into

- Making "only ask a human when it matters" an **engineered property, not a vibe**: we solved it with three inspectable layers — policy route (auto/ask/reject), tool-category gating, and per-case context. The same YAML powers all three.
- **The model was confidently wrong in both directions.** A polite follow-up mentioning fee relief triaged as a mere "question" (our eval harness caught it — the fix is regression-tested). Another mail sat at 90% confidence on a partial address change: confidence alone wasn't enough, so we added condition flags (`ask_if: billing_address_unclear`) and `min_confidence` — below the threshold the agent asks instead of guessing.
- **Governance must speak the tenant's language**: decision reasons are generated in the club's locale, so a German club's board reads *"Warum du?"* — policy transparency that a volunteer actually reads.

## Accomplishments we're proud of

- The agent **refuses to invent**: it flagged a "brother already in the club" claim it couldn't verify instead of granting a sibling discount.
- Escalation is **explainable to a non-programmer**: every decision card shows the exact policy line that stopped the agent.
- A complete, honest product loop — overnight run → morning decision cards → updated register and outbox — for about **one cent per night**, fully local except the one LLM call.

## What we learned

Autonomy is a spectrum you can **data-drive**. The hardest part wasn't making the agent capable — it was engineering the places where it must *stop*. For volunteer organizations, the policy file **is** the product: governance that a non-programmer can read, edit, and trust.

## What's next for ClubSteward

- IMAP/SMTP adapters for real mailboxes (same pipeline, folder boundaries stay)
- Multi-club hosting with per-club policy files
- Optional managed runtime for clubs that don't want to run a laptop overnight

## Built with

python, strands-agents-sdk, litellm, glm-5-turbo (z.ai), pydantic, fastapi, vanilla-js, uv

