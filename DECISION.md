# DECISION — Concept Selection (Phase 1)

Date: 2026-08-23 · Status: **RECOMMENDATION PENDING KOSI'S VETO** (veto window: first 3 days of Phase 2)

All three concepts share one architecture substrate, so build risk is similar for whichever wins:
**local folder = inbox → batch agent pipeline → decision queue (only real judgment calls) → drafts in outbox + updated structured data.**
No cloud, no APIs behind logins, no scraping, no costs. Jurors run it from README via `uv sync`.

---

## Concept A — "The Deadline Guardian" (Track: Everyday Agents)

- **Problem:** People lose money to auto-renewing contracts (gym, phone, insurance, streaming) because cancellation deadlines (esp. German-style notice periods) slip by. Renewal price hikes go unnoticed.
- **Audience:** Anyone with 10+ recurring contracts; extremely credible in DE/EU, universal enough for EN framing.
- **Agent does autonomously:** watches a documents folder (PDFs/scans/emails exported), extracts contract parties, renewal dates, notice periods, price changes; maintains a deadline ledger; drafts ready-to-send cancellation letters well before deadlines; files everything.
- **Asks human only when:** (a) cancellation would forfeit a benefit (loyalty discount), (b) ambiguous terms (two plausible notice dates), (c) price increase below/above a threshold the human set — "auto-object below €5, ask above".
- **Strands depth:** custom doc-tools (parsing ledger state), HumanInTheLoop intervention with custom classifier (our policy), session/memory across runs (ledger persistence), scheduled background runs, observability (decision trace per contract).
- **Feasibility to Sep 7:** good; main risk = PDF extraction quality (mitigate: demo corpus in .txt/.eml, PDF via pymupdf best-effort).
- **Demo dramaturgy:** drop 5 letters → ledger builds itself → one "price hike detected, cancel or negotiate?" decision → finished cancellation letter appears. Money saved, on camera.

## Concept B — "Cashflow Chaser" (Track: Professional Agents)

- **Problem:** Freelancers/small studios hate dunning: tracking who paid, writing escalating reminders, deciding when to get firm. Unpaid invoices quietly kill cashflow.
- **Audience:** solo professionals & micro-businesses (huge, global, relatable).
- **Agent does autonomously:** reads invoices/ledger from a local bookkeeping export (CSV/JSON), matches payments, detects overdue, sends (drafts to outbox) tier-1 friendly reminders on schedule, updates ledger, logs every touch.
- **Asks human only when:** escalation to tier-2/3 (firm tone), writing off small amounts, contradiction (client claims paid, bank says no), discount/deal offers.
- **Strands depth:** multi-agent (triage agent + drafter agent as tools), policy-driven HITL (tier thresholds), sessions per debtor thread, evals (did reminder tone match tier?), traces per case.
- **Feasibility to Sep 7:** very good (structured data easier than PDF).
- **Demo dramaturgie:** 12 invoices, 3 overdue → agent quietly reminds, catches a "we paid already" contradiction, asks ONE escalation question, outbox fills. Ending: aging report before/after.

## Concept C — "ClubSteward" (Track: Good Neighbor Agents) ← RECOMMENDED

- **Problem:** Community sports/hobby clubs (Vereine, leagues, PTAs, scout troops) run on a few burned-out volunteers. The club secretary drowns in member emails: sign-ups, cancellations, address changes, fee hardship requests — repetitive, but each needs judgment and a kind, correct reply.
- **Audience:** volunteer club committees worldwide (in DE alone ~570k Vereine; US: leagues, PTAs, HOAs). The jury *knows* someone like this.
- **Agent does autonomously:** processes a shared club inbox folder overnight; classifies lifecycle events; updates the member register (CSV) correctly; drafts warm, on-brand replies into the outbox; applies club rules (fee tables, seasons, waiting lists) from a small policy file the club edits — not code.
- **Asks human only when:** hardship/fee-waiver requests (money + empathy decisions), ambiguous cancellation timing (mid-season?), contradictory member records, anything the policy file marks `ask`.
- **Strands depth (highest of the three):** multi-agent pipeline (triage → act → draft, orchestrated as agents-as-tools or graph), HumanInTheLoop with **custom classifier = club policy** (the creative centerpiece: policy-as-data, not code), memory (member context across sessions), session management for overnight batches, full decision traces, optional Evals run on a labeled corpus.
- **Feasibility to Sep 7:** very good (plain-text emails; no PDF parsing risk). Demo corpus: 8–10 realistic EN mails (signup kid with medical note, address change, cancellation, hardship, "did my kid get in?", duplicate member...).
- **Demo dramaturgy:** evening: inbox fills. Overnight: agent works silently — terminal shows 8 processed, 0 interruptions… then 2 decision cards: hardship waiver + mid-season cancellation. Secretary answers both in seconds. Morning: member register updated, 8 replies drafted. Closing line: "Your club ran itself. You made two calls."

---

## Scoring matrix (1–5, 5 = best for winning)

| Criterion (weight for judging) | A Deadline Guardian | B Cashflow Chaser | C ClubSteward |
|---|---|---|---|
| Demo impact on video            | 4 | 5 | 5 |
| Feasibility by Sep 7            | 4 | 4.5 | 4.5 |
| Impact credibility              | 4 | 4 | **5** |
| Originality                     | 3 | 3.5 | **5** |
| Strands depth                   | 4 | 4.5 | **5** |
| **Sum**                         | **19** | **21.5** | **24.5** |

## Recommendation: C — ClubSteward (Good Neighbor Agents)

Reasoning:
1. **Originality:** subscription/dunning agents already exist in OSS and SaaS (verified via search: multiple subscription-audit agents, nonprofit triage agents). Nobody serves volunteer club secretaries — yet it's the purest expression of the hackathon theme: the agent *serves a group*, runs quietly, and surfaces only decisions deserving human warmth/judgment.
2. **Theme fit:** "only surface when a real decision is needed" is the product's soul — hardship waivers are genuinely human decisions. Easy to make judges feel it.
3. **Strands showcase:** policy-as-data classifier on top of the SDK's HITL intervention + multi-agent pipeline = creative AND deep use of Strands (two judging criteria at once).
4. **Build risk:** same substrate as A/B, but plain-text emails avoid A's PDF risk. Timeline comfortable.
5. **Fallback option:** architecture is shared — if C stumbles, B is a reskin away (invoices instead of emails). That de-risks Phase 2.

Risks / mitigations:
- Name "ClubSteward" needs a quick trademark/site check before repo goes public (working title only).
- Demo must be English (jury), while the story nods to German "Verein" culture (authentic, memorable).
- Multi-player privacy: demo corpus is fully synthetic; no real member data anywhere.

**Default:** Build ClubSteward. Kosi has veto while Phase 2 runs < 3 days — see `PROGRESS.md` for the deadline.
