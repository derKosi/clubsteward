"""Session recorder: captures a real run's artifacts so it can be replayed without an LLM.

Why: judges (and anyone without a Z.ai key) must still see the full experience.
Replay applies the recorded effects (drafts, register updates, decision queue,
console transcript) — clearly labeled as a recorded session, never presented as live.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _snapshot(data_dir: Path) -> dict[str, Any]:
    outbox = {p.name: p.read_text(encoding="utf-8") for p in sorted((data_dir / "outbox").glob("*.eml"))}
    decisions = {p.name: p.read_text(encoding="utf-8") for p in sorted((data_dir / "decisions").glob("*.json"))}
    register = (data_dir / "register.csv").read_text(encoding="utf-8") if (data_dir / "register.csv").exists() else ""
    log = (data_dir / "activity.log").read_text(encoding="utf-8") if (data_dir / "activity.log").exists() else ""
    return {"outbox": outbox, "decisions": decisions, "register": register, "log": log}


class RunRecorder:
    """Records pipeline + decide steps with artifact diffs per step."""

    def __init__(self, data_dir: Path):
        self.data_dir = data_dir
        self._prev = _snapshot(data_dir)
        self._pending_decide: dict[str, Any] | None = None
        self.doc: dict[str, Any] = {
            "recorded_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "model": "",
            "pipeline_steps": [],
            "decide_steps": [],
            "final": None,
        }

    def set_model(self, model_id: str) -> None:
        self.doc["model"] = model_id

    def _diff(self) -> dict[str, Any]:
        cur = _snapshot(self.data_dir)
        drafts_added = {k: v for k, v in cur["outbox"].items() if self._prev["outbox"].get(k) != v}
        decisions_added = {k: v for k, v in cur["decisions"].items() if self._prev["decisions"].get(k) != v}
        register_changed = cur["register"] if cur["register"] != self._prev["register"] else None
        log_changed = cur["log"] if cur["log"] != self._prev["log"] else None
        self._prev = cur
        return {
            "drafts": drafts_added,
            "decisions": decisions_added,
            "register": register_changed,
            "log": log_changed,
        }

    def pipeline_step(self, mail_file: str, lines: list[str], moves: list[str]) -> None:
        self.doc["pipeline_steps"].append({
            "mail_file": mail_file,
            "lines": lines,
            "moves": moves,  # e.g. ["inbox→processed"] or ["inbox→decisions"]
            "effects": self._diff(),
        })

    def decide_step_begin(self, decision_id: str, subject: str, lines: list[str]) -> None:
        """Start a decide step: record transcript now, effects captured at end()."""
        self._pending_decide = {"decision_id": decision_id, "subject": subject, "lines": lines, "effects": {}}

    def decide_step_end(self) -> None:
        """Close the pending decide step, capturing artifact effects of the execution."""
        if self._pending_decide is not None:
            self._pending_decide["effects"] = self._diff()
            self.doc["decide_steps"].append(self._pending_decide)
            self._pending_decide = None

    def finish(self, lines: list[str]) -> None:
        self.doc["final"] = {"lines": lines, "artifacts": _snapshot(self.data_dir)}

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.doc, indent=1, ensure_ascii=False), encoding="utf-8")
