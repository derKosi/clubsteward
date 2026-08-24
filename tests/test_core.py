"""Unit tests for ClubSteward policy, models, and interventions (no LLM calls)."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clubsteward.interventions import policy_classifier  # noqa: E402
from clubsteward.models import Intent, MailItem, TriageResult  # noqa: E402
from clubsteward.policy import ClubPolicy  # noqa: E402

DEMO = ROOT / "demo" / "corpus"


class _State:
    def __init__(self, data):
        self._d = data

    def get(self, k, default=None):
        return self._d.get(k, default)

    def set(self, k, v):
        self._d[k] = v


class _Agent:
    def __init__(self, data):
        self.state = _State(data)


class _Event:
    def __init__(self, tool, agent):
        self.tool_use = {"name": tool, "toolUseId": "t1", "input": {}}
        self.agent = agent


@pytest.fixture(scope="module")
def policy() -> ClubPolicy:
    return ClubPolicy.load(DEMO / "policy.yaml")


class TestPolicy:
    def test_rules_load(self, policy):
        assert policy.club_name == "Riverside Juniors FC"
        intents = {r.intent for r in policy.rules}
        assert {"signup", "hardship_waiver", "cancellation", "spam", "unknown"} <= intents

    def test_rule_decisions(self, policy):
        assert policy.rule_for("signup").decision == "auto"
        assert policy.rule_for("hardship_waiver").decision == "ask"
        assert policy.rule_for("spam").decision == "reject"
        assert policy.rule_for("nonexistent") is None

    def test_fees_present(self, policy):
        assert policy.fees["annual_member"] == 96.0


class TestClassifier:
    def _agent(self, autonomy):
        return _Agent({"clubsteward:case": {"autonomy": autonomy, "intent": "signup"}})

    def test_read_tools_always_free(self):
        for autonomy in ("auto", "ask", "auto_preapproved", None_marker := "unset"):
            agent = _Agent({}) if autonomy == "unset" else self._agent(autonomy)
            ev = _Event("register_lookup", agent)
            r = policy_classifier(ev)
            assert r.requires_human_in_the_loop is False

    def test_write_free_when_auto(self):
        ev = _Event("register_update", self._agent("auto"))
        assert policy_classifier(ev).requires_human_in_the_loop is False

    def test_write_free_when_preapproved(self):
        ev = _Event("save_draft", _Agent({"clubsteward:case": {"autonomy": "auto_preapproved", "intent": "cancellation", "decision_id": "abc"}}))
        assert policy_classifier(ev).requires_human_in_the_loop is False

    def test_write_blocked_when_ask(self):
        ev = _Event("register_update", _Agent({"clubsteward:case": {"autonomy": "ask", "intent": "hardship_waiver"}}))
        assert policy_classifier(ev).requires_human_in_the_loop is True

    def test_write_blocked_without_case(self):
        ev = _Event("save_draft", _Agent({}))
        assert policy_classifier(ev).requires_human_in_the_loop is True

    def test_unknown_tool_fails_closed(self):
        ev = _Event("rm_rf", _Agent({"clubsteward:case": {"autonomy": "auto", "intent": "signup"}}))
        assert policy_classifier(ev).requires_human_in_the_loop is True


class TestMailParsing:
    def test_parse_eml(self):
        mail = MailItem.parse(DEMO / "01-signup-irena.eml")
        assert mail.from_email == "daniel.novak@example.com"
        assert mail.from_name == "Daniel Novak"
        assert "Irena" in mail.body

    def test_parse_all_corpus(self):
        mails = [MailItem.parse(p) for p in sorted(DEMO.glob("*.eml"))]
        assert len(mails) >= 8  # 8 base corpus + optional follow-up scenario


class TestEvaluatePolicy:
    def test_evaluate(self, policy):
        from clubsteward.agents import evaluate_policy

        t_auto = TriageResult(intent=Intent.SIGNUP, summary="s", proposed_action="a", confidence=1.0)
        t_ask = TriageResult(intent=Intent.HARDSHIP_WAIVER, summary="s", proposed_action="a", confidence=1.0)
        t_spam = TriageResult(intent=Intent.SPAM, summary="s", proposed_action="a", confidence=1.0)
        assert evaluate_policy(policy, t_auto)[0] == "auto"
        assert evaluate_policy(policy, t_ask)[0] == "ask"
        assert evaluate_policy(policy, t_spam)[0] == "reject"

    def test_ask_if_escalates_auto_on_flag(self, policy):
        from clubsteward.agents import evaluate_policy

        t = TriageResult(intent=Intent.SIGNUP, summary="s", proposed_action="a",
                         confidence=1.0, flags=["medical"])
        decision, reason = evaluate_policy(policy, t)
        assert decision == "ask"
        assert "medical" in reason

    def test_ask_if_no_flag_stays_auto(self, policy):
        from clubsteward.agents import evaluate_policy

        t = TriageResult(intent=Intent.SIGNUP, summary="s", proposed_action="a",
                         confidence=1.0, flags=[])
        assert evaluate_policy(policy, t)[0] == "auto"

    def test_ask_if_waiting_list_escalates(self, policy):
        from clubsteward.agents import evaluate_policy

        t = TriageResult(intent=Intent.SIGNUP, summary="s", proposed_action="a",
                         confidence=1.0, flags=["waiting_list"])
        decision, reason = evaluate_policy(policy, t)
        assert decision == "ask"
        assert "waiting" in reason


class TestSafetyFlagCheck:
    def test_backstop_adds_medical_flag(self):
        from clubsteward.agents import safety_flag_check

        t = TriageResult(intent=Intent.SIGNUP, summary="s", proposed_action="a", confidence=1.0, flags=[])
        mail = MailItem.parse(DEMO / "10-signup-medical.eml")
        t2 = safety_flag_check(t, mail)
        assert "medical" in t2.flags

    def test_backstop_no_false_positive(self):
        from clubsteward.agents import safety_flag_check

        t = TriageResult(intent=Intent.QUESTION, summary="s", proposed_action="a", confidence=1.0, flags=[])
        mail = MailItem.parse(DEMO / "05-question-fixtures.eml")
        t2 = safety_flag_check(t, mail)
        assert "medical" not in t2.flags


class TestRecorder:
    def _mk(self, tmp_path):
        from clubsteward.recorder import RunRecorder, _snapshot
        for sub in ("outbox", "decisions"):
            (tmp_path / sub).mkdir(parents=True, exist_ok=True)
        (tmp_path / "register.csv").write_text("member_id\n", encoding="utf-8")
        return RunRecorder(tmp_path), _snapshot

    def test_pipeline_step_captures_draft_effect(self, tmp_path):
        rec, _ = self._mk(tmp_path)
        rec.set_model("test-model")
        (tmp_path / "outbox" / "d1.eml").write_text("To: a\n", encoding="utf-8")
        rec.pipeline_step("m1.eml", ["line"], ["inbox→processed"])
        rec.finish(["end"])
        rec.save(tmp_path / "session.json")
        import json
        doc = json.loads((tmp_path / "session.json").read_text())
        assert doc["model"] == "test-model"
        assert "d1.eml" in doc["pipeline_steps"][0]["effects"]["drafts"]

    def test_decide_step_captures_post_execution_effects(self, tmp_path):
        rec, _ = self._mk(tmp_path)
        rec.decide_step_begin("d1", "subj", ["l1"])
        (tmp_path / "outbox" / "d2.eml").write_text("To: b\n", encoding="utf-8")  # execution effect
        rec.decide_step_end()
        rec.finish(["end"])
        rec.save(tmp_path / "session.json")
        import json
        doc = json.loads((tmp_path / "session.json").read_text())
        assert "d2.eml" in doc["decide_steps"][0]["effects"]["drafts"]


class TestSessionRouting:
    def test_act_agent_for_is_stable_per_member(self, tmp_path):
        """Same member email → same agent instance (persistent session) within one run."""
        from clubsteward.agents import ClubSteward
        from clubsteward.config import Config

        cfg = Config(api_key="test", base_url="http://localhost", model_id="m", data_dir=tmp_path)
        pol = ClubPolicy(club_name="X", season="s", rules=[])
        ck = ClubSteward(cfg, pol)
        a1 = ck.act_agent_for("miriam@example.com")
        a2 = ck.act_agent_for("miriam@example.com")
        b = ck.act_agent_for("other@example.com")
        assert a1 is a2
        assert a1 is not b

    def test_session_files_created_shape(self, tmp_path):
        """Session dirs use a sanitized member key under data_dir/sessions."""
        from clubsteward.agents import ClubSteward
        from clubsteward.config import Config

        cfg = Config(api_key="test", base_url="http://localhost", model_id="m", data_dir=tmp_path)
        pol = ClubPolicy(club_name="X", season="s", rules=[])
        ck = ClubSteward(cfg, pol)
        ck.act_agent_for("weird/address@example.com")
        sessions = list((tmp_path / "sessions").iterdir())
        assert len(sessions) == 1
        assert "weird" in sessions[0].name and "@" not in sessions[0].name
