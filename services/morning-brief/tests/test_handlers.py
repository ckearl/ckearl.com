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
    monkeypatch.setattr(handlers.store, "save_pushed", lambda kind, body: saved.append(body) if kind == "todos" else None)
    monkeypatch.setattr(handlers.store, "latest", lambda: None)
    return saved


def test_a_late_list_updates_todays_brief(monkeypatch):
    setup_todos(monkeypatch)
    today = handlers.datetime.now(handlers.config.TIMEZONE).date().isoformat()
    brief = {
        "date": today,
        "sources": [
            {"name": "Calendar", "state": "ok", "note": "Updated 4:30 AM"},
            {"name": "Reminders", "state": "stale", "note": "Last received Nov 1"},
        ],
    }
    stored = []
    monkeypatch.setattr(handlers.store, "latest", lambda: brief)
    monkeypatch.setattr(handlers.store, "save", stored.append)
    assert handlers.receive_todos(todos_request("todos-key"), None)["statusCode"] == 200
    assert stored[0]["todos"]["items"] == [{"title": "Fix the gate"}]
    assert stored[0]["sources"][0]["name"] == "Calendar"
    assert stored[0]["sources"][1]["state"] == "ok"
    assert stored[0]["sources"][1]["note"].startswith("Updated ")


def test_a_list_does_not_touch_an_old_brief(monkeypatch):
    setup_todos(monkeypatch)
    stored = []
    monkeypatch.setattr(handlers.store, "latest", lambda: {"date": "2026-01-01", "sources": []})
    monkeypatch.setattr(handlers.store, "save", stored.append)
    assert handlers.receive_todos(todos_request("todos-key"), None)["statusCode"] == 200
    assert stored == []


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


def test_work_saves_todays_events_with_the_shortcut_key(monkeypatch):
    saved = []
    monkeypatch.setenv("TODOS_KEY_HASH", TODOS_HASH)
    monkeypatch.setattr(handlers.store, "save_pushed", lambda kind, body: saved.append((kind, body)))
    body = '{"events": [{"start": "2026-11-03T09:00:00-07:00", "end": "2026-11-03T10:00:00-07:00"}]}'
    response = handlers.receive_work(todos_request("todos-key", body), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"received": 1}
    assert saved[0][0] == "work"
    assert len(saved[0][1]["events"]) == 1
    assert handlers.receive_work(todos_request("wrong", body), None)["statusCode"] == 401
    assert handlers.receive_work(todos_request("todos-key", "nope"), None)["statusCode"] == 400
    assert len(saved) == 1


def goal_request(monkeypatch, body):
    monkeypatch.setenv("BRIEF_TOKEN_SECRET", "signing-secret")
    token = handlers.auth.issue_token()
    return {"headers": {"Authorization": f"Bearer {token}"}, "body": body}


def test_goal_needs_a_login(monkeypatch):
    monkeypatch.setenv("BRIEF_TOKEN_SECRET", "signing-secret")
    monkeypatch.setenv("TODOS_KEY_HASH", TODOS_HASH)
    body = '{"kind": "5k", "date": "2030-01-01"}'
    assert handlers.save_goal({"headers": {}, "body": body}, None)["statusCode"] == 401
    assert handlers.save_goal(todos_request("todos-key", body), None)["statusCode"] == 401


def test_goal_saves_and_replans_todays_brief(monkeypatch):
    saved, briefs = [], []
    today = handlers.datetime.now(handlers.config.TIMEZONE).date()
    goal_date = (today + handlers.training.timedelta(days=60)).isoformat()
    monkeypatch.setattr(handlers.store, "save_pushed", lambda kind, body: saved.append((kind, body)))
    monkeypatch.setattr(handlers.store, "latest", lambda: {"date": today.isoformat(), "training": {"focus": "old"}})
    monkeypatch.setattr(handlers.store, "save", briefs.append)
    monkeypatch.setattr(handlers.training, "fetch", lambda now: {"focus": "new"})
    response = handlers.save_goal(goal_request(monkeypatch, json.dumps({"name": "Trot", "kind": "5k", "date": goal_date})), None)
    assert response["statusCode"] == 200
    assert saved == [("goal", {"name": "Trot", "kind": "5k", "date": goal_date})]
    assert briefs[0]["training"] == {"focus": "new"}
    assert json.loads(response["body"])["training"] == {"focus": "new"}


def test_goal_can_be_cleared_and_rejects_bad_input(monkeypatch):
    saved = []
    monkeypatch.setattr(handlers.store, "save_pushed", lambda kind, body: saved.append((kind, body)))
    monkeypatch.setattr(handlers.store, "latest", lambda: None)
    assert handlers.save_goal(goal_request(monkeypatch, '{"kind": "ultra", "date": "2030-01-01"}'), None)["statusCode"] == 400
    assert handlers.save_goal(goal_request(monkeypatch, '{"clear": true}'), None)["statusCode"] == 200
    assert saved == [("goal", {})]


def authed(monkeypatch, body):
    monkeypatch.setenv("BRIEF_TOKEN_SECRET", "signing-secret")
    token = handlers.auth.issue_token()
    return {"headers": {"Authorization": f"Bearer {token}"}, "body": body}


def todays_date():
    return handlers.datetime.now(handlers.config.TIMEZONE).date()


def test_meals_save_and_update_todays_brief(monkeypatch):
    stored, pushed = [], []
    brief = {"date": todays_date().isoformat(), "sources": []}
    monkeypatch.setattr(handlers.store, "latest", lambda: brief)
    monkeypatch.setattr(handlers.store, "save", stored.append)
    monkeypatch.setattr(handlers.meals.store, "latest_pushed", lambda kind: pushed[-1] if pushed else None)
    monkeypatch.setattr(handlers.meals.store, "save_pushed", lambda kind, body: pushed.append(body))
    body = json.dumps({"days": {todays_date().isoformat(): {"dinner": "Tacos"}}})
    response = handlers.save_meals(authed(monkeypatch, body), None)
    assert response["statusCode"] == 200
    assert json.loads(response["body"])["meals"][0]["dinner"] == "Tacos"
    assert stored[0]["meals"][0]["dinner"] == "Tacos"


def test_meals_need_the_page_login(monkeypatch):
    monkeypatch.setenv("BRIEF_TOKEN_SECRET", "signing-secret")
    monkeypatch.setenv("TODOS_KEY_HASH", TODOS_HASH)
    assert handlers.save_meals(todos_request("todos-key", '{"days": {}}'), None)["statusCode"] == 401
    assert handlers.add_event(todos_request("todos-key", "{}"), None)["statusCode"] == 401


def test_meals_reject_a_bad_body(monkeypatch):
    assert handlers.save_meals(authed(monkeypatch, '{"days": "tacos"}'), None)["statusCode"] == 400


def test_add_event_creates_it_and_adds_todays_to_the_schedule(monkeypatch):
    created, stored = [], []
    brief = {"date": todays_date().isoformat(), "schedule": [{"title": "Work", "start": "08:00", "end": "17:00"}], "sources": []}
    monkeypatch.setattr(handlers.calendars, "create", created.append)
    monkeypatch.setattr(handlers.store, "latest", lambda: brief)
    monkeypatch.setattr(handlers.store, "save", stored.append)
    body = json.dumps({"title": "Read", "date": todays_date().isoformat(), "start": "21:00", "end": "21:30"})
    response = handlers.add_event(authed(monkeypatch, body), None)
    assert response["statusCode"] == 200
    assert created[0]["title"] == "Read"
    assert [item["title"] for item in stored[0]["schedule"]] == ["Work", "Read"]
    assert json.loads(response["body"])["item"]["start"] == "21:00"


def test_add_event_reports_a_google_failure(monkeypatch):
    def fail(_event):
        raise handlers.requests.HTTPError("403")

    monkeypatch.setattr(handlers.calendars, "create", fail)
    body = json.dumps({"title": "Read", "date": todays_date().isoformat(), "start": "21:00", "end": "21:30"})
    assert handlers.add_event(authed(monkeypatch, body), None)["statusCode"] == 502


def test_add_event_rejects_bad_times(monkeypatch):
    body = json.dumps({"title": "Read", "date": todays_date().isoformat(), "start": "21:30", "end": "21:00"})
    assert handlers.add_event(authed(monkeypatch, body), None)["statusCode"] == 400
