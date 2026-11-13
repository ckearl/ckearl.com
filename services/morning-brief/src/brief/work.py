"""The work Outlook calendar. An iPhone Shortcut reads today's events from the phone's calendar
and sends them each morning, so nothing needs access to the work account. Only the times are
kept: the page shows each one as "Work", and titles never reach this backend or Claude."""

import json
from datetime import date, datetime, timedelta

from brief import calendars, config, store

MAX_EVENTS = 50
MAX_AGE = timedelta(hours=24)
TRUE_TEXT = {"yes", "true", "1"}


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


def fetch(today: date) -> dict:
    saved = store.latest_pushed("work")
    if saved is None:
        raise LookupError("No work events received yet")
    items = [item for item in (to_item(event, today) for event in saved["events"]) if item]
    return {"items": items, "receivedAt": saved["receivedAt"]}


def merge(brief: dict, now: datetime) -> None:
    """Folds the work blocks into the schedule, and marks the source stale if today's weren't sent."""
    saved = brief.pop("work", None)
    if saved is None:
        return
    received = datetime.fromisoformat(saved["receivedAt"]).astimezone(config.TIMEZONE)
    if now - received > MAX_AGE:
        brief["sources"][-1] = {
            "name": "Work calendar",
            "state": "stale",
            "note": f"Last received {received.strftime('%b')} {received.day}",
        }
        return
    brief["schedule"] = calendars.order(brief.get("schedule", []) + saved["items"])
