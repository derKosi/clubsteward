"""ClubSteward agents: triage (understand) and act (execute) on a Strands agent loop."""

from __future__ import annotations

from strands import Agent
from strands.models.litellm import LiteLLMModel
from strands.session import FileSessionManager

from .config import Config
from .interventions import make_hitl
from .models import MailItem, TriageResult
from .policy import ClubPolicy
from .tools import (
    log_activity,
    register_add,
    register_lookup,
    register_update,
    save_draft,
)

TRIAGE_SYSTEM = """You are the triage brain of ClubSteward, an agent that helps a volunteer run
a local community club's inbox (sports club, PTA, carnival club, neighborhood association).
Emails may arrive in ANY language (English, German, Spanish, ...) — classify by meaning, not language.
Use intent "spam" for scam/phishing/lottery/ad mail that has nothing to do with the club.
IMPORTANT: any mail that requests, references, or follows up on a fee reduction, waiver,
instalment plan, or financial hardship — even phrased as a polite question or thank-you —
is intent "hardship_waiver", never "question". Money decisions always go to a human.
Exception: routine fee questions that merely accompany a signup (what does membership
cost, is there a sibling discount, how do I pay) are plain "signup" — hardship_waiver
is for existing or joining members who say they struggle to pay and ask for relief.
Same rule for leaving the club: any mail that floats pausing, stepping back, or
cancelling the membership — even undecided, even phrased as asking for advice
("what would you recommend?") — is intent "cancellation", never "question". Exit decisions
always go to a human. Exception: normal squad moves WITHIN the club ("move up to U16",
switch to the Tuesday group) and changes of contact details are NOT exits.
Use intent "offer" when someone offers the club something (money, sponsorship,
equipment, rooms, volunteer work, partnerships) — inbound generosity is decided
by a human; the reply may only promise that a human will follow up.
If a mail mixes several topics, classify it by the topic that needs the MOST human
attention (complaint > cancellation > hardship_waiver > offer > signup > address_change > question),
and say so in the summary.
Angry mails about noise, behaviour, safety, fairness, or broken promises are "complaint",
even when politely worded or in another language.
Also set "flags" with short lowercase tags for anything special that needs human attention:
"medical" (health conditions, medication, allergies, asthma, inhalers, epilepsy, injuries),
"waiting_list" (team full, waiting for a spot), "refund" (money back requested),
"duplicate" (possible duplicate member/record), "legal", or a similar short tag of your own.
Empty list if nothing special applies. ALWAYS check the body for health/medical mentions
before answering — this flag protects children.
Be conservative: if the sender asks for money relief or cancellation, extract amounts and reasons.
Respond ONLY with the structured schema."""

ACT_SYSTEM = """You are the executor of ClubSteward, a club-secretary agent. You receive one triaged
case at a time. Use the tools to update the member register, draft replies, and log activity.
You may have conversation history with this member from previous nights — use it to stay
consistent (e.g. reference an instalment plan you offered before) but never contradict new facts.
Rules:
- Drafts must be warm, human, concise (max ~120 words), in the club's tone, signed as configured.
- Never invent fees or members; look up before updating; add only with complete data.
- Every case ends with a log entry stating what was done and why.
- If a tool returns ERROR, stop retrying and report the problem in your final answer."""


def make_model(cfg: Config):
    import os

    # GLM spends reasoning tokens from the same budget; 1024 truncated rich
    # triage JSON ("Unterminated string") and long act runs mid-tool-call.
    max_tokens = int(os.environ.get("ZAI_MAX_TOKENS", "4096"))
    # A hung LLM call must not freeze the night: timeout raises, the act
    # try/except files that one mail into _errors and the run continues.
    timeout = int(os.environ.get("ZAI_TIMEOUT", "180"))
    return LiteLLMModel(
        client_args={"api_key": cfg.api_key, "api_base": cfg.base_url},
        model_id=f"openai/{cfg.model_id}",
        params={"max_tokens": max_tokens, "temperature": 0.2, "timeout": timeout},
    )


class ClubSteward:
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
    """Classify one mail; returns the agent's structured TriageResult.

    One plain retry: GLM structured output occasionally fails to parse
    ("Unterminated string", dropped tool call). The prompt is used temporarily
    (never added to history), so the second attempt starts clean.
    """
    prompt = (
        f"Classify this club inbox email. Check carefully for special conditions "
        f"(medical/health, waiting list, refund, ...) and set flags accordingly.\n\n"
        f"From: {mail.from_name} <{mail.from_email}>\n"
        f"Subject: {mail.subject}\nDate: {mail.date}\n\n"
        f"{mail.body[:2500]}"
    )
    try:
        return triage_agent.structured_output(TriageResult, prompt)
    except Exception:
        return triage_agent.structured_output(TriageResult, prompt)


MEDICAL_KEYWORDS = (
    "asthma", "inhaler", "allerg", "epilep", "diabet", "medication", "medicine",
    "health condition", "medical", "injury", "injured", "concussion", "epipen",
)


def safety_flag_check(triage: TriageResult, mail: MailItem) -> TriageResult:
    """Deterministic backstop: never let a medical mention slip through unflagged.

    The LLM sets flags most of the time, but for child-safety escalations we do not
    rely on model attention alone — a keyword scan over subject+body re-adds the
    'medical' flag if the triage agent missed it. Policy ask_if then escalates.
    """
    haystack = f"{mail.subject} {mail.body}".lower()
    if any(k in haystack for k in MEDICAL_KEYWORDS) and "medical" not in [f.lower() for f in triage.flags]:
        triage.flags.append("medical")
    return triage


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
    """Return (decision, reason). decision in {auto, ask, reject}.

    Two escalation axes for otherwise-auto intents, most specific first:
      ask_if conditions in the policy name flags (e.g. "medical", "waiting_list")
      that the triage agent extracted; below policy.min_confidence the agent
      asks rather than guesses. Both are policy-as-data, no code changes.
    """
    rule = policy.rule_for(triage.intent.value)
    if rule is None:
        return "ask", f"No policy rule for intent '{triage.intent.value}' — defaulting to ask."
    if rule.decision == "reject":
        return "reject", f"Policy: intent '{rule.intent}' is rejected ({rule.note})"
    if rule.decision == "ask":
        return "ask", f"Policy: intent '{rule.intent}' requires human decision ({rule.note})"

    # decision == "auto": check ask_if conditions against extracted flags.
    # ask_if entries are explicit flag names (e.g. "medical", "waiting_list");
    # matching is exact after normalization (lowercase, underscores -> spaces).
    if rule.ask_if:
        triage_flags = {" ".join(f.lower().strip().replace("_", " ").split()) for f in triage.flags}
        for cond in rule.ask_if:
            key = " ".join(cond.lower().strip().replace("_", " ").split())
            if key in triage_flags:
                return "ask", f"Policy escalation: '{rule.intent}' is normally auto, but flag '{key}' matches ask_if"
    if triage.confidence < policy.min_confidence:
        return (
            "ask",
            f"Policy escalation: agent is only {triage.confidence:.0%} sure "
            f"(below the {policy.min_confidence:.0%} threshold) — asking instead of guessing",
        )
    return "auto", f"Policy: intent '{rule.intent}' is auto-approved ({rule.note})"
