"""Batch pipeline: process every mail in the inbox through triage → policy → act/ask.

Run: uv run python -m clubsteward.pipeline
"""

from __future__ import annotations

import shutil
import sys
import uuid
from collections.abc import Callable
from pathlib import Path

from .agents import (
    ClubSteward,
    TriageTokenTracker,
    evaluate_policy,
    safety_flag_check,
    triage_one,
)
from .config import Config
from .interventions import set_case
from .metrics import cost_estimate, new_summary, record_act, record_triage
from .metrics import save as save_summary
from .models import Decision, MailItem
from .policy import ClubPolicy
from .recorder import RunRecorder
from .tools import set_config


def run(max_mails: int | None = None, recorder: RunRecorder | None = None, club: str | None = None,
        should_stop: Callable[[], bool] | None = None) -> int:
    cfg = Config.load(club)
    brand = cfg.brand
    if brand.name and cfg.club_id != "demo":
        print(f"=== {brand.name} — {brand.tagline} ===" if brand.tagline else f"=== {brand.name} ===")
    if not cfg.api_key:
        print("ERROR: ZAI_API_KEY not set (see .env.example)")
        return 2
    set_config(cfg)
    policy = ClubPolicy.load(cfg.data_dir / "policy.yaml")
    ck = ClubSteward(cfg, policy)
    if recorder:
        recorder.set_model(cfg.model_id)

    for d in (cfg.outbox_dir, cfg.decisions_dir, cfg.processed_dir, cfg.errors_dir):
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
        if should_stop and should_stop():
            remaining = len(mails) - mails.index(path)
            print(f"\n⏹ Stop requested — {remaining} mail(s) stay in the inbox for the next run.")
            break
        trace = process_mail(cfg, ck, policy, summary, tracker, path, recorder)
        if trace["outcome"] in ("processed", "rejected"):
            processed += 1
        elif trace["outcome"] == "queued":
            asked += 1
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


def process_mail(cfg: Config, ck: ClubSteward, policy: ClubPolicy, summary, tracker,
                 path: Path, recorder: RunRecorder | None = None) -> dict:
    """Triage → policy → act/queue for ONE mail: file moves, summary, prints.

    Returns a trace so callers (nightly run, web step mode) can show what
    happened: triage fields, decision + reason, the drafted reply (auto) or
    the queued decision id (ask). outcome in {processed, rejected, queued, error}.
    """
    mail = MailItem.parse(path)
    print(f"\n--- {path.name} ---")
    trace: dict = {"file": path.name, "from_name": mail.from_name, "from_email": mail.from_email,
                   "subject": mail.subject, "body": mail.body}
    try:
        triage = triage_one(ck.triage_agent, mail, locale=cfg.brand.locale)
    except Exception as e:
        print(f"  TRIAGE FAILED: {e}")
        shutil.move(str(path), cfg.errors_dir / path.name)
        record_triage(summary, path.name, "unknown", "reject", None, triage_tokens=0)
        trace.update(intent="unknown", confidence=0.0, flags=[], summary="", details={},
                     proposed_action="", decision=None, reason=f"triage failed: {e}", outcome="error")
        return trace
    triage = safety_flag_check(triage, mail)
    decision, reason = evaluate_policy(policy, triage)
    record_triage(summary, path.name, triage.intent.value, decision, None,
                  triage_tokens=tracker.delta() if tracker else 0)
    line1 = f"  intent={triage.intent.value} confidence={triage.confidence:.2f} → {decision.upper()}"
    print(line1)
    trace.update(intent=triage.intent.value, confidence=triage.confidence, flags=list(triage.flags or []),
                 summary=triage.summary, details=triage.details, proposed_action=triage.proposed_action)
    if decision == "reject":
        shutil.move(str(path), cfg.processed_dir / path.name)
        if recorder:
            recorder.pipeline_step(path.name, [line1], ["inbox→processed"])  # spam: processed + discarded silently
        trace.update(decision="reject", reason=reason, outcome="rejected")
        return trace
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
        if recorder:
            recorder.pipeline_step(path.name, [line1, line2], ["inbox→decisions"])
        trace.update(decision="ask", reason=reason, decision_id=d.id, outcome="queued")
        return trace
    # auto path: run act agent (HITL classifier approves writes via policy)
    agent = ck.act_agent_for(mail.from_email)
    set_case(agent, {
        "autonomy": "auto",
        "intent": triage.intent.value,
        "mail_file": path.name,
    })
    try:
        result = agent(act_prompt(mail, triage, policy))
    except Exception as e:
        # one broken act run (e.g. MaxTokensReached) must not kill the night —
        # file the mail into _errors like a triage failure and keep going.
        print(f"  ACT FAILED: {e}")
        shutil.move(str(path), cfg.errors_dir / path.name)
        record_act(summary, path.name, None, [])
        if recorder:
            recorder.pipeline_step(path.name, [line1, f"  ACT FAILED: {e}"], ["inbox→_errors"])
        trace.update(decision="auto", reason=reason, error=str(e), outcome="error")
        return trace
    record_act(summary, path.name, result, agent.messages)
    line3 = f"  act: {str(result)[:140]}"
    print(line3)
    shutil.move(str(path), cfg.processed_dir / path.name)
    if recorder:
        recorder.pipeline_step(path.name, [line1, line3], ["inbox→processed"])
    trace.update(decision="auto", reason=reason, draft=_draft_for(cfg, mail.from_email), outcome="processed")
    return trace


def _draft_for(cfg: Config, to_email: str) -> dict | None:
    """The draft the act agent just saved for this recipient (one per recipient)."""
    for p in sorted(cfg.outbox_dir.glob("draft_*.eml")):
        text = p.read_text(encoding="utf-8")
        head, _, body = text.partition("\n\n")
        if any(ln.strip() == f"To: {to_email}" for ln in head.splitlines()):
            subject = next((ln[8:].strip() for ln in head.splitlines() if ln.lower().startswith("subject:")), "")
            return {"file": p.name, "subject": subject, "to": to_email, "body": body.strip()}
    return None


def run_one(club: str | None = None) -> dict:
    """Process exactly ONE mail — the first in the inbox — and return its trace.

    The step mode behind the console's 'Process next mail' button: the same
    code path as the nightly run, one click per mail, state stays in folders.
    """
    cfg = Config.load(club)
    if not cfg.api_key:
        raise RuntimeError("ZAI_API_KEY not set (see .env.example)")
    set_config(cfg)
    policy = ClubPolicy.load(cfg.data_dir / "policy.yaml")
    ck = ClubSteward(cfg, policy)
    for d in (cfg.outbox_dir, cfg.decisions_dir, cfg.processed_dir, cfg.errors_dir):
        d.mkdir(parents=True, exist_ok=True)
    mails = sorted(p for p in cfg.inbox_dir.glob("*.eml"))
    if not mails:
        return {"outcome": "empty"}
    summary = new_summary()
    tracker = TriageTokenTracker(ck.triage_agent)
    return process_mail(cfg, ck, policy, summary, tracker, mails[0])


def act_prompt(mail: MailItem, triage, policy: ClubPolicy | None = None) -> str:
    fees = ""
    sig = ""
    if policy is not None:
        fees = "\n".join(f"  {k}: {v}" for k, v in policy.fees.items())
        sig = policy.reply_signature.strip()
    return (
        f"Process this case for the club automatically.\n\n"
        f"CLUB FACTS (authoritative — NEVER invent or change amounts; if a fee is not listed, say you will confirm):\n"
        f"  club: {policy.club_name if policy else '-'}\n"
        f"  season: {policy.season if policy else '-'}\n"
        f"  tone: {policy.tone if policy else '-'}\n"
        f"  fees:\n{fees if fees else '    (none listed)'}\n"
        f"  signature (use EXACTLY this signature):\n{sig}\n\n"
        f"MAIL from {mail.from_name} <{mail.from_email}> subject '{mail.subject}':\n{mail.body[:2000]}\n\n"
        f"TRIAGE: intent={triage.intent.value}, summary={triage.summary}\n"
        f"DETAILS: {triage.details}\n"
        f"Proposed action: {triage.proposed_action}\n\n"
        f"Reply in the language of the member's mail (this club's default: German if unsure). "
        f"Use the tools to update the register and draft a reply to {mail.from_email}. Finish with a log entry."
    )


if __name__ == "__main__":
    sys.exit(run())
