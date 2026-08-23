"""Batch pipeline: process every mail in the inbox through triage → policy → act/ask.

Run: uv run python -m clubkeeper.pipeline
"""

from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path

from .agents import ClubKeeper, TriageTokenTracker, evaluate_policy, safety_flag_check, triage_one
from .config import Config
from .interventions import set_case
from .metrics import new_summary, record_act, record_triage, save as save_summary, cost_estimate
from .models import Decision, MailItem
from .policy import ClubPolicy
from .recorder import RunRecorder
from .tools import set_config


def run(max_mails: int | None = None, recorder: RunRecorder | None = None) -> int:
    cfg = Config.load()
    if not cfg.api_key:
        print("ERROR: ZAI_API_KEY not set (see .env.example)")
        return 2
    set_config(cfg)
    policy = ClubPolicy.load(cfg.data_dir / "policy.yaml")
    ck = ClubKeeper(cfg, policy)
    if recorder:
        recorder.set_model(cfg.model_id)

    for d in (cfg.outbox_dir, cfg.decisions_dir, cfg.processed_dir):
        d.mkdir(parents=True, exist_ok=True)

    mails = sorted(p for p in cfg.inbox_dir.glob("*.eml"))
    if max_mails:
        mails = mails[:max_mails]
    if not mails:
        print("Inbox is empty — nothing to do.")
        return 0

    print(f"Processing {len(mails)} mail(s) with model {cfg.model_id} ...")
    summary = new_summary()
    tracker = TriageTokenTracker(ck.triage_agent)
    processed, asked = 0, 0
    for path in mails:
        mail = MailItem.parse(path)
        print(f"\n--- {path.name} ---")
        try:
            triage = triage_one(ck.triage_agent, mail)
        except Exception as e:
            print(f"  TRIAGE FAILED: {e}")
            continue
        triage = safety_flag_check(triage, mail)
        decision, reason = evaluate_policy(policy, triage)
        record_triage(summary, path.name, triage.intent.value, decision, None, triage_tokens=tracker.delta())
        line1 = f"  intent={triage.intent.value} confidence={triage.confidence:.2f} → {decision.upper()}"
        print(line1)
        if decision == "reject":
            shutil.move(str(path), cfg.processed_dir / path.name)
            processed += 1
            if recorder:
                recorder.pipeline_step(path.name, [line1], ["inbox→processed"])  # spam: processed + discarded silently
            continue
        if decision == "ask":
            d = Decision(
                id=str(uuid.uuid4())[:8],
                mail_file=path.name,
                from_name=mail.from_name,
                from_email=mail.from_email,
                subject=mail.subject,
                triage=triage,
                policy_reason=reason,
            )
            (cfg.decisions_dir / f"{d.id}.json").write_text(d.model_dump_json(indent=2), encoding="utf-8")
            line2 = f"  → decision queued: {d.id} ({reason})"
            print(line2)
            shutil.move(str(path), cfg.decisions_dir / path.name)
            asked += 1
            if recorder:
                recorder.pipeline_step(path.name, [line1, line2], ["inbox→decisions"])
            continue
        # auto path: run act agent (HITL classifier approves writes via policy)
        agent = ck.act_agent_for(mail.from_email)
        set_case(agent, {
            "autonomy": "auto",
            "intent": triage.intent.value,
            "mail_file": path.name,
        })
        result = agent(act_prompt(mail, triage))
        record_act(summary, path.name, result, agent.messages)
        line3 = f"  act: {str(result)[:140]}"
        print(line3)
        shutil.move(str(path), cfg.processed_dir / path.name)
        processed += 1
        if recorder:
            recorder.pipeline_step(path.name, [line1, line3], ["inbox→processed"])
    tail1 = f"\nDone: {processed} auto-processed, {asked} queued for human decision."
    tail2 = f"Outbox drafts: {len(list(cfg.outbox_dir.glob('*.eml')))} | Decisions pending: {len(list(cfg.decisions_dir.glob('*.json')))}"
    print(tail1)
    print(tail2)
    save_summary(summary, cfg.data_dir / "run_summary.json")
    tail3 = (f"Run summary: {summary.mails_total} mails · {summary.auto} auto / {summary.ask} ask / {summary.rejected} reject · "
             f"{summary.total_tokens} tokens (~€{cost_estimate(summary.total_tokens)})")
    print(tail3)
    if recorder:
        recorder.finish([tail1, tail2, tail3])
    return 0


def act_prompt(mail: MailItem, triage) -> str:
    return (
        f"Process this case for the club automatically.\n\n"
        f"MAIL from {mail.from_name} <{mail.from_email}> subject '{mail.subject}':\n{mail.body[:2000]}\n\n"
        f"TRIAGE: intent={triage.intent.value}, summary={triage.summary}\n"
        f"DETAILS: {triage.details}\n"
        f"Proposed action: {triage.proposed_action}\n\n"
        f"Use the tools to update the register and draft a reply to {mail.from_email}. Finish with a log entry."
    )


if __name__ == "__main__":
    sys.exit(run())
