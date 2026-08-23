# builder.aws.com Post Drafts (bonus points; "Agents for Humans" in title)

Three drafts, 500–900 words each when fleshed out. Pick 1–2 to publish.

---

## Draft 1 — "Agents for Humans: How We Made a YAML File the Brain of an AI Agent"

Angle: policy-as-data + Strands HumanInTheLoop custom classifier. The technical star post.

Outline:
1. Hook: volunteers can't code, but they CAN edit rules. What if the club's policy
   file literally was the agent's approval classifier?
2. The stack: Strands Agents SDK, GLM (Z.ai) via LiteLLM (OpenAI-compatible), zero AWS
   spend, local files. Why: the audience is a volunteer with a laptop.
3. The mechanism: HumanInTheLoop intervention + custom classifier function —
   read tools free, writes gated by policy/autonomy, fail-closed on unknowns.
   Code snippet: the 25-line classifier + 10-line YAML.
4. What surprised us: LLM-cautiousness pays off — the agent asked a father to confirm
   his son's membership rather than inventing a sibling discount (honest beats fluent).
5. Takeaway: autonomy is a spectrum you can data-drive. For groups (clubs, PTAs,
   small orgs), the policy file IS the product.

## Draft 2 — "Agents for Humans: Building an Agent That Only Interrupts You When It Matters"

Angle: the decision-queue UX; autonomy calibration. The product-feel post.

Outline:
1. Hook: notifications from tools feel like work. We inverted it: the agent works
   at night, interrupts exactly three times, each interruption is a real decision.
2. Night loop: triage (structured output) → policy gate → act. Per-member sessions
   so it remembers promises (instalment plans!) across weeks.
3. The decision cards: what the human sees — original mail, extracted facts, policy
   reason, proposed action, approve/edit/deny. Edit = natural language instructions
   the agent executes.
4. Metrics as trust: run_summary.json — 9 mails, 29k tokens, ~€0.01. Volunteers can
   audit everything: activity.log is the agent's diary.
5. Takeaway: "only surface when a real decision is needed" is a designable property:
   policy gate + risk-tiered tool approval + queue-not-interrupt.

## Draft 3 — "Agents for Humans: What Building a Club Secretary Taught Us About Agent Safety"

Angle: fail-closed design, honesty over fluency, sandboxing. The trust post.

Outline:
1. Hook: an agent that writes to a member register and drafts replies to families
   needs guardrails more than features.
2. Our five: (a) drafts never send; (b) lookup-before-write (no invented members);
   (c) unknown intent → ask, unknown tool → deny; (d) all IO in a demo sandbox
   folder; (e) full audit log + run metrics.
3. Anecdote: the spam mail — classified, discarded, zero human seconds. And the
   agent flagging "brother not in register" instead of granting a discount.
4. Sessions & privacy: member data stays in local files; sessions on-disk per member;
   nothing leaves the machine except the anonymized classification call.
5. Takeaway: for community orgs, trustworthy-by-default beats powerful-by-default.
