"""Human decision loop: work through pending decisions in demo/data/decisions.

Run: uv run python -m clubkeeper.decide
"""

from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

from .agents import ClubKeeper, triage_one
from .config import Config
from .models import Decision, MailItem
from .policy import ClubPolicy
from .tools import set_config


def show(d: Decision) -> None:
    print("=" * 60)
    print(f"DECISION {d.id} — {d.subject}")
    print(f"From: {d.from_name} <{d.from_email}>")
    print(f"Intent: {d.triage.intent.value} | confidence {d.triage.confidence:.2f}")
    print(f"Summary: {d.triage.summary}")
    print(f"Details: {json.dumps(d.triage.details, ensure_ascii=False)}")
    print(f"Proposed: {d.triage.proposed_action}")
    print(f"Policy:   {d.policy_reason}")
    mail_path = Config.load().decisions_dir / d.mail_file
    if mail_path.exists():
        print("-" * 60)
        print(MailItem.parse(mail_path).body[:900])
    print("=" * 60)


def run(assume: str | None = None) -> int:
    cfg = Config.load()
    if not cfg.api_key:
        print("ERROR: ZAI_API_KEY not set")
        return 2
    set_config(cfg)
    policy = ClubPolicy.load(cfg.data_dir / "policy.yaml")
    ck = ClubKeeper(cfg, policy)

    pending = sorted(cfg.decisions_dir.glob("*.json"))
    if not pending:
        print("No pending decisions.")
        return 0

    for pj in pending:
        d = Decision.model_validate_json(pj.read_text())
        show(d)
        if assume:
            answer = assume
        else:
            answer = input("Approve proposed action? [y]es / [e]dit instructions / [n]o: ").strip().lower()
        if answer in ("y", "yes"):
            approve(d, ck)
            pj.unlink()
            shutil.move(str(cfg.decisions_dir / d.mail_file), cfg.processed_dir / d.mail_file)
            print(f"→ {d.id} approved & executed.")
        elif answer in ("e", "edit"):
            instr = input("Extra instructions for the agent: ")
            approve(d, ck, extra=instr)
            pj.unlink()
            shutil.move(str(cfg.decisions_dir / d.mail_file), cfg.processed_dir / d.mail_file)
            print(f"→ {d.id} executed with instructions.")
        else:
            d.status = "denied"
            pj.write_text(d.model_dump_json(indent=2), encoding="utf-8")
            print(f"→ {d.id} denied (kept as denied.json).")
    return 0


def approve(d: Decision, ck: ClubKeeper, extra: str = "") -> None:
    mail_path = Config.load().decisions_dir / d.mail_file
    mail = MailItem.parse(mail_path)
    prompt = (
        f"The human club secretary has APPROVED this case with the following judgment.\n"
        f"Human note: {extra or 'approved as proposed'}\n\n"
        f"MAIL from {mail.from_name} <{mail.from_email}> subject '{mail.subject}':\n{mail.body[:2000]}\n\n"
        f"TRIAGE: intent={d.triage.intent.value}, summary={d.triage.summary}\nDETAILS: {d.triage.details}\n"
        f"Proposed action: {d.triage.proposed_action}\n\n"
        f"Execute now with the tools (register update, draft reply, log entry)."
    )
    result = ck.act_agent(prompt)
    print(str(result)[:200])


if __name__ == "__main__":
    assume = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("y", "n") else None
    sys.exit(run(assume))
