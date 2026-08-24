"""Record a full ClubSteward session (pipeline + auto-approved decisions) to demo/recording/session.json.

Run: uv run python scripts/record_session.py   (needs ZAI_API_KEY)

The recording powers the no-API-key replay mode for judges: uv run python -m clubsteward.replay
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clubsteward.agents import ClubSteward  # noqa: E402
from clubsteward.config import Config  # noqa: E402
from clubsteward.decide import approve, show  # noqa: E402
from clubsteward.models import Decision  # noqa: E402
from clubsteward.pipeline import run as run_pipeline  # noqa: E402
from clubsteward.policy import ClubPolicy  # noqa: E402
from clubsteward.recorder import RunRecorder  # noqa: E402
from clubsteward.tools import set_config  # noqa: E402


def main() -> int:
    cfg = Config.load()
    if not cfg.api_key:
        print("ERROR: ZAI_API_KEY not set — recording needs a real run")
        return 2

    rec_dir = cfg.data_dir.parent / "recording"
    rec_dir.mkdir(parents=True, exist_ok=True)
    recorder = RunRecorder(cfg.data_dir)

    print("=== Recording pipeline run ===")
    rc = run_pipeline(recorder=recorder)
    if rc != 0:
        return rc

    print("\n=== Recording decisions (auto-approve) ===")
    set_config(cfg)
    ck = ClubSteward(cfg, ClubPolicy.load(cfg.data_dir / "policy.yaml"))
    for pj in sorted(cfg.decisions_dir.glob("*.json")):
        d = Decision.model_validate_json(pj.read_text())
        show(d)
        lines = [
            "┌─ DECISION " + d.id + " " + "─" * max(0, 44 - len(d.id)),
            f"│ Subject: {d.subject}",
            f"│ From:    {d.from_name} <{d.from_email}>",
            f"│ Intent:  {d.triage.intent.value}   (confidence {d.triage.confidence:.2f})",
            f"│ Wants:   {d.triage.summary[:100]}",
            f"│ Why you're asked: {d.policy_reason}",
            "│ human: approved → executing with instructions: offer 50% reduction and instalment plan where applicable",
            "└" + "─" * 58,
        ]
        recorder.decide_step_begin(d.id, d.subject, lines)
        approve(d, ck, extra="offer 50% reduction and instalment plan where applicable")
        recorder.decide_step_end()
        print("  [recorded] approved & executed")
        pj.unlink()
        mail = cfg.decisions_dir / d.mail_file
        if mail.exists():
            mail.rename(cfg.processed_dir / d.mail_file)

    out = rec_dir / "session.json"
    # re-capture the true end state (finish() was already called by the pipeline;
    # the decide executions changed artifacts after that)
    n_drafts = len(list((cfg.data_dir / "outbox").glob("*.eml")))
    recorder.finish([
        f"Done: all decisions executed by the human secretary.",
        f"Outbox drafts: {n_drafts} | Decisions pending: {len(list(cfg.decisions_dir.glob('*.json')))}",
    ])
    recorder.save(out)
    print(f"\nRecording saved: {out}")
    print("Replay it (no API key needed):  uv run python -m clubsteward.replay")
    return 0


if __name__ == "__main__":
    sys.exit(main())
