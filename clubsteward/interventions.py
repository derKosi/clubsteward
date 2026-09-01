"""Policy-driven human-in-the-loop: club policy as a Strands intervention classifier.

How it works
------------
The act agent runs with the SDK's `HumanInTheLoop` intervention. Our custom
classifier consults

1. the tool category (read-only tools always run free), and
2. the CURRENT CASE context stored in `agent.state` (`clubsteward:case`),
   set by the pipeline / decide CLI before each invocation:

   autonomy="auto"              → policy says this intent is routine → writes proceed
   autonomy="human_supervised"  → a human is interactively approving each write (stdio)
   autonomy="auto_preapproved"  → human already approved the case; writes proceed, audit notes the decision id

So the club's YAML policy literally becomes the SDK's approval classifier —
policy-as-data all the way down, and every escalation shows the exact tool
call (with inputs) that needs a human judgment.
"""

from __future__ import annotations

from typing import Any

from strands.vended_interventions.hitl import HumanInTheLoop
from strands.vended_interventions.hitl.classifier import (
    ClassifierResult,
)

READ_TOOLS = {"register_lookup", "log_activity"}
WRITE_TOOLS = {"register_update", "register_add", "save_draft"}

CASE_STATE_KEY = "clubsteward:case"


def set_case(agent: Any, case: dict[str, Any]) -> None:
    """Attach the current case context to the agent's app state."""
    agent.state.set(CASE_STATE_KEY, case)


def policy_classifier(event: Any, **_kwargs: Any) -> ClassifierResult:
    """HumanInTheLoop classifier backed by club policy + case context."""
    tool_name = event.tool_use["name"]
    case = (event.agent.state.get(CASE_STATE_KEY) or {})
    autonomy = case.get("autonomy", "ask")
    intent = case.get("intent", "unknown")

    if tool_name in READ_TOOLS:
        return ClassifierResult(
            requires_human_in_the_loop=False,
            reason=f"read-only tool '{tool_name}'",
        )

    if tool_name in WRITE_TOOLS:
        if autonomy == "auto":
            return ClassifierResult(
                requires_human_in_the_loop=False,
                reason=f"policy: intent '{intent}' is auto-approved for this club",
            )
        if autonomy == "auto_preapproved":
            return ClassifierResult(
                requires_human_in_the_loop=False,
                reason=f"human decision {case.get('decision_id', '?')} approved this case",
            )
        return ClassifierResult(
            requires_human_in_the_loop=True,
            reason=f"policy: intent '{intent}' requires a human decision before '{tool_name}'",
        )

    # Unknown tool: fail closed
    return ClassifierResult(
        requires_human_in_the_loop=True,
        reason=f"tool '{tool_name}' is not classified — failing closed",
    )


def make_hitl(interactive: bool) -> HumanInTheLoop:
    """Build the policy-driven HITL intervention.

    interactive=True  → ask via stdio: the human approves each write live (y/n/t)
    interactive=False → batch/overnight mode: no prompts; the classifier's
                        'requires approval' verdicts must never trigger here,
                        because ask-cases are queued, not executed.
    """
    return HumanInTheLoop(
        allowed_tools=sorted(READ_TOOLS),
        classifier=policy_classifier,
        ask="stdio" if interactive else None,
        enable_trust=True,
    )
