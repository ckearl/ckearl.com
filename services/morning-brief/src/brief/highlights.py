"""A YouTube highlights video for each score, from the YouTube Data API.

Each league's official channel (and a US broadcaster's, for soccer) is read first: an uploads page
costs 1 unit of the 10,000 a day. A game with no match there gets one YouTube search, at 100 units,
up to MAX_SEARCHES a day. A video only counts if its title names both teams and says it's
highlights, and it went up within a few days after the start. Otherwise the game has no video.
"""

import logging
import os
import re
import unicodedata
from datetime import datetime, timedelta

from brief.http import HEADERS, get_json

logger = logging.getLogger(__name__)

API = "https://www.googleapis.com/youtube/v3"
MAX_PAGES = 6
MAX_SEARCHES = 25
POSTED_WITHIN = timedelta(days=4)

# Official channel first, then a broadcaster that posts the same games in the US.
CHANNELS = {
    "nba": ["UCWJ2lWNubArHWmf3FIHbfcQ"],  # NBA
    "nfl": ["UCDVYQ4Zhbm3S2dlz7P1GBDg"],  # NFL
    "nhl": ["UCqFMzb-4AUf6WAIbl132QKA"],  # NHL
    "mlb": ["UCoLrcjPV5PbUrUyXq5mjc_A"],  # MLB
    "epl": ["UCqZQlzSHbVJrwrn5XvzrzcA", "UCG5qGWdu8nIRZqJ_GgDwQ-w"],  # NBC Sports, Premier League
    "ucl": ["UCET00YnetHT7tOpu12v8jxg"],  # CBS Sports Golazo
    "laliga": ["UCTv-XvfzLX3i4IGWAm4sbmA", "UC6c1z7bA__85CIWZ_jpCK-Q"],  # LALIGA, ESPN FC
    "seriea": ["UCBJeMCIeLQos7wacox4hmLQ", "UCET00YnetHT7tOpu12v8jxg"],  # Serie A, CBS Sports Golazo
    "bundesliga": ["UC6UL29enLNe4mqwTfAyeNuw"],  # Bundesliga
    "ligue1": ["UCQsH5XtIc9hONE1BQjucM0g"],  # Ligue 1
}

# Words that mark a recap, in English, Italian, Spanish and French.
RECAP = re.compile(r"\b(highlights?|sintesi|resumen|resume)\b")
# Long versions, preferred when a game has more than one.
LONG = re.compile(r"\b(extended|full game highlights|maxi sintesi)\b")
NOT_RECAP = re.compile(r"\b(live|pre match|preview|classic|reaction|shorts?|every (throw|catch|play))\b")
CLUB_WORDS = {"fc", "cf", "ac", "as", "sc", "ss", "ssc", "afc", "rc", "rcd", "cd", "ud", "sd", "sv", "vfb", "vfl", "tsg", "1"}


def plain(text: str) -> str:
    """Lowercase, no accents, words separated by single spaces, padded so " word " matches."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return f" {' '.join(re.findall(r'[a-z0-9]+', text))} "


def aliases(team: dict) -> set[str]:
    """The ways a title might name an ESPN team: "Memphis Grizzlies", "Grizzlies", "Napoli"."""
    found = set()
    for key in ("displayName", "shortDisplayName", "name"):
        words = plain(team.get(key) or "").split()
        for variant in (words, [word for word in words if word not in CLUB_WORDS]):
            if len(" ".join(variant)) >= 3:
                found.add(" ".join(variant))
    return found


def matches(title: str, game: dict) -> bool:
    text = plain(title)
    names = game["_match"]["names"]
    return (
        bool(RECAP.search(text))
        and not NOT_RECAP.search(text)
        and all(any(f" {alias} " in text for alias in side) for side in names)
    )


def posted_in_time(published: str, game: dict) -> bool:
    start = game["_match"]["start"]
    return start <= parse_time(published) <= start + POSTED_WITHIN


def parse_time(stamp: str) -> datetime:
    return datetime.fromisoformat(stamp.replace("Z", "+00:00"))


def best(videos: list[dict], game: dict) -> dict | None:
    """The first channel's long version, else its recap, else the next channel's."""
    found = [video for video in videos if posted_in_time(video["published"], game) and matches(video["title"], game)]
    found.sort(key=lambda video: (video["rank"], not LONG.search(plain(video["title"]))))
    return found[0] if found else None


def watch_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


class YouTube:
    def __init__(self, key: str) -> None:
        # In a header, not the URL, so a logged request error can't include the key.
        self.headers = {**HEADERS, "X-Goog-Api-Key": key}
        self.searches = 0

    def uploads(self, channel: str, since: datetime, rank: int) -> list[dict]:
        """The channel's uploads, newest first, back to `since`."""
        videos, token = [], None
        for _ in range(MAX_PAGES):
            params = {"part": "snippet", "playlistId": "UU" + channel[2:], "maxResults": 50}
            body = get_json(f"{API}/playlistItems", {**params, **({"pageToken": token} if token else {})}, self.headers)
            for item in body.get("items", []):
                snippet = item["snippet"]
                videos.append(
                    {"id": snippet["resourceId"]["videoId"], "title": snippet["title"], "published": snippet["publishedAt"], "rank": rank}
                )
            token = body.get("nextPageToken")
            if not token or (videos and parse_time(videos[-1]["published"]) < since):
                break
        return videos

    def search(self, game: dict) -> list[dict]:
        if self.searches >= MAX_SEARCHES:
            return []
        self.searches += 1
        start = game["_match"]["start"]
        body = get_json(
            f"{API}/search",
            {
                "part": "snippet",
                "type": "video",
                "maxResults": 10,
                "q": f"{game['away']['name']} vs {game['home']['name']} highlights",
                "publishedAfter": start.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "publishedBefore": (start + POSTED_WITHIN).strftime("%Y-%m-%dT%H:%M:%SZ"),
            },
            self.headers,
        )
        return [
            {"id": item["id"]["videoId"], "title": item["snippet"]["title"], "published": item["snippet"]["publishedAt"], "rank": 99}
            for item in body.get("items", [])
            if item.get("id", {}).get("videoId")
        ]


def find(groups: list[dict], youtube: YouTube) -> None:
    """Sets "highlights" on each game that has a video."""
    for group in groups:
        games = [game for game in group["games"] if "_match" in game]
        if not games:
            continue
        since = min(game["_match"]["start"] for game in games)
        videos: list[dict] = []
        for rank, channel in enumerate(CHANNELS.get(group["league"], [])):
            try:
                videos += youtube.uploads(channel, since, rank)
            except Exception:
                logger.exception("Reading YouTube channel %s failed", channel)
        for game in games:
            video = best(videos, game)
            if video is None:
                try:
                    video = best(youtube.search(game), game)
                except Exception:
                    logger.exception("YouTube search failed")
            if video:
                game["highlights"] = watch_url(video["id"])


def attach(groups: list[dict]) -> None:
    """Adds highlights where it can, and always removes the matching details."""
    try:
        key = os.environ.get("YOUTUBE_API_KEY")
        if key:
            find(groups, YouTube(key))
        else:
            logger.warning("No YOUTUBE_API_KEY; scores have no highlights")
    except Exception:
        logger.exception("Finding highlights failed")
    finally:
        for group in groups:
            for game in group["games"]:
                game.pop("_match", None)
