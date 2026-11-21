"""Recent scores from ESPN's public scoreboard endpoints."""

from datetime import date, timedelta

from brief import config, highlights
from brief.http import get_json

BASE_URL = "https://site.api.espn.com/apis/site/v2/sports"
ESPN_SITE = "https://www.espn.com/"


def abbreviation(league: str, team: dict) -> str:
    abbr = team["abbreviation"].lower()
    return config.ABBREVIATION_ALIASES.get((league, abbr), abbr)


def gamecast_url(event: dict) -> str | None:
    for link in event.get("links", []):
        href = link.get("href", "")
        if "summary" in link.get("rel", []) and href.startswith(ESPN_SITE):
            return href
    return None


def parse_games(payload: dict, league: str, followed: set[str] | None) -> list[dict]:
    games = []
    for event in payload.get("events", []):
        if not event["status"]["type"]["completed"]:
            continue
        competition = event["competitions"][0]
        sides = {
            competitor["homeAway"]: {
                "_team": competitor["team"],
                "abbr": abbreviation(league, competitor["team"]),
                "name": competitor["team"]["shortDisplayName"],
                "score": int(competitor["score"]),
            }
            for competitor in competition["competitors"]
        }
        teams = {place: side.pop("_team") for place, side in sides.items()}
        if followed is not None and not followed & {sides["home"]["abbr"], sides["away"]["abbr"]}:
            continue
        game = {
            "home": sides["home"],
            "away": sides["away"],
            "status": event["status"]["type"]["shortDetail"],
            "url": gamecast_url(event),
        }
        if event.get("date"):
            # Only for finding highlights; highlights.attach removes it.
            game["_match"] = {
                "names": [highlights.aliases(teams["away"]), highlights.aliases(teams["home"])],
                "start": highlights.parse_time(event["date"]),
            }
        games.append(game)
    return games


def window_label(today: date, days: int) -> str:
    if days == 1:
        return f"{(today - timedelta(days=1)).strftime('%A')} night"
    return f"Last {days} days"


def fetch(today: date) -> list[dict]:
    groups = []
    for league, (path, label, days, followed) in config.LEAGUES.items():
        games = []
        for offset in range(1, days + 1):
            day = (today - timedelta(days=offset)).strftime("%Y%m%d")
            # ESPN answers a date range with a 400, so each day is its own request.
            games += parse_games(get_json(f"{BASE_URL}/{path}/scoreboard", {"dates": day}), league, followed)
        if games:
            groups.append({"league": league, "label": label, "when": window_label(today, days), "games": games})
    highlights.attach(groups)
    return groups
