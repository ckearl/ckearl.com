from datetime import date

from brief import calendars

TODAY = date(2026, 11, 3)


def timed(title, start="2026-11-03T09:00:00-07:00", end="2026-11-03T10:00:00-07:00", **extra):
    return {"summary": title, "start": {"dateTime": start}, "end": {"dateTime": end}, **extra}


def test_converts_times_to_mountain_time():
    event = timed("Basketball", "2026-11-04T02:30:00+00:00", "2026-11-04T04:00:00+00:00")
    assert calendars.build([event], TODAY) == [
        {"title": "Basketball", "calendar": "personal", "start": "19:30", "end": "21:00"}
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


def test_uses_selected_calendars_and_skips_holidays_and_birthdays():
    listing = {
        "items": [
            {"id": "me@example.com", "selected": True},
            {"id": "hidden@example.com"},
            {"id": "en.usa#holiday@group.v.calendar.google.com", "selected": True},
            {"id": "addressbook#contacts@group.v.calendar.google.com", "selected": True},
        ]
    }
    assert calendars.calendar_ids(listing) == ["me@example.com"]


def test_fetch_reads_each_selected_calendar(monkeypatch):
    requested = []

    def fake_get_json(url, params=None, headers=None):
        assert headers["Authorization"] == "Bearer access"
        requested.append((url, params))
        if url.endswith("calendarList"):
            return {"items": [{"id": "me@example.com", "selected": True}]}
        return {"items": [timed("Lunch")]}

    monkeypatch.setattr(calendars, "access_token", lambda: "access")
    monkeypatch.setattr(calendars, "get_json", fake_get_json)
    assert calendars.fetch(TODAY)[0]["title"] == "Lunch"
    url, params = requested[1]
    assert url.endswith("/calendars/me%40example.com/events")
    assert params["timeMin"] == "2026-11-03T00:00:00-07:00"
    assert params["timeMax"] == "2026-11-04T00:00:00-07:00"
