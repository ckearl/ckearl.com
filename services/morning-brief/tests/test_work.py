import json
from datetime import date, datetime

import pytest

from brief import config, work

TODAY = date(2026, 11, 3)
NOW = datetime(2026, 11, 3, 4, 30, tzinfo=config.TIMEZONE)


def parse(events):
    return work.parse(json.dumps({"events": events}))


def test_keeps_only_times_never_titles():
    events = parse([{"title": "Quarterly review", "start": "2026-11-03T09:00:00-07:00", "end": "2026-11-03T10:00:00-07:00"}])
    assert events == [{"start": "2026-11-03T09:00:00-07:00", "end": "2026-11-03T10:00:00-07:00", "allDay": False}]


@pytest.mark.parametrize("value", [True, "Yes", "yes", "true", "1", 1])
def test_reads_all_day_however_the_shortcut_writes_it(value):
    events = parse([{"start": "2026-11-03T00:00:00-07:00", "end": "2026-11-04T00:00:00-07:00", "allDay": value}])
    assert events[0]["allDay"] is True


def test_skips_events_without_readable_times():
    assert parse([{"start": "9 AM", "end": "10 AM"}, {"start": "2026-11-03T09:00:00-07:00"}]) == []


def test_rejects_a_body_that_is_not_an_event_list():
    with pytest.raises(ValueError):
        work.parse('{"items": []}')
    with pytest.raises(ValueError):
        work.parse("not json")


def test_limits_the_number_of_events():
    event = {"start": "2026-11-03T09:00:00-07:00", "end": "2026-11-03T10:00:00-07:00"}
    assert len(parse([event] * 500)) == work.MAX_EVENTS


def test_items_show_todays_blocks_as_work(monkeypatch):
    saved = {
        "events": [
            {"start": "2026-11-03T16:00:00+00:00", "end": "2026-11-03T17:00:00+00:00", "allDay": False},
            {"start": "2026-11-04T09:00:00-07:00", "end": "2026-11-04T10:00:00-07:00", "allDay": False},
            {"start": "2026-11-03T00:00:00-07:00", "end": "2026-11-04T00:00:00-07:00", "allDay": True},
        ],
        "receivedAt": NOW.isoformat(),
    }
    monkeypatch.setattr(work.store, "latest_pushed", lambda kind: saved if kind == "work" else None)
    assert work.fetch(TODAY, NOW)["items"] == [
        {"title": "Work", "calendar": "work", "owner": "mine", "start": "09:00", "end": "10:00"},
        {"title": "Work", "calendar": "work", "owner": "mine", "start": "00:00", "end": "23:59", "allDay": True},
    ]


SATURDAY = date(2026, 11, 7)


def test_fetch_uses_the_usual_hours_when_nothing_was_sent(monkeypatch):
    monkeypatch.setattr(work.store, "latest_pushed", lambda kind: None)
    monkeypatch.delenv("WORK_HOURS", raising=False)
    assert work.fetch(TODAY, NOW)["items"] == [
        {"title": "Work", "calendar": "work", "owner": "mine", "start": "08:00", "end": "17:00", "usual": True}
    ]
    assert work.fetch(SATURDAY, NOW)["items"] == []


def test_fetch_uses_the_usual_hours_when_the_sent_times_are_old(monkeypatch):
    saved = {"events": [{"start": "2026-11-03T09:00:00-07:00", "end": "2026-11-03T10:00:00-07:00", "allDay": False}], "receivedAt": "2026-11-01T04:15:00-07:00"}
    monkeypatch.setattr(work.store, "latest_pushed", lambda kind: saved)
    monkeypatch.setenv("WORK_HOURS", "Mon-Thu,07:30-16:30")
    assert work.fetch(TODAY, NOW)["items"][0]["start"] == "07:30"
    assert work.fetch(date(2026, 11, 6), NOW)["items"] == []


def test_bad_work_hours_fall_back_to_the_default(monkeypatch):
    monkeypatch.setenv("WORK_HOURS", "weekdays 9 to 5")
    assert work.usual_hours() == ({0, 1, 2, 3, 4}, "08:00", "17:00")


def test_merge_adds_work_to_the_schedule_in_time_order():
    lunch = {"title": "Lunch", "calendar": "personal", "owner": "mine", "start": "12:00", "end": "13:00"}
    gym = {"title": "Gym", "calendar": "personal", "owner": "mine", "start": "06:00", "end": "07:00"}
    brief = {"schedule": [gym, lunch], "work": {"items": [{"title": "Work", "calendar": "work", "owner": "mine", "start": "09:00", "end": "10:00"}]}}
    work.merge(brief)
    assert [item["title"] for item in brief["schedule"]] == ["Gym", "Work", "Lunch"]
    assert "work" not in brief


def test_merge_works_when_google_failed():
    brief = {"work": {"items": [{"title": "Work", "calendar": "work", "owner": "mine", "start": "09:00", "end": "10:00"}]}}
    work.merge(brief)
    assert [item["title"] for item in brief["schedule"]] == ["Work"]


def test_merge_does_nothing_when_work_failed():
    brief = {"schedule": [], "sources": []}
    work.merge(brief)
    assert brief == {"schedule": [], "sources": []}
