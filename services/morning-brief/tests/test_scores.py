import json
from datetime import date
from pathlib import Path

from brief import scores

FIXTURE = json.loads((Path(__file__).parent / "fixtures" / "nba_scoreboard.json").read_text())


def event(home, away, completed=True, status="Final"):
    side = lambda place, abbr, score: {
        "homeAway": place,
        "score": score,
        "team": {"abbreviation": abbr, "shortDisplayName": abbr.title()},
    }
    return {
        "status": {"type": {"completed": completed, "shortDetail": status}},
        "competitions": [{"competitors": [side("home", home, "2"), side("away", away, "1")]}],
    }


def test_parses_a_real_espn_scoreboard():
    games = scores.parse_games(FIXTURE, "nba", None)
    assert len(games) == 2
    assert isinstance(games[0]["home"]["score"], int)
    assert games[0]["home"]["abbr"].islower()


def test_skips_games_not_finished():
    assert scores.parse_games({"events": [event("LAL", "BOS", completed=False)]}, "nba", None) == []


def test_keeps_only_followed_teams():
    payload = {"events": [event("SEA", "KC"), event("DAL", "NYG")]}
    games = scores.parse_games(payload, "nfl", {"sea"})
    assert [game["home"]["abbr"] for game in games] == ["sea"]


def test_followed_team_can_be_away():
    assert scores.parse_games({"events": [event("KC", "SEA")]}, "nfl", {"sea"})


def test_mammoth_abbreviation_matches_the_logo_file():
    games = scores.parse_games({"events": [event("UTA", "PHI")]}, "nhl", {"utah"})
    assert games[0]["home"]["abbr"] == "utah"


def test_window_labels():
    monday = date(2026, 11, 2)
    assert scores.window_label(monday, 1) == "Sunday night"
    assert scores.window_label(monday, 3) == "Last 3 days"
