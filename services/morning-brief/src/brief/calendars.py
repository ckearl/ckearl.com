"""Today's events from Google Calendar, and new events added from the page. The only change this
ever makes is adding an event to the primary calendar when the page asks for one.

Every calendar on the account is read, whether or not it's checked in the Google Calendar app.
CALENDAR_OWNERS marks the ones that aren't mine, as comma-separated `id=hers`, `id=shared` or
`id=skip`. It lives in .env so the IDs stay out of this public repo."""

import json
import os
import re
from datetime import date, datetime, time, timedelta

import requests

from brief import config
from brief.http import HEADERS, TIMEOUT, get_json

TOKEN_URL = "https://oauth2.googleapis.com/token"
API_URL = "https://www.googleapis.com/calendar/v3"
SKIPPED_CALENDARS = ("#holiday@group.v.calendar.google.com", "#contacts@group.v.calendar.google.com")


def access_token() -> str:
    response = requests.post(
        TOKEN_URL,
        data={
            "client_id": os.environ["GOOGLE_CLIENT_ID"],
            "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
            "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
            "grant_type": "refresh_token",
        },
        headers=HEADERS,
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json()["access_token"]


OWNERS = ("mine", "hers", "shared", "skip")


def owners() -> dict[str, str]:
    tagged = {}
    for pair in os.environ.get("CALENDAR_OWNERS", "").split(","):
        calendar_id, _, owner = pair.strip().rpartition("=")
        if calendar_id and owner in OWNERS:
            tagged[calendar_id] = owner
    return tagged


def calendar_ids(calendars: dict) -> list[str]:
    return [
        calendar["id"] for calendar in calendars.get("items", []) if not calendar["id"].endswith(SKIPPED_CALENDARS)
    ]


def declined(event: dict) -> bool:
    return any(person.get("self") and person.get("responseStatus") == "declined" for person in event.get("attendees", []))


def clock(value: dict, today: date, fallback: str) -> str:
    moment = datetime.fromisoformat(value["dateTime"]).astimezone(config.TIMEZONE)
    return moment.strftime("%H:%M") if moment.date() == today else fallback


def to_item(event: dict, today: date) -> dict:
    item = {"title": event.get("summary") or "Busy", "calendar": "personal", "owner": event.get("owner", "mine")}
    if "date" in event["start"]:
        item |= {"start": "00:00", "end": "23:59", "allDay": True}
    else:
        item |= {"start": clock(event["start"], today, "00:00"), "end": clock(event["end"], today, "23:59")}
    if event.get("location"):
        item["place"] = event["location"].split(",")[0]
    return item


def build(events: list[dict], today: date) -> list[dict]:
    items: dict[tuple, dict] = {}
    for event in events:
        if event.get("status") != "cancelled" and not declined(event):
            item = to_item(event, today)
            key = (item["start"], item["end"], item["title"])
            if key in items and items[key]["owner"] != item["owner"]:
                item["owner"] = "shared"
            items[key] = item
    return order(list(items.values()))


def order(items: list[dict]) -> list[dict]:
    return sorted(items, key=lambda item: (not item.get("allDay"), item["start"], item["title"]))


def events(start_day: date, days: int) -> list[dict]:
    """Raw events from every calendar between the start of start_day and days later, each tagged with its owner."""
    headers = {**HEADERS, "Authorization": f"Bearer {access_token()}"}
    start = datetime.combine(start_day, time.min, tzinfo=config.TIMEZONE)
    end = datetime.combine(start_day + timedelta(days=days), time.min, tzinfo=config.TIMEZONE)
    params = {"timeMin": start.isoformat(), "timeMax": end.isoformat(), "singleEvents": "true", "maxResults": 250}
    tagged = owners()
    found = []
    for calendar_id in calendar_ids(get_json(f"{API_URL}/users/me/calendarList", headers=headers)):
        owner = tagged.get(calendar_id, "mine")
        if owner == "skip":
            continue
        url = f"{API_URL}/calendars/{requests.utils.quote(calendar_id, safe='')}/events"
        found += [{**event, "owner": owner} for event in get_json(url, params, headers).get("items", [])]
    return found


def on_day(event: dict, day: date) -> bool:
    if "date" in event["start"]:
        return date.fromisoformat(event["start"]["date"]) <= day < date.fromisoformat(event["end"]["date"])
    start = datetime.fromisoformat(event["start"]["dateTime"]).astimezone(config.TIMEZONE)
    end = datetime.fromisoformat(event["end"]["dateTime"]).astimezone(config.TIMEZONE)
    return start.date() <= day and (end.date() > day or (end.date() == day and end.time() > time.min))


def week(start_day: date, days: int = 7) -> dict[date, list[dict]]:
    """Each day's schedule items, from one request per calendar."""
    found = events(start_day, days)
    return {
        day: build([event for event in found if on_day(event, day)], day)
        for day in (start_day + timedelta(days=offset) for offset in range(days))
    }


def fetch(today: date) -> list[dict]:
    return build(events(today, 1), today)


MAX_EVENT_TITLE = 120
CLOCK = re.compile(r"([01]\d|2[0-3]):[0-5]\d")


def parse_event(body: str, today: date) -> dict:
    """{"title", "date": "YYYY-MM-DD", "start": "HH:MM", "end": "HH:MM"} or with "allDay": true instead of times."""
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("Expected an event object")
    title = payload.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("The event needs a name")
    try:
        day = date.fromisoformat(str(payload.get("date")))
    except ValueError:
        raise ValueError("The event needs a date") from None
    if not today - timedelta(days=1) <= day <= today + timedelta(days=366):
        raise ValueError("Pick a date within the next year")
    event = {"title": title.strip()[:MAX_EVENT_TITLE], "date": day.isoformat()}
    if payload.get("allDay") is True:
        return event | {"allDay": True}
    start, end = payload.get("start"), payload.get("end")
    if not (isinstance(start, str) and CLOCK.fullmatch(start) and isinstance(end, str) and CLOCK.fullmatch(end)):
        raise ValueError("The event needs a start and end time")
    if end <= start:
        raise ValueError("The event has to end after it starts")
    return event | {"start": start, "end": end}


def google_event(event: dict) -> dict:
    day = date.fromisoformat(event["date"])
    if event.get("allDay"):
        return {"summary": event["title"], "start": {"date": day.isoformat()}, "end": {"date": (day + timedelta(days=1)).isoformat()}}
    zone = str(config.TIMEZONE)

    def moment(clock: str) -> dict:
        return {"dateTime": f"{day.isoformat()}T{clock}:00", "timeZone": zone}

    return {"summary": event["title"], "start": moment(event["start"]), "end": moment(event["end"])}


def create(event: dict) -> None:
    """Adds the event to the primary calendar."""
    response = requests.post(
        f"{API_URL}/calendars/primary/events",
        json=google_event(event),
        headers={**HEADERS, "Authorization": f"Bearer {access_token()}"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()


def as_item(event: dict) -> dict:
    """The new event as a schedule row, for adding it to today's brief right away."""
    item = {"title": event["title"], "calendar": "personal", "owner": "mine"}
    if event.get("allDay"):
        return item | {"start": "00:00", "end": "23:59", "allDay": True}
    return item | {"start": event["start"], "end": event["end"]}
