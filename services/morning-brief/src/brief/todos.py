"""The Reminders list. An iPhone Shortcut sends every open item each morning, and each send
replaces the last, so finished items drop off. The brief reads the list and never changes it."""

import json
import re
from datetime import datetime, timedelta

from brief import config, store

MAX_ITEMS = 200
MAX_TITLE = 200
MAX_NOTES = 500
MAX_AGE = timedelta(hours=24)


def text(item: dict, field: str, limit: int) -> str:
    value = item.get(field) or ""
    if not isinstance(value, str):
        raise ValueError(f"{field} must be text")
    return value.strip()[:limit]


def clean(item: dict) -> dict | None:
    if not isinstance(item, dict):
        raise ValueError("Each item must be an object")
    title = text(item, "title", MAX_TITLE)
    if not title:
        return None
    cleaned = {"title": title}
    due = re.match(r"\d{4}-\d{2}-\d{2}", text(item, "due", MAX_TITLE))
    if due:
        cleaned["due"] = due.group()
    notes = text(item, "notes", MAX_NOTES)
    if notes:
        cleaned["notes"] = notes
    return cleaned


def parse(body: str) -> list[dict]:
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("items"), list):
        raise ValueError("Expected an object with an items list")
    items = [item for item in map(clean, payload["items"]) if item][:MAX_ITEMS]
    return sorted(items, key=lambda item: (item.get("due") is None, item.get("due", "")))


def fetch() -> dict:
    saved = store.latest_todos()
    if saved is None:
        raise LookupError("No list received yet")
    return {"list": config.TODO_LIST, **saved}


def flag_stale(brief: dict, now: datetime) -> None:
    saved = brief.get("todos")
    if not saved:
        return
    received = datetime.fromisoformat(saved["receivedAt"]).astimezone(config.TIMEZONE)
    if now - received > MAX_AGE:
        brief["sources"][-1] = {
            "name": "Reminders",
            "state": "stale",
            "note": f"Last received {received.strftime('%b')} {received.day}",
        }
