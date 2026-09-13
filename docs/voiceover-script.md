# ClubSteward — Voiceover Script v4 (EN, word-for-word)

**v4, 13.09.** — GLM-Referenzen entfernt (AWS-lastige Jury — Modell bewusst ungenannt, jetzt
„powered by any LLM"; Close nur noch „built with Strands"). YAML-Sätze korrigiert: „…not code
that the league wrote" (Reihenfolge = hörbar langsamer), Karnevalsverein hat **eigenes** YAML
(nicht „same YAML file" — anderer Verein, andere Policy).

**v3, 13.09.** — Demo-Club gewechselt: **SV Grünwald → Maplewood Little League** (EN-Club,
passend zur EN-Narration). Persona: **Dana** (Player Agent, Maplewood — konsistent mit den
Draft-Signaturen auf dem Screen). NEU: Segment 07 mit deutschem Dilemma (KG Rheinklause,
in derselben Stimme vorgelesen — der Multilingual-Beweis). Stimme: **de-DE-SeraphinaMultilingualNeural**
(Kosi-Freigabe 13.09., 5★). Video: komplett neuer Playwright-Cut (v2-Video bleibt Fallback).

Target: ~4:30 at natural pace (150 wpm), hard limit 5:00. Timings follow the v2 beat skeleton;
final timing comes from the rendered segments. [PAUSE] = 1s beat. Screen cues in (parentheses) —
do not read aloud.

---

## [0:00] HOOK (24s · Segment 01-hook)

(Slow pan: hero page, then the inbox list with 10 English mails)

Every community club runs on the same scarce resource:
a volunteer willing to be the secretary. [PAUSE]
Dana spends six hours a week on league emails.
Sign-ups. Schedules. Fee questions.
And once a month — a mail that needs a human heart,
like a mom, recently laid off, asking for help with the season fee.

## [0:25] INTRODUCING CLUBSTEWARD (18s · Segment 02-intro)

(Hero "How it works" cards, then the console with the six club chips)

ClubSteward is an agent that runs the club's inbox. [PAUSE]
Built on the Strands Agents SDK, powered by any LLM —
and it hands Dana only the decisions that deserve her judgment. [PAUSE]
Any club. Any language.

## [0:45] RESET + THE INBOX (24s · Segment 03-reset)

(Click "Reset data" — ten mails appear in the inbox)

Ten mails arrived for Maplewood Little League —
every one a scenario a real league board deals with every season. [PAUSE]
Watch what the agent does on its own — and where it stops.

## [1:10] STEP MODE — THE ESCALATION (38s · Segment 04-step)

(▶ Process next mail. Left: the mail. Right: the analysis.)

A mom registers her son for T-Ball. Routine — [PAUSE]
except for one word: EpiPen. [PAUSE]
The agent flags it medical, and the league's own policy
stops it in its tracks: a human decides. [PAUSE]
That rule is one line of YAML — not code that the league wrote. [PAUSE]

(Next step: a picture-day question → draft appears on the right)

And the routine ones? A picture-day question —
answered, drafted, register checked. No human touched it.

## [1:50] THE MORNING — HUMAN DECISIONS (46s · Segment 05-morning)

(Scroll to "Decisions for you" — the queued cards)

Morning. Each card tells Dana three things:
what the mail said, what the agent proposes —
and exactly why it's asking. [PAUSE]

(Open Tanya's hardship card, click "Approve + instruct", type)

Tanya was laid off in January; her daughter lives for Majors season. [PAUSE]
Dana adds one instruction — a partial scholarship,
plus credit for weekends running the snack shack — [PAUSE]
and the agent writes the reply. Warm, correct,
in the league's own voice, in seconds.

## [2:40] OUTBOX — NOTHING SENDS ITSELF (24s · Segment 06-outbox)

(Outbox: first pair open — incoming mail left, draft right)

Nothing is ever sent automatically. [PAUSE]
Dana reviews every draft next to the mail it answers —
and because every member has a persistent session,
the agent remembers what it promised last week. Volunteers don't have to.

## [3:05] ANY LANGUAGE — THE GERMAN CLUB (24s · Segment 07-anylanguage)

(Hard cut: console switches to KG Rheinklause — German decision cards,
carnival-purple branding. Render EN and DE parts as separate files!)

And any language? Watch. [PAUSE]

(Seraphina reads the German mail excerpt natively — on screen: the mail)

»Ich bin seit März in Kurzarbeit. Gibt es eine Ermäßigung
oder Ratenzahlung? Ich bin seit elf Jahren dabei —
und würde ungern pausieren.« [PAUSE]

(Same voice, back to English — decision card stays on screen)

Same agent. A different club, with its own YAML file —
and the board reads its decision cards in German. Nothing reconfigured.

## [3:30] RUN NIGHT + STOP (26s · Segment 08-runnight)

(Click "Run night" — the log streams. Then click Stop.)

Prefer to let the whole night run at once? One click. [PAUSE]
And if Dana needs to leave — stop is one click too.
The remaining mails simply wait in the inbox.

## [3:55] HOW IT'S BUILT (26s · Segment 09-built)

(policy.yaml with the ask_if lines, register, hero live stats)

The entire governance model is one YAML file,
driving the SDK's Human-in-the-Loop intervention. [PAUSE]
Read tools run free. Writes need policy or a human.
Unknown tools fail closed. [PAUSE]
No cloud. No accounts. About one cent per night.

## [4:20] CLOSE (16s · Segment 10-close)

(Hero page, full outbox, "Inbox zero 🎉")

Six hours a week back — for every Dana, in every club. [PAUSE]
That's an agent for humans. [PAUSE]
ClubSteward — built with Strands.

---

## Recording notes

- ≈ 560 words; rendered runtime ~3:30 (Seraphina liegt über 150 wpm — gemessene Werte in
  `docs/voiceover-v4/`, nicht die [t]-Stamps oben). Hard limit 5:00.
- Voice: `de-DE-SeraphinaMultilingualNeural` (edge-tts; Kosi-Freigabe 13.09., 5★ —
  runner-ups: en-US-Emma 4★, en-US-Ava 3.8★). Samples: `C:\Dev\derKosi\voice-samples\`.
- **Segment 07 is bilingual**: render `07-anylanguage-en1` (intro), `07-anylanguage-de`
  (German excerpt), `07-anylanguage-en2` (outro) as THREE files, concat with beats —
  guarantees the clean accent switch instead of relying on auto-language detection.
- Old segments `01…09` in `docs/voiceover/` belong to v2 (SV Grünwald) — keep until
  v2 video is validated, then replace with the new set + rebuild `list.txt` (10 segments).
- Emphasis words: **one word: EpiPen**, **not code**, **never sent automatically**,
  **fails closed**, **one cent**, **seit elf Jahren dabei**.
- Production prerequisite: run `kg-rheinklause` pipeline once BEFORE recording so the
  German decision cards exist (console beat 07 shows them, not a run).
- EN captions on YouTube. German UI now appears only in beat 07 — that IS the feature.
