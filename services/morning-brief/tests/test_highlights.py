from datetime import datetime, timezone

from brief import highlights, scores


def team(display, short=None, name=None):
    return {"displayName": display, "shortDisplayName": short or display, "name": name or short or display}


def game(away, home, start="2026-11-20T01:00Z"):
    return {
        "away": {"name": away["shortDisplayName"]},
        "home": {"name": home["shortDisplayName"]},
        "_match": {"names": [highlights.aliases(away), highlights.aliases(home)], "start": highlights.parse_time(start)},
    }


KNICKS = team("New York Knicks", "Knicks")
WOLVES = team("Minnesota Timberwolves", "Timberwolves")
COLTS = team("Indianapolis Colts", "Colts")
TEXANS = team("Houston Texans", "Texans")


def video(title, published="2026-11-20T04:00:00Z", rank=0, video_id="v"):
    return {"id": video_id, "title": title, "published": published, "rank": rank}


def test_matches_real_league_titles():
    assert highlights.matches("EXTENDED: KNICKS at TIMBERWOLVES | FULL GAME HIGHLIGHTS | November 19, 2026", game(KNICKS, WOLVES))
    assert highlights.matches("Indianapolis Colts vs Houston Texans Game Highlights | 2026 NFL Season Week 11", game(COLTS, TEXANS))
    assert highlights.matches("Stars vs. Knights | NHL Highlights | Nov 19, 2026", game(team("Dallas Stars", "Stars"), team("Vegas Golden Knights", "Golden Knights", "Knights")))
    assert highlights.matches(
        "MAXI SINTESI FROSINONE-SASSUOLO 4-2 | EXTENDED HIGHLIGHTS | SERIE A ENILIVE 2026/27",
        game(team("Frosinone"), team("Sassuolo")),
    )


def test_club_prefixes_and_accents_dont_block_a_match():
    atleti = team("Atlético Madrid", "Atlético")
    assert highlights.matches("Atletico Madrid vs. Sevilla | LALIGA Highlights", game(atleti, team("Sevilla FC", "Sevilla")))


def test_rejects_clips_previews_and_other_games():
    knicks_wolves = game(KNICKS, WOLVES)
    assert not highlights.matches("KAT Gets Real About His Love for Minnesota, Then Delivers a COLD Knicks Quote", knicks_wolves)
    assert not highlights.matches("LIVE 🔴 Knicks vs Timberwolves highlights", knicks_wolves)
    assert not highlights.matches("Knicks vs Celtics Full Game Highlights", knicks_wolves)
    assert not highlights.matches(
        "PARMA-ROMA 2-3 | CLASSIC HIGHLIGHTS SERIE A 2025/26", game(team("Parma"), team("AS Roma", "Roma"))
    )


def test_best_prefers_the_official_long_version_posted_after_the_game():
    knicks_wolves = game(KNICKS, WOLVES)
    videos = [
        video("Knicks vs Timberwolves highlights", rank=1, video_id="broadcaster"),
        video("KNICKS at TIMBERWOLVES | HIGHLIGHTS", video_id="short"),
        video("EXTENDED: KNICKS at TIMBERWOLVES | FULL GAME HIGHLIGHTS", video_id="long"),
        video("EXTENDED: KNICKS at TIMBERWOLVES | FULL GAME HIGHLIGHTS", published="2026-03-01T00:00:00Z", video_id="old"),
    ]
    assert highlights.best(videos, knicks_wolves)["id"] == "long"
    assert highlights.best(videos[-1:], knicks_wolves) is None


class FakeYouTube:
    def __init__(self, uploads, found=()):
        self.channel_videos, self.found, self.searched = uploads, list(found), []

    def uploads(self, _channel, _since, rank):
        return [{**item, "rank": rank} for item in self.channel_videos]

    def search(self, game):
        self.searched.append(game["away"]["name"])
        return self.found


def test_find_searches_only_for_games_the_channels_missed():
    groups = [{"league": "nba", "games": [game(KNICKS, WOLVES), game(team("Boston Celtics", "Celtics"), team("Miami Heat", "Heat"))]}]
    youtube = FakeYouTube(
        [video("KNICKS at TIMBERWOLVES | FULL GAME HIGHLIGHTS", video_id="k")],
        found=[video("Celtics vs Heat highlights", rank=99, video_id="c")],
    )
    highlights.find(groups, youtube)
    assert [g.get("highlights") for g in groups[0]["games"]] == [
        "https://www.youtube.com/watch?v=k",
        "https://www.youtube.com/watch?v=c",
    ]
    assert youtube.searched == ["Celtics"]


def test_attach_without_a_key_still_removes_matching_details(monkeypatch):
    monkeypatch.delenv("YOUTUBE_API_KEY", raising=False)
    groups = [{"league": "nba", "games": [game(KNICKS, WOLVES)]}]
    highlights.attach(groups)
    assert "_match" not in groups[0]["games"][0]
    assert "highlights" not in groups[0]["games"][0]


def test_scores_carry_match_details_from_espn():
    event = {
        "date": "2026-11-20T01:00Z",
        "status": {"type": {"completed": True, "shortDetail": "Final"}},
        "competitions": [
            {
                "competitors": [
                    {"homeAway": "home", "score": "110", "team": {"abbreviation": "MIN", **WOLVES}},
                    {"homeAway": "away", "score": "104", "team": {"abbreviation": "NY", **KNICKS}},
                ]
            }
        ],
    }
    [parsed] = scores.parse_games({"events": [event]}, "nba", None)
    assert parsed["_match"]["start"] == datetime(2026, 11, 20, 1, tzinfo=timezone.utc)
    assert "knicks" in parsed["_match"]["names"][0]
    assert "_team" not in parsed["home"]


def test_the_api_key_never_goes_in_a_url(monkeypatch):
    calls = []
    monkeypatch.setattr(highlights, "get_json", lambda url, params=None, headers=None: calls.append((url, params, headers)) or {"items": []})
    youtube = highlights.YouTube("secret")
    youtube.uploads("UCabc", datetime(2026, 11, 19, tzinfo=timezone.utc), 0)
    youtube.search(game(KNICKS, WOLVES))
    assert all("secret" not in url and "secret" not in str(params) and headers["X-Goog-Api-Key"] == "secret" for url, params, headers in calls)
