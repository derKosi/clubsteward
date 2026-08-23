# REQUIREMENTS — Agents for Humans Hackathon (AWS / Devpost)

Source: https://agentsforhumans.devpost.com/ (main + rules + FAQ), read 2026-08-23.
Official rules take precedence over anything else. Deviations: none found so far.

## Timeline (official)

- [x] Submission period: Aug 10, 2026 (9:00 PT) – **Sep 14, 2026 (17:00 PT)** — internal target: Sep 12
- [ ] Judging: Sep 15 – Oct 8, 2026; Winners ~Oct 14, 2026
- [ ] AWS credits ($50) request form by Sep 11, 12:00 PT — OPTIONAL, only if we ever want AWS (we build cloud-free)

## Hard submission requirements (from "What to Submit" + Rules §4)

- [ ] Text description (English): what it does, who it's for, how it works
- [ ] PUBLIC repo URL (GitHub/GitLab/Bitbucket) usable by judges for free until judging ends (Oct 8)
- [ ] Repo contains: all source code, assets, setup instructions
- [ ] Open-source license file MIT or Apache-2.0 in repo
- [ ] License visible in repo "About" section (GitHub side panel — Kosi does this at go-live)
- [x] README (problem, demo, quickstart, architecture, decisions table)
- [x] Architecture diagram (docs/architecture.svg + mermaid in README)
- [ ] Demo video ≤ 5 minutes, public on YouTube or Vimeo
- [ ] Video demonstrates the working project (end-to-end, no fake demos)
- [ ] AWS Builder ID provided at submission (Kosi creates, Phase 4)
- [ ] Track selected: exactly ONE of Everyday / Professional / Good Neighbor
- [ ] All materials in English
- [ ] Project newly created during submission period (Aug 10 – Sep 14); any pre-existing code disclosed
- [ ] Project runs on juror's machine from README instructions without costs or secrets (our own constraint, matches "free for judges")

## Scoring criteria (Section 6; weights unpublished — serve all)

- [ ] Technological Implementation — skillful/deep Strands use; live demo link and/or AgentCore deployment strengthen score (optional)
- [ ] Design — complete, coherent product experience (CLI ok if the experience is right)
- [ ] Potential Impact — credible, specific use case for a real audience
- [ ] Creativity & Originality — non-obvious use of Strands
- [ ] Presentation — video shows end-to-end + pitch (problem, audience, why it matters)

## Bonus

- [ ] builder.aws.com blog post(s), public, "Agents for Humans" in title (hashtag requirement removed 8/12) — positively impacts score; multiple posts allowed

## Eligibility (verified)

- [x] Germany eligible (excluded: Italy, Brazil, Russia, UAE, others — not us)
- [x] Solo or team allowed; one representative submits on Devpost
- [x] Multiple submissions allowed if substantially different

## Our internal guardrails (from mission brief)

- [ ] No cloud costs, no accounts needed for build; no scraping of login-walled sites
- [ ] Secrets never committed (.env ignored; demo runs without any API key if optional LLM-free replay mode used)
- [ ] Submission itself only WITH Kosi (Phase 4, Sep 12)
