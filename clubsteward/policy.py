"""Club policy as data — the club edits this file, nobody edits code.

Every rule maps an intent to an autonomy decision:
  auto  → agent acts and drafts, no human needed
  ask   → agent pauses and puts the case into the human decision queue
  reject→ agent does not process (spam etc.)

`ask_if` conditions allow fine-grained overrides, e.g. "auto for changes,
ask whenever money or membership status is affected".
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class PolicyRule(BaseModel):
    intent: str
    decision: str  # auto | ask | reject
    ask_if: list[str] = Field(default_factory=list, description="conditions (free text, evaluated by the LLM classifier)")
    note: str = ""


class ClubPolicy(BaseModel):
    club_name: str
    season: str
    fees: dict[str, float] = Field(default_factory=dict)
    tone: str = "friendly, warm, concise club volunteer"
    reply_signature: str = ""
    rules: list[PolicyRule]

    @classmethod
    def load(cls, path) -> "ClubPolicy":
        data = yaml.safe_load(Path(str(path)).read_text(encoding="utf-8"))
        return cls(**data)

    def rule_for(self, intent: str) -> PolicyRule | None:
        for r in self.rules:
            if r.intent == intent:
                return r
        return None
