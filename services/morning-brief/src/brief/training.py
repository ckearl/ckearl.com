"""The training plan. Rules choose every workout, so it costs nothing, can be tested and can't
improvise. It plans the week around the goal event saved from the page, the sports on the
calendar and the last month of Garmin workouts, then adjusts today for what Garmin saw
yesterday and last night. The rules are in
docs/superpowers/plans/2026-11-01-morning-brief-training-and-claude.md.

This is a plan, not coaching or medical advice."""

import json
import logging
import os
import re
from datetime import date, datetime, timedelta

from brief import calendars, config, garmin, store

logger = logging.getLogger(__name__)

# Run goals, with the weekly miles and long run they build to and the weeks of taper before race day.
GOALS = {
    "5k": {"label": "5K", "miles": 3.1, "peak": 15, "long": 6, "taper": 1},
    "10k": {"label": "10K", "miles": 6.2, "peak": 20, "long": 8, "taper": 1},
    "half": {"label": "Half marathon", "miles": 13.1, "peak": 25, "long": 11, "taper": 2},
    "marathon": {"label": "Marathon", "miles": 26.2, "peak": 35, "long": 18, "taper": 3},
    "swim": {"label": "Swim event", "miles": 0, "peak": 10, "long": 5, "taper": 1},
}
FITNESS = {"label": "General fitness", "miles": 0, "peak": 15, "long": 6, "taper": 0}

# Calendar titles with these words count as a hard day.
SPORT_WORDS = (
    "basketball", "soccer", "futsal", "pickleball", "volleyball", "tennis", "football", "frisbee",
    "hike", "hiking", "ski", "snowboard", "climb", "bouldering", "hockey", "rugby", "lacrosse",
)

FLOOR_MILES = 6
GROWTH = 1.10
RECOVERY_SHARE = 0.8
TAPER_SHARE = 0.7
HARD_EFFECT = 3.5
SHORT_SLEEP_HOURS = 6.5
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
FULL_DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

# Day preferences, Monday = 0. Sunday stays free unless a race falls on it.
REST_DAYS = {6}
LONG_DAYS = [5, 4, 3]
QUALITY_DAYS = [1, 2, 3, 0, 4]
EASY_DAYS = [0, 2, 3, 1, 4, 5]
SWIM_DAYS = [2, 4, 0, 1, 3, 5]
STRENGTH_DAYS = [0, 3, 1, 4, 2]

CALISTHENICS = {
    "kind": "calisthenics",
    "title": "Calisthenics, 15 minutes",
    "detail": "Three rounds: 12 pike push-ups, 15 push-ups, 10 squat jumps, 30-second plank.",
    "hard": False,
}
STRENGTH = {
    "kind": "strength",
    "title": "Strength, 40 minutes",
    "detail": "Shoulders, chest and vertical jump: overhead press, bench or weighted push-ups, pull-ups, box jumps, split squats.",
    "hard": False,
}


# Settings

def easy_pace() -> tuple[int, int] | None:
    """Seconds per mile, slow end last, from TRAINING_EASY_PACE such as "8:30-8:45"."""
    times = re.findall(r"(\d+):(\d\d)", os.environ.get("TRAINING_EASY_PACE", ""))
    if not times:
        return None
    seconds = sorted(int(minutes) * 60 + int(rest) for minutes, rest in times)
    return seconds[0], seconds[-1]


def pace_text(seconds: tuple[int, int]) -> str:
    low, high = (f"{value // 60}:{value % 60:02d}" for value in seconds)
    return low if low == high else f"{low}–{high}"


def fallback_miles() -> float:
    try:
        return float(os.environ.get("TRAINING_BASE_MILES", "7.5"))
    except ValueError:
        return 7.5


# Goal saved from the page

def parse_goal(body: str, today: date) -> dict | None:
    """A goal event, or None to clear it and go back to general fitness."""
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("Expected an object")
    if payload.get("clear"):
        return None
    kind = payload.get("kind")
    if kind not in GOALS:
        raise ValueError("Unknown event kind")
    try:
        day = date.fromisoformat(str(payload.get("date")))
    except ValueError as error:
        raise ValueError("Expected a YYYY-MM-DD date") from error
    if not today <= day <= today + timedelta(days=730):
        raise ValueError("The date must be within the next two years")
    name = str(payload.get("name") or "").strip()[:80] or GOALS[kind]["label"]
    return {"name": name, "kind": kind, "date": day.isoformat()}


# The week

def monday(day: date) -> date:
    return day - timedelta(days=day.weekday())


def round_half(value: float) -> float:
    return max(0.5, round(value * 2) / 2)


def miles_text(value: float) -> str:
    return f"{value:g} mile" + ("" if value == 1 else "s")


def sport_on(items: list[dict]) -> str | None:
    for item in items:
        title = item.get("title", "")
        words = re.findall(r"[a-z]+", title.lower())
        if item.get("owner", "mine") != "hers" and any(word.startswith(SPORT_WORDS) for word in words):
            return title
    return None


def base_miles(activities: list[dict], week_start: date) -> float | None:
    """Average weekly running miles over the four weeks before this one."""
    start = (week_start - timedelta(days=28)).isoformat()
    runs = [item["miles"] for item in activities if item["kind"] == "run" and start <= item["date"] < week_start.isoformat()]
    return round(sum(runs) / 4, 1) if activities else None


def phase(goal: dict | None, week_start: date) -> tuple[str, int | None]:
    if goal:
        weeks_out = (monday(date.fromisoformat(goal["date"])) - week_start).days // 7
        if weeks_out >= 0:
            taper = GOALS[goal["kind"]]["taper"]
            if weeks_out == 0:
                return "race", 0
            if weeks_out < taper:
                return "taper", weeks_out
            return ("recovery" if (weeks_out - taper) % 4 == 3 else "build"), weeks_out
    return ("recovery" if week_start.isocalendar().week % 4 == 0 else "build"), None


def target_miles(spec: dict, base: float, week_phase: str) -> float:
    build = min(spec["peak"], max(FLOOR_MILES, base * GROWTH))
    share = {"build": 1, "recovery": RECOVERY_SHARE, "taper": TAPER_SHARE, "race": 0.4}[week_phase]
    return round_half(build * share)


def run_item(kind: str, miles: float, pace: tuple[int, int] | None, week_number: int) -> dict:
    easy = f"Conversational, {pace_text(pace)} per mile." if pace else "Conversational pace."
    if kind == "long":
        return {"kind": "run", "type": "long", "title": f"Long run, {miles_text(miles)}", "detail": f"{easy} Easy the whole way.", "miles": miles, "hard": True}
    if kind == "quality":
        if week_number % 2:
            detail = "1 mile easy, then 6 × 400 m hard with 400 m jogs between, then easy to finish."
            return {"kind": "run", "type": "quality", "title": f"Intervals, {miles_text(miles)}", "detail": detail, "miles": miles, "hard": True}
        tempo = f" at about {pace_text((pace[0] - 60, pace[1] - 60))}" if pace else ""
        detail = f"1 mile easy, {miles_text(max(1, miles - 2))} comfortably hard{tempo}, 1 mile easy."
        return {"kind": "run", "type": "quality", "title": f"Tempo run, {miles_text(miles)}", "detail": detail, "miles": miles, "hard": True}
    return {"kind": "run", "type": "easy", "title": f"Easy run, {miles_text(miles)}", "detail": easy, "miles": miles, "hard": False}


def swim_item(goal_kind: str | None) -> dict:
    if goal_kind == "swim":
        return {"kind": "swim", "title": "Swim, 45 minutes", "detail": "Warm up 200, then 8 × 100 steady with 20 seconds rest, then easy laps.", "hard": False}
    return {"kind": "swim", "title": "Swim, 30 minutes", "detail": "Easy laps, mostly freestyle.", "hard": False}


def spread_pick(candidates: list[int], taken: set[int], count: int) -> list[int]:
    """Picks days far from the ones already taken, preferring candidates in their listed order."""
    chosen: list[int] = []
    for _ in range(count):
        options = [day for day in candidates if day not in taken and day not in chosen]
        if not options:
            break
        used = taken | set(chosen)
        best = max(options, key=lambda day: (min((abs(day - other) for other in used), default=7), -candidates.index(day)))
        chosen.append(best)
    return chosen


def plan_week(week_start: date, goal: dict | None, activities: list[dict], calendar_week: dict[date, list[dict]]) -> dict:
    spec = GOALS[goal["kind"]] if goal else FITNESS
    goal_kind = goal["kind"] if goal else None
    week_phase, weeks_out = phase(goal, week_start)
    measured = base_miles(activities, week_start)
    base = measured if measured is not None else fallback_miles()
    target = target_miles(spec, base, week_phase)
    pace = easy_pace()
    week_number = week_start.isocalendar().week

    days = [week_start + timedelta(days=offset) for offset in range(7)]
    sports = {index: name for index, day in enumerate(days) if (name := sport_on(calendar_week.get(day, [])))}
    race = date.fromisoformat(goal["date"]).weekday() if week_phase == "race" else None
    blocked = REST_DAYS | set(sports) | ({race} if race is not None else set())
    hard_days = set(sports) | ({race} if race is not None else set())
    items: list[list[dict]] = [[] for _ in days]

    for index, name in sports.items():
        items[index].append({"kind": "sport", "title": name, "detail": "Counts as a hard day.", "hard": True})

    run_days: set[int] = set()
    if race is not None:
        title = goal["name"] if goal["name"] != spec["label"] else spec["label"]
        items[race].append({"kind": "race", "title": f"Race day: {title}", "detail": "Start easier than feels right, and finish strong.", "hard": True})
        if goal_kind != "swim":
            run_days.add(race)
        easy_days = spread_pick([day for day in EASY_DAYS if day not in blocked and abs(day - race) > 1], hard_days | run_days, 2)
        for day in easy_days:
            items[day].append(run_item("easy", round_half(max(2, target / 2)), pace, week_number))
        run_days |= set(easy_days)
    else:
        runs = 2 if target < 8 else 3 if target < 18 else 4
        if goal_kind == "swim":
            runs = min(runs, 2)
        long_day = next((day for day in LONG_DAYS if day not in blocked), None)
        quality_day = None
        wants_quality = goal_kind not in (None, "swim") and week_phase == "build" and runs >= 3
        if wants_quality:
            near_hard = hard_days | ({long_day} if long_day is not None else set())
            quality_day = next(
                (day for day in QUALITY_DAYS if day not in blocked and day != long_day and all(abs(day - other) > 1 for other in near_hard)),
                None,
            )
        long_miles = min(spec["long"], max(3, round_half(target * {2: 0.55, 3: 0.4}.get(runs, 0.33)))) if long_day is not None else 0
        quality_miles = max(3, round_half(target * 0.2)) if quality_day is not None else 0
        if long_day is not None:
            items[long_day].append(run_item("long", long_miles, pace, week_number))
            run_days.add(long_day)
            hard_days.add(long_day)
        if quality_day is not None:
            items[quality_day].append(run_item("quality", quality_miles, pace, week_number))
            run_days.add(quality_day)
            hard_days.add(quality_day)
        easy_count = runs - len(run_days)
        easy_days = spread_pick([day for day in EASY_DAYS if day not in blocked], run_days | set(sports), easy_count)
        if easy_days:
            each = round_half(max(2, (target - long_miles - quality_miles) / len(easy_days)))
            for day in easy_days:
                items[day].append(run_item("easy", each, pace, week_number))
            run_days |= set(easy_days)

    swims = 3 if goal_kind == "swim" else 1
    swim_free = [day for day in SWIM_DAYS if day not in blocked and day not in hard_days]
    swim_days = spread_pick([day for day in swim_free if day not in run_days] + [day for day in swim_free if day in run_days], set(), swims)
    for day in swim_days:
        items[day].append(swim_item(goal_kind))

    strength_count = {"race": 0, "taper": 1}.get(week_phase, 2)
    before_hard = {day - 1 for day in hard_days}
    strength_days = spread_pick([day for day in STRENGTH_DAYS if day not in blocked and day not in hard_days and day not in before_hard], set(), strength_count)
    for day in strength_days:
        items[day].append(dict(STRENGTH))

    for index in range(7):
        if index != race:
            items[index].append(dict(CALISTHENICS))

    return {
        "start": week_start,
        "phase": week_phase,
        "weeksOut": weeks_out,
        "base": base,
        "measured": measured is not None,
        "target": target,
        "runs": len(run_days),
        "swims": len(swim_days),
        "strength": len(strength_days),
        "sports": sports,
        "days": {day: day_items for day, day_items in zip(days, items)},
    }


# Today

def soften(item: dict, pace: tuple[int, int] | None, week_number: int) -> dict:
    if item.get("type") == "quality":
        return run_item("easy", item["miles"], pace, week_number)
    if item.get("type") == "long":
        return run_item("easy", round_half(item["miles"] * 0.7), pace, week_number)
    return item


def adjust_today(today: date, items: list[dict], yesterday_plan: list[dict], yesterday_sport: str | None, data: dict) -> tuple[list[dict], list[str]]:
    notes: list[str] = []
    yesterday = (today - timedelta(days=1)).isoformat()
    done = [item for item in data.get("activities", []) if item["date"] == yesterday]
    planned_run = any(item["kind"] == "run" for item in yesterday_plan)
    if planned_run and not any(item["kind"] == "run" for item in done):
        notes.append("Yesterday's run didn't happen, so it's dropped rather than added to today.")

    reasons = []
    planned_hard = any(item["hard"] for item in yesterday_plan)
    strongest = max((item["effect"] for item in done), default=0)
    if not planned_hard and (strongest >= HARD_EFFECT or yesterday_sport):
        what = f"training effect {strongest:.1f}" if strongest >= HARD_EFFECT else yesterday_sport
        reasons.append(f"yesterday went harder than planned ({what})")

    nights = [data.get("sleep", {}).get((today - timedelta(days=back)).isoformat()) for back in range(3)]
    if all(nights):
        average = sum(nights) / 3
        if average < SHORT_SLEEP_HOURS:
            reasons.append(f"sleep averaged {average:.1f} hours over the last three nights")
    hrv = data.get("hrv", {}).get(today.isoformat())
    if hrv and hrv["last"] < hrv["low"]:
        reasons.append(f"HRV was {hrv['last']}, below your usual range")

    hard = [item for item in items if item.get("type") in ("quality", "long")]
    if reasons and hard:
        pace = easy_pace()
        week_number = today.isocalendar().week
        items = [soften(item, pace, week_number) for item in items]
        notes.append(f"{reasons[0][0].upper()}{reasons[0][1:]}{''.join(', and ' + reason for reason in reasons[1:])}, so today's {hard[0]['title'].split(',')[0].lower()} turns easy.")
    elif reasons:
        notes.append(f"{reasons[0][0].upper()}{reasons[0][1:]}. Today is already easy.")
    return items, notes


def week_summary(week: dict, goal: dict | None) -> str:
    floor = week["phase"] == "build" and week["target"] > week["base"] * GROWTH + 0.5
    phase_words = {
        "build": "a gentle start" if floor or not week["measured"] else "about 10% more than your recent average",
        "recovery": "an easier week to absorb the last three",
        "taper": "a taper, so you start the race fresh",
        "race": "race week, so the runs stay short",
    }
    runs = f"{week['runs']} run" + ("" if week["runs"] == 1 else "s")
    text = f"This week is {miles_text(week['target'])} over {runs}, {phase_words[week['phase']]}."
    if week["measured"]:
        text += f" The last four weeks averaged {miles_text(week['base'])}."
    if week["sports"]:
        named = [f"{name} on {FULL_DAY_NAMES[index]}" for index, name in sorted(week["sports"].items())]
        text += f" {' and '.join(named)} {'counts' if len(named) == 1 else 'count'} as hard {'day' if len(named) == 1 else 'days'}, and the runs fit around {'it' if len(named) == 1 else 'them'}."
    return text


def focus(goal: dict | None, today: date, week: dict) -> str:
    if not goal or week["weeksOut"] is None:
        return "General fitness. Add an event to train toward it."
    when = date.fromisoformat(goal["date"])
    spec = GOALS[goal["kind"]]
    label = goal["name"] if goal["name"] == spec["label"] else f"{goal['name']} ({spec['label']})"
    days = (when - today).days
    away = "today" if days == 0 else "tomorrow" if days == 1 else f"in {days} days" if days < 14 else f"in {days // 7} weeks"
    return f"{label}, {when.strftime('%b')} {when.day}, {away}"


def short_label(item: dict) -> str:
    if item["kind"] == "run":
        word = item["title"].split(",")[0].split()[0]
        return f"{word} {item['miles']:g} mi"
    return {"swim": "Swim", "strength": "Strength", "race": "Race"}.get(item["kind"], item["title"])


def build(today: date, goal: dict | None, data: dict, calendar_days: dict[date, list[dict]]) -> dict:
    activities = data.get("activities", [])
    week = plan_week(monday(today), goal, activities, calendar_days)
    yesterday = today - timedelta(days=1)
    last_week = week if monday(yesterday) == week["start"] else plan_week(monday(yesterday), goal, activities, calendar_days)
    items, notes = adjust_today(
        today,
        list(week["days"][today]),
        last_week["days"][yesterday],
        sport_on(calendar_days.get(yesterday, [])),
        data,
    )

    done = [item for item in activities if week["start"].isoformat() <= item["date"] <= today.isoformat()]
    miles_done = round(sum(item["miles"] for item in done if item["kind"] == "run"), 1)
    meters = [
        {"label": "Miles", "done": miles_done, "target": week["target"]},
        {"label": "Runs", "done": sum(item["kind"] == "run" for item in done), "target": week["runs"]},
        {"label": "Swims", "done": sum(item["kind"] == "swim" for item in done), "target": week["swims"]},
        {"label": "Strength", "done": sum(item["kind"] == "strength" for item in done), "target": week["strength"]},
    ]
    plan = [
        {
            "day": DAY_NAMES[day.weekday()],
            "date": day.isoformat(),
            "items": [short_label(item) for item in day_items if item["kind"] != "calisthenics"] or ["Calisthenics only"],
            **({"today": True} if day == today else {}),
        }
        for day, day_items in week["days"].items()
    ]
    training = {
        "focus": focus(goal, today, week),
        "today": [{"title": item["title"], "detail": item["detail"]} for item in items],
        "why": " ".join(notes) or week_summary(week, goal),
        "week": [meter for meter in meters if meter["target"]],
        "plan": plan,
    }
    if goal:
        training["goal"] = goal
    return training


def fetch(now: datetime) -> dict:
    today = now.astimezone(config.TIMEZONE).date()
    goal = store.latest_pushed("goal")
    if goal and date.fromisoformat(goal["date"]) < today:
        goal = None
    try:
        data = garmin.fetch(today)
    except Exception:
        logger.exception("Garmin failed")
        data = None
    last_monday = monday(today) - timedelta(days=7)
    calendar_days = calendars.week(last_monday, 14)
    training = build(today, goal, data or {}, calendar_days)
    if data is None:
        training["why"] = f"Garmin was unavailable, so this skips yesterday's workouts and last night's sleep. {training['why']}"
    return training
