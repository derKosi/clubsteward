"""POST /api/clubs/{id}/reset — restores the corpus, also clears _errors."""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import clubsteward.web as web  # noqa: E402
from clubsteward.club import reset_club  # noqa: E402

client = TestClient(web.app)


def _fake_club(tmp_path: Path) -> Path:
    (tmp_path / "policy.yaml").write_text("club_name: T\n", encoding="utf-8")
    (tmp_path / "corpus").mkdir()
    (tmp_path / "corpus" / "m1.eml").write_text("From: a@x.de\n\nhi\n", encoding="utf-8")
    (tmp_path / "_errors").mkdir()
    (tmp_path / "_errors" / "stale.eml").write_text("old failure\n", encoding="utf-8")
    return tmp_path


def test_reset_club_restores_corpus_and_clears_errors(tmp_path):
    d = _fake_club(tmp_path)
    n = reset_club(d)
    assert n == 1
    assert (d / "inbox" / "m1.eml").read_text(encoding="utf-8").startswith("From: a@x.de")
    assert [p.name for p in (d / "_errors").iterdir()] == [".gitkeep"]


def test_reset_club_raises_without_corpus(tmp_path):
    import pytest

    with pytest.raises(FileNotFoundError):
        reset_club(tmp_path)


def test_reset_endpoint_restores(tmp_path, monkeypatch):
    d = _fake_club(tmp_path)
    monkeypatch.setattr(web, "_club_dir", lambda cid: d)
    r = client.post("/api/clubs/t/reset")
    assert r.status_code == 200
    assert r.json() == {"reset": True, "club": "t", "inbox": 1}
    assert (d / "inbox" / "m1.eml").exists()


def test_reset_endpoint_404_without_corpus(tmp_path, monkeypatch):
    d = tmp_path
    (d / "policy.yaml").write_text("club_name: T\n", encoding="utf-8")
    monkeypatch.setattr(web, "_club_dir", lambda cid: d)
    assert client.post("/api/clubs/t/reset").status_code == 404
