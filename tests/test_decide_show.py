"""Regression test for the club-mode fix in decide.show(): the mail excerpt
must be read from the passed cfg's decisions dir, not from the default
demo data dir."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clubsteward.config import Config  # noqa: E402
from clubsteward.decide import show  # noqa: E402
from clubsteward.models import Decision, Intent, TriageResult  # noqa: E402


def _decision(mail_file: str) -> Decision:
    return Decision(
        id="d-test-01",
        mail_file=mail_file,
        from_name="Maria Muster",
        from_email="maria@example.org",
        subject="Wechsel zur U10",
        triage=TriageResult(
            intent=Intent.QUESTION,
            summary="Teamwechsel anfragen",
            proposed_action="register_update",
            flags=[],
        ),
        policy_reason="hardship ask_if",
    )


def test_show_reads_mail_from_passed_cfg(tmp_path, capsys, monkeypatch):
    monkeypatch.delenv("CLUBSTEWARD_STORAGE", raising=False)
    cfg = Config(api_key="test", base_url="http://localhost", model_id="m", data_dir=tmp_path)
    mail = tmp_path / "decisions" / "mail-01.eml"
    mail.parent.mkdir(parents=True)
    mail.write_text(
        "From: Maria Muster <maria@example.org>\nSubject: Wechsel zur U10\n\n"
        "Hallo, wir wollen zur U10 wechseln.\n",
        encoding="utf-8",
    )
    show(_decision(mail.name), cfg)
    out = capsys.readouterr().out
    assert "DECISION d-test-01" in out
    assert "--- mail (excerpt) ---" in out  # excerpt found via the passed cfg
    assert "U10 wechseln" in out
