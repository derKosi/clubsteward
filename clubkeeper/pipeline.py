"""Batch pipeline: process every mail in the inbox through triage → policy → act/ask.

Run: uv run python -m clubkeeper.pipeline
"""

from __future__ import annotations

import json
import shutil
import sys
import uuid
from pathlib import Path

from .agents import ClubKeeper, evaluate_policy, triage_one
from .config import Config
from .interventions import set_case
from .models import Decision, MailItem
from .policy import ClubPolicy
from .tools import set_config


def run(max_mails: int | None = None) -> int:
    cfg = Config.load()
    if not cfg.api_key:
        print("ERROR: ZAI_API_KEY not set (see .env.example)")
        return 2
    set_config(cfg)
    policy = ClubPolicy.load(cfg.data_dir / "policy.yaml")
    ck = ClubKeeper(cfg, policy)

    for d in (cfg.outbox_dir, cfg.decisions_dir, cfg.processed_dir):
        d.mkdir(parents=True, exist_ok=True)

    mails = sorted(p for p in cfg.inbox_dir.glob("*.eml"))
    if max_mails:
        mails = mails[:max_mails]
    if not mails:
        print("Inbox is empty — nothing to do.")
        return 0

    print(f"Processing {len(mails)} mail(s) with model {cfg.model_id} ...")
    processed, asked = 0, 0
    for path in mails:
        mail = MailItem.parse(path)
        print(f"\n--- {path.name} ---")
        try:
            triage = triage_one(ck.triage_agent, mail)
        except Exception as e:
            print(f"  TRIAGE FAILED: {e}")
            continue
        decision, reason = evaluate_policy(policy, triage)
        print(f"  intent={triage.intent.value} confidence={triage.confidence:.2f} → {decision.upper()}")
        if decision == "reject":
            shutil.move(str(path), cfg.processed_dir / path.name)
            processed += 1
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
            print(f"  → decision queued: {d.id} ({reason})")
            shutil.move(str(path), cfg.decisions_dir / path.name)
            asked += 1
            mail_text = mail.body  # act later, after human answers
            continue
        # auto path: run act agent (HITL classifier approves writes via policy)
        agent = ck.act_agent_for(mail.from_email)
        set_case(agent, {
            "autonomy": "auto",
            "intent": triage.intent.value,
            "mail_file": path.name,
        })
        result = agent(act_prompt(mail, triage))
        print(f"  act: {str(result)[:140]}")
        shutil.move(str(path), cfg.processed_dir / path.name)
        processed += 1

    print(f"\nDone: {processed} auto-processed, {asked} queued for human decision.")
    print(f"Outbox drafts: {len(list(cfg.outbox_dir.glob('*.eml')))} | Decisions pending: {len(list(cfg.decisions_dir.glob('*.json')))}")
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
