"""Triage evaluation: run the real triage agent over the labeled demo corpus
and report intent accuracy + confidence stats.

Run: bash scripts/run_eval.sh        (needs ZAI_API_KEY)
     uv run python scripts/eval_triage.py --json   → machine-readable report

Expected labels live in the filename prefix map below (demo corpus is small and
hand-labeled). This is a regression harness: if triage accuracy drops after a
prompt/model change, this catches it.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clubkeeper.agents import ClubKeeper, triage_one  # noqa: E402
from clubkeeper.config import Config  # noqa: E402
from clubkeeper.models import MailItem  # noqa: E402
from clubkeeper.policy import ClubPolicy  # noqa: E402
from clubkeeper.tools import set_config  # noqa: E402

EXPECTED = {
    "01-signup-irena.eml": "signup",
    "02-address-johnson.eml": "address_change",
    "03-hardship-kwame.eml": "hardship_waiver",
    "04-cancel-noah.eml": "cancellation",
    "05-question-fixtures.eml": "question",
    "06-email-change-sofia.eml": "address_change",
    "07-complaint-training.eml": "complaint",
    "08-spam-prize.eml": "spam",
    "09-hardship-followup.eml": "hardship_waiver",
    "10-signup-medical.eml": "signup",
}


def main() -> int:
    cfg = Config.load()
    if not cfg.api_key:
        print("ERROR: ZAI_API_KEY not set")
        return 2
    set_config(cfg)
    data_dir = ROOT / "demo" / "data"
    policy = ClubPolicy.load(data_dir / "policy.yaml")
    ck = ClubKeeper(cfg, policy)

    corpus = ROOT / "demo" / "corpus"
    results = []
    correct = 0
    for name, expected in EXPECTED.items():
        path = corpus / name
        if not path.exists():
            continue
        mail = MailItem.parse(path)
        try:
            t = triage_one(ck.triage_agent, mail)
            actual = t.intent.value
            ok = actual == expected
            correct += ok
            results.append({"mail": name, "expected": expected, "actual": actual, "confidence": round(t.confidence, 2), "ok": ok})
            mark = "OK " if ok else "MISS"
            print(f"[{mark}] {name:32} expected={expected:16} actual={actual:16} conf={t.confidence:.2f}")
        except Exception as e:
            results.append({"mail": name, "expected": expected, "actual": f"ERROR: {e}", "ok": False})
            print(f"[ERR ] {name:32} {e}")

    n = len(results)
    acc = correct / n if n else 0.0
    avg_conf = sum(r["confidence"] for r in results if isinstance(r.get("confidence"), float)) / max(1, n)
    print(f"\nAccuracy: {correct}/{n} = {acc:.0%}   avg confidence: {avg_conf:.2f}")

    if "--json" in sys.argv:
        out = ROOT / "docs" / "triage-eval-report.json"
        out.parent.mkdir(exist_ok=True)
        out.write_text(json.dumps({
            "model": cfg.model_id,
            "accuracy": acc,
            "correct": correct,
            "total": n,
            "avg_confidence": round(avg_conf, 2),
            "results": results,
        }, indent=2), encoding="utf-8")
        print(f"report: {out}")
    return 0 if acc >= 0.9 else 1


if __name__ == "__main__":
    sys.exit(main())
