import json
from datetime import date

import pytest

from brief import calendars

TODAY = date(2026, 11, 3)


def timed(title, start="2026-11-03T09:00:00-07:00", end="2026-11-03T10:00:00-07:00", **extra):
    return {"summary": title, "start": {"dateTime": start}, "end": {"dateTime": end}, **extra}


def test_converts_times_to_mountain_time():
    event = timed("Basketball", "2026-11-04T02:30:00+00:00", "2026-11-04T04:00:00+00:00")
    assert calendars.build([event], TODAY) == [
        {"title": "Basketball", "calendar": "personal", "owner": "mine", "start": "19:30", "end": "21:00"}
    ]


def test_all_day_events_come_first():
    allday = {"summary": "Day off", "start": {"date": "2026-11-03"}, "end": {"date": "2026-11-04"}}
    items = calendars.build([timed("Lunch"), allday], TODAY)
    assert [item["title"] for item in items] == ["Day off", "Lunch"]
    assert items[0]["allDay"] is True


def test_event_spanning_midnight_is_clipped_to_today():
    event = timed("Overnight", "2026-11-02T22:00:00-07:00", "2026-11-04T01:00:00-07:00")
    item = calendars.build([event], TODAY)[0]
    assert (item["start"], item["end"]) == ("00:00", "23:59")


def test_skips_cancelled_and_declined_events():
    cancelled = timed("Cancelled", status="cancelled")
    declined = timed("Declined", attendees=[{"self": True, "responseStatus": "declined"}])
    accepted = timed("Accepted", attendees=[{"self": True, "responseStatus": "accepted"}, {"responseStatus": "declined"}])
    assert [item["title"] for item in calendars.build([cancelled, declined, accepted], TODAY)] == ["Accepted"]


def test_same_event_on_two_calendars_shows_once():
    assert len(calendars.build([timed("Dinner"), timed("Dinner")], TODAY)) == 1


def test_private_event_without_a_title_shows_as_busy():
    event = timed("x")
    del event["summary"]
    assert calendars.build([event], TODAY)[0]["title"] == "Busy"


def test_place_keeps_only_the_first_part_of_an_address():
    event = timed("Lunch with a friend", location="Corner Cafe, 100 N Main St, Provo, UT")
    assert calendars.build([event], TODAY)[0]["place"] == "Corner Cafe"


def test_reads_every_calendar_except_holidays_and_birthdays():
    listing = {
        "items": [
            {"id": "me@example.com", "selected": True},
            {"id": "unchecked@example.com"},
            {"id": "en.usa#holiday@group.v.calendar.google.com", "selected": True},
            {"id": "addressbook#contacts@group.v.calendar.google.com", "selected": True},
        ]
    }
    assert calendars.calendar_ids(listing) == ["me@example.com", "unchecked@example.com"]


def test_owners_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("CALENDAR_OWNERS", "her@example.com=hers, family@group=shared,feed@example.com=skip,bad=nobody")
    assert calendars.owners() == {"her@example.com": "hers", "family@group": "shared", "feed@example.com": "skip"}


def test_owners_default_to_none(monkeypatch):
    monkeypatch.delenv("CALENDAR_OWNERS", raising=False)
    assert calendars.owners() == {}


def test_each_item_keeps_its_owner():
    items = calendars.build([timed("Class", owner="hers"), timed("Gym", "2026-11-03T06:00:00-07:00", owner="mine")], TODAY)
    assert [(item["title"], item["owner"]) for item in items] == [("Gym", "mine"), ("Class", "hers")]


def test_an_event_on_both_our_calendars_is_shared():
    items = calendars.build([timed("Dinner", owner="mine"), timed("Dinner", owner="hers")], TODAY)
    assert [item["owner"] for item in items] == ["shared"]


def test_fetch_reads_every_calendar_tags_owners_and_skips_skipped(monkeypatch):
    requested = []
    monkeypatch.setenv("CALENDAR_OWNERS", "her@example.com=hers,feed@example.com=skip")

    def fake_get_json(url, params=None, headers=None):
        assert headers["Authorization"] == "Bearer access"
        requested.append((url, params))
        if url.endswith("calendarList"):
            return {"items": [{"id": "me@example.com"}, {"id": "her@example.com"}, {"id": "feed@example.com"}]}
        title = "Lunch" if "me%40" in url else "Class"
        return {"items": [timed(title)]}

    monkeypatch.setattr(calendars, "access_token", lambda: "access")
    monkeypatch.setattr(calendars, "get_json", fake_get_json)
    items = calendars.fetch(TODAY)
    assert [(item["title"], item["owner"]) for item in items] == [("Class", "hers"), ("Lunch", "mine")]
    assert [url.rsplit("/", 2)[-2] for url, _ in requested[1:]] == ["me%40example.com", "her%40example.com"]
    _, params = requested[1]
    assert params["timeMin"] == "2026-11-03T00:00:00-07:00"
    assert params["timeMax"] == "2026-11-04T00:00:00-07:00"


def test_week_groups_events_by_day_including_multi_day_ones(monkeypatch):
    found = [
        timed("Basketball", "2026-11-03T19:00:00-07:00", "2026-11-03T21:00:00-07:00", owner="mine"),
        timed("Late game", "2026-11-04T22:00:00-07:00", "2026-11-05T00:00:00-07:00", owner="mine"),
        {"summary": "Trip", "start": {"date": "2026-11-05"}, "end": {"date": "2026-11-07"}, "owner": "mine"},
    ]
    monkeypatch.setattr(calendars, "events", lambda start, days: found)
    days = calendars.week(TODAY, 4)
    assert [[item["title"] for item in days[day]] for day in sorted(days)] == [
        ["Basketball"],
        ["Late game"],
        ["Trip"],
        ["Trip"],
    ]


EVENT_DAY = date(2026, 11, 15)


def event_body(**fields):
    return json.dumps({"title": "Dentist", "date": "2026-11-16", "start": "09:00", "end": "09:45", **fields})


def test_parse_event_keeps_a_timed_event():
    assert calendars.parse_event(event_body(), EVENT_DAY) == {"title": "Dentist", "date": "2026-11-16", "start": "09:00", "end": "09:45"}


def test_parse_event_keeps_an_all_day_event():
    assert calendars.parse_event(event_body(allDay=True, start=None), EVENT_DAY) == {"title": "Dentist", "date": "2026-11-16", "allDay": True}


@pytest.mark.parametrize(
    "fields",
    [
        {"title": " "},
        {"date": "soon"},
        {"date": "2028-01-01"},
        {"start": "9am"},
        {"start": "25:00"},
        {"end": "08:00"},
    ],
)
def test_parse_event_rejects_bad_fields(fields):
    with pytest.raises(ValueError):
        calendars.parse_event(event_body(**fields), EVENT_DAY)


def test_google_event_uses_mountain_time_and_an_exclusive_all_day_end():
    timed = calendars.google_event({"title": "Dentist", "date": "2026-11-16", "start": "09:00", "end": "09:45"})
    assert timed["start"] == {"dateTime": "2026-11-16T09:00:00", "timeZone": "America/Denver"}
    all_day = calendars.google_event({"title": "Trip", "date": "2026-11-30", "allDay": True})
    assert all_day["end"] == {"date": "2026-12-01"}


def test_create_posts_to_the_primary_calendar(monkeypatch):
    sent = {}

    class Response:
        def raise_for_status(self):
            pass

    def post(url, json, headers, timeout):
        sent.update(url=url, json=json, auth=headers["Authorization"])
        return Response()

    monkeypatch.setattr(calendars, "access_token", lambda: "token")
    monkeypatch.setattr(calendars.requests, "post", post)
    calendars.create({"title": "Dentist", "date": "2026-11-16", "start": "09:00", "end": "09:45"})
    assert sent["url"].endswith("/calendars/primary/events")
    assert sent["json"]["summary"] == "Dentist"
    assert sent["auth"] == "Bearer token"
