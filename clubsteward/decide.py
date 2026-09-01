"""Human decision loop: work through pending decisions in demo/data/decisions.

Run: uv run python -m clubsteward.decide          (interactive)
     uv run python -m clubsteward.decide y        (approve all — scripted demos)
"""

from __future__ import annotations

import json
import shutil
import sys

from .agents import ClubSteward
from .config import Config
from .interventions import set_case
from .models import Decision, MailItem
from .policy import ClubPolicy
from .tools import set_config

# ANSI colors (plain fallback if not a tty)
if sys.stdout.isatty():
    C_TITLE = "\033[1;96m"   # cyan bold
    C_DIM = "\033[2m"        # dim
    C_YELLOW = "\033[93m"
    C_GREEN = "\033[92m"
    C_RED = "\033[91m"
    C_BOLD = "\033[1m"
    R = "\033[0m"            # reset
else:
    C_TITLE = C_DIM = C_YELLOW = C_GREEN = C_RED = C_BOLD = R = ""


def show(d: Decision, cfg: Config) -> None:
    print()
    print(f"{C_TITLE}┌─ DECISION {d.id} " + "─" * max(0, 46 - len(d.id)) + f"{R}")
    print(f"{C_BOLD}│ Subject:{R} {d.subject}")
    print(f"{C_BOLD}│ From:{R}    {d.from_name} <{d.from_email}>")
    print(f"{C_BOLD}│ Intent:{R}  {d.triage.intent.value}   {C_DIM}(confidence {d.triage.confidence:.2f}){R}")
    print(f"{C_BOLD}│ Wants:{R}   {d.triage.summary}")
    if d.triage.details:
        details = json.dumps(d.triage.details, ensure_ascii=False)
        print(f"{C_BOLD}│ Facts:{R}   {details[:200]}")
    print(f"{C_BOLD}│ Agent proposes:{R} {d.triage.proposed_action[:200]}")
    print(f"{C_YELLOW}│ Why you're asked:{R} {d.policy_reason}{R}")
    mail_path = cfg.decisions_dir / d.mail_file
    if mail_path.exists():
        body = MailItem.parse(mail_path).body
        print(f"{C_DIM}│ --- mail (excerpt) ---{R}")
        for ln in body.splitlines()[:12]:
            print(f"{C_DIM}│ {ln}{R}")
    print(f"{C_TITLE}└{'─' * 58}{R}")


def run(assume: str | None = None, club: str | None = None) -> int:
    cfg = Config.load(club)
    brand = cfg.brand
    if brand.name and cfg.club_id != "demo":
        print(f"{C_TITLE}=== {brand.name} — Entscheidungen ==={R}" if brand.tagline else f"{C_TITLE}=== {brand.name} ==={R}")
    if not cfg.api_key:
        print(f"{C_RED}ERROR: ZAI_API_KEY not set{R}")
        return 2
    set_config(cfg)
    policy = ClubPolicy.load(cfg.data_dir / "policy.yaml")
    ck = ClubSteward(cfg, policy)

    pending = sorted(cfg.decisions_dir.glob("*.json"))
    if not pending:
        print("No pending decisions.")
        return 0
    print(f"{C_BOLD}{len(pending)} decision(s) need a human.{R}")

    for pj in pending:
        d = Decision.model_validate_json(pj.read_text())
        show(d, cfg)
        if assume:
            answer = assume
        else:
            answer = input(f"{C_BOLD}Approve? [y]es / [e]dit (give instructions) / [n]o: {R}").strip().lower()
        if answer in ("y", "yes"):
            approve(d, ck, club=club)
            _cleanup(cfg, d, pj)
            print(f"{C_GREEN}→ {d.id} approved & executed.{R}")
        elif answer in ("e", "edit"):
            instr = input("Extra instructions for the agent: ")
            approve(d, ck, extra=instr, club=club)
            _cleanup(cfg, d, pj)
            print(f"{C_GREEN}→ {d.id} executed with your instructions.{R}")
        else:
            d.status = "denied"
            pj.write_text(d.model_dump_json(indent=2), encoding="utf-8")
            print(f"{C_RED}→ {d.id} denied (kept as record).{R}")
    print(f"\n{C_GREEN}Inbox zero. The club ran itself — you made the calls that mattered.{R}")
    return 0


def _cleanup(cfg, d: Decision, pj) -> None:
    pj.unlink()
    mail = cfg.decisions_dir / d.mail_file
    if mail.exists():
        shutil.move(str(mail), cfg.processed_dir / d.mail_file)


def approve(d: Decision, ck: ClubSteward, extra: str = "", club: str | None = None) -> None:
    mail_path = Config.load(club).decisions_dir / d.mail_file
    mail = MailItem.parse(mail_path)
    # Human decided → write pre-approved; the audit trail carries the decision id
    agent = ck.act_agent_for(mail.from_email)
    set_case(agent, {
        "autonomy": "auto_preapproved",
        "intent": d.triage.intent.value,
        "decision_id": d.id,
        "mail_file": d.mail_file,
    })
    pol = ck.policy
    fees = "\n".join(f"  {k}: {v}" for k, v in pol.fees.items()) if pol else "(none)"
    sig = pol.reply_signature.strip() if pol else ""
    prompt = (
        f"The human club secretary has APPROVED this case with the following judgment.\n"
        f"Human note: {extra or 'approved as proposed'}\n\n"
        f"CLUB FACTS (authoritative — NEVER invent amounts; reply in the member's language, German default):\n"
        f"  club: {pol.club_name if pol else '-'} | tone: {pol.tone if pol else '-'}\n"
        f"  fees:\n{fees}\n"
        f"  signature (use EXACTLY):\n{sig}\n\n"
        f"MAIL from {mail.from_name} <{mail.from_email}> subject '{mail.subject}':\n{mail.body[:2000]}\n\n"
        f"TRIAGE: intent={d.triage.intent.value}, summary={d.triage.summary}\nDETAILS: {d.triage.details}\n"
        f"Proposed action: {d.triage.proposed_action}\n\n"
        f"Execute now with the tools (register update, draft reply, log entry)."
    )
    result = agent(prompt)
    print(f"{C_DIM}  agent: {str(result)[:160]}{R}")


if __name__ == "__main__":
    assume = sys.argv[1] if len(sys.argv) > 1 and sys.argv[1] in ("y", "n") else None
    sys.exit(run(assume))
