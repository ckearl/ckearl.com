"""Builds one day's brief. Each source fails alone and reports its state."""

import logging
from collections.abc import Callable
from datetime import date, datetime
from typing import Any

from brief import calendars, claude, config, listening, meals, news, routine, scores, ski, teams, todos, training, weather, words, work

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


def fresh_schedule(today: date, now: datetime) -> list[dict]:
    """Today's calendar as it is now, with work hours and routines, for a replan."""
    brief = {"schedule": calendars.fetch(today), "work": work.fetch(today, now)}
    work.merge(brief)
    routine.merge(brief, today)
    return brief["schedule"]


def build(now: datetime | None = None) -> dict:
    now = now or datetime.now(config.TIMEZONE)
    today = now.date()
    stamp = f"{now.hour % 12 or 12}:{now.minute:02d} {'AM' if now.hour < 12 else 'PM'}"
    brief: dict = {"date": today.isoformat(), "generatedAt": now.isoformat(), "scores": [], "sources": []}
    collect("schedule", "Calendar", lambda: calendars.fetch(today), brief, stamp)
    collect("work", "Work hours", lambda: work.fetch(today, now), brief, stamp)
    work.merge(brief)
    routine.merge(brief, today)
    collect("todos", "Reminders", todos.fetch, brief, stamp)
    todos.flag_stale(brief, now)
    collect("training", "Training", lambda: training.fetch(now), brief, stamp)
    collect("meals", "Meals", lambda: meals.week(today), brief, stamp)
    collect("weather", "Weather", lambda: weather.fetch(today, brief.get("schedule")), brief, stamp)
    collect("scores", "Scores", lambda: scores.fetch(today), brief, stamp)
    collect("teams", "Teams", lambda: teams.fetch(now), brief, stamp)
    collect("news", "News", news.fetch, brief, stamp)
    collect("words", "Words", lambda: words.fetch(today), brief, stamp)
    collect("listening", "Listening", lambda: listening.fetch(today), brief, stamp)
    collect("ski", "Ski", lambda: ski.fetch(now), brief, stamp)
    collect("judgment", "Claude", lambda: claude.fetch(brief, today), brief, stamp)
    claude.merge(brief)
    return brief
