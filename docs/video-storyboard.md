# ClubKeeper — Demo Video Storyboard (≤ 5 min, target 3:30)

Structure per hackathon judging: Problem → Audience → Live demo (end-to-end) → Why it matters.
Screen recording + voiceover (no camera needed, officially allowed). English.

---

## 0:00–0:25 — HOOK / PROBLEM (voiceover over static shots)

- Visual: slow pan over a messy inbox folder; counter "47 unread".
- VO: "Every community club runs on the same scarce resource: a volunteer willing to
  be the secretary. Sarah spends six hours a week on member emails. Sign-ups.
  Address changes. Fee questions. And once a month — a letter that needs a human heart,
  not a template."

## 0:25–0:45 — INTRODUCING CLUBKEEPER (title card + architecture flash)

- Visual: architecture.svg (2s), then terminal.
- VO: "ClubKeeper is an agent built with the Strands Agents SDK. It runs at night,
  does the repetitive 80%, and hands Sarah only the decisions that deserve her judgment."

## 0:45–2:45 — LIVE DEMO (real terminal, sped up 2x where idle)

1. `uv run python scripts/reset_demo.py` — "Nine emails arrive overnight."
2. `uv run python -m clubkeeper.pipeline` — show live output:
   - "signup → AUTO", "address change → AUTO", "question → AUTO"
   - "hardship waiver → QUEUED", "cancellation → QUEUED", "complaint → QUEUED"
   - "spam → DISCARDED"
   - run summary line: tokens, cost (~€0.01)
   - VO during: "No human touched any of this. The agent read the policy file —
     a YAML the club edits — updated the member register, and drafted replies."
3. Show `demo/data/outbox/` — open the welcome draft (Irena) — VO: "Notice: it asked
   Daniel to confirm his son's record instead of guessing a sibling discount."
4. `uv run python -m clubkeeper.decide` — the three decision cards:
   - hardship (Kwame's mother) → show mail + policy reason → approve with instruction
     "offer 50% reduction + instalments"
   - cancellation (Noah) → approve
   - complaint → approve with instruction "apologize, promise coach escalation"
   - VO: "Three decisions, ninety seconds. Sarah stays the human in the loop —
     on exactly the things that need one."
5. Show updated register.csv (M007 Irena added), the hardship reply draft
   (references the instalment plan), activity.log lines.

## 2:45–3:15 — THE MEMORY BEAT (differentiator)

- Re-run with mail 09 (Miriam's follow-up): agent remembers the instalment plan,
  answers consistently, asks for Yaw's details.
- VO: "Because every member has a persistent session, the agent remembers last week's
  promises. Volunteers don't have to."

## 3:15–3:45 — HOW IT'S BUILT (Strands depth, fast)

- Flash: policy.yaml (10 rules), interventions.py classifier (15 lines), README section.
- VO: "The entire governance model is thirty lines of YAML driving the SDK's
  Human-in-the-Loop intervention. Read tools run free. Writes need policy or human
  approval. Unknown tools fail closed. No cloud, no accounts — it runs on a laptop
  for about a cent a night."

## 3:45–4:00 — CLOSE

- Visual: outbox full, empty inbox, decision queue cleared.
- VO: "Six hours a week back for every Sarah in every club. That's an agent for humans."
- Card: repo URL + "Built with Strands Agents SDK · GLM by Z.ai"

---

## Production notes

- Record: `asciinema` or OBS at 1920x1080, 2x speed for idle parts, real-time for decide CLI.
- Terminal font ≥ 16pt; use `grep -v reasoningContent`-style clean output (pipeline already clean).
- The decide CLI input prompts must be visible — record in real time there.
- Voiceover: record separately (Audacity), Kosi reads; or TTS for draft, re-record final.
- Keep total ≤ 5:00 hard limit; target 3:30–4:00.
