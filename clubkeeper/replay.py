"""Replay a recorded ClubKeeper session — no LLM, no API key needed.

Run: uv run python -m clubkeeper.replay [path/to/session.json]
Default recording: demo/recording/session.json (created by scripts/record_session.py)

The replay prints the recorded transcript step by step and applies the recorded
artifacts to the demo sandbox, clearly labeled as a RECORDED session.
"""

from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

from .config import Config

BADGE = "\033[93m[RECORDED SESSION — not a live LLM call]\033[0m"


def _print_lines(lines: list[str], delay: float = 0.35) -> None:
    for ln in lines:
        print(ln)
        time.sleep(delay)


def _apply_effects(data_dir: Path, effects: dict[str, Any]) -> None:
    for name, content in (effects.get("drafts") or {}).items():
        (data_dir / "outbox").mkdir(parents=True, exist_ok=True)
        (data_dir / "outbox" / name).write_text(content, encoding="utf-8")
    for name, content in (effects.get("decisions") or {}).items():
        (data_dir / "decisions").mkdir(parents=True, exist_ok=True)
        (data_dir / "decisions" / name).write_text(content, encoding="utf-8")
    if effects.get("register"):
        (data_dir / "register.csv").write_text(effects["register"], encoding="utf-8")
    if effects.get("log"):
        (data_dir / "activity.log").write_text(effects["log"], encoding="utf-8")


def run(recording_path: Path | None = None, speed: float = 1.0) -> int:
    cfg = Config.load()
    path = recording_path or cfg.data_dir.parent / "recording" / "session.json"
    if not path.exists():
        print(f"No recording found at {path}")
        print("Create one first: uv run python scripts/record_session.py (needs ZAI_API_KEY)")
        return 2

    doc = json.loads(path.read_text(encoding="utf-8"))

    print(BADGE)
    print(f"Recorded: {doc['recorded_at']}  Model: {doc.get('model', '?')}")
    print("=" * 60)

    delay = 0.35 / max(speed, 0.1)
    for step in doc.get("pipeline_steps", []):
        print(f"\n--- {step['mail_file']} ---")
        _print_lines(step.get("lines", []), delay)
        for mv in step.get("moves", []):
            print(f"  [move] {mv}")
        _apply_effects(cfg.data_dir, step.get("effects") or {})
        if step.get("moves"):
            src, dst = step["moves"][-1].split("→")
            src_path = cfg.data_dir / src / step["mail_file"]
            dst_path = cfg.data_dir / dst / step["mail_file"]
            if src_path.exists():
                dst_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(src_path), dst_path)

    if doc.get("decide_steps"):
        print("\n" + "=" * 60)
        print("HUMAN DECISIONS (as recorded)")
        print("=" * 60)
        for step in doc["decide_steps"]:
            _print_lines(step.get("lines", []), delay)
            _apply_effects(cfg.data_dir, step.get("effects") or {})
        # end state: all recorded decisions resolved — queue holds only .eml copies
        # which move to processed, matching the recorded session
        for step in doc["decide_steps"]:
            dp = cfg.data_dir / "decisions" / f"{step['decision_id']}.json"
            if dp.exists():
                dp.unlink()
        for eml in list((cfg.data_dir / "decisions").glob("*.eml")):
            dst = cfg.data_dir / "processed" / eml.name
            if not dst.exists():
                shutil.move(str(eml), dst)

    print("\n" + "=" * 60)
    _print_lines((doc.get("final") or {}).get("lines", []), delay)
    fin = (doc.get("final") or {}).get("artifacts") or {}
    _apply_effects(cfg.data_dir, fin)

    print(BADGE)
    n_drafts = len(list((cfg.data_dir / "outbox").glob("*.eml")))
    print(f"Replay complete: {n_drafts} drafts in outbox, register updated, decisions cleared.")
    return 0


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    speed = 1.0
    for a in sys.argv[1:]:
        if a.startswith("--speed="):
            try:
                speed = float(a.split("=", 1)[1])
            except ValueError:
                pass
    sys.exit(run(Path(args[0]) if args else None, speed=speed))
