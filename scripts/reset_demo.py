"""Reset the demo sandbox to its pristine corpus state.

Run: uv run python scripts/reset_demo.py
"""

from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "demo" / "data"
CORPUS = ROOT / "demo" / "corpus"


def main() -> None:
    # corpus/ is the pristine source of truth (committed to git)
    for sub in ("inbox", "outbox", "decisions", "processed"):
        target = DATA / sub
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True)
        (target / ".gitkeep").touch()
    if (DATA / "activity.log").exists():
        (DATA / "activity.log").unlink()
    if CORPUS.exists():
        for f in sorted(CORPUS.glob("*.eml")):
            shutil.copy(f, DATA / "inbox" / f.name)
        if (CORPUS / "register.csv").exists():
            shutil.copy(CORPUS / "register.csv", DATA / "register.csv")
        if (CORPUS / "policy.yaml").exists():
            shutil.copy(CORPUS / "policy.yaml", DATA / "policy.yaml")
    print("Demo sandbox reset: inbox=8 mails, empty outbox/decisions/processed, fresh register.")


if __name__ == "__main__":
    main()
