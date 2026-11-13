"""Today's events from Google Calendar. Read-only: this never changes a calendar.

Every calendar on the account is read, whether or not it's checked in the Google Calendar app.
CALENDAR_OWNERS marks the ones that aren't mine, as comma-separated `id=hers`, `id=shared` or
`id=skip`. It lives in .env so the IDs stay out of this public repo."""

import os
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


def fetch(today: date) -> list[dict]:
    headers = {**HEADERS, "Authorization": f"Bearer {access_token()}"}
    start = datetime.combine(today, time.min, tzinfo=config.TIMEZONE)
    end = datetime.combine(today + timedelta(days=1), time.min, tzinfo=config.TIMEZONE)
    params = {"timeMin": start.isoformat(), "timeMax": end.isoformat(), "singleEvents": "true", "maxResults": 50}
    tagged = owners()
    events = []
    for calendar_id in calendar_ids(get_json(f"{API_URL}/users/me/calendarList", headers=headers)):
        owner = tagged.get(calendar_id, "mine")
        if owner == "skip":
            continue
        url = f"{API_URL}/calendars/{requests.utils.quote(calendar_id, safe='')}/events"
        events += [{**event, "owner": owner} for event in get_json(url, params, headers).get("items", [])]
    return build(events, today)
