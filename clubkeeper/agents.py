"""ClubKeeper agents: triage (understand) and act (execute) on a Strands agent loop."""

from __future__ import annotations

from strands import Agent
from strands.models.litellm import LiteLLMModel

from .config import Config
from .interventions import make_hitl
from .models import Decision, Draft, Intent, MailItem, TriageResult
from .policy import ClubPolicy, PolicyRule
from .tools import log_activity, register_add, register_lookup, register_update, save_draft

TRIAGE_SYSTEM = """You are the triage brain of ClubKeeper, an agent that helps a volunteer run
a local community sports club's inbox. Classify each member email precisely and extract facts.
Use intent "spam" for scam/phishing/lottery/ad mail that has nothing to do with the club.
Be conservative: if the sender asks for money relief or cancellation, extract amounts and reasons.
Respond ONLY with the structured schema."""

ACT_SYSTEM = """You are the executor of ClubKeeper, a club-secretary agent. You receive one triaged
case at a time. Use the tools to update the member register, draft replies, and log activity.
Rules:
- Drafts must be warm, human, concise (max ~120 words), in the club's tone, signed as configured.
- Never invent fees or members; look up before updating; add only with complete data.
- Every case ends with a log entry stating what was done and why.
- If a tool returns ERROR, stop retrying and report the problem in your final answer."""


def make_model(cfg: Config):
    return LiteLLMModel(
        client_args={"api_key": cfg.api_key, "api_base": cfg.base_url},
        model_id=f"openai/{cfg.model_id}",
        params={"max_tokens": 1024, "temperature": 0.2},
    )


class ClubKeeper:
    def __init__(self, cfg: Config, policy: ClubPolicy, interactive: bool = False):
        self.cfg = cfg
        self.policy = policy
        self.triage_agent = Agent(
            model=make_model(cfg),
            system_prompt=TRIAGE_SYSTEM,
            tools=[],
            callback_handler=None,
        )
        self.act_agent = Agent(
            model=make_model(cfg),
            system_prompt=ACT_SYSTEM,
            tools=[register_lookup, register_update, register_add, save_draft, log_activity],
            interventions=[make_hitl(interactive)],
            callback_handler=None,
        )


def triage_one(triage_agent: Agent, mail: MailItem) -> TriageResult:
    prompt = (
        f"Classify this club inbox email.\n\n"
        f"From: {mail.from_name} <{mail.from_email}>\n"
        f"Subject: {mail.subject}\nDate: {mail.date}\n\n"
        f"{mail.body[:2500]}"
    )
    return triage_agent.structured_output(TriageResult, prompt)


def evaluate_policy(policy: ClubPolicy, triage: TriageResult) -> tuple[str, str]:
    """Return (decision, reason). decision in {auto, ask, reject}."""
    rule = policy.rule_for(triage.intent.value)
    if rule is None:
        return "ask", f"No policy rule for intent '{triage.intent.value}' — defaulting to ask."
    if rule.decision == "auto":
        return "auto", f"Policy: intent '{rule.intent}' is auto-approved ({rule.note})"
    if rule.decision == "reject":
        return "reject", f"Policy: intent '{rule.intent}' is rejected ({rule.note})"
    # 'ask' base decision: check ask_if conditions against extracted details
    return "ask", f"Policy: intent '{rule.intent}' requires human decision ({rule.note})"
