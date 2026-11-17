import json
from datetime import date

import pytest

from brief import feedback

TODAY = date(2026, 11, 17)


def body(**overrides):
    return json.dumps({"date": "2026-11-17", "kind": "music", "title": "Piano", "start": "20:00", "outcome": "done", **overrides})


def test_parse_keeps_a_mark_for_today():
    assert feedback.parse(body(), TODAY) == {"date": "2026-11-17", "kind": "music", "title": "Piano", "start": "20:00", "outcome": "done"}


@pytest.mark.parametrize(
    "overrides",
    [{"outcome": "maybe"}, {"date": "2026-11-16"}, {"start": "8pm"}, {"title": " "}, {"kind": 3}],
)
def test_parse_rejects_bad_marks(overrides):
    with pytest.raises(ValueError):
        feedback.parse(body(**overrides), TODAY)


def test_save_replaces_the_same_suggestion_and_drops_old_ones(monkeypatch):
    stored = {
        "entries": [
            {"date": "2026-10-01", "kind": "music", "title": "Old", "start": "07:00", "outcome": "skipped"},
            {"date": "2026-11-17", "kind": "music", "title": "Piano", "start": "20:00", "outcome": "skipped"},
        ]
    }
    saved = []
    monkeypatch.setattr(feedback.store, "latest_pushed", lambda kind: stored)
    monkeypatch.setattr(feedback.store, "save_pushed", lambda kind, value: saved.append((kind, value)))
    feedback.save(feedback.parse(body(), TODAY), TODAY)
    feedback.save(feedback.parse(body(outcome="clear"), TODAY), TODAY)
    assert saved[0] == ("feedback", {"entries": [{"date": "2026-11-17", "kind": "music", "title": "Piano", "start": "20:00", "outcome": "done"}]})
    assert saved[1] == ("feedback", {"entries": []})


def test_habits_sum_up_the_weeks_before_today(monkeypatch):
    entries = [
        {"date": "2026-11-10", "kind": "music", "title": "Piano", "start": "20:00", "outcome": "done"},
        {"date": "2026-11-11", "kind": "music", "title": "Piano", "start": "06:45", "outcome": "skipped"},
        {"date": "2026-11-12", "kind": "music", "title": "Guitar", "start": "19:30", "outcome": "done"},
        {"date": "2026-11-17", "kind": "music", "title": "Piano", "start": "06:45", "outcome": "skipped"},
    ]
    monkeypatch.setattr(feedback.store, "latest_pushed", lambda kind: {"entries": entries})
    assert feedback.habits(TODAY) == {"music": {"done": 2, "skipped": 1, "doneAt": ["19:30", "20:00"], "skippedAt": ["06:45"]}}


def test_apply_sets_and_clears_the_outcome():
    suggestions = [{"title": "Piano", "start": "20:00", "end": "20:25", "kind": "music"}, {"title": "Read", "start": "21:00", "end": "21:30", "kind": "reading"}]
    marked = feedback.apply(suggestions, {"title": "Piano", "start": "20:00", "outcome": "skipped"})
    assert marked[0]["outcome"] == "skipped" and "outcome" not in marked[1]
    assert "outcome" not in feedback.apply(marked, {"title": "Piano", "start": "20:00", "outcome": "clear"})[0]
