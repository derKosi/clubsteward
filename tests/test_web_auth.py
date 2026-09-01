"""Optional shared-token gate on /api/* (CLUBSTEWARD_WEB_TOKEN).

Unset -> open local demo mode (as before). Set -> 401 without the
X-API-Token header, 200 with it. Pages stay public either way.
"""

from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from clubsteward.web import app  # noqa: E402

client = TestClient(app)


def test_api_open_when_no_token_configured(monkeypatch):
    monkeypatch.delenv("CLUBSTEWARD_WEB_TOKEN", raising=False)
    assert client.get("/api/clubs").status_code == 200


def test_api_returns_401_without_header_when_token_configured(monkeypatch):
    monkeypatch.setenv("CLUBSTEWARD_WEB_TOKEN", "s3cret")
    assert client.get("/api/clubs").status_code == 401


def test_api_allows_matching_token(monkeypatch):
    monkeypatch.setenv("CLUBSTEWARD_WEB_TOKEN", "s3cret")
    r = client.get("/api/clubs", headers={"X-API-Token": "s3cret"})
    assert r.status_code == 200


def test_api_rejects_wrong_token(monkeypatch):
    monkeypatch.setenv("CLUBSTEWARD_WEB_TOKEN", "s3cret")
    r = client.get("/api/clubs", headers={"X-API-Token": "wrong"})
    assert r.status_code == 401
