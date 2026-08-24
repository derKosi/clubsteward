"""SQLite storage adapter — same interface as the CSV register, per-club database.

Enable per club via brand/config: set `storage: sqlite` in the club's mail.yaml
(or CLUBSTEWARD_STORAGE=sqlite env). Falls back to CSV when unset.
The DB file lives inside the club folder (clubs/<id>/clubsteward.db) so tenant
isolation and "delete club = delete data" stay intact.
"""

from __future__ import annotations

import sqlite3
from pathlib import Path

from .models import REGISTER_FIELDS

SCHEMA = """
CREATE TABLE IF NOT EXISTS members (
    member_id TEXT PRIMARY KEY,
    first_name TEXT, last_name TEXT, email TEXT, birth_year TEXT,
    team TEXT, fee_status TEXT, joined TEXT, notes TEXT
);
CREATE TABLE IF NOT EXISTS activity (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT DEFAULT (datetime('now')),
    event TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT, finished_at TEXT, mails INTEGER,
    auto INTEGER, ask INTEGER, rejected INTEGER, tokens INTEGER
);
"""


def db_path(data_dir: Path) -> Path:
    return data_dir / "clubsteward.db"


def init_db(data_dir: Path) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path(data_dir))
    conn.executescript(SCHEMA)
    # seed from register.csv on first use (one-way import keeps CSV as bootstrap)
    csv = data_dir / "register.csv"
    if csv.exists():
        import csv as _csv
        rows = list(_csv.DictReader(csv.open(newline="", encoding="utf-8")))
        n = conn.execute("SELECT COUNT(*) FROM members").fetchone()[0]
        if n == 0 and rows:
            conn.executemany(
                f"INSERT INTO members ({','.join(REGISTER_FIELDS)}) VALUES ({','.join('?' * len(REGISTER_FIELDS))})",
                [tuple(r.get(f, "") for f in REGISTER_FIELDS) for r in rows],
            )
    conn.commit()
    return conn


def load_register_sqlite(data_dir: Path) -> list[dict[str, str]]:
    conn = init_db(data_dir)
    cur = conn.execute(f"SELECT {','.join(REGISTER_FIELDS)} FROM members ORDER BY member_id")
    rows = [dict(zip(REGISTER_FIELDS, r)) for r in cur.fetchall()]
    conn.close()
    return rows


def save_register_sqlite(data_dir: Path, rows: list[dict[str, str]]) -> None:
    conn = init_db(data_dir)
    conn.execute("DELETE FROM members")
    conn.executemany(
        f"INSERT INTO members ({','.join(REGISTER_FIELDS)}) VALUES ({','.join('?' * len(REGISTER_FIELDS))})",
        [tuple(r.get(f, "") for f in REGISTER_FIELDS) for r in rows],
    )
    conn.commit()
    conn.close()


def log_activity_sqlite(data_dir: Path, event: str) -> None:
    conn = init_db(data_dir)
    conn.execute("INSERT INTO activity (event) VALUES (?)", (event,))
    conn.commit()
    conn.close()
