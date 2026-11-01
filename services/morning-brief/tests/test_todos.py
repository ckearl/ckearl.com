import json
from datetime import datetime

import pytest

from brief import config, todos

NOW = datetime(2026, 11, 2, 4, 30, tzinfo=config.TIMEZONE)


def parse(items):
    return todos.parse(json.dumps({"items": items}))


def test_keeps_title_due_day_and_notes():
    items = parse([{"title": " Fix the gate ", "due": "2026-11-03T09:00:00-07:00", "notes": "Needs a hinge"}])
    assert items == [{"title": "Fix the gate", "due": "2026-11-03", "notes": "Needs a hinge"}]


def test_leaves_out_empty_fields_and_blank_titles():
    assert parse([{"title": "Call the plumber", "due": "", "notes": ""}, {"title": "  "}]) == [{"title": "Call the plumber"}]


def test_ignores_a_due_date_it_cannot_read():
    assert parse([{"title": "Rake", "due": "tomorrow"}]) == [{"title": "Rake"}]


def test_dated_items_come_first_soonest_first_and_undated_keep_their_order():
    items = parse([{"title": "B"}, {"title": "Later", "due": "2026-11-09"}, {"title": "A"}, {"title": "Soon", "due": "2026-11-03"}])
    assert [item["title"] for item in items] == ["Soon", "Later", "B", "A"]


def test_an_empty_list_is_valid():
    assert parse([]) == []


def test_limits_size():
    items = parse([{"title": "x" * 500, "notes": "y" * 900}] * 300)
    assert len(items) == todos.MAX_ITEMS
    assert len(items[0]["title"]) == todos.MAX_TITLE
    assert len(items[0]["notes"]) == todos.MAX_NOTES


@pytest.mark.parametrize("body", ["", "not json", "[]", '{"items": 5}', '{"items": ["text"]}', '{"nope": []}', '{"items": [{"title": 5}]}'])
def test_rejects_malformed_bodies(body):
    with pytest.raises(ValueError):
        todos.parse(body)


def test_fetch_adds_the_list_name(monkeypatch):
    monkeypatch.setattr(todos.store, "latest_todos", lambda: {"items": [], "receivedAt": NOW.isoformat()})
    assert todos.fetch()["list"] == "to do @ 집"


def test_fetch_fails_before_anything_has_been_sent(monkeypatch):
    monkeypatch.setattr(todos.store, "latest_todos", lambda: None)
    with pytest.raises(LookupError):
        todos.fetch()


def test_flags_a_list_that_is_over_a_day_old():
    brief = {
        "todos": {"items": [], "receivedAt": "2026-10-31T04:00:00-06:00"},
        "sources": [{"name": "Reminders", "state": "ok", "note": "Updated 4:30 AM"}],
    }
    todos.flag_stale(brief, NOW)
    assert brief["sources"] == [{"name": "Reminders", "state": "stale", "note": "Last received Oct 31"}]


def test_a_fresh_list_or_a_missing_one_changes_nothing():
    fresh = {"todos": {"items": [], "receivedAt": "2026-11-02T04:00:00-07:00"}, "sources": [{"state": "ok"}]}
    missing = {"sources": [{"state": "failed"}]}
    todos.flag_stale(fresh, NOW)
    todos.flag_stale(missing, NOW)
    assert fresh["sources"] == [{"state": "ok"}]
    assert missing["sources"] == [{"state": "failed"}]
