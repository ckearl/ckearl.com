import hashlib
import json

import handlers

HASH = hashlib.sha256(b"secret").hexdigest()


def request(password=None, origin="https://ckearl.com"):
    headers = {"Origin": origin}
    if password:
        headers["X-Brief-Password"] = password
    return {"headers": headers}


def setup(monkeypatch, brief):
    monkeypatch.setenv("BRIEF_PASSWORD_HASH", HASH)
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://ckearl.com,http://localhost:53000")
    monkeypatch.setattr(handlers.store, "latest", lambda: brief)


def test_rejects_a_missing_or_wrong_password(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    assert handlers.today(request(), None)["statusCode"] == 401
    response = handlers.today(request("wrong"), None)
    assert response["statusCode"] == 401
    assert "2026-11-02" not in response["body"]


def test_returns_the_brief_with_the_right_password(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    response = handlers.today(request("secret"), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["date"] == "2026-11-02"
    assert response["headers"]["Cache-Control"] == "no-store"


def test_fails_closed_without_a_configured_password(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    monkeypatch.delenv("BRIEF_PASSWORD_HASH")
    assert handlers.today(request("secret"), None)["statusCode"] == 401


def test_cors_only_echoes_allowed_origins(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    allowed = handlers.today(request("secret", "http://localhost:53000"), None)
    assert allowed["headers"]["Access-Control-Allow-Origin"] == "http://localhost:53000"
    blocked = handlers.today(request("secret", "https://evil.test"), None)
    assert blocked["headers"]["Access-Control-Allow-Origin"] == "https://ckearl.com"


def test_empty_store_returns_404(monkeypatch):
    setup(monkeypatch, None)
    assert handlers.today(request("secret"), None)["statusCode"] == 404
