# ClubSteward — Demo Video Storyboard v2 (≤ 5 min, target ~4:00)

**v2, 11.09.** — komplett auf die **Web-Console** umgestellt (alter Terminal-Beats-Plan ist obsolet).
Screen-Recording: Safari 1440×900, Console `/app?club=sv-gruenwald`. EN-Voiceover;
**das deutsche UI ist ein Feature** (Tenant-Sprache) — YouTube-Untertitel EN empfohlen.

Struktur nach Judging-Schema: Problem → Audience → Live-Demo (end-to-end) → Why it matters → How it's built.

Demo-Club: **SV Grünwald** (deutsch, 12 Mails, kompletter Policy-Satz inkl. medical / ask_if / offer / Spam).

---

## 0:00–0:25 — HOOK / PROBLEM (über statische Shots)

- Visual: Hero-Page mit Live-Stats; dann langsamer Scroll über das **Inbox-Panel** (12 reale deutsche Vereins-Mails).
- VO: "Every community club runs on the same scarce resource: a volunteer willing to be
  the secretary. Sarah spends six hours a week on member emails. Sign-ups. Address
  changes. Fee questions. And once a month — a letter that needs a human heart,
  not a template."

## 0:25–0:45 — INTRODUCING CLUBSTEWARD (15–20 s)

- Visual: Hero „How it works"-Karten (2–3 s je), dann Console mit den **6 Vereins-Chips** (deutscher Karnevalsverein, Fußballverein, Nachbarschaftsverein, US Little League, US PTA, spanische Vecinos-Asociación).
- VO: "ClubSteward is an agent that runs the club's inbox. Built on the Strands Agents
  SDK, powered by GLM — and it hands Sarah only the decisions that deserve her judgment.
  Any club. Any language."

## 0:45–1:10 — RESET + DIE INBOX (25 s)

- Visual: Klick auf **↺ Reset data** → Bestätigen → 12 Mails landen in der Inbox, alle Zähler auf Startzustand.
- VO: "Twelve mails arrived for SV Grünwald — every one a scenario a real board
  deals with weekly. Watch what the agent does on its own — and where it stops."

## 1:10–2:05 — STEP-MODUS: AUTO vs. ESKALATION (55 s — der Kernbeat)

- Visual: Klick auf **▶ Process next mail**. Zweispaltiges Panel: **links die Mail, rechts die Live-Analyse**.
  1. Mail 01 (U10-Anmeldung) → Analyse erscheint: Intent-Chip `signup`, Konfidenz, Fakten —
     dann **Flag `medical` leuchtet auf** und das Ergebnis ist **QUEUED** („⚖️ filed as decision —
     approve it in Decisions for you").
     - VO: "A father signs up his son for the U10s. Routine — except for one word: asthma.
       The agent flags it medical, and the club's own policy stops it in its tracks.
       A human decides. That rule is one line of YAML the club wrote — not code."
  2. Mail 03 (Trainingszeiten-Frage) → **AUTO**: rechts erscheint der fertige **Entwurf**
     („✉️ Draft — ready in the outbox").
     - VO: "And the routine ones? A fixtures question — answered, drafted, register checked.
       No human touched it."
- Hinweis: die Warte-Zeilen („🧠 the agent reads the mail…") rotieren live — gut für Tempo.

## 2:05–2:55 — DECISIONS: DER MORGEN (50 s)

- Visual: Scroll zu **⚖️ Decisions for you** (Badge „N pending"). Karten auf Deutsch:
  - 02 Kuendigung (mitten in der Saison), 04 Ratenzahlung (Hardship), 07 unsicher (Zukunft Emir),
    12 Adresse nur teilweise (`billing_address_unclear`), ggf. 09 Angebot (neuer `offer`-Intent).
  - Jede Karte zeigt: Mail-Betreff, Intent-Chip, Konfidenz-Prozent, 💡 Zusammenfassung,
    **„Agent proposes"**-Box, Fakten-Grid und die **„Warum du?"**-Zeile mit dem exakten Policy-Grund.
- Aktion: Karte 04 öffnen → **✎ Approve + instruct** → eintippen:
  „Bietet Emma Familie drei Raten zu je 32 € an — und bestätigt den Platz."
  → Spinner „the agent is executing…" → Toast „✓ Approved with your instructions — done".
- VO: "Morning. Each card tells Sarah three things: what the mail said, what the agent
  proposes — and exactly why it's asking. Sarah adds one instruction — an instalment
  plan for a family that's short this month — and the agent writes the reply.
  Warm, correct, in the club's voice, in seconds."

## 2:55–3:20 — OUTBOX: SIDE-BY-SIDE (25 s)

- Visual: **📤 Outbox drafts** → erstes Paar ist aufgeklappt: **links die eingegangene Mail,
  rechts der Entwurf** — inkl. Signatur-Zusatz „(Entwurf erstellt von ClubSteward … vom Menschen freigegeben)".
- VO: "Nothing is ever sent automatically. Sarah reviews every draft next to the mail it
  answers — and because every member has a persistent session, the agent remembers what
  it promised last week. Volunteers don't have to."

## 3:20–3:45 — RUN NIGHT + STOP (25 s)

- Visual: Klick **🌙 Run night** → Button wird zu **⏹ Stop** → Log streamt Mail für Mail →
  Klick auf ⏹ → „Stopped — remaining mails stay in the inbox".
- VO: "Prefer to let the whole night run at once? One click. And if Sarah needs to leave,
  stop is one click too — the remaining mails simply wait in the inbox."

## 3:45–4:10 — HOW IT'S BUILT (25 s)

- Visual: policy.yaml (die `ask_if:`-Zeilen), dann Register-Panel (neue Mitglieder drin),
  dann Hero-Live-Stats.
- VO: "The entire governance model is a thirty-line YAML file driving the SDK's
  Human-in-the-Loop intervention. Read tools run free. Writes need policy or a human.
  Unknown tools fail closed. No cloud, no accounts — about one cent per night."

## 4:10–4:25 — CLOSE (15 s)

- Visual: Hero-Page mit Live-Stats (Mails handled, Outbox gefüllt), Outbox „Inbox zero 🎉".
- VO: "Six hours a week back — for every Sarah, in every club.
  That's an agent for humans. ClubSteward — built with Strands and GLM."
- Card: repo URL + „Built with the Strands Agents SDK · GLM by Z.ai".

---

## Production notes

- **Recording:** OBS oder QuickTime, Region 1440×900, 30 fps. Console-Schrift ist groß genug
  (Karten 13.5–17 px); Browser-Zoom 110 % ist optional für mehr Präsenz.
- **Step-Panel-Wartezeit:** jede LLM-Stufe dauert 10–30 s — fürs Video **nicht** beschleunigen
  beim ersten Step (Suspense!), weitere Steps 2–4× timelapse.
- **Die Warte-Zeilen rotieren alle 8 s** — bei langen Wartezeiten im Schnitt auf die Analyse springen.
- **Typing-Beat** (Approve + instruct) in Echtzeit lassen — das ist der „Human in the loop"-Moment.
- **docs/demo.gif** (Terminal-Replay) optional als 2–3 s B-Roll im „How it's built"-Block
  („…or run it headless from the CLI"). Der Replay-Modus existiert weiterhin ohne API-Key.
- Voiceover: Segmente in `docs/voiceover/` (edge-tts, en-US-AriaNeural oder Freigabe-Alternative),
  Master via concat-Skript; Skript: `docs/voiceover-script.md`.
- Hard limit 5:00 — die Memory-Zeile im Outbox-Beat ist der kürzbare Block.
