"""Run summary: metrics from Strands AgentResults, written to demo/data/run_summary.json.

Gives the club transparency: how many mails, which route (auto/ask/reject),
tokens and latency per step, and total cost estimate for the night.
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class StepMetric(BaseModel):
    mail_file: str
    intent: str
    route: str  # auto | ask | reject
    triage_tokens: int = 0
    act_tokens: int = 0
    act_latency_ms: int = 0
    tool_calls: int = 0
    notes: str = ""


class RunSummary(BaseModel):
    started_at: str
    finished_at: str = ""
    mails_total: int = 0
    auto: int = 0
    ask: int = 0
    rejected: int = 0
    total_tokens: int = 0
    steps: list[StepMetric] = Field(default_factory=list)

    def finish(self) -> None:
        self.finished_at = datetime.now(UTC).isoformat(timespec="seconds")
        self.total_tokens = sum(s.triage_tokens + s.act_tokens for s in self.steps)


def _usage_from_result(result: Any) -> tuple[int, int]:
    """Extract (total_tokens, latency_ms) from a Strands AgentResult-ish object."""
    metrics = getattr(result, "metrics", None) or getattr(result, "event_loop_metrics", None)
    tokens = 0
    if metrics is not None:
        try:
            usage = metrics.accumulated_usage  # dict: inputTokens/outputTokens/totalTokens
            if isinstance(usage, dict):
                tokens = int(usage.get("totalTokens", 0) or 0)
            else:
                tokens = int(getattr(usage, "totalTokens", 0) or 0)
        except Exception:
            pass
    latency = 0
    if metrics is not None:
        try:
            lm = metrics.accumulated_metrics
            latency = int(lm.get("latencyMs", 0) if isinstance(lm, dict) else getattr(lm, "latencyMs", 0))
        except Exception:
            pass
    return tokens, latency


def _tool_calls_from_messages(messages: Any) -> int:
    n = 0
    for m in messages or []:
        content = getattr(m, "content", None) or (m.get("content") if isinstance(m, dict) else None) or []
        for c in content:
            if isinstance(c, dict) and "toolUse" in c:
                n += 1
    return n


def new_summary() -> RunSummary:
    return RunSummary(started_at=datetime.now(UTC).isoformat(timespec="seconds"))


def record_triage(summary: RunSummary, mail_file: str, intent: str, route: str, result: Any, triage_tokens: int = 0) -> None:
    tokens, _ = _usage_from_result(result)
    summary.steps.append(StepMetric(mail_file=mail_file, intent=intent, route=route, triage_tokens=triage_tokens or tokens))
    summary.mails_total += 1
    if route == "auto":
        summary.auto += 1
    elif route == "ask":
        summary.ask += 1
    else:
        summary.rejected += 1


def record_act(summary: RunSummary, mail_file: str, result: Any, messages: list[dict]) -> None:
    tokens, latency = _usage_from_result(result)
    for s in reversed(summary.steps):
        if s.mail_file == mail_file:
            s.act_tokens = tokens
            s.act_latency_ms = latency
            s.tool_calls = _tool_calls_from_messages(messages)
            break


def save(summary: RunSummary, path: Path) -> None:
    summary.finish()
    path.write_text(json.dumps(summary.model_dump(), indent=2), encoding="utf-8")


def cost_estimate(total_tokens: int) -> float:
    """Rough cost in EUR for glm-5-turbo class models (per 1M tokens, blended)."""
    per_m = 0.30
    return round(total_tokens / 1_000_000 * per_m, 4)
