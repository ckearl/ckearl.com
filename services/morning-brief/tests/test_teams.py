from datetime import datetime, timezone

from brief import teams

NOW = datetime(2026, 11, 2, 12, tzinfo=timezone.utc)
META = {"abbr": "UTA", "name": "Utah Jazz", "bg": "#000", "fg": "#fff"}


def side(team_id, name, place, score=None):
    side_data = {"id": team_id, "homeAway": place, "team": {"id": team_id, "shortDisplayName": name}}
    if score is not None:
        side_data["score"] = score
    return side_data


def game(date, ours, theirs):
    return {
        "date": date,
        "competitions": [
            {
                "status": {"type": {"completed": True}},
                "competitors": [side("1", "Jazz", "home", ours), side("2", "Lakers", "away", theirs)],
            }
        ],
    }


def team(next_event=None, record="3-3"):
    return {"id": "1", "nextEvent": next_event or [], "record": {"items": [{"summary": record}]}}


def test_reports_a_recent_win_with_higher_score_first():
    schedule = {"events": [game("2026-11-01T02:00Z", {"displayValue": "114"}, {"displayValue": "108"})]}
    assert teams.last_result(team(), schedule, NOW) == "Beat Lakers 114–108."


def test_reports_a_loss_with_plain_score_values():
    schedule = {"events": [game("2026-11-01T02:00Z", "2", "3")]}
    assert teams.last_result(team(), schedule, NOW) == "Lost to Lakers 3–2."


def test_reports_a_draw():
    schedule = {"events": [game("2026-11-01T02:00Z", "1", "1")]}
    assert teams.last_result(team(), schedule, NOW) == "Drew 1–1 with Lakers."


def test_ignores_old_results():
    assert teams.last_result(team(), {"events": [game("2026-10-01T02:00Z", "2", "1")]}, NOW) is None


def test_next_game_uses_mountain_time_and_broadcast():
    event = {
        "date": "2026-11-05T02:00Z",
        "competitions": [
            {
                "competitors": [side("1", "Jazz", "home"), side("2", "Kings", "away")],
                "broadcasts": [{"media": {"shortName": "KJZZ"}}],
            }
        ],
    }
    assert teams.next_game(team([event])) == "Wed 7:00 PM vs Kings, KJZZ"


def test_off_season_still_builds():
    built = teams.build(META, {"team": team(record=None)}, {"events": []}, NOW)
    assert built["update"] == "No recent games."
    assert built["next"] == "No game scheduled"
