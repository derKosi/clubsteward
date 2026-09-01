"""ClubSteward web console + product page — FastAPI, no external deps.

Run:  uv run python -m clubsteward.web   (http://localhost:8000)

Pages
  /                     hero product page (live stats from the 6 clubs)
  /app                  console: club switcher, run night, decision cards, outbox, register

API (JSON)
  GET  /api/clubs
  POST /api/clubs/{id}/run            (starts the real pipeline with the LLM)
  GET  /api/clubs/{id}/state          (inbox/outbox/decisions/register counts + lists)
  GET  /api/clubs/{id}/decisions      (pending decision cards)
  POST /api/clubs/{id}/decisions/{did}/{action}   action: approve|deny|edit
  POST /api/clubs/{id}/inbox          (upload .eml — 'email client integration' without accounts)
"""

from __future__ import annotations

import os
import secrets
import shutil
import threading
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from .club import club_dirs, load_brand
from .config import Config
from .models import Decision, MailItem
from .policy import ClubPolicy
from .tools import load_register_state

ROOT = Path(__file__).resolve().parent.parent
WEB = ROOT / "webapp" / "static"

app = FastAPI(title="ClubSteward", version="0.1.0")


def _require_api_token(x_api_token: str | None = Header(default=None)) -> None:
    """Optional shared-token gate for deployments beyond localhost.

    Set CLUBSTEWARD_WEB_TOKEN to require `X-API-Token: <value>` (constant-time
    compared) on every /api/* call. Unset (default) = open local demo mode.
    The HTML pages stay public; without the token every API call fails 401,
    so the console cannot read or act.
    """
    expected = os.environ.get("CLUBSTEWARD_WEB_TOKEN", "").strip()
    if not expected:
        return
    if not x_api_token or not secrets.compare_digest(x_api_token, expected):
        raise HTTPException(401, "missing or invalid X-API-Token header")


api = APIRouter(prefix="/api", dependencies=[Depends(_require_api_token)])

# ---- run lock: one pipeline run at a time (single-box SaaS stage 1) ----
_run_lock = threading.Lock()
_run_status: dict[str, Any] = {"running": False, "club": None, "started_at": None, "last_log": []}


def _club_dir(club_id: str) -> Path:
    d = ROOT / "clubs" / club_id
    if not (d / "policy.yaml").exists():
        raise HTTPException(404, f"unknown club '{club_id}'")
    return d


def _capture_prints():
    """Collect stdout lines of a pipeline run into _run_status['last_log']."""
    import contextlib
    import io

    buf = io.StringIO()
    return buf, contextlib.redirect_stdout(buf)


# ---------------------------------------------------------------- API

@api.get("/clubs")
def api_clubs() -> list[dict]:
    out = []
    for d in club_dirs():
        b = load_brand(d)
        out.append({
            "id": d.name,
            "name": b.get("name", d.name),
            "tagline": b.get("tagline", ""),
            "color": (b.get("colors") or {}).get("primary", "#333"),
            "accent": (b.get("colors") or {}).get("accent", "#fff"),
            "locale": b.get("locale", "en"),
            "inbox": len(list((d / "inbox").glob("*.eml"))),
            "decisions": len(list((d / "decisions").glob("*.json"))),
            "drafts": len(list((d / "outbox").glob("*.eml"))),
        })
    return out


@api.post("/clubs/{club_id}/run")
def api_run(club_id: str):
    _club_dir(club_id)
    if _run_lock.locked():
        raise HTTPException(409, "a run is already in progress")
    # run in a background thread; return immediately (UI polls state)
    def _run():
        from .pipeline import run as pipeline_run
        _run_status.update(running=True, club=club_id, last_log=[])
        buf, redir = _capture_prints()
        with _run_lock, redir:
            try:
                pipeline_run(club=club_id)
            except Exception as e:
                _run_status["last_log"] = [f"ERROR: {e}"]
        _run_status["last_log"] = [ln for ln in buf.getvalue().splitlines() if ln.strip()][-40:]
        _run_status["running"] = False
    threading.Thread(target=_run, daemon=True).start()
    return {"started": True, "club": club_id}


@api.get("/clubs/{club_id}/run/status")
def api_run_status(club_id: str):
    _club_dir(club_id)
    return {
        "running": _run_status["running"] and _run_status["club"] == club_id,
        "log": _run_status["last_log"] if _run_status["club"] == club_id else [],
    }


@api.get("/clubs/{club_id}/state")
def api_state(club_id: str):
    _club_dir(club_id)  # validates club id (raises 404)
    cfg = Config.load(club_id)
    reg_rows = load_register_state(cfg)
    drafts = []
    for p in sorted(cfg.outbox_dir.glob("*.eml")):
        text = p.read_text(encoding="utf-8")
        to, _, rest = text.partition("\n\n")
        drafts.append({"file": p.name, "to": to.replace("To: ", ""), "body": rest.strip()[:600]})
    return {
        "club": club_id,
        "inbox": [p.name for p in sorted(cfg.inbox_dir.glob("*.eml"))],
        "decisions_pending": len(list(cfg.decisions_dir.glob("*.json"))),
        "drafts": drafts,
        "register": reg_rows,
        "log": cfg.log_path.read_text(encoding="utf-8").strip().splitlines()[-30:] if cfg.log_path.exists() else [],
    }


@api.get("/clubs/{club_id}/decisions")
def api_decisions(club_id: str) -> list[dict]:
    _club_dir(club_id)  # validates club id (raises 404)
    cfg = Config.load(club_id)
    out = []
    for p in sorted(cfg.decisions_dir.glob("*.json")):
        dec = Decision.model_validate_json(p.read_text(encoding="utf-8"))
        mail_body = ""
        mp = cfg.decisions_dir / dec.mail_file
        if mp.exists():
            mail_body = MailItem.parse(mp).body[:1500]
        out.append({
            "id": dec.id,
            "subject": dec.subject,
            "from": f"{dec.from_name} <{dec.from_email}>",
            "intent": dec.triage.intent.value,
            "confidence": dec.triage.confidence,
            "summary": dec.triage.summary,
            "details": dec.triage.details,
            "flags": dec.triage.flags,
            "proposed": dec.triage.proposed_action,
            "policy_reason": dec.policy_reason,
            "mail_body": mail_body,
        })
    return out


class EditBody(BaseModel):
    instructions: str = ""


@api.post("/clubs/{club_id}/decisions/{did}/{action}")
def api_decision_action(club_id: str, did: str, action: str, body: EditBody | None = None):
    _club_dir(club_id)
    if action not in ("approve", "deny", "edit"):
        raise HTTPException(400, "action must be approve|deny|edit")
    cfg = Config.load(club_id)
    pj = cfg.decisions_dir / f"{did}.json"
    if not pj.exists():
        raise HTTPException(404, f"decision '{did}' not found")
    from .agents import ClubSteward
    from .decide import approve
    from .tools import set_config
    dec = Decision.model_validate_json(pj.read_text(encoding="utf-8"))

    if action == "deny":
        dec.status = "denied"
        pj.write_text(dec.model_dump_json(indent=2), encoding="utf-8")
        return {"result": "denied", "id": did}

    set_config(cfg)
    ck = ClubSteward(cfg, ClubPolicy.load(cfg.data_dir / "policy.yaml"))
    approve(dec, ck, extra=(body.instructions if body else ""), club=club_id)
    pj.unlink()
    mail = cfg.decisions_dir / dec.mail_file
    if mail.exists():
        shutil.move(str(mail), cfg.processed_dir / dec.mail_file)
    return {"result": "executed", "id": did, "instructions": (body.instructions if body else "")}


@api.post("/clubs/{club_id}/inbox")
async def api_upload_mail(club_id: str, file: UploadFile = File(...)):
    _club_dir(club_id)
    if not file.filename or not file.filename.endswith(".eml"):
        raise HTTPException(400, "please upload an .eml file")
    dest = _club_dir(club_id) / "inbox" / Path(file.filename).name
    dest.write_bytes(await file.read())
    return {"uploaded": dest.name}


# ---------------------------------------------------------------- Pages

app.include_router(api)


@app.get("/", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse((WEB / "index.html").read_text(encoding="utf-8"))


@app.get("/app", response_class=HTMLResponse)
def console() -> HTMLResponse:
    return HTMLResponse((WEB / "app.html").read_text(encoding="utf-8"))
