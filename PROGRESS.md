# PROGRESS

> **Zustand 11.09.:** Phase 0–3 abgeschlossen, Eval 10/10, SV-Grünwald-Demo-Stand final (3 auto / 7 ask / 1 reject, `_errors` leer). 54 Tests grün. Rest: Video + Voiceover (11./12.09., gemeinsam), Submission 12.09. Nächster Einstieg: `docs/TODO.md` + GH Project-Board (github.com/users/derKosi/projects/5).

## Session 2026-08-23 — Phase 0: Setup & Recon

**Done**
- Repo `~/derKosi/AgentForHumans` initialized (git, uv, Python 3.12, strands-agents 1.53.0 + litellm extra)
- Z.ai access verified: key stored encrypted (sops, `~/.secrets/zai.env`), models endpoint lists glm-4.5 … glm-5.3
- Raw chat smoke test: `glm-5-turbo` answers "SMOKE_OK" (119 tokens)
- Strands smoke test: minimal agent + custom `word_count` tool → agent calls the tool and reports result. `tool_called=True`, exit 0.
  - Gotcha: tool results in `agent.messages` use `{"toolUse": {...}}` content blocks (no `type` field).
  - Gotcha: Z.ai warns `reasoningContent is not supported in multi-turn conversations` — harmless with Chat Completions API.
- Hackathon rules/main/FAQ read; binary checklist in `REQUIREMENTS.md`
- Strands docs recon: HITL intervention (`HumanInTheLoop` with LLM risk classifier + trust memory), Interventions framework, LiteLLM model provider, multi-agent patterns (agents-as-tools, swarm, graph, workflow), GoalLoop plugin, observability (metrics/traces/logs), Evals SDK.
  - Note: SDK is being rebranded "Strands Harness" (monorepo `strands-agents/harness-sdk`); PyPI package `strands-agents` unchanged.

**Learned**
- HITL is a first-class SDK feature (vended intervention) — great fit for the hackathon theme; can be extended with a custom policy layer.
- LiteLLM path for custom OpenAI-compatible providers: `LiteLLMModel(client_args={api_key, api_base}, model_id="openai/<model>")`.

**Blocked / decisions needed**
- none

**Next**
- Phase 1: three concepts + scoring matrix + `DECISION.md` ← done this session, see below

## Session 2026-08-23 — Phase 1: Concept Decision

**Done**
- Originality research (web): subscription-audit agents and generic nonprofit triage agents already exist in OSS; volunteer-club secretary agent = open niche.
- Three concepts worked out (all on shared architecture: local inbox → batch agent → decision queue → outbox + ledger):
  - A) Deadline Guardian (Everyday) — contract renewal/cancellation deadlines
  - B) Concept Cashflow Chaser (Professional) — freelancer dunning
  - C) **ClubKeeper (Good Neighbor) — RECOMMENDED**: club secretary inbox agent with policy-as-data decision layer
- Scoring matrix (demo, feasibility, impact, originality, Strands depth): A 19 · B 21.5 · C 24.5
- `DECISION.md` written with full reasoning + fallback (B shares the architecture)

**Learned**
- The shared substrate makes the concept switchable until ~Sep 1 at near-zero cost.
- HITL custom-classifier + policy-as-data is both the creative centerpiece AND Strands-depth showcase.

**Blocked / decisions needed**
- Kosi's veto on concept C (default: we build C). Veto window: while Phase 2 < 3 days old (until ~Aug 26, 12:00).

**Next**
- Phase 2 build kickoff (architecture skeleton, demo corpus, pipeline skeleton) — started same day, see below

## Session 2026-08-23 — Phase 2 kickoff: ClubKeeper v0.1 end-to-end

**Done**
- Package `clubkeeper/`: models (MailItem, TriageResult, Decision), policy-as-data loader (YAML), config, 5 structured tools (register lookup/update/add, save_draft, log_activity), triage agent (structured output), act agent (tool loop), batch pipeline, human decision CLI.
- Demo corpus: 8 synthetic English club emails covering all intents (signup, address change, hardship, cancellation, question, complaint, spam) + register.csv (6 members) + policy.yaml (Riverside Juniors FC).
- `scripts/reset_demo.py` — restores pristine sandbox from `demo/corpus/`.
- End-to-end verified (real LLM, glm-5-turbo): 8 mails → 5 auto-processed, 3 queued (hardship, cancellation, complaint), spam correctly REJECTED. Then `decide y` approved all 3 → executed, outbox 7 drafts, register updated, activity log written.
- Quality highlights: agent caught that "brother Tomas" is NOT in the register and asked instead of inventing; hardship reply offered concrete options (50% reduction / instalments) with warm tone.

**Learned**
- Z.ai emits `reasoningContent` warnings on multi-turn Chat Completions — harmless noise; filter in logs.
- `Agent.structured_output(PydanticModel, prompt)` works reliably with GLM via LiteLLM `openai/` prefix.
- Decision JSONs + policy_reason give a clean audit trail (judges love this).

**Blocked / decisions needed**
- none (concept C in build; veto window closed)

**Next**
- demo/run_demo.sh (<3 min end-to-end), README with architecture + GIF, tests (unit for policy/tools), Strands depth upgrades: HumanInTheLoop intervention w/ custom classifier replacing manual policy eval, session persistence, multi-agent orchestration polish.

## Session 2026-08-23 (2) — Strands HITL integration + tests + demo script

**Done**
- Read the SDK's actual `strands.vended_interventions.hitl` implementation; integrated it properly:
  - `clubkeeper/interventions.py`: custom `policy_classifier` (HumanInTheLoopClassifier contract) — read tools free; write tools free only under policy `auto` or human `auto_preapproved`; fail-closed otherwise. `ask="stdio"` for interactive mode; trust enabled.
  - Pipeline sets case context (`clubkeeper:case`) in agent state per mail; decide CLI marks approved cases `auto_preapproved` (decision id in audit trail).
  - Act agent now constructed with `interventions=[make_hitl(...)]` — the club YAML literally drives the SDK approval gate.
- Unit tests `tests/test_core.py`: 12 tests, all green (policy loading, evaluate_policy, classifier matrix incl. fail-closed, .eml parsing). No LLM needed.
- `demo/run_demo.sh` — one-command end-to-end (reset → pipeline → decide → morning report), `--interactive` flag for live HITL prompts.
- Full E2E re-run with new architecture: 5 auto / 3 queued / spam rejected → decide approved all 3 → 7 drafts, 7 log entries. EXIT 0.
- Fresh-clone gate: clone → uv sync → 12 tests pass → reset → run_demo syntax OK.
- README rewritten: problem, what it does, policy-as-data, mermaid architecture, quickstart, decisions table, design decisions.

**Learned**
- SDK HITL: `allowed_tools` + `classifier` + `ask="stdio"` + `enable_trust` — classifier contract `(event) -> ClassifierResult`; precedence: negated > trusted > wildcard > allowed > classifier > default-ask.
- Pyright strictness on protocol params: accept `**kwargs` in classifier signature.

**Blocked / decisions needed**
- none

**Next**
- Session persistence (strands session_manager) for multi-day runs, multi-agent polish (agents-as-tools triage→act as true sub-agents), observability/traces, GIF for README, Phase 3 assets (video script, builder.aws draft posts).

## Session 2026-08-23 (3) — Sessions, metrics, Phase-3 assets

**Done**
- Member memory: `act_agent_for()` gives every member a persistent Strands `FileSessionManager` session (demo/data/sessions/). Proven with corpus mail 09 (Miriam's follow-up): agent referenced the earlier instalment plan and handled brother Yaw consistently. Sessions carry across nightly runs.
- Run metrics: `clubkeeper/metrics.py` — run_summary.json with per-mail route, triage/act tokens, tool calls, latency; cost estimate printed at end of pipeline (~€0.009 for 9 mails / 29.6k tokens on GLM). SDK detail: usage lives on `agent.event_loop_metrics.accumulated_usage` (dict), AgentResult carries `.metrics`.
- TriageTokenTracker for per-mail deltas from the cumulative counter.
- Investigated GraphBuilder orchestration; rejected with reasoning (structured triage data would have to round-trip through string node results — the plain two-agent pipeline + policy gate expresses the same topology more honestly). Documented as design decision.
- Architecture diagram: docs/architecture.svg (mermaid-cli, no-emoji variant — renderer chokes on emojis/variation selectors) + architecture.mmd source. Content verified (all nodes/labels/arrows present).
- Phase-3 assets drafted: docs/video-storyboard.md (4 min, problem→demo→memory beat→close), docs/builder-posts-drafts.md (3 angles), docs/devpost-credits-helper.md (copy-paste text for Kosi's registration + $50 credits form, Good Neighbor track).
- REQUIREMENTS.md: architecture diagram + README checked off.
- Fresh-clone gate: 14 tests pass, reset works, docs present.

**Learned**
- mermaid-cli on this VM needs `-p puppeteer-config.json` with `--no-sandbox`; run it from the repo dir (background cwd quirk wrote the first SVG into /tmp/afh-clone).
- Emoji in mermaid labels break rendering here — use plain text labels.

**Blocked / decisions needed**
- none

**Next**
- Decide CLI polish for video (colored decision cards), demo GIF for README, optional: replay mode without API key (judges without Z.ai key), then Phase 3 video recording prep.

## Session 2026-08-23 (4) — Replay mode (no API key) + recorder tests

**Done**
- `clubkeeper/recorder.py`: RunRecorder captures per-step transcript lines, file moves, and artifact diffs (drafts/decisions/register/log) of a REAL run.
- `scripts/record_session.py/.sh`: records pipeline + auto-approved decisions into `demo/recording/session.json` (committed).
- `clubkeeper/replay.py`: replays the recording without any API key — step-by-step transcript, applies artifacts, moves files; every output bracketed by `[RECORDED SESSION — not a live LLM call]`. `--speed=N` flag.
- Fixed: decide-step effects must be captured AFTER execution (begin/end split); final snapshot must be retaken after decide executions (was restoring cleared decision queue).
- Verified end-to-end on a FRESH CLONE with `env -u ZAI_API_KEY`: replay ends with 0 pending decisions, 5 drafts, 9 processed, register updated.
- README: "No API key?" replay section. Tests: 16 (recorder effect capture added).

**Learned**
- Replay = recorded effects + transcript, not video: cheap, inspectable, honest (label requirement from mission brief: replays clearly marked — done via badge lines).
- Diff-based recording automatically stays small: only changed artifacts per step.

**Blocked / decisions needed**
- none

**Next**
- Decide CLI polish (colored cards) for the video, demo GIF, run_demo.sh replay fallback, Phase-3 video recording.

## Session 2026-08-23 (5) — CLI polish, replay fallback, demo GIF

**Done**
- decide.py rewritten: colored decision cards (title bar, subject/from/intent/wants/facts/proposal/why-asked + mail excerpt), colored approval/denial feedback, "Inbox zero" closing line. Non-tty falls back to plain text (CI-safe).
- run_demo.sh: automatic replay fallback when no ZAI_API_KEY/GLM_API_KEY is set — judges get the full experience either way, recording clearly labeled.
- Live-tested the colored CLI: 3 decisions approved, queue empty, closing line shown.
- Demo GIF for README: asciinema recorded the replay (cast verified: all markers present), rendered with agg (monokai, 1.2x) → docs/demo.gif (691x490, ~860 KB), embedded in README with "recorded replay" caption.
- Tooling installed: asciinema 2.4.0 (uv tool), agg 1.9.0 (/tmp/agg — move to ~/.local/bin for reuse).

**Learned**
- agg renders asciinema v2 casts directly; --speed at record time (replay --speed=6) keeps the GIF short.
- GIF from 30 events ≈ 860 KB — fine for GitHub README.

**Blocked / decisions needed**
- none

**Next**
- Move agg binary to ~/.local/bin; optional: regenerate GIF with decide-CLI colors once; Phase 3 (video recording per storyboard) in a fresh session; Phase 4 with Kosi.

## Session 2026-08-23 (6) — Eval harness, prompt fix, Devpost draft, better GIF

**Done**
- Triage eval harness `scripts/eval_triage.py` (+ run_eval.sh): labeled 9-mail corpus, intent accuracy + confidence report, JSON output, exit 1 below 90%.
- First run caught a REAL autonomy bug: mail 09 (hardship follow-up) classified as `question` (=auto route!) — fixed via TRIAGE_SYSTEM prompt rule (any mail touching fee relief/waivers = hardship_waiver, never question). Re-run: **9/9 = 100%**, avg conf 0.97. Reports in docs/triage-eval-report.json.
- Devpost submission text drafted (docs/devpost-submission-draft.md) — all sections per Devpost structure, track: Good Neighbor Agents.
- Decision cards in recording upgraded (subject/from/intent/wants/why-asked box lines); session re-recorded; demo GIF regenerated with cards (1.8 MB).
- agg 1.9.0 moved to ~/.local/bin.

**Learned**
- The eval immediately paid for itself: prompt-level fix + regression protection — great judging story ("eval caught a follow-up misread as routine question = silent autonomy leak").
- Box-drawing chars in recorded lines render fine in agg/monokai.

**Blocked / decisions needed**
- none

**Next**
- Phase 3 video recording (fresh session, per storyboard) & Kosi's registrations (Devpost, AWS Builder ID, optional credits). Phase 4 submission together.

## Session 2026-08-23 (8b) — Medical backstop, eval corpus to 10, recording refreshed

**Done**
- Triage reliability hardening: richer flag instructions in system prompt + per-prompt reminder + **deterministic `safety_flag_check` backstop** (keyword scan re-adds `medical` flag if the LLM misses it — child-safety escalations never depend on model attention alone).
- Unit tests for the backstop (hit + no false positive) → 21 total.
- Eval corpus extended to 10 mails (medical signup included), EXPECTED map updated.
- Recording re-captured: 10 pipeline steps, 5 decide cards incl. the medical escalation ("normally auto, but flag 'medical' matches ask_if condition"). GIF regenerated with the escalation beat (2.2 MB).
- README decisions table + devpost draft + video storyboard updated with the escalation story.

**Learned**
- Non-determinism management: one 0.97-confidence triage run can still drop a flag. For safety-critical escalations: LLM proposes, deterministic code guarantees. That's the "belt and braces" pattern worth a builder.aws paragraph of its own.

**Blocked / decisions needed**
- none

**Next**
- Phase 2 + demo assets complete. Video (fresh session, with Kosi), registrations, Sep 12 submission.

## Session 2026-08-23 (9) — ask_if conditions live (policy escalation engine)

**Done**
- `TriageResult.flags`: special-condition tags extracted by the triage agent (medical, waiting_list, refund, duplicate, legal, ...).
- `evaluate_policy` now evaluates `ask_if`: an auto intent escalates to ask when a triage flag matches a policy condition (word/phrase matching). Escalation reason names the flag AND the matched condition.
- Corpus mail 10 (Yusuf, asthma inhaler): E2E-proven — signup+medical flag → queued with "normally auto, but flag 'medical' matches ask_if condition".
- 3 new unit tests (escalation on medical/waiting_list, stay-auto without flags) → 19 total.
- Robustness: LLMs emit `flags: null` → pydantic before-validator normalizes; eval had dropped to 78% from parse errors, now 100% again (9/9).
- Tried SDK's newer `structured_output_model` constructor path — produced worse classifications (hardship follow-up read as question again); reverted to `Agent.structured_output(model, prompt)` which is deprecated-but-reliable with GLM. Documented here; revisit if SDK fixes.
- Pushed to GitHub (private).

**Learned**
- Deprecated API ≠ worse API: the constructor path lost the system-prompt emphasis for GLM. Eval harness caught the regression within one run — its whole purpose.
- Null-tolerance in pydantic models is mandatory for LLM output.

**Blocked / decisions needed**
- none

**Next**
- Nothing left in Phase 2 scope. Remaining: video (fresh session), Kosi registrations, Phase 4 together (Sep 12).

## Session 2026-08-23 (10) — Multi-club white-label + SaaS stage 1

**Done**
- Multi-club white-label: `clubs/` (Karneval, Fussball, Ortsgemeinschaft — German corpora), club CLI (`list/new/run/decide/status/reset`), `brand.yaml`, policy facts in prompts (no invented fees), German replies (dd272cf).
- International clubs: US Little League (EpiPen escalation), US PTA, Spanish vecinos (complaint fix via multilingual triage); `HOSTING.md` — SaaS stages, tenant isolation by design (48dc360).
- SaaS stage 1: web console (FastAPI hero page + decision cards UI, E2E-proven via API), sqlite storage adapter, Dockerfile, email integration guide (drag&drop today, IMAP/SMTP adapter spec) (29db705).
- `docs/TODO.md` submission checklist (Kosi tasks, video session, Sep 12 submission) (c120961).

**Learned**
- Policy-as-data extends cleanly to multi-tenant: same engine, per-club corpora + brand.yaml — zero engine changes.
- FastAPI decision-cards UI E2E via API tests is enough for stage 1; no SPA needed (KISS).

**Blocked / decisions needed**
- none

**Next**
- Video session with Kosi (early Sep), then Phase 4.

## Session 2026-08-23 (11) — Repo live: CI, Project-Board, Session-Abschluss

**Done**
- `gh auth refresh` durch (Scopes `workflow` + `project`) — der Commit `075c378` (CI: Tests nur PR+v*-Tags, Release nur v*-Tags) wurde gepusht; beide Workflows remote aktiv, kein per-Commit-Run (Kosis CI-Regel).
- GH Project „ClubKeeper" #5 angelegt (github.com/users/derKosi/projects/5): 15 Draft-Items aus docs/TODO.md, board-only — keine Repo-Issues, damit beim Public-Schalten am 12.09. nichts Internes sichtbar wird. CI-Item auf Done.
- `docs/TODO.md` aktualisiert (CI+Board erledigt), committet `90d4349`, gepusht. Branch synchron mit origin/main.
- PROGRESS.md Session (10) nachgetragen (Clubs + SaaS stage 1 — in der vorherigen Session nicht geloggt).

**Learned**
- gh project CLI: `item-edit` braucht `--project-id` UND `--id`; Draft-Items tragen den Status top-level (`status`), nicht in `fieldValues`.

**Blocked / decisions needed**
- none — Projekt pausiert auf Kosis Wunsch bis zur Video-Session (~Anfang Sept.).

**Next**
- Kosis 20-Min-Block (Devpost + AWS Builder ID, optional Credits-Formular) — Links in TODO.md/Board.
- Voiceover-Freigabe (docs/voiceover/).
- Video-Session (frisch, nach Storyboard) → Submission 12.09. gemeinsam.

## Session 2026-08-24 (12) — Kosi-Block: Registrierungen, Devpost, Rename → ClubSteward, Repo public

**Done**
- Kosi: Devpost + Hackathon registriert, AWS Builder ID angelegt, $50-Credits-Formular abgeschickt (Good Neighbor).
- Devpost-Formular gemeinsam ausgefüllt: Name/Pitch/Story/Built-with/Additional-info; paste-Datei docs/devpost-paste.md (Stories in gepflegtem EN, Markdown-clean). Architektur-Diagramm (Pflichtfeld!) gebaut: scripts/gen_architecture.py → docs/architecture.svg/.png (geometrisch validiert, 0 Overlaps).
- Namens-Check nachgeholt: "ClubKeeper" kollidiert (clubkeeperapp.com, clubkeeper.app, clubkeeper.org). Kosi entschied: Rename VOR public. **ClubSteward** verifiziert frei (GitHub 0 Repos, PyPI, Devpost-Slug, Web, .io/.dev) → Rename durchgeführt: 97 Dateien, Paket clubsteward/, Session-State-Keys clubsteward:case, EMLs. 21/21 Tests grün, Replay verifiziert.
- GitHub: Repo umbenannt zu github.com/derKosi/clubsteward, PUBLIC, MIT erkannt, Description gesetzt. Board #5 → "ClubSteward". Fresh-Clone-Gate auf dem öffentlichen Repo: clone → uv sync → 21 Tests → Replay ohne API-Key, alles grün.
- Voiceover: alle 8 Segmente + Preview + Master (3:26) mit ClubSteward neu gerendert. ABER: Kosi fiel auf — TTS lief auf de-DE-Stimme (Config-Fehler). Behoben: tts.edge.voice = en-US-AriaNeural; neue Preview-Note gerendert. **Segmente+Master warten auf Kosis Stimm-Freigabe, dann Re-Render.**
- Eval live re-gerannt: 10/10 = 100%, avg conf 0.97 (Report aktualisiert); Draft-Texte 9→10-Mail-Corpus korrigiert.
- Architektur-PNG + Demo-GIF nach Rename regeneriert.

**Offen / Next**
- Kosi hört 00-preview-note.mp3 (Aria) → Freigabe oder Alternativ-Stimme (Guy/Jenny/Sonia).
- Devpost-Formular: Story neu pasten (ClubSteward-Header + 10-mail), Architecture-PNG neu hochladen (Version 20:07), Repo-URL ist drin.
- Video-Session Anfang Sept (ComfyUI auf Kosis GPU lokal, VM liefert Skripte/Assets), Blog 8.–10.09., Submission 12.09.

## Session 2026-08-24 (12b) — Open-Core/Lizenz-Check (autonom, 15-min-Block)

**Done**
- Zweigleisigkeits-Check auf Kosis Frage: verifiziert Sole-Autor (43 Commits, nur Kosi),
  Hackathon-Lizenzpflicht (MIT/Apache bis Judging-Ende), Architektur = bereits Open Core
  by construction (Tenant=Ordner, SaaS=dünne Orchestrierung → clubsteward-cloud privat).
- Urteil: Repo NICHT zurückziehen (Qualitätsgates grün, 0 Forks), AGPL empfohlen: NEIN
  (MIT-Core + Closed-Cloud statt Copyleft — Vereinsmarkt kauft Vertrauen/On-Prem).
- Entscheidungsvorlage 15.09.: ~/steward-open-core-memo.md (bewusst außerhalb des Repos).

## Session 2026-09-10 — Sonderzeichen-Bugfix (MailItem charset) + Safari-Layout-Anfang

**Done**
- **Root Cause** gefunden für kaputte Sonderzeichen (`f??r` statt `für`): Korpus-/Decision-Mails haben **keinen `Content-Type`/charset-Header** → Python `email` dekodiert den Body als `us-ascii` mit `errors='replace'` → jedes UTF-8-Byte wird zu eigenem U+FFFD (daher 2×`?` pro Umlaut). Subject war nicht betroffen (Policy-Header-Parsing dekodiert korrekt).
- **Fix** `clubsteward/models.py`: neuer Helper `_decode_text_part()` — `get_payload(decode=True)` (CTE-aware), dekodiert mit deklariertem Charset, Fallback UTF-8. Wirkt auf Pipeline, decide, Web-UI (Decision-Cards parsen MailItem zur Laufzeit).
- **10 kaputte Dateien repariert** (alles `clubs/*/sessions/session_*/…/message_0.json` — Prompts mit eingebettetem Mailtext): chirurgischer Raw-String-Austausch, validiert dadurch, dass `mangle(saubere_korpus_mail)[:2000]` byte-exakt den korrupten Abschnitt reproduziert → repair = exakt das, was die gefixte Pipeline geschrieben hätte. Repo-weiter Scan: 0 U+FFFD übrig.
- **Regressionstests** `tests/test_core.py::TestMailCharset` (UTF-8 ohne Header + deklariertes iso-8859-1). 43 passed, ruff clean.
- Webapp (Port 8765) gestartet, API verifiziert: av-la-alameda Decision-Cards jetzt mit korrektem `pensión`, `Señores`, `¿habría`.

**Learned**
- macOS `screencapture` braucht **Screen-Recording-Permission** für den Terminal-App — ohne die liefert es nur das Desktop-Wallpaper (Safari-Fenster unsichtbar). Permission wurde erteilt, **Neustart (logout) nötig** → Safari-Layout-Review im nächsten Session-Teil.
- `uv run pytest` ohne Scope sammelt `scripts/smoke_test.py` ein, das ohne `ZAI_API_KEY` beim Import exitet → `uv run pytest tests` verwenden (vorbestehendes Verhalten).

**Blocked**
- Safari-Layout-Review + Screenshots: wartet auf Neustart nach Screen-Recording-Permission.

**Next**
- Webapp neu starten: `nohup uv run uvicorn clubsteward.web:app --host 127.0.0.1 --port 8765 > /tmp/clubsteward_web.log 2>&1 &`
- Safari (osascript) auf `http://127.0.0.1:8765/app`, Screenshots via `screencapture -x -R0,25,1440,815` (Bounds via `osascript … bounds of front window` → `0, 25, 1440, 840`), Layout-Review der Console (Club-Switcher, Decision-Cards, Outbox, Register) + Sonderzeichen final visuell prüfen.
- Änderungen liegen **uncommittet** bereit: `clubsteward/models.py` (Fix), `tests/test_core.py` (Test), 10× `message_0.json` (Repair), `PROGRESS.md`. Konventioneller Commit z. B. `fix: decode mail bodies without charset header as UTF-8 (umlauts were U+FFFD)`.

## Session 2026-09-10 (2) — Web-UI-Überholung (Safari ferngesteuert)

**Done**
- Safari-Fernsteuerung aktiv (nach Neustart): `osascript` setzt die URL, `screencapture -x -R0,25,1440,815` macht Screenshots → Layout-Review per Read-Bild. Workflow: Edit → URL neu setzen → Screenshot → Review.
- **Decision Cards redesigned** (`webapp/static/app.html`): Größter inhaltlicher Mangel war, dass `proposed_action` und `details` in der API lagen, aber NICHT angezeigt wurden. Jetzt: **„Agent proposes“**-Block (teal), Facts-Grid (details als Key-Value, Listen mit `·`), Confidence-Chip mit Farbskala (≥90 grün / ≥75 gelb / sonst rot), Intent-Chip (mono), relatives Datum (`created_at` neu in `/decisions`-API), Original-Mail einklappbar (`<details>`), **Inline „Approve + instruct“** (Textarea statt hässlichem `prompt()`), Toast-Feedback nach Aktionen, Working-State während der LLM-Ausführung.
- **XSS-Hygiene**: `esc()`-Helper für alle API-Strings in beiden Seiten (Korpus ist synthetisch, aber Juroren lesen Code).
- **KPI/Toolbar**: Pending-Decisions-KPI rot hervorgehoben bei >0; Run-night/Drop-.eml-Buttons sauber gestapelt; Log auto-scrollt während des Runs; Toast bei Run-Ende; **Inbox-Zero-Empty-State (🎉)**.
- **Deep-Links** (echtes Produktfeature + Test-Navigation): `/app?club=<id>` wählt Club direkt und sync't die URL (`history.replaceState`), Anker `#decisions` `#outbox` `#register` mit `scroll-margin-top`. Wichtig, weil Safari ohne „Allow JavaScript from Apple Events“ kein Scrollen/Clicken via osascript erlaubt — Anchors decken die Navigation ab.
- **Draft-Anzeige-Fix** (`clubsteward/web.py` `api_state`): Header-Block wurde als Ganzes als „To“ genommen → `To:`/`Subject:` werden jetzt zeilenweise geparst; UI zeigt Subject als Draft-Titel, „to …“ als Meta.
- **Produktseite mit echten Live-Stats** statt hartcodiert: `api_clubs` liefert jetzt `handled` (processed/*.eml); Hero zeigt 6 clubs · 17 mails handled · 14 warm replies · 7 decisions waiting (live aus den 6 Clubs).
- Visuell verifiziert in Safari: av-la-alameda (Sonderzeichen korrekt), maplewood (4 Karten + `medical`-Flag-Chip), kg-rheinklause (Empty-State + Drafts mit Subject-Titel), Produktseite (Live-Stats).
- 43 Tests grün, ruff clean.

**Learned**
- CSS-Falle: `.instruct { display:flex }` überschreibt das UA-Stylesheet für das `hidden`-Attribut → Panel war immer sichtbar. Fix: `.instruct[hidden] { display:none }`.
- `screencapture` erfasst das vorderste Fenster der Region — Safari muss per `activate` in den Vordergrund, sonst gibt's ein Terminal-Screenshot.

**Offen / Next**
- Interaktionszustände (Mail expandiert, Inline-Edit geöffnet, Toast) noch nicht bildlich verifiziert — dafür braucht Safari **Develop → Allow JavaScript from Apple Events** (Settings → Advanced → Develop-Menü einblenden). Danach kann die Fernsteuerung auch klicken/scrollen/DOM lesen.
- Uncommittet liegen jetzt zwei Pakete bereit: (1) charset-Fix von Session (1) — models.py + tests + 10 repaired message_0.json; (2) dieses UI-Paket — web.py, webapp/static/*, PROGRESS.md.

## Session 2026-09-10 (3) — min_confidence-Policy, Robustheits-Fixes, SV-Grünwald-Corpus

**Done**
- **Safari-Fernsteuerung komplett** (Allow JavaScript from Apple Events an): Mail-Expand, Inline-Edit, Toast, Upload-Flow per do-JavaScript gebildlich verifiziert. Toast "📥 1 mail dropped into the inbox" e2e bestätigt. KPI-Label "drafts ready" → "drafts ready to send".
- Zwei Pakete committet + gepusht: charset-Fix (bc647d9) und UI-Paket (d34d5fc).
- **Policy `min_confidence` (a94949d? → a94946d)**: zweite Eskalations-Achse neben Intent/ask_if — Triage-Confidence unter policy.min_confidence (default 0.75, alle 7 YAMLs) eskaliert auto → ask, Reason nennt %-Wert und Schwelle. 4 Tests → 48 grün.
- **Z.ai-Key auf diesem Mac verfügbar** (Kosi legte ihn in ~/.zshenv, außerhalb des Repos, 600). Verifiziert: Key in 0 Dateien, 0 Commits.
- **Echte Pipeline-Runs für SV Grünwald** (10 Mails, GLM glm-5-turbo, ~€0.0086): 5 auto / 3 ask / 1 reject / 1 triage-fail, 5 Drafts, Register-Update echt (Mia Hoffmann Adresse). Demo-Zustand steht.
- **Bug 1 (Repo-Bug!): `threading.local`-Config** — tools.set_config setzte thread-local; der SDK führt Tools auf Executor-Threads aus → jeder Tool-Call warf "Config not set". Auf der VM zufällig nie sichtbar. Fix: process-global Fallback + thread-local Override, Unit-Test mit echtem Thread.
- **Bug 2: max_tokens 1024** — GLMs Reasoning-Anteil frisst das Budget → TRIAGE FAILED "No tool_calls"/"Unterminated string" bei langen Mails + act-Abbrüche (MaxTokensReachedException tötete den GESAMTEN Run). Fix: 4096 (env ZAI_MAX_TOKENS), plus act-try/except → Mail nach _errors, Run läuft weiter.
- **Befund fürs Pitching**: Mail 07 („Pause, Wechsel oder Kündigung?") kam als `question` @ 0.82 durch und lief AUTO — GLM ist bei Mehrdeutigkeit zu selbstbewusst; 0.82 > 0.75-Schwelle. Genau die stille Autonomie-Lücke. → TRIAGE_SYSTEM um Exit-Regel („Aussetzen/Wechsel/Kündigung auch fragend = cancellation") + Multi-Intent-Regel („most human attention wins", Mail 08s Beschwerde wurde von address_change überdeckt) erweitert — **uncommittet, Eval-Gate steht aus**.
- corpus 07–10 (lang, realistisch): 07 mehrdeutiger Ausstieg, 08 Multi-Intent+wirre Adresse, 09 Support-Angebot mehrdeutig, 10 Anmeldung+medical (Kontrollgruppe). Mail 10 triaged weiter nicht (GLM-Structured-Output-Quirk, char ~407) — liegt in _errors, Retry-Idee für nächste Session.

**Learned**
- Sessions tragen Erinnerung — auch Fehler-Erinnerung: Run 2 mit Run-1-Kaputt-Sessions wiederholte die Tool-Fehler trotz Fix. Bei Diagnose immer sessions/ löschen.
- `club reset` leert `_errors` nicht → Altdateien können neue Scheiterungen maskieren.
- `tail` im Background-Run puffert bis zum Ende; Fortschritt über Verzeichnis-Zähler pollsen.

**Offen / Next**
- Eval gegen die neue TRIAGE_SYSTEM-Regel laufen lassen (scripts/run_eval.sh), dann Prompt committen; danach SV-Grünwald full re-run als finaler Demo-Stand.
- Triage-Retry (1×) bei Parse-Fail als Robustheits-Fix.
- Mail 10 Triage-Fail debuggen (GLM-Quirk?) — ggf. Mail leicht kürzen.

## Session 2026-09-11 (4) — Eval-Gate, offer-Intent, Robustheit, finaler Demo-Stand, UX-Review

**Done**
- **Eval-Gate hat gearbeitet**: Erste Eval gegen die neuen TRIAGE_SYSTEM-Regeln: 8/10. Die Regeln überkorrigierten — Irena (Signup mit Sibling-Diskount-Frage) → hardship_waiver, Sofia („might move up to U16") → cancellation. Geschärft mit expliziten Ausnahmen (Gebührenfrage bei Anmeldung ≠ Hardship; Squad-Wechsel IM Verein ≠ Exit). Danach 2× **10/10 = 100 %**, Ø conf 0.97.
- **Neuer Intent `offer`**: Run 1 hatte das Sponsoring-Angebot (Mail 09) als `question` @ 0.93 AUTO beantwortet — Draft versprach „zuständige Person meldet sich", keiner im Vorstand sah es. Jetzt: Angebote (Geld/Sponsoring/Sachmittel/Ehrenamt) = eigener Intent; **keine Policy-Regel nötig** — fehlende Regel fail-closed → ask (getestet). README-Entscheidungen-Tabelle um Offer-Zeile ergänzt.
- **`save_draft`: ein Draft pro Empfänger** — der Act-Agent hatte bei Mail 09 mitten im Draft self-corrected („gibt es aktuell noch. Moment — noch nicht, richtig.") und eine zweite Version als `_2` abgelegt; die holprige Erstversion blieb im Outbox. Jetzt ersetzt ein Re-Save den früheren Draft desselben Empfängers (auch betreffübergreifend), 3 Tests.
- **Triage-Retry (1×)** bei Parse-Fail: `structured_output` nutzt den Prompt temporär (nicht in der History) — der Retry startet sauber, keine „Fehler-Erinnerung". 2 Tests (retry + Abbruch nach 2. Fail).
- **Finaler SV-Grünwald-Re-Run** (~€0.0023, EXIT 0, `_errors` leer): 3 auto / 7 ask / 1 reject — 01 medical-ASK (echtes Asthma), 02 Kündigung, 03/05 AUTO mit Drafts + Register-Update (Mia Hoffmann), 06 Spam-REJECT, **07 cancellation ASK** (vorher stille Lücke: question @ 0.82 AUTO), **08 complaint ASK** (Multi-Intent), **09 offer ASK**, **10 medical-ASK ohne Triage-Fail** (max_tokens 4096 + Retry haben den GLM-Quirk behoben — Debug nicht mehr nötig).
- **UX-Review im Safari (Top 5, bewusst NICHT gefixt)**:
  1. Sprach-Mix in den Decision-Cards: deutsche Clubs lesen englische Summaries/Facts/„AGENT PROPOSES" (Mails+Drafts sind deutsch) — `brand.locale`/Policy-Tone könnte die Karten lokalisieren. Größtes echtes Nutzerproblem.
  2. Karten-Länge: Offer-Card ~2 Screens (6-Facts-Grid + langer Summary-Block), Approve ganz unten — 7 Entscheidungen am Morgen = Scroll-Arbeit. Facts/Details default-einklappen oder kompakte Zeilen mit Expand.
  3. Club-Switcher: 6 Pills, alle gleich, Umbrauch in Zeile 2 — keine Pending-Counts sichtbar („SV Grünwald (7)"), Multi-Club-Bediener muss durchklicken.
  4. Member-Register: horizontale Scrollbar, E-Mail-Spalte abgeschnitten (emma.schneider@example…) — E-Mail ist aber das Feld, das Mitglieder prüfen.
  5. Nach Approve verschwindet die Karte — keine „heute ausgeführt"-Sicht (Audit-Trail existiert als JSON/Log, aber nicht im UI); Trust-Feature „was hat der Agent über Nacht gemacht" fehlt noch. (Deny ohne Inline-Grund.)
  Kleinere Notizen: „Why you:"-Label gewöhnungsbedürftig; Empty-State 🎉 und Live-Stats auf der Produktseite wirken gut.
- **Docs: Stage 1.6 „Local-first model cascade"** (docs/HOSTING.md): Kosis Idee — kleines lokales Modell (LM Studio/Ollama, OpenAI-kompatibel) macht Erst-Triage, externes LLM nur bei niedriger Confidence; Kosis Frage beantwortet: **Strands bleibt unangetastet** (Modell kommt nur als LiteLLM-Provider via make_model() rein — Basis-URL-Swap, kein Framework-Wechsel; Kaskade = dieselbe „unter Confidence X → eskalieren"-Achse wie min_confidence, nur aufs Modell-Level gehoben). Eval-Harness misst lokale Qualität ehrlich. Empfehlung: NICHT vor Submission implementieren. Entscheider-Item in docs/TODO.md.

**Learned**
- Eval vor jedem Prompt-Commit ist Pflicht: genau die beiden neuen Regeln hatten zwei Korpus-Mails kippen lassen — ohne Gate wäre der Commit als „Verbesserung" gegangen.
- Fail-closed macht neue Intents billig: neuer Enum-Wert + Prompt-Zeile = sofort korrektes Verhalten in allen 7 Club-Policies ohne YAML-Änderung.

**Blocked / decisions needed**
- Local-first-Kaskade: Video-Thema oder Roadmap? (Kosi, vor der Vertonung — docs/TODO.md)

**Next**
- Video + Voiceover mit Kosi (heute Nacht/morgen), dann Submission 12.09.

## Session 2026-09-11 (5) — Demo-Control: Reset & Run live, Stop, Live-Log, LLM-Timeout

**Done**
- **Kosis Fragen geklärt**: KG Rheinklause „alles abgearbeitet" = UI-Test-Rest von gestern (alle Decisions approved); OG Lindenthal „keine Daten" = nie gefahren (nur Corpus+Policy) → **erstmals gelaufen**: 3 auto / 2 ask / 1 reject, EXIT 0.
- **Demo-Mails für die Eskalations-Achsen** (Kosis Wunsch: Fälle, in denen das LLM NICHT >95 % sure ist):
  - sv-gruenwald Mail 11 „Wegen der Sache" (absichtlich vage): Triage `unknown` @ **0.55** mit Flags vague/possible_scam → „nie raten"-ASK. Der robuste Low-Confidence-Beat fürs Video.
  - sv-gruenwald Mail 12 „Adresse, aber nur teilweise?": GLM blieb bei 0.90 (zu selbstbewusst, wie Mail 07 lehrte) — aber Triage setzte Flag `billing_address_unclear` → **Policy-as-Data**: `ask_if`-Zeile in der address_change-Regel. (Varianz: im Final-Run Flag nicht wieder da → AUTO @ 0.95; legitim, Adresswechsel ist auto-appropriat.)
  - maplewood Mail 07 „Snack schedule – heads-up about Nia" (Kosis Wunsch: 2. englisches Beispiel, sozial, unkontrovers, 2. medizinisch): Frage zur Snack-Rotation, Tochter mit Weizen-Allergie (Cöliakie — bewusst NICHT Erdnuss, das hat Mail 01 schon). Triage `question` @ 0.90 + Flag `medical` → neue `ask_if: medical`-Zeilen auf question/address_change in der Maplewood-Policy („alles Medizinische geht an einen Menschen") → ASK. Club neu gefahren: 2 auto / 5 ask / 1 reject.
- **Reset & Run live** (Web-Konsole): `POST /clubs/{id}/reset` (teilt sich `reset_club()` mit dem CLI — **räumt jetzt auch `_errors`**, die alte Falle) + Button „↺ Reset & run live" (Confirm → Reset → automatischer Run).
- **Live-Log**: `run/status` drained jetzt den stdout-Puffer des laufenden Runs — Zeilen erscheinen WÄHREND des Laufs in der Konsole (vorher: erst am Ende).
- **Stop** (Kosis Idee): `should_stop`-Callback in `pipeline.run` (geprüft zwischen den Mails), `POST /clubs/{id}/stop` (409 ohne laufenden Run), „Run night"-Button wird während des Laufs zu „⏹ Stop". E2E bewiesen an kg-rheinklause: Mail 01 lief fertig, dann „⏹ Stop requested — 5 mail(s) stay in the inbox", Endstand inbox=5/processed=1. Resume = einfach „Run night".
- **LLM-Timeout (Robustheit!)**: Beim Stop-Test hing ein Act-LLM-Call **6+ Minuten** — kein Timeout im Modell-Client, Stop kann dazwischen nicht greifen. Fix: `timeout=180` (env `ZAI_TIMEOUT`) in `make_model` → Raise → act-try/except filet die Mail in `_errors`, Run läuft weiter. `.env.example` dokumentiert ZAI_MAX_TOKENS/ZAI_TIMEOUT.
- Finaler sv-gruenwald-Stand (via Reset&Live-Pfad gefahren): **12 Mails · 4 auto / 8 ask / 1 reject**, ~€0.0043 — Karten inkl. offer-, medical- und „nie raten"-Eskalation.
- 59 Tests grün, ruff clean.

**Learned**
- Stop zwischen Mails ist billig und ehrlich (folder-based State) — aber ohne LLM-Timeout ist jeder „Stop" der Mutter eines hängenden Calls ausgeliefert. Timeout zuerst, Kontrolle zweiter.
- GLMs Selbstbewusstsein ist nicht per Mailtext steuerbar (0.55 bei echter Vagheit, 0.90 bei gebauter Ambiguität) — für deterministische Demo-Beats: Policy-Flags + fail-closed, nicht Prompt-Gebetse.

**Offen**
- Safari-„Allow JavaScript from Apple Events" ist wieder aus (Safari-Neustart) → Button-Klicks via osascript nicht möglich; fürs Video egal (Kosi klickt selbst), sonst: Develop → Allow JavaScript from Apple Events.

**Next**
- Video + Voiceover (heute Nacht/morgen), Submission 12.09.

## Session 2026-09-11 (6) — Locale-Fix (deutsche Karten), Draft-Gegenüberstellung, EN-Blind-Spot-Mails

**Done**
- **Sprach-Fix (Kosis Befund: „Agent proposes" bei deutschen Clubs auf Englisch)**: Ursache — TRIAGE_SYSTEM ist englisch und sagte keine Ausgabesprache; GLM antwortete default-englisch (Act-Drafts waren schon deutsch wegen expliziter Sprachanweisung). Fix: `triage_prompt_text(mail, language)` — Triage schreibt summary/proposed_action/details jetzt in der **Club-Sprache** (`brand.locale` → German/English/Spanish), Pipeline übergibt `locale=cfg.brand.locale`. Erste Verifikation zeigte den klassischen Fallstrick: der Webapp-Prozess hatte noch den VOR dem Fix geladenen Code → Mischbild. Re-Run per CLI (frischer Prozess): **alle 8 sv-gruenwald-Karten deutsch**. 2 Tests.
- **Draft-Gegenüberstellung (Kosis Wunsch)**: Outbox zeigt jetzt **links 📥 Incoming, rechts ✉️ Draft** (Join: Draft `To:` ↔ verarbeitete Mail `From:` — 1:1 seit dem Ein-Draft-pro-Empfänger-Fix). `api_state` liefert `source` pro Draft; UI-Grid mit scrollbarer Vorschau, stackt mobil. Visuell verifiziert: 3 Draft-Paare inkl. Mail 12, wo der Agent zwei Rückfragen statt zu raten gestellt hat.
- **EN-Blind-Spot-Mails (5, ohne AI-Auswertung — nur Corpus)**: jefferson-pta `07-data-deletion` (Datenlöschung/Privacy, DSGVO-artig) + `08-thank-you-bookfair` (Dankeschön → warm-reply-AUTO-Beat); maplewood `08-waiting-list-majors` (Waiting-List-Flag), `09-refund-double-charge` (Refund-Flag, Doppelabbuchung), `10-duplicate-signup` (Duplicate-Flag, doppelte Registrierung). Maplewood-Policy: `ask_if` um `duplicate` (signup) und `refund` (question) erweitert. **Damit abgedeckt: alle benannten Flags aus TRIAGE_SYSTEM haben jetzt mindestens einen Corpus-Vertreter** (medical, waiting_list, refund, duplicate; refund/duplicate laufen noch nie durch die Pipeline — bewusst, kosten 0 €).
- Finaler sv-gruenwald-Stand: 12 Mails · 4 auto / 8 ask / 1 reject, alle Karten deutsch, Mail 11 `unknown` @ 0.55 → „nie raten". 61 Tests grün, ruff clean.

**Learned**
- uvicorn ohne --reload hält den Modulzustand des Prozessstarts fest — Prompt-Änderungen sind für laufende Webapp-Runs unsichtbar. Für Demo-Runs nach Code-Änderungen: CLI (frischer Prozess) oder Webapp-Neustart.

**Next**
- Video + Voiceover, Submission 12.09. (Puffer 14.09., 17:00 PT).

## Session 2026-09-11 (7) — Step-Modus (Klick für Klick), Tenant-Leak-Fix, Störungs-Postmortem

**Done**
- **Störungs-Postmortem**: Ein UI-Run um 16:12 (Kosi klickte währenddessen) lief in die Z.ai-Störungsphase — alle 6 kg-Mails: Triage-Calls scheiterten (0 Tokens empfangen), landeten korrekt konserviert in `_errors`, Spam trotzdem aussortiert, Run nicht gestorben. Degradation funktionierte wie designed; repariert per `club reset` + Re-Run (4 auto / 2 ask / 1 reject). **Fehler meinerseits**: den Dirty-State blind mit `git add -A` + falscher Message („sv-gruenwald") committet — Inhalt war korrekt (kg-Snapshot), Message unsauber. Regel: vor `add -A` immer Status lesen.
- **og-lindenthal Re-Run mit Locale-Fix**: Karten jetzt deutsch (u. a. „Beschwerde: Festplatz nach dem Sommerfest" → deutsche Weiterleitungs-Empfehlung).
- **Step-Modus-Backend (05151f1)**: `process_mail()` aus `pipeline.run` extrahiert (identisches Verhalten: Moves, Summary, Recorder, Prints) + gibt Trace-Dict zurück (Triage-Felder, Decision + Reason, Draft, Decision-Id). `run_one(club)` verarbeitet genau die erste Inbox-Mail über denselben Code-Pfad. Web: `GET /clubs/{id}/inbox/next` + `POST /clubs/{id}/process-one` (synchron, 409 bei laufendem Batch).
- **Step-Modus-UI (0baa3e8 + 8b9205e)**: full-width Inbox-Karte mit Mail-Liste + „▶ Process next mail". Klick → links die Incoming-Mail, rechts rotierende Warte-Strings, dann Analyse (Intent/Confidence/Flags/Summary) + „Why you"-Reason + Draft bzw. Queued-Hinweis; danach Decisions/Outbox live aktualisiert. Batch („Run night") + Stop + Reset bleiben daneben.
- **Tenant-Leak, zwei Iterationen**: (1) Step-Panel blieb beim Club-Wechsel stehen und renderte Ergebnisse ins falsche Rendering → Fix. (2) Kosis Test: Zurückwechseln zeigte die laufende Mail nicht mehr → **`stepStates{}` pro Tenant**: Wechseln re-bindet das Panel nur; der Serverprozess läuft unberührt weiter, zurück = „processing…" wieder sichtbar, Fertigstellung landet im richtigen Tenant (Toast auch bei Abwesenheit). Backend war zu keinem Zeitpunkt leaky (Run-Lock serialisiert; `set_config` pro Run).
- E2E bewiesen: kg per Step-Endpoint (signup @ 0.96, deutsche Reason, Draft „Willkommen Milla! – Anmeldung Kindergarde") + echter UI-Klick via Accessibility.

**Learned**
- Wer UI-Zustand tenant-übergreifend stehen lässt, baut einen Cross-Tenant-Leak — Panel-Zustand gehört in ein per-Tenant-Model, nicht in den DOM.
- Ein „abgebrochener" Browser-Fetch bricht den Serverprozess NICHT ab (FastAPI-Threadpool) — Abbruch-Semantik muss man pro Schicht bewusst entscheiden.

**Next**
- „Why you"-Reasons auf Tenant-Sprache heben (läuft), dann Video + Voiceover.
