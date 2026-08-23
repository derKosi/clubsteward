"""ClubKeeper agents: triage (understand) and act (execute) on a Strands agent loop."""

from __future__ import annotations

from strands import Agent
from strands.models.litellm import LiteLLMModel

from .config import Config
from .interventions import make_hitl
from .models import Decision, Draft, Intent, MailItem, TriageResult
from .policy import ClubPolicy, PolicyRule
from .tools import log_activity, register_add, register_lookup, register_update, save_draft

from strands.session import FileSessionManager

TRIAGE_SYSTEM = """You are the triage brain of ClubKeeper, an agent that helps a volunteer run
a local community sports club's inbox. Classify each member email precisely and extract facts.
Use intent "spam" for scam/phishing/lottery/ad mail that has nothing to do with the club.
IMPORTANT: any mail that requests, references, or follows up on a fee reduction, waiver,
instalment plan, or financial hardship — even phrased as a polite question or thank-you —
is intent "hardship_waiver", never "question". Money decisions always go to a human.
Be conservative: if the sender asks for money relief or cancellation, extract amounts and reasons.
Respond ONLY with the structured schema."""

ACT_SYSTEM = """You are the executor of ClubKeeper, a club-secretary agent. You receive one triaged
case at a time. Use the tools to update the member register, draft replies, and log activity.
You may have conversation history with this member from previous nights — use it to stay
consistent (e.g. reference an instalment plan you offered before) but never contradict new facts.
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
        self._act_sessions: dict[str, Agent] = {}  # member email → act agent with session

    def act_agent_for(self, member_key: str) -> Agent:
        """Return an act agent with a persistent per-member conversation session.

        The same member gets the same agent (and thus conversation history) across
        nightly runs — the agent 'remembers' prior arrangements (instalment plans,
        past waivers) and drafts follow-ups that reflect them.
        """
        if member_key not in self._act_sessions:
            sessions_dir = self.cfg.data_dir / "sessions"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in member_key)[:80]
            mgr = FileSessionManager(session_id=f"member-{safe}", storage_dir=str(sessions_dir))
            self._act_sessions[member_key] = Agent(
                model=make_model(self.cfg),
                system_prompt=ACT_SYSTEM,
                tools=[register_lookup, register_update, register_add, save_draft, log_activity],
                interventions=[make_hitl(False)],
                callback_handler=None,
                session_manager=mgr,
            )
        return self._act_sessions[member_key]


def triage_one(triage_agent: Agent, mail: MailItem) -> TriageResult:
    prompt = (
        f"Classify this club inbox email.\n\n"
        f"From: {mail.from_name} <{mail.from_email}>\n"
        f"Subject: {mail.subject}\nDate: {mail.date}\n\n"
        f"{mail.body[:2500]}"
    )
    return triage_agent.structured_output(TriageResult, prompt)


def triage_tokens(triage_agent: Agent) -> int:
    """Best-effort total tokens used by the triage agent so far (cumulative)."""
    try:
        usage = triage_agent.event_loop_metrics.accumulated_usage  # dict
        return int(usage.get("totalTokens", 0)) if isinstance(usage, dict) else 0
    except Exception:
        return 0


class TriageTokenTracker:
    """Tracks per-mail token deltas from the triage agent's cumulative counter."""

    def __init__(self, triage_agent: Agent):
        self._agent = triage_agent
        self._last = 0

    def delta(self) -> int:
        total = triage_tokens(self._agent)
        d = max(0, total - self._last)
        self._last = total
        return d


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
