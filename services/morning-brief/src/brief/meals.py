"""The week's meals, written on the page. Each save sends the days it covers and replaces just
those days. The brief shows the coming week and gives it to Claude to time shopping and prep."""

import json
from datetime import date, timedelta

from brief import store

MEALS = ("lunch", "dinner")
MAX_TEXT = 120
DAYS_SHOWN = 7
DAYS_AHEAD = 14


def parse(body: str, today: date) -> dict[str, dict]:
    """{"days": {"YYYY-MM-DD": {"lunch": "...", "dinner": "..."}}} for today through two weeks out."""
    payload = json.loads(body)
    if not isinstance(payload, dict) or not isinstance(payload.get("days"), dict):
        raise ValueError("Expected an object with a days map")
    days = {}
    for key, meals in payload["days"].items():
        try:
            day = date.fromisoformat(key)
        except (TypeError, ValueError):
            raise ValueError(f"{key} isn't a date") from None
        if not today <= day <= today + timedelta(days=DAYS_AHEAD):
            raise ValueError("Meals can be planned up to two weeks ahead")
        if not isinstance(meals, dict):
            raise ValueError("Each day must be an object")
        cleaned = {}
        for meal in MEALS:
            value = meals.get(meal) or ""
            if not isinstance(value, str):
                raise ValueError(f"{meal} must be text")
            if value.strip():
                cleaned[meal] = value.strip()[:MAX_TEXT]
        days[day.isoformat()] = cleaned
    return days


def save(days: dict[str, dict], today: date) -> None:
    saved = (store.latest_pushed("meals") or {}).get("days", {})
    merged = {key: value for key, value in {**saved, **days}.items() if key >= today.isoformat() and value}
    store.save_pushed("meals", {"days": merged})


def week(today: date) -> list[dict]:
    """The next seven days, each with whatever meals are written down."""
    saved = (store.latest_pushed("meals") or {}).get("days", {})
    days = []
    for offset in range(DAYS_SHOWN):
        day = today + timedelta(days=offset)
        days.append({"date": day.isoformat(), "day": day.strftime("%a"), **saved.get(day.isoformat(), {})})
    return days
