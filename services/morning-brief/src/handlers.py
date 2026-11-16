import json
import logging
import os
from datetime import datetime

import requests

from brief import assemble, auth, calendars, config, meals, store, todos, training, work

logging.getLogger().setLevel(logging.INFO)


def generate(_event, _context):
    brief = assemble.build()
    store.save(brief)
    return {"date": brief["date"], "sources": brief["sources"]}


def cors_headers(event: dict) -> dict:
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    origin = headers.get("origin", "")
    allowed = os.environ.get("ALLOWED_ORIGINS", "").split(",")
    return {
        "Access-Control-Allow-Origin": origin if origin in allowed else allowed[0],
        "Access-Control-Allow-Headers": "Authorization,Content-Type",
        "Access-Control-Allow-Methods": "GET,POST,OPTIONS",
        "Vary": "Origin",
    }


def respond(event: dict, status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Cache-Control": "no-store", **cors_headers(event)},
        "body": json.dumps(body, ensure_ascii=False),
    }


def session(event, _context):
    try:
        password = json.loads(event.get("body") or "{}").get("password", "")
    except (AttributeError, ValueError):
        password = ""
    if not auth.password_matches(password):
        return respond(event, 401, {"error": "unauthorized"})
    return respond(event, 200, {"token": auth.issue_token()})


def today(event, _context):
    if not auth.authorized(event):
        return respond(event, 401, {"error": "unauthorized"})
    brief = store.latest()
    if brief is None:
        return respond(event, 404, {"error": "no brief yet"})
    return respond(event, 200, brief)


def receive_todos(event, _context):
    if not auth.todos_key_matches(event):
        return respond(event, 401, {"error": "unauthorized"})
    try:
        items = todos.parse(event.get("body") or "")
    except ValueError:
        return respond(event, 400, {"error": "invalid list"})
    now = datetime.now(config.TIMEZONE)
    saved = {"items": items, "receivedAt": now.isoformat()}
    store.save_pushed("todos", saved)
    update_todays_todos(saved, now)
    return respond(event, 200, {"received": len(items)})


def clock_stamp(now: datetime) -> str:
    return f"{now.hour % 12 or 12}:{now.minute:02d} {'AM' if now.hour < 12 else 'PM'}"


def todays_brief(now: datetime) -> dict | None:
    brief = store.latest()
    return brief if brief and brief["date"] == now.date().isoformat() else None


def update_todays_todos(saved: dict, now: datetime) -> None:
    """A list that arrives after the 4:30 brief still shows today."""
    brief = todays_brief(now)
    if brief is None:
        return
    brief["todos"] = {"list": config.TODO_LIST, **saved}
    fresh = {"name": "Reminders", "state": "ok", "note": f"Updated {clock_stamp(now)}"}
    brief["sources"] = [fresh if source["name"] == "Reminders" else source for source in brief["sources"]]
    store.save(brief)


def receive_work(event, _context):
    if not auth.todos_key_matches(event):
        return respond(event, 401, {"error": "unauthorized"})
    try:
        events = work.parse(event.get("body") or "")
    except ValueError:
        return respond(event, 400, {"error": "invalid events"})
    store.save_pushed("work", {"events": events, "receivedAt": datetime.now(config.TIMEZONE).isoformat()})
    return respond(event, 200, {"received": len(events)})


def save_goal(event, _context):
    """Saves the event to train for from the page, then replans today's Training section."""
    if not auth.authorized(event):
        return respond(event, 401, {"error": "unauthorized"})
    now = datetime.now(config.TIMEZONE)
    try:
        goal = training.parse_goal(event.get("body") or "", now.date())
    except ValueError as error:
        return respond(event, 400, {"error": str(error)})
    store.save_pushed("goal", goal or {})
    brief = store.latest()
    if brief is None or brief["date"] != now.date().isoformat():
        return respond(event, 200, {"goal": goal})
    try:
        brief["training"] = training.fetch(now)
    except Exception:
        logging.exception("Replanning failed")
        return respond(event, 200, {"goal": goal})
    store.save(brief)
    return respond(event, 200, {"goal": goal, "training": brief["training"]})


def save_meals(event, _context):
    """Saves meals written on the page and shows them in today's brief right away."""
    if not auth.authorized(event):
        return respond(event, 401, {"error": "unauthorized"})
    now = datetime.now(config.TIMEZONE)
    try:
        days = meals.parse(event.get("body") or "", now.date())
    except ValueError as error:
        return respond(event, 400, {"error": str(error)})
    meals.save(days, now.date())
    week = meals.week(now.date())
    brief = todays_brief(now)
    if brief is not None:
        brief["meals"] = week
        store.save(brief)
    return respond(event, 200, {"meals": week})


def add_event(event, _context):
    """Adds an event to the primary Google Calendar, and to today's schedule if it's today."""
    if not auth.authorized(event):
        return respond(event, 401, {"error": "unauthorized"})
    now = datetime.now(config.TIMEZONE)
    try:
        new_event = calendars.parse_event(event.get("body") or "", now.date())
    except ValueError as error:
        return respond(event, 400, {"error": str(error)})
    try:
        calendars.create(new_event)
    except requests.RequestException:
        logging.exception("Adding the event failed")
        return respond(event, 502, {"error": "Google Calendar didn't take the event. Try again in a minute."})
    item = calendars.as_item(new_event)
    brief = todays_brief(now) if new_event["date"] == now.date().isoformat() else None
    if brief is not None:
        brief["schedule"] = calendars.order(brief.get("schedule", []) + [item])
        store.save(brief)
    return respond(event, 200, {"event": new_event, "item": item if brief is not None else None})
