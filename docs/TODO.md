# TODO — bis zur Submission (12.09. intern / 14.09. hart)

Stand: 23.08.2026 · Agent-seitige Arbeit: fertig · Alles Weitere braucht Kosi oder eine gemeinsame Session.

## Kosi allein (ca. 20 min)

- [x] Devpost-Account + Hackathon-Registrierung → https://agentsforhumans.devpost.com/ (erledigt 24.08.)
- [x] AWS Builder ID (gratis, kein AWS-Account nötig) → https://profile.aws.amazon.com/ (erledigt 24.08.)
- [x] Optional: $50 AWS-Credits-Formular (bis 11.09., 12:00 PT; first-come-first-served)
      → https://forms.gle/6sjzKiX6bKUMA5NEA — Text zum Copy-Pasten: docs/devpost-credits-helper.md
      (Track: Good Neighbor Agents angeben, sonst wird abgelehnt!)
- [x] `gh auth refresh -s workflow,project` — erledigt 23.08., CI-Workflows
      (tests.yml + release.yml) gepusht (Commit 075c378), GH Project-Board angelegt:
      https://github.com/users/derKosi/projects/5

## Freigabe fällig

- [ ] Voiceover abhöhren und freigeben/ablehnen:
      docs/voiceover/00-preview-note.mp3 (15s) · docs/voiceover/voiceover-master.mp3 (3:34 komplett)
      Freigabe → TTS geht ins Video · Ablehnung → Kosi spricht Skript selbst
      (docs/voiceover-script.md, wortgenau, mit Betonungen)

## Gemeinsame Session: Video (Anfang September, frische Session)

- [ ] Screen-Recording der Live-Demo nach docs/video-storyboard.md (Terminal, 1920x1080, Font ≥16pt)
- [ ] Decide-CLI-Szenen in Echtzeit aufnehmen (die Eingaben müssen sichtbar sein)
- [ ] Schnitt: Sektionen + Voiceover-Track (fertige 8 Segmente liegen in docs/voiceover/)
- [ ] EN-Untertitel auf YouTube (Auto-Captions korrigieren)
- [ ] Upload YouTube oder Vimeo, öffentlich, Link in Devpost-Eintrag

## Kosi: Blog-Post veröffentlichen (~8.–10.09., Bonuspunkte)

- [ ] builder.aws.com-Konto, Post publishen: docs/builder-post-policy-layer.md
      (Titel enthält "Agents for Humans" · Repo-URL ersetzen · echte Run-Zahlen drin)

## Gemeinsame Session: Submission (12.09. — Puffer bis 14.09., 17:00 PT)

- [x] Architecture diagram (form-required): docs/architecture.png (3360×2000) ·
      Quellen: docs/architecture.svg + scripts/gen_architecture.py (erledigt 24.08.)

- [ ] Repo public schalten: github.com/derKosi/clubsteward
- [ ] Repo-"About": Beschreibung + MIT-Lizenz sichtbar (GitHub erkennt LICENSE-Datei schon)
- [ ] Final-Check mit Agent: Fresh-Clone-Gate, Secret-Scan, README-Quickstart
- [ ] Devpost-Projekt anlegen: Text aus docs/devpost-submission-draft.md einfügen
- [ ] Track wählen: Good Neighbor Agents (nur diesen einen)
- [ ] Repo-URL + Video-Link eintragen, AWS Builder ID angeben
- [ ] Submit bis 12.09. (hartes Limit: 14.09., 17:00 PT / 15.09., 02:00 MESZ)

## Referenzen

- Checkliste Abgabe-Pflichten: REQUIREMENTS.md (alle agent-seitigen Punkte ✓)
- Zeitplan & Regeln: agentsforhumans.devpost.com (Rules-Tab)
- Alles Wichtige im Repo: README.md · docs/ (Storyboard, Skript, Audio, Posts, Drafts)
