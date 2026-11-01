from datetime import datetime

from brief import assemble, config

NOW = datetime(2026, 11, 2, 5, 30, tzinfo=config.TIMEZONE)


def test_one_failed_source_does_not_stop_the_others(monkeypatch):
    def broken(_today):
        raise TimeoutError

    monkeypatch.setattr(assemble.weather, "fetch", broken)
    monkeypatch.setattr(assemble.scores, "fetch", lambda _today: [{"league": "nba"}])
    monkeypatch.setattr(assemble.teams, "fetch", lambda _now: [])
    monkeypatch.setattr(assemble.news, "fetch", lambda: [])
    monkeypatch.setattr(assemble.words, "fetch", lambda _today: {})

    brief = assemble.build(NOW)

    assert "weather" not in brief
    assert brief["scores"] == [{"league": "nba"}]
    states = {source["name"]: source["state"] for source in brief["sources"]}
    assert states["Weather"] == "failed"
    assert states["Scores"] == "ok"
    assert brief["date"] == "2026-11-02"
