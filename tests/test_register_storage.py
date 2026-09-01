"""Unit tests for the register storage layer: _save_rows/_load_rows and the
register_* tools in both storage modes (CSV default + SQLite flag/env).

No LLM calls — pure file/SQLite round-trips in a tmp sandbox.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clubsteward import tools  # noqa: E402
from clubsteward.config import Config  # noqa: E402

SEED = [
    {
        "member_id": "M001", "first_name": "Maria", "last_name": "Muster",
        "email": "maria@example.org", "birth_year": "2014", "team": "U12",
        "fee_status": "paid", "joined": "2026-01-05", "notes": "",
    },
    {
        "member_id": "M002", "first_name": "Nico", "last_name": "Neumann",
        "email": "nico@example.org", "birth_year": "2013", "team": "U14",
        "fee_status": "invoice_sent", "joined": "2026-02-11", "notes": "",
    },
]


def make_cfg(tmp_path: Path, sqlite: bool) -> Config:
    """Config pointing at a tmp sandbox; sqlite mode via storage.flag."""
    if sqlite:
        (tmp_path / "storage.flag").write_text("sqlite\n", encoding="utf-8")
    return Config(api_key="test", base_url="http://localhost", model_id="test-model", data_dir=tmp_path)


@pytest.fixture
def clean_env(monkeypatch):
    """Isolate module config + force-default storage mode (env may override)."""
    monkeypatch.delenv("CLUBSTEWARD_STORAGE", raising=False)
    tools._cfg = None
    yield
    tools._cfg = None


class TestCsvMode:
    def test_save_and_load_roundtrip(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=False)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        rows = tools._load_rows(cfg)
        assert [r["email"] for r in rows] == ["maria@example.org", "nico@example.org"]
        assert rows[0]["team"] == "U12"
        assert (tmp_path / "register.csv").exists()  # CSV mode writes the CSV file
        assert not (tmp_path / "clubsteward.db").exists()  # ...and no sqlite side effects

    def test_register_update_persists(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=False)
        tools.set_config(cfg)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        out = tools.register_update("maria@example.org", "team=U10,fee_status=invoice_sent")
        assert out.startswith("UPDATED")
        rows = tools._load_rows(cfg)
        assert rows[0]["team"] == "U10"
        assert rows[0]["fee_status"] == "invoice_sent"
        assert rows[1]["team"] == "U14"  # untouched row stays intact

    def test_register_add_persists(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=False)
        tools.set_config(cfg)
        out = tools.register_add(
            email="lena@example.org", first_name="Lena", last_name="Lang",
            team="U10", birth_year="2015",
        )
        assert out.startswith("ADDED")
        rows = tools._load_rows(cfg)
        assert len(rows) == 1
        assert rows[0]["email"] == "lena@example.org"
        assert rows[0]["member_id"] == "M001"

    def test_register_update_unknown_member(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=False)
        tools.set_config(cfg)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        out = tools.register_update("ghost@example.org", "team=U10")
        assert out.startswith("ERROR")


class TestSqliteMode:
    def test_save_and_load_roundtrip(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=True)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        rows = tools._load_rows(cfg)
        assert [r["email"] for r in rows] == ["maria@example.org", "nico@example.org"]
        assert rows[0]["fee_status"] == "paid"
        assert (tmp_path / "clubsteward.db").exists()  # sqlite mode writes the DB file
        assert not (tmp_path / "register.csv").exists()  # ...and no CSV side effects

    def test_register_update_persists(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=True)
        tools.set_config(cfg)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        out = tools.register_update("nico@example.org", "fee_status=paid")
        assert out.startswith("UPDATED")
        rows = tools._load_rows(cfg)
        assert rows[1]["fee_status"] == "paid"

    def test_register_add_persists(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=True)
        tools.set_config(cfg)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        out = tools.register_add(
            email="lena@example.org", first_name="Lena", last_name="Lang",
            team="U10", birth_year="2015",
        )
        assert out.startswith("ADDED")
        rows = tools._load_rows(cfg)
        assert [r["email"] for r in rows] == ["maria@example.org", "nico@example.org", "lena@example.org"]

    def test_env_var_forces_sqlite_without_flag(self, tmp_path, monkeypatch):
        monkeypatch.setenv("CLUBSTEWARD_STORAGE", "sqlite")
        cfg = make_cfg(tmp_path, sqlite=False)  # no storage.flag, env decides
        tools._save_rows(cfg, [dict(r) for r in SEED])
        assert (tmp_path / "clubsteward.db").exists()
        rows = tools._load_rows(cfg)
        assert len(rows) == 2


class TestRegisterState:
    """load_register_state: read-only console view (CSV default, sqlite when a DB exists)."""

    def test_csv_mode(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=False)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        rows = tools.load_register_state(cfg)
        assert [r["email"] for r in rows] == ["maria@example.org", "nico@example.org"]
        assert not (tmp_path / "clubsteward.db").exists()

    def test_sqlite_mode_reads_db(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=True)
        tools._save_rows(cfg, [dict(r) for r in SEED])
        rows = tools.load_register_state(cfg)
        assert len(rows) == 2

    def test_sqlite_flag_without_db_falls_back_to_csv(self, tmp_path, clean_env):
        from clubsteward.models import save_register
        cfg = make_cfg(tmp_path, sqlite=True)  # flag set, but no DB created yet
        save_register(cfg.register_path, [dict(r) for r in SEED])
        rows = tools.load_register_state(cfg)
        assert [r["email"] for r in rows] == ["maria@example.org", "nico@example.org"]
        assert not (tmp_path / "clubsteward.db").exists()  # a read must not bootstrap a DB

    def test_missing_register_yields_empty(self, tmp_path, clean_env):
        cfg = make_cfg(tmp_path, sqlite=False)
        assert tools.load_register_state(cfg) == []
