"""Domain models for ClubKeeper."""

from __future__ import annotations

import csv
import email
import email.policy
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator


class Intent(str, Enum):
    SIGNUP = "signup"
    ADDRESS_CHANGE = "address_change"
    CANCELLATION = "cancellation"
    HARDSHIP_WAIVER = "hardship_waiver"
    QUESTION = "question"
    COMPLAINT = "complaint"
    SPAM = "spam"
    UNKNOWN = "unknown"


class Action(str, Enum):
    AUTO = "auto"      # agent acts + drafts, human not needed
    ASK = "ask"        # human decision required before acting
    REJECT = "reject"  # do not process (spam etc.)


class MailItem(BaseModel):
    """A parsed inbound email from the club inbox folder."""

    path: Path
    from_email: str
    from_name: str
    subject: str
    date: str
    body: str

    @classmethod
    def parse(cls, path: Path) -> "MailItem":
        msg = email.message_from_bytes(path.read_bytes(), policy=email.policy.default)
        body = msg.get_body(preferencelist=("plain",))
        text = body.get_content() if body else ""
        if not isinstance(text, str):
            text = ""
        from_addr = msg.get("From", "unknown@example.org")
        name, _, addr = str(from_addr).partition("<")
        return cls(
            path=path,
            from_email=addr.strip().rstrip(">") or str(from_addr),
            from_name=name.strip().strip('"') or str(from_addr),
            subject=str(msg.get("Subject", "(no subject)")),
            date=str(msg.get("Date", "")),
            body=text.strip(),
        )

    def preview(self, chars: int = 160) -> str:
        return f"From: {self.from_name} <{self.from_email}> | {self.subject}\n{self.body[:chars]}"


class TriageResult(BaseModel):
    """Structured classification of one inbound mail (LLM output)."""

    intent: Intent
    member_email: str | None = Field(None, description="sender email if it matches/claims a member")
    member_name: str | None = None
    summary: str = Field(..., description="one sentence: what the sender wants")
    proposed_action: str = Field(..., description="what the agent proposes to do")
    details: dict[str, Any] = Field(default_factory=dict, description="extracted facts: address, team, child name, amounts...")
    flags: list[str] = Field(default_factory=list, description="special-condition tags: medical, waiting_list, refund, duplicate, legal ...")
    confidence: float = Field(0.0, ge=0.0, le=1.0)

    @field_validator("flags", mode="before")
    @classmethod
    def _flags_none_to_list(cls, v):
        """LLMs sometimes emit null for optional lists — normalize to []."""
        return v if isinstance(v, list) else ([] if v is None else [v])


class Decision(BaseModel):
    """One item in the human decision queue."""

    id: str
    mail_file: str
    from_name: str
    from_email: str
    subject: str
    triage: TriageResult
    policy_reason: str
    status: str = "pending"  # pending | approved | denied
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"))


class Draft(BaseModel):
    """A drafted reply saved to the outbox."""

    to: str
    subject: str
    body: str


REGISTER_FIELDS = ["member_id", "first_name", "last_name", "email", "birth_year", "team", "fee_status", "joined", "notes"]


def load_register(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return [dict(row) for row in csv.DictReader(f)]


def save_register(path: Path, rows: list[dict[str, str]]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=REGISTER_FIELDS)
        w.writeheader()
        w.writerows(rows)
