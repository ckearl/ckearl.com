"""Builds one day's brief. Each source fails alone and reports its state."""

import logging
from collections.abc import Callable
from datetime import datetime
from typing import Any

from brief import calendars, config, listening, news, scores, ski, teams, todos, weather, words

logger = logging.getLogger(__name__)


def collect(name: str, label: str, fetch: Callable[[], Any], brief: dict, stamp: str) -> None:
    try:
        value = fetch()
        if value is not None:
            brief[name] = value
        brief["sources"].append({"name": label, "state": "ok", "note": f"Updated {stamp}"})
    except Exception as error:
        logger.exception("%s failed", label)
        brief["sources"].append({"name": label, "state": "failed", "note": f"Unavailable ({type(error).__name__})"})


def build(now: datetime | None = None) -> dict:
    now = now or datetime.now(config.TIMEZONE)
    today = now.date()
    stamp = f"{now.hour % 12 or 12}:{now.minute:02d} {'AM' if now.hour < 12 else 'PM'}"
    brief: dict = {"date": today.isoformat(), "generatedAt": now.isoformat(), "scores": [], "sources": []}
    collect("schedule", "Calendar", lambda: calendars.fetch(today), brief, stamp)
    collect("todos", "Reminders", todos.fetch, brief, stamp)
    todos.flag_stale(brief, now)
    collect("weather", "Weather", lambda: weather.fetch(today), brief, stamp)
    collect("scores", "Scores", lambda: scores.fetch(today), brief, stamp)
    collect("teams", "Teams", lambda: teams.fetch(now), brief, stamp)
    collect("news", "News", news.fetch, brief, stamp)
    collect("words", "Words", lambda: words.fetch(today), brief, stamp)
    collect("listening", "Listening", lambda: listening.fetch(today), brief, stamp)
    collect("ski", "Ski", lambda: ski.fetch(now), brief, stamp)
    return brief
