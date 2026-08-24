# builder.aws.com Post — FINAL DRAFT (publish ~Sep 8–10)

Title: **Agents for Humans: How We Made a YAML File the Brain of an AI Agent**

~850 words. Publish as-is or trim the "belt and braces" section if over limit.
Replace `<repo-url>` before publishing.

---

When we started building for the Agents for Humans Hackathon, we kept circling one
question: who is actually allowed to decide what an AI agent may do on its own?

Our answer became the core of ClubSteward, an open-source club-secretary agent for
volunteer sports clubs — and the answer is: **the club decides, in a file the club
can edit.**

## The problem worth solving

Community clubs run on burned-out volunteers. The club secretary of every sports
club, PTA, and scout troop spends five to ten hours a week on member email:
sign-ups, address changes, fixture questions. Most of it is repetitive. But some
of it — a single parent asking for a fee waiver, a child with asthma joining a
team — deserves a human being, not a template.

We wanted an agent that takes the repetitive 80% and never touches the 20% that
needs judgment. The question was how to make that boundary **a property of the
system**, not a hope.

## Policy as data — literally

The Strands Agents SDK ships a Human-in-the-Loop intervention: an approval gate
in front of tool calls, with a pluggable classifier that decides which calls need
a human. Most examples use an LLM risk classifier. We replaced it with the club's
own policy file:

```yaml
rules:
  - intent: signup           # complete signups are routine
    decision: auto
    ask_if:
      - "medical notes that require coach coordination"
  - intent: hardship_waiver  # money + empathy = human decides
    decision: ask
  - intent: spam
    decision: reject
```

That's not documentation — that YAML *is* the runtime classifier. A triage agent
(using the SDK's structured output) classifies each inbound mail and extracts
short flags: `medical`, `waiting_list`, `refund`. The policy gate routes on
intent (`auto` / `ask` / `reject`), and `ask_if` conditions escalate otherwise
automatic cases when a flag matches. The same file also drives the tool-level
approval gate: read tools always run free; write tools run only when the policy
says `auto` — or when a human has approved the specific case.

Volunteers edit YAML, not Python. When they decide address changes should
require approval, they change one line — and the agent's behavior changes.

## Belt and braces: LLM proposes, code guarantees

During testing our eval harness caught something uncomfortable: a sign-up email
mentioning an asthma inhaler sailed through as `auto`. The triage model had
simply... not set the `medical` flag that time. Confidence was 0.97. It didn't
matter.

For a child-safety escalation, "most of the time" is not an architecture. So we
added a deterministic backstop: a keyword scan over subject and body that re-adds
the `medical` flag if the model missed it. The LLM proposes; code guarantees.
Since then, the escalation has never been skipped — not once, in any run.

The same harness caught two subtler bugs earlier: polite follow-up emails about
fee waivers being classified as routine questions (a silent autonomy leak — fixed
with a prompt rule, verified by regression eval), and models emitting `flags:
null` instead of an empty list (a pydantic validator now normalizes it).

## What the agent actually does

Overnight, unattended, ClubSteward processes the club inbox folder:

- **Triages** every mail (intent, facts, confidence, flags)
- **Updates the member register** — sign-ups, address and email changes
- **Drafts warm replies** into an outbox — nothing is ever sent automatically
- **Queues real judgment calls** as decision cards: original mail, extracted
  facts, the agent's proposal, and the exact policy line that triggered the
  escalation
- **Discards spam** silently
- **Remembers families** — persistent per-member sessions mean the agent recalls
  last week's instalment plan when a parent writes again
- **Reports itself** — an audit log and a run summary: 10 mails, ~40k tokens,
  about one euro-cent per night

Fail-closed everywhere: unknown intents are queued, unknown tools require
approval, lookups happen before writes, and the agent asks members for missing
data instead of inventing it. In one recorded run it flagged that a claimed
sibling "wasn't in the register" rather than granting a sibling discount.

## Why no cloud

Our users are volunteers with a laptop. So the whole thing runs locally:
Strands Agents SDK, GLM via LiteLLM's OpenAI-compatible provider, folders in,
folders out. No accounts, no cloud bill, no login-walled scraping. Judges can
clone the repo and replay a recorded real session without any API key — clearly
labeled as recorded, because a replay must never masquerade as live.

## What we learned

1. **Autonomy is a spectrum you can data-drive.** For groups — clubs, PTAs,
   small nonprofits — the policy file IS the product.
2. **Eval before you trust.** Our nine-mail labeled corpus caught every real bug
   we shipped, within one run each time.
3. **Safety-critical escalations get deterministic backstops.** Model attention
   is a wonderful thing to not depend on.

The repo (`<repo-url>`, MIT) has the full demo: ten synthetic club emails, a
one-command end-to-end run, and a replay mode for anyone without an API key.

*Built with the Strands Agents SDK for the Agents for Humans Hackathon.*
