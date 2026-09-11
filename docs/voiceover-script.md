# ClubSteward — Voiceover Script v2 (EN, word-for-word)

Target: ~4:05 at natural pace (150 wpm). Timings match docs/video-storyboard.md **v2 (Web-Console)**.
[PAUSE] = 1s beat. Screen cues in (parentheses) — do not read aloud.

---

## [0:00] HOOK (24s · Segment 01-hook)

(Slow pan: hero page, then the inbox list with 12 German mails)

Every community club runs on the same scarce resource:
a volunteer willing to be the secretary. [PAUSE]
Sarah spends six hours a week on member emails.
Sign-ups. Address changes. Fee questions.
And once a month — a letter that needs a human heart,
like a single parent asking for a fee waiver.

## [0:25] INTRODUCING CLUBSTEWARD (18s · Segment 02-intro)

(Hero "How it works" cards, then the console with the six club chips)

ClubSteward is an agent that runs the club's inbox. [PAUSE]
Built on the Strands Agents SDK, powered by GLM —
and it hands Sarah only the decisions that deserve her judgment. [PAUSE]
Any club. Any language.

## [0:45] RESET + THE INBOX (24s · Segment 03-reset)

(Click "Reset data" — twelve mails appear in the inbox)

Twelve mails arrived for SV Grünwald —
every one a scenario a real club board deals with weekly. [PAUSE]
Watch what the agent does on its own — and where it stops.

## [1:10] STEP MODE — THE ESCALATION (38s · Segment 04-step)

(▶ Process next mail. Left: the mail. Right: the analysis.)

A father signs up his son for the U10s. Routine — [PAUSE]
except for one word: asthma. [PAUSE]
The agent flags it medical, and the club's own policy stops it in its tracks:
a human decides. [PAUSE]
That rule is one line of YAML the club wrote — not code. [PAUSE]

(Next step: a fixtures question → draft appears on the right)

And the routine ones? A fixtures question —
answered, drafted, register checked. No human touched it.

## [1:50] THE MORNING — HUMAN DECISIONS (50s · Segment 05-morning)

(Scroll to "Decisions for you" — German cards)

Morning. Each card tells Sarah three things:
what the mail said, what the agent proposes —
and exactly why it's asking. In the club's own language. [PAUSE]

(Open the instalment card, click "Approve + instruct", type)

Sarah adds one instruction —
an instalment plan for a family that's short this month — [PAUSE]
and the agent writes the reply. Warm, correct,
in the club's voice, in seconds.

## [2:45] OUTBOX — NOTHING SENDS ITSELF (24s · Segment 06-outbox)

(Outbox: first pair open — incoming mail left, draft right)

Nothing is ever sent automatically. [PAUSE]
Sarah reviews every draft next to the mail it answers —
and because every member has a persistent session,
the agent remembers what it promised last week. Volunteers don't have to.

## [3:15] RUN NIGHT + STOP (26s · Segment 07-runnight)

(Click "Run night" — the log streams. Then click Stop.)

Prefer to let the whole night run at once? One click. [PAUSE]
And if Sarah needs to leave — stop is one click too.
The remaining mails simply wait in the inbox.

## [3:45] HOW IT'S BUILT (26s · Segment 08-built)

(policy.yaml with the ask_if lines, register, hero live stats)

The entire governance model is a thirty-line YAML file,
driving the SDK's Human-in-the-Loop intervention. [PAUSE]
Read tools run free. Writes need policy or a human.
Unknown tools fail closed. [PAUSE]
No cloud. No accounts. About one cent per night.

## [4:10] CLOSE (16s · Segment 09-close)

(Hero page, full outbox, "Inbox zero 🎉")

Six hours a week back — for every Sarah, in every club. [PAUSE]
That's an agent for humans. [PAUSE]
ClubSteward — built with Strands and GLM.

---

## Recording notes

- ≈ 570 words ≈ 4:05 at 150 wpm. Hard limit 5:00.
- Segments: `01-hook … 09-close` in `docs/voiceover/` (edge-tts; Stimme = Freigabe Kosi:
  en-US-AriaNeural oder Guy/Jenny/Sonia — siehe 00-preview-note.mp3).
- Emphasis words: **only**, **one word: asthma**, **not code**, **never sent automatically**, **fails closed**, **one cent**.
- EN captions on YouTube (German UI on screen — that's the multilingual feature, say it in S5).
