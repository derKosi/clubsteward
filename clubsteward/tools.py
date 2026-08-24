"""Structured tools the ClubSteward agents can call.

All tools operate on the demo sandbox (demo/data/**) only — no network, no real mail.
"""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Annotated, Any

from strands import tool

from .config import Config
from .models import REGISTER_FIELDS, load_register, save_register
from .store import load_register_sqlite, save_register_sqlite, log_activity_sqlite


def _load_rows(cfg):
    return load_register_sqlite(cfg.data_dir) if _use_sqlite(cfg) else load_register(cfg.register_path)


def _save_rows(cfg, rows):
    if _use_sqlite(cfg):
        save_register_sqlite(cfg.data_dir, rows)
    else:
        _save_rows(cfg, rows)

# Config is injected per run (module-level default avoids global mutable state at import time)
_cfg: Config | None = None


def _use_sqlite(cfg: Config) -> bool:
    import os
    if os.environ.get("CLUBSTEWARD_STORAGE", "").lower() == "sqlite":
        return True
    flag = cfg.data_dir / "storage.flag"
    return flag.exists() and flag.read_text(encoding="utf-8").strip().lower() == "sqlite"


def set_config(cfg: Config) -> None:
    global _cfg
    _cfg = cfg
    if cfg.data_dir.name != "data":  # club mode: bootstrap sqlite if flagged
        from . import store
        if _use_sqlite(cfg):
            store.init_db(cfg.data_dir)


def _require_cfg() -> Config:
    if _cfg is None:
        raise RuntimeError("Config not set — call set_config() before running agents")
    return _cfg


@tool
def register_lookup(query: Annotated[str, "member email or name to look up"]) -> str:
    """Look up a member in the club register by email or name. Returns the matching rows."""
    cfg = _require_cfg()
    rows = _load_rows(cfg)
    q = query.strip().lower()
    hits = [r for r in rows if q in r.get("email", "").lower() or q in (r.get("first_name", "") + " " + r.get("last_name", "")).lower()]
    if not hits:
        return "NOT_FOUND"
    return "\n".join(", ".join(f"{k}={v}" for k, v in r.items()) for r in hits)


@tool
def register_update(
    email: Annotated[str, "member email (unique key)"],
    updates: Annotated[str, "comma-separated key=value pairs, e.g. 'team=U12,fee_status=paid'"],
) -> str:
    """Update fields of an existing member in the register (by email)."""
    cfg = _require_cfg()
    rows = _load_rows(cfg)
    changes: dict[str, str] = {}
    for pair in updates.split(","):
        k, _, v = pair.partition("=")
        k, v = k.strip(), v.strip()
        if k and k in REGISTER_FIELDS:
            changes[k] = v
    for r in rows:
        if r.get("email", "").lower() == email.lower():
            r.update(changes)
            _save_rows(cfg, rows)
            return f"UPDATED {email}: {changes}"
    return f"ERROR member not found: {email}"


@tool
def register_add(
    email: Annotated[str, "new member's contact email"],
    first_name: Annotated[str, "first name"],
    last_name: Annotated[str, "last name"],
    team: Annotated[str, "team to join, e.g. U12"],
    birth_year: Annotated[str, "birth year, e.g. 2014"],
    notes: Annotated[str, "optional notes, e.g. medical"] = "",
) -> str:
    """Add a new member to the register."""
    cfg = _require_cfg()
    rows = _load_rows(cfg)
    if any(r.get("email", "").lower() == email.lower() for r in rows):
        return f"ERROR member already exists: {email}"
    member_id = f"M{len(rows) + 1:03d}"
    rows.append({
        "member_id": member_id,
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "birth_year": birth_year,
        "team": team,
    "fee_status": "invoice_sent",
        "joined": "2026-08-23",
        "notes": notes,
    })
    _save_rows(cfg, rows)
    return f"ADDED {member_id} {first_name} {last_name} ({team})"


@tool
def save_draft(
    to: Annotated[str, "recipient email"],
    subject: Annotated[str, "email subject"],
    body: Annotated[str, "email body text"],
) -> str:
    """Save a reply draft to the club outbox (demo sandbox; nothing is actually sent)."""
    cfg = _require_cfg()
    cfg.outbox_dir.mkdir(parents=True, exist_ok=True)
    safe = "".join(c if c.isalnum() or c in "-_." else "_" for c in subject)[:60]
    stamp = cfg.outbox_dir / f"draft_{safe}.eml"
    n = 1
    while stamp.exists():
        n += 1
        stamp = cfg.outbox_dir / f"draft_{safe}_{n}.eml"
    stamp.write_text(f"To: {to}\nSubject: {subject}\n\n{body}\n", encoding="utf-8")
    return f"DRAFT SAVED {stamp.name}"


@tool
def log_activity(event: Annotated[str, "one-line activity log entry"]) -> str:
    """Append a line to the club activity log (what the agent did and why)."""
    cfg = _require_cfg()
    if _use_sqlite(cfg):
        log_activity_sqlite(cfg.data_dir, event)
    else:
        with cfg.log_path.open("a", encoding="utf-8") as f:
            f.write(event + "\n")
    return "LOGGED"
