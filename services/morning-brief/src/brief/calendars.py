"""Today's events from Google Calendar. Read-only: this never changes a calendar."""

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


def calendar_ids(calendars: dict) -> list[str]:
    return [
        calendar["id"]
        for calendar in calendars.get("items", [])
        if calendar.get("selected") and not calendar["id"].endswith(SKIPPED_CALENDARS)
    ]


def declined(event: dict) -> bool:
    return any(person.get("self") and person.get("responseStatus") == "declined" for person in event.get("attendees", []))


def clock(value: dict, today: date, fallback: str) -> str:
    moment = datetime.fromisoformat(value["dateTime"]).astimezone(config.TIMEZONE)
    return moment.strftime("%H:%M") if moment.date() == today else fallback


def to_item(event: dict, today: date) -> dict:
    item = {"title": event.get("summary") or "Busy", "calendar": "personal"}
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
            items[(item["start"], item["end"], item["title"])] = item
    return sorted(items.values(), key=lambda item: (not item.get("allDay"), item["start"], item["title"]))


def fetch(today: date) -> list[dict]:
    headers = {**HEADERS, "Authorization": f"Bearer {access_token()}"}
    start = datetime.combine(today, time.min, tzinfo=config.TIMEZONE)
    end = datetime.combine(today + timedelta(days=1), time.min, tzinfo=config.TIMEZONE)
    params = {"timeMin": start.isoformat(), "timeMax": end.isoformat(), "singleEvents": "true", "maxResults": 50}
    events = []
    for calendar_id in calendar_ids(get_json(f"{API_URL}/users/me/calendarList", headers=headers)):
        url = f"{API_URL}/calendars/{requests.utils.quote(calendar_id, safe='')}/events"
        events += get_json(url, params, headers).get("items", [])
    return build(events, today)
