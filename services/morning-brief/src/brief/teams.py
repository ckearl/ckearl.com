"""Latest result, record and next game for the teams in the My Teams window."""

from datetime import datetime, timedelta

from brief import config
from brief.http import get_json
from brief.scores import BASE_URL

RECENT_RESULT = timedelta(days=8)


def score_value(competitor: dict) -> str:
    score = competitor.get("score")
    return score.get("displayValue", "0") if isinstance(score, dict) else str(score)


def split_sides(competition: dict, team_id: str) -> tuple[dict, dict]:
    """Returns (us, them). `team_id` may be ESPN's numeric ID."""
    competitors = competition["competitors"]
    us = next(c for c in competitors if str(c.get("id")) == team_id or str(c["team"].get("id")) == team_id)
    them = next(c for c in competitors if c is not us)
    return us, them


def last_result(team: dict, schedule: dict, now: datetime) -> str | None:
    played = [
        event
        for event in schedule.get("events", [])
        if event["competitions"][0].get("status", {}).get("type", {}).get("completed")
    ]
    if not played:
        return None
    event = played[-1]
    when = datetime.fromisoformat(event["date"].replace("Z", "+00:00"))
    if now - when > RECENT_RESULT:
        return None
    us, them = split_sides(event["competitions"][0], str(team["id"]))
    ours, theirs = int(float(score_value(us))), int(float(score_value(them)))
    opponent = them["team"].get("shortDisplayName") or them["team"].get("displayName")
    if ours == theirs:
        return f"Drew {ours}–{theirs} with {opponent}."
    verb = "Beat" if ours > theirs else "Lost to"
    return f"{verb} {opponent} {max(ours, theirs)}–{min(ours, theirs)}."


def next_game(team: dict) -> str:
    events = team.get("nextEvent") or []
    if not events:
        return "No game scheduled"
    event = events[0]
    competition = event["competitions"][0]
    us, them = split_sides(competition, str(team["id"]))
    when = datetime.fromisoformat(event["date"].replace("Z", "+00:00")).astimezone(config.TIMEZONE)
    clock = f"{when.hour % 12 or 12}:{when.minute:02d} {'AM' if when.hour < 12 else 'PM'}"
    place = "vs" if us.get("homeAway") == "home" else "at"
    opponent = them["team"].get("shortDisplayName") or them["team"].get("displayName")
    text = f"{when.strftime('%a')} {clock} {place} {opponent}"
    broadcasts = competition.get("broadcasts") or []
    if broadcasts:
        text += f", {broadcasts[0]['media']['shortName']}"
    return text


def build(meta: dict, team_payload: dict, schedule: dict, now: datetime) -> dict:
    team = team_payload["team"]
    parts = [last_result(team, schedule, now)]
    record = (team.get("record", {}).get("items") or [{}])[0].get("summary")
    if record:
        parts.append(f"Record {record}.")
    if team.get("standingSummary"):
        parts.append(f"{team['standingSummary']}.")
    return {
        "team": {key: meta[key] for key in ("abbr", "name", "bg", "fg")},
        "update": " ".join(part for part in parts if part) or "No recent games.",
        "next": next_game(team),
    }


def fetch(now: datetime) -> list[dict]:
    teams = []
    for meta in config.TEAMS:
        url = f"{BASE_URL}/{meta['path']}/teams/{meta['id']}"
        teams.append(build(meta, get_json(url), get_json(f"{url}/schedule"), now))
    return teams
