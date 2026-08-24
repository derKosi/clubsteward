# REQUIREMENTS — Agents for Humans Hackathon (AWS / Devpost)

Source: https://agentsforhumans.devpost.com/ (main + rules + FAQ), read 2026-08-23.
Official rules take precedence over anything else. Deviations: none found so far.

## Timeline (official)

- [x] Submission period: Aug 10, 2026 (9:00 PT) – **Sep 14, 2026 (17:00 PT)** — internal target: Sep 12
- [ ] Judging: Sep 15 – Oct 8, 2026; Winners ~Oct 14, 2026
- [ ] AWS credits ($50) request form by Sep 11, 12:00 PT — OPTIONAL (we build cloud-free; form text ready in docs/devpost-credits-helper.md)

## Hard submission requirements (from "What to Submit" + Rules §4)

- [x] Text description (English) — DRAFT READY: docs/devpost-submission-draft.md (paste at submission)
- [x] PUBLIC repo URL — repo exists PRIVATE (github.com/derKosi/clubsteward), flip to public at submission
- [x] Repo contains all source code, assets, setup instructions — fresh-clone gate passing (tests + replay, no key needed)
- [x] Open-source license file MIT — LICENSE present, GitHub detects it
- [ ] License visible in repo "About" section — Kosi at go-live (add topic "mit" + description)
- [x] README (problem, demo GIF, quickstart, architecture, decisions table, design decisions)
- [x] Architecture diagram — docs/architecture.svg + mermaid in README
- [ ] Demo video ≤ 5 minutes, public on YouTube or Vimeo — STORYBOARD + VO SCRIPT READY (docs/video-storyboard.md, docs/voiceover-script.md); record early Sep
- [ ] Video demonstrates the working project end-to-end — run live demo per storyboard
- [ ] AWS Builder ID provided at submission — Kosi creates (profile.aws.amazon.com, free)
- [x] Track selected: Good Neighbor Agents (single track)
- [x] All materials in English (code, docs, corpus, drafts)
- [x] Project newly created during submission period (repo started Aug 23, 2026; no pre-existing code)
- [x] Runs on juror's machine from README, no costs, no secret required (replay mode works keyless; live mode needs free Z.ai key)

## Scoring criteria (Section 6; weights unpublished — serve all)

- [x] Technological Implementation — HITL intervention w/ custom policy classifier, structured output, per-member sessions, tools, metrics, eval harness; replay for judges (live demo link optional, AgentCore optional)
- [x] Design — complete CLI product loop: overnight run → decision cards → outbox + audit; fail-closed everywhere
- [x] Potential Impact — volunteer club secretaries worldwide (specific, credible, story in README)
- [x] Creativity & Originality — policy-as-data IS the runtime approval classifier; ask_if flag escalation; deterministic safety backstop
- [ ] Presentation — video pending (script ready)

## Bonus

- [ ] builder.aws.com blog post(s), "Agents for Humans" in title — FULL POST READY: docs/builder-post-policy-layer.md (publish ~Sep 8–10; 2 more angles outlined in docs/builder-posts-drafts.md)

## Eligibility (verified)

- [x] Germany eligible (excluded: Italy, Brazil, Russia, UAE, others — not us)
- [x] Solo or team allowed; one representative submits on Devpost
- [x] Multiple submissions allowed if substantially different

## Our internal guardrails (from mission brief)

- [x] No cloud costs, no accounts needed for build; no scraping of login-walled sites
- [x] Secrets never committed (secret scan of full history clean; .env ignored; key in sops outside repo)
- [x] No fake demos: replay clearly labeled [RECORDED SESSION]; video will show live run
- [ ] Submission itself only WITH Kosi (Phase 4, Sep 12)

## Open TODOs (owner: Kosi unless noted)

1. Devpost account + hackathon registration (agentsforhumans.devpost.com)
2. AWS Builder ID (profile.aws.amazon.com)
3. Optional: $50 credits form (by Sep 11, text ready)
4. Optional: `gh auth refresh -s workflow` then I push CI workflow (file ready locally)
5. Video recording session with agent (early Sep) + upload YouTube/Vimeo
6. Publish builder.aws post (agent finalizes with real run numbers)
7. Sep 12: repo public + About/license + Devpost submission (together)
