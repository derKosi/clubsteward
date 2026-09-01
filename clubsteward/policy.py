"""Club policy as data — the club edits this file, nobody edits code.

Every rule maps an intent to an autonomy decision:
  auto  → agent acts and drafts, no human needed
  ask   → agent pauses and puts the case into the human decision queue
  reject→ agent does not process (spam etc.)

`ask_if` lists flag names (e.g. [medical, waiting_list]) that escalate an
otherwise auto decision to ask the human. Entries must be flag names, not prose.
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, Field, field_validator


class PolicyRule(BaseModel):
    intent: str
    decision: str  # auto | ask | reject
    ask_if: list[str] = Field(default_factory=list, description="flag names as emitted by triage (e.g. [medical, waiting_list]) — exact match after normalization")
    note: str = ""

    @field_validator("ask_if")
    @classmethod
    def _ask_if_entries_are_flag_names(cls, v: list[str]) -> list[str]:
        """Fail loudly on prose entries: matching is exact flag equivalence, so a
        sentence would silently NEVER match and escalations would be lost."""
        for cond in v:
            if len(cond.split()) > 3:
                raise ValueError(
                    f"ask_if entry '{cond}' looks like prose — use a flag name "
                    f"(e.g. 'medical', 'waiting_list') as emitted by the triage agent"
                )
        return [c.strip() for c in v]


class ClubPolicy(BaseModel):
    club_name: str
    season: str
    fees: dict[str, float] = Field(default_factory=dict)
    tone: str = "friendly, warm, concise club volunteer"
    reply_signature: str = ""
    rules: list[PolicyRule]

    @classmethod
    def load(cls, path) -> ClubPolicy:
        data = yaml.safe_load(Path(str(path)).read_text(encoding="utf-8"))
        return cls(**data)

    def rule_for(self, intent: str) -> PolicyRule | None:
        for r in self.rules:
            if r.intent == intent:
                return r
        return None
