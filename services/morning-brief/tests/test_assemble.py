from datetime import datetime

from brief import assemble, config

NOW = datetime(2026, 11, 2, 5, 30, tzinfo=config.TIMEZONE)


def test_one_failed_source_does_not_stop_the_others(monkeypatch):
    def broken(_today):
        raise TimeoutError

    monkeypatch.setattr(assemble.weather, "fetch", broken)
    monkeypatch.setattr(assemble.calendars, "fetch", lambda _today: [])
    monkeypatch.setattr(assemble.scores, "fetch", lambda _today: [{"league": "nba"}])
    monkeypatch.setattr(assemble.teams, "fetch", lambda _now: [])
    monkeypatch.setattr(assemble.news, "fetch", lambda: [])
    monkeypatch.setattr(assemble.words, "fetch", lambda _today: {})
    monkeypatch.setattr(assemble.listening, "fetch", lambda _today: {})
    monkeypatch.setattr(assemble.ski, "fetch", lambda _now: None)
    monkeypatch.setattr(assemble.todos, "fetch", lambda: {"items": [], "receivedAt": NOW.isoformat()})
    monkeypatch.setattr(assemble.claude, "fetch", lambda _brief, _today: {"game_plan": [], "top_stories": [], "sports_line": "Quiet night."})

    brief = assemble.build(NOW)

    assert "ski" not in brief
    assert "weather" not in brief
    assert brief["scores"] == [{"league": "nba"}]
    states = {source["name"]: source["state"] for source in brief["sources"]}
    assert states["Weather"] == "failed"
    assert states["Scores"] == "ok"
    assert states["Ski"] == "ok"
    assert states["Reminders"] == "ok"
    assert brief["todos"]["items"] == []
    assert brief["date"] == "2026-11-02"
    assert states["Claude"] == "ok"
    assert brief["roundup"] == [{"label": "Sports", "text": "Quiet night."}]
    assert "judgment" not in brief


def test_a_claude_failure_still_publishes_the_brief(monkeypatch):
    def broken(*_args):
        raise TimeoutError

    for source in (assemble.weather, assemble.calendars, assemble.scores, assemble.teams, assemble.news):
        monkeypatch.setattr(source, "fetch", lambda *_args: [])
    for source in (assemble.words, assemble.listening, assemble.ski):
        monkeypatch.setattr(source, "fetch", lambda *_args: None)
    monkeypatch.setattr(assemble.todos, "fetch", lambda: {"items": [], "receivedAt": NOW.isoformat()})
    monkeypatch.setattr(assemble.claude, "fetch", broken)

    brief = assemble.build(NOW)

    states = {source["name"]: source["state"] for source in brief["sources"]}
    assert states["Claude"] == "failed"
    assert "gamePlan" not in brief
