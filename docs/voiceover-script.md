# ClubSteward — Voiceover Script (word-for-word, EN)

Target: ~3:45 at natural pace. Timings match docs/video-storyboard.md.
[PAUSE] = 1s beat. Screen cues in (parentheses) — do not read aloud.

---

## [0:00] HOOK (22s)

(Slow pan over inbox folder, counter "47 unread")

Every community club runs on the same scarce resource:
a volunteer willing to be the secretary. [PAUSE]
Sarah spends six hours a week on member emails.
Sign-ups. Address changes. Fixture questions.
And once a month — a letter that needs a human heart,
like a single parent asking for a fee waiver.

## [0:25] INTRODUCING CLUBSTEWARD (20s)

(Architecture diagram, 2 seconds, then terminal title)

ClubSteward is an agent that runs the club's inbox overnight. [PAUSE]
It's built on the Strands Agents SDK,
and it hands Sarah only the decisions that deserve her judgment.

## [0:45] LIVE DEMO — THE NIGHT RUN (55s)

(Terminal: reset_demo.py, then pipeline)

Nine emails arrived overnight. Watch what happens. [PAUSE]
(runs)

The agent reads every mail —
and its own club policy decides what it may do alone. [PAUSE]

Sign-up? Automatic. Address change? Automatic.
The register updates itself, and warm replies land in the outbox. [PAUSE]

This one mentions a fee waiver — money and empathy.
The agent won't touch it. It queues a decision for Sarah. [PAUSE]

Same for the mid-season cancellation, and the complaint. [PAUSE]

And the spam? Gone. Silently.

## [1:55] THE ESCALATION BEAT (25s)

(Scroll up to the medical signup line)

Now watch this one closely. [PAUSE]
It's a sign-up — the same kind that ran automatically a minute ago.
But this one mentions an asthma inhaler. [PAUSE]
The agent flagged it "medical", and the club's own policy rule
stops it in its tracks: a human decides. [PAUSE]
That rule is one line of YAML the club wrote — not code.

## [2:20] THE MORNING — HUMAN DECISIONS (35s)

(Decide CLI, decision cards appear one by one)

Morning. Five decisions are waiting — each one a card:
the original mail, what the agent understood,
what it proposes, and exactly why it's asking. [PAUSE]

Sarah approves the hardship case with one instruction:
"fifty percent reduction, and offer instalments." [PAUSE]

The agent writes the reply — warm, correct, done in seconds. [PAUSE]

The rest: approve, approve, approve. [PAUSE]

Inbox zero. The club ran itself overnight.
Sarah made the five calls that mattered.

## [2:55] THE MEMORY BEAT (20s)

(Second run with the follow-up mail)

And when the same family writes again next week,
ClubSteward remembers the instalment plan it proposed —
because every member has a persistent session. [PAUSE]
Volunteers don't have to keep promises in their heads.

## [3:15] HOW IT'S BUILT (20s)

(policy.yaml on screen, then intervention code)

The entire governance model is thirty lines of YAML,
driving the SDK's Human-in-the-Loop intervention. [PAUSE]
Read tools run free. Writes need policy or human approval.
Unknown tools fail closed. [PAUSE]
No cloud. No accounts. About one cent per night.

## [3:35] CLOSE (15s)

(Full outbox, cleared queue, run summary)

Six hours a week back — for every Sarah, in every club. [PAUSE]
That's an agent for humans. [PAUSE]

ClubSteward — built with Strands and GLM.
Link in the description.

---

## Recording notes

- Natural pace ≈ 150 wpm; this script ≈ 560 words ≈ 3:45.
- If runs take longer on camera, cut the memory beat narration shorter (it's the flexible block).
- Emphasis words: **only**, **won't touch it**, **one line of YAML**, **fails closed**, **one cent**.
- German accent is fine — clarity over polish; judges read subtitles too (add EN captions on YouTube).
