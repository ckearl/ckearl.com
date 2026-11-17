"""Daily routines that hold time on the calendar without being events, so the day plan works
around them. MORNING_HELP is the stretch each morning spent helping get out the door for school,
such as "Mon-Fri,07:00-07:40". It holds the longest version, since how much it takes varies."""

from datetime import date

from brief import calendars, work

DEFAULT_MORNING_HELP = "Mon-Fri,07:00-07:40"


def morning_help(today: date) -> dict | None:
    days, start, end = work.hours_setting("MORNING_HELP", DEFAULT_MORNING_HELP)
    if today.weekday() not in days:
        return None
    return {"title": "Morning help", "calendar": "routine", "owner": "mine", "start": start, "end": end}


def merge(brief: dict, today: date) -> None:
    item = morning_help(today)
    if item:
        brief["schedule"] = calendars.order(brief.get("schedule", []) + [item])
