import json
from datetime import date

import pytest

from brief import meals

TODAY = date(2026, 11, 15)


def parse(days):
    return meals.parse(json.dumps({"days": days}), TODAY)


def test_keeps_lunch_and_dinner_trimmed():
    assert parse({"2026-11-16": {"lunch": " Leftover soup ", "dinner": "Tacos", "snack": "Chips"}}) == {
        "2026-11-16": {"lunch": "Leftover soup", "dinner": "Tacos"}
    }


def test_an_emptied_day_comes_back_empty():
    assert parse({"2026-11-16": {"lunch": "", "dinner": "  "}}) == {"2026-11-16": {}}


@pytest.mark.parametrize(
    "days",
    [
        {"2026-11-14": {"dinner": "Yesterday"}},
        {"2026-12-15": {"dinner": "Too far"}},
        {"next tuesday": {"dinner": "Tacos"}},
        {"2026-11-16": "Tacos"},
        {"2026-11-16": {"dinner": 5}},
    ],
)
def test_rejects_bad_days(days):
    with pytest.raises(ValueError):
        parse(days)


def test_rejects_a_body_without_days():
    with pytest.raises(ValueError):
        meals.parse('{"meals": []}', TODAY)


def test_save_replaces_only_the_days_sent_and_drops_past_and_empty_days(monkeypatch):
    stored = {"days": {"2026-11-10": {"dinner": "Old"}, "2026-11-16": {"dinner": "Tacos"}, "2026-11-17": {"dinner": "Soup"}}}
    saved = []
    monkeypatch.setattr(meals.store, "latest_pushed", lambda kind: stored if kind == "meals" else None)
    monkeypatch.setattr(meals.store, "save_pushed", lambda kind, body: saved.append((kind, body)))
    meals.save({"2026-11-16": {}, "2026-11-18": {"dinner": "Curry"}}, TODAY)
    assert saved == [("meals", {"days": {"2026-11-17": {"dinner": "Soup"}, "2026-11-18": {"dinner": "Curry"}}})]


def test_week_lists_the_next_seven_days(monkeypatch):
    monkeypatch.setattr(meals.store, "latest_pushed", lambda kind: {"days": {"2026-11-16": {"dinner": "Tacos"}}})
    week = meals.week(TODAY)
    assert len(week) == 7
    assert week[0] == {"date": "2026-11-15", "day": "Sun"}
    assert week[1] == {"date": "2026-11-16", "day": "Mon", "dinner": "Tacos"}
