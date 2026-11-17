"""The work day. The employer blocks every way of reading the Outlook calendar, so the brief
uses the usual work hours from WORK_HOURS, such as "Mon-Fri,08:00-17:00". If an iPhone Shortcut
or flow ever sends real meeting times, those are used instead while they're fresh. Only times are
kept: the page shows each block as "Work", and titles never reach this backend or Claude."""

import json
import os
import re
from datetime import date, datetime, timedelta

from brief import calendars, config, store

MAX_EVENTS = 50
MAX_AGE = timedelta(hours=24)
TRUE_TEXT = {"yes", "true", "1"}
DEFAULT_HOURS = "Mon-Fri,08:00-17:00"
DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


HOURS = re.compile(r"\s*(\w{3})-(\w{3})[\s,]+(\d\d:\d\d)-(\d\d:\d\d)\s*")


def hours_setting(name: str, default: str) -> tuple[set[int], str, str]:
    """Days (Monday is 0) and a start and end from a setting such as "Mon-Fri,08:00-17:00"."""
    match = HOURS.fullmatch(os.environ.get(name) or default)
    if not match or match[1].lower() not in DAY_NAMES or match[2].lower() not in DAY_NAMES or match[3] >= match[4]:
        match = HOURS.fullmatch(default)
    first, last = DAY_NAMES.index(match[1].lower()), DAY_NAMES.index(match[2].lower())
    return set(range(first, last + 1)), match[3], match[4]


def usual_hours() -> tuple[set[int], str, str]:
    """The workdays (Monday is 0) and the start and end of the work day."""
    return hours_setting("WORK_HOURS", DEFAULT_HOURS)


def usual_item(today: date) -> dict | None:
    days, start, end = usual_hours()
    if today.weekday() not in days:
        return None
    return {"title": "Work", "calendar": "work", "owner": "mine", "start": start, "end": end, "usual": True}


def moment(value) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.strip())
    except ValueError:
        return None
    return parsed.isoformat() if parsed.tzinfo else None


def clean(event) -> dict | None:
    if not isinstance(event, dict):
        raise ValueError("Each event must be an object")
    start, end = moment(event.get("start")), moment(event.get("end"))
    if not start or not end:
        return None
    all_day = event.get("allDay")
    return {"start": start, "end": end, "allDay": all_day is True or all_day == 1 or str(all_day).lower() in TRUE_TEXT}


def parse(body: str) -> list[dict]:
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("Expected an object with an events list")
    return [event for event in map(clean, payload["events"]) if event][:MAX_EVENTS]


def to_item(event: dict, today: date) -> dict | None:
    start = datetime.fromisoformat(event["start"]).astimezone(config.TIMEZONE)
    end = datetime.fromisoformat(event["end"]).astimezone(config.TIMEZONE)
    if event["allDay"]:
        # All-day times are midnight in the phone's zone, so compare dates without converting.
        start_day = datetime.fromisoformat(event["start"]).date()
        if start_day != today:
            return None
        return {"title": "Work", "calendar": "work", "owner": "mine", "start": "00:00", "end": "23:59", "allDay": True}
    if start.date() > today or end.date() < today:
        return None
    google_shaped = {"summary": "Work", "start": {"dateTime": event["start"]}, "end": {"dateTime": event["end"]}}
    return calendars.to_item(google_shaped, today) | {"calendar": "work"}


def fetch(today: date, now: datetime) -> dict:
    """Sent meeting times while they're under a day old, otherwise the usual work hours."""
    saved = store.latest_pushed("work")
    if saved and now - datetime.fromisoformat(saved["receivedAt"]) <= MAX_AGE:
        return {"items": [item for item in (to_item(event, today) for event in saved["events"]) if item]}
    usual = usual_item(today)
    return {"items": [usual] if usual else []}


def merge(brief: dict) -> None:
    """Folds the work blocks into the schedule."""
    saved = brief.pop("work", None)
    if saved:
        brief["schedule"] = calendars.order(brief.get("schedule", []) + saved["items"])
