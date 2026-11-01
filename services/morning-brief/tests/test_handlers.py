import hashlib
import json

import handlers

HASH = hashlib.sha256(b"secret").hexdigest()


def login(password, origin="https://ckearl.com"):
    return {"headers": {"Origin": origin}, "body": json.dumps({"password": password})}


def request(token=None, origin="https://ckearl.com"):
    headers = {"Origin": origin}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return {"headers": headers}


def setup(monkeypatch, brief):
    monkeypatch.setenv("BRIEF_PASSWORD_HASH", HASH)
    monkeypatch.setenv("BRIEF_TOKEN_SECRET", "signing-secret")
    monkeypatch.setenv("ALLOWED_ORIGINS", "https://ckearl.com,http://localhost:53000")
    monkeypatch.setattr(handlers.store, "latest", lambda: brief)


def token_for(monkeypatch):
    return json.loads(handlers.session(login("secret"), None)["body"])["token"]


def test_login_rejects_a_wrong_or_malformed_password(monkeypatch):
    setup(monkeypatch, {})
    assert handlers.session(login("wrong"), None)["statusCode"] == 401
    assert handlers.session({"headers": {}, "body": "not json"}, None)["statusCode"] == 401
    assert handlers.session({"headers": {}, "body": "[]"}, None)["statusCode"] == 401
    assert handlers.session({"headers": {}}, None)["statusCode"] == 401
    assert handlers.session({"headers": {}, "body": '{"password": 5}'}, None)["statusCode"] == 401


def test_login_fails_closed_without_a_configured_password(monkeypatch):
    setup(monkeypatch, {})
    monkeypatch.delenv("BRIEF_PASSWORD_HASH")
    assert handlers.session(login("secret"), None)["statusCode"] == 401


def test_rejects_missing_forged_and_password_credentials(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    assert handlers.today(request(), None)["statusCode"] == 401
    assert handlers.today(request("9999999999.forged"), None)["statusCode"] == 401
    response = handlers.today(request("secret"), None)
    assert response["statusCode"] == 401
    assert "2026-11-02" not in response["body"]
    old_header = {"headers": {"X-Brief-Password": "secret"}}
    assert handlers.today(old_header, None)["statusCode"] == 401


def test_a_token_with_a_changed_expiry_is_rejected(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    expires, signed = token_for(monkeypatch).split(".")
    assert handlers.today(request(f"{int(expires) + 1}.{signed}"), None)["statusCode"] == 401


def test_a_token_expires_after_30_days(monkeypatch):
    setup(monkeypatch, {})
    event = request(handlers.auth.issue_token(now=1000))
    assert handlers.auth.authorized(event, now=1000 + 29 * 86400)
    assert not handlers.auth.authorized(event, now=1000 + 30 * 86400)


def test_returns_the_brief_with_a_valid_token(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    response = handlers.today(request(token_for(monkeypatch)), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["date"] == "2026-11-02"
    assert response["headers"]["Cache-Control"] == "no-store"


def test_fails_closed_without_a_signing_secret(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    token = token_for(monkeypatch)
    monkeypatch.delenv("BRIEF_TOKEN_SECRET")
    assert handlers.today(request(token), None)["statusCode"] == 401


def test_cors_only_echoes_allowed_origins(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    allowed = handlers.session(login("secret", "http://localhost:53000"), None)
    assert allowed["headers"]["Access-Control-Allow-Origin"] == "http://localhost:53000"
    blocked = handlers.session(login("secret", "https://evil.test"), None)
    assert blocked["headers"]["Access-Control-Allow-Origin"] == "https://ckearl.com"


def test_empty_store_returns_404(monkeypatch):
    setup(monkeypatch, None)
    assert handlers.today(request(token_for(monkeypatch)), None)["statusCode"] == 404


TODOS_HASH = hashlib.sha256(b"todos-key").hexdigest()


def todos_request(key=None, body='{"items": [{"title": "Fix the gate"}]}'):
    headers = {"Authorization": f"Bearer {key}"} if key else {}
    return {"headers": headers, "body": body}


def setup_todos(monkeypatch):
    saved = []
    monkeypatch.setenv("TODOS_KEY_HASH", TODOS_HASH)
    monkeypatch.setattr(handlers.store, "save_todos", saved.append)
    return saved


def test_todos_saves_the_list_with_the_right_key(monkeypatch):
    saved = setup_todos(monkeypatch)
    response = handlers.receive_todos(todos_request("todos-key"), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"received": 1}
    assert saved[0]["items"] == [{"title": "Fix the gate"}]
    assert "receivedAt" in saved[0]


def test_todos_rejects_other_credentials_without_saving(monkeypatch):
    saved = setup_todos(monkeypatch)
    monkeypatch.setenv("BRIEF_TOKEN_SECRET", "signing-secret")
    monkeypatch.setenv("BRIEF_PASSWORD_HASH", HASH)
    token = handlers.auth.issue_token()
    assert handlers.receive_todos(todos_request(), None)["statusCode"] == 401
    assert handlers.receive_todos(todos_request("wrong"), None)["statusCode"] == 401
    assert handlers.receive_todos(todos_request(token), None)["statusCode"] == 401
    assert handlers.receive_todos(todos_request("secret"), None)["statusCode"] == 401
    assert saved == []


def test_todos_fails_closed_without_a_configured_key(monkeypatch):
    saved = setup_todos(monkeypatch)
    monkeypatch.delenv("TODOS_KEY_HASH")
    assert handlers.receive_todos(todos_request("todos-key"), None)["statusCode"] == 401
    assert saved == []


def test_todos_rejects_a_bad_body_and_keeps_the_saved_list(monkeypatch):
    saved = setup_todos(monkeypatch)
    assert handlers.receive_todos(todos_request("todos-key", "not json"), None)["statusCode"] == 400
    assert saved == []


def test_the_todos_key_cannot_read_the_brief(monkeypatch):
    setup(monkeypatch, {"date": "2026-11-02"})
    setup_todos(monkeypatch)
    assert handlers.today(request("todos-key"), None)["statusCode"] == 401
