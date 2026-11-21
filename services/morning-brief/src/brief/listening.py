"""Yesterday's listening and five soundtrack picks for today, from the spotify_stats snapshot in S3.

The picks mix three ways of finding something:
- Unexplored corner: an album by an artist you've explored that you've barely played, or an artist
  you've barely played in a genre you play a lot.
- New release: out in the last few weeks from an artist you play a lot.
- Back in rotation: an album you played a lot and haven't played in months.

The first two need the Spotify API. If it fails, the picks fall back to albums back in rotation.
Nothing suggested in the last three weeks comes back, and the daily choice is seeded by the date,
so a rerun of the same day gives the same picks.
"""

import gzip
import json
import logging
import os
import random
import re
from collections import defaultdict
from collections.abc import Callable
from datetime import date, datetime, time, timedelta, timezone

import boto3

from brief import config, store
from brief.spotify import Spotify

logger = logging.getLogger(__name__)

SNAPSHOT_KEY = "data/snapshot.json"
MS_PER_HOUR = 60 * 60 * 1000
MS_PER_MINUTE = 60 * 1000

SUGGESTIONS = 5
# The order picks fill in. A kind that comes up short is filled by the others.
MIX = ["corner", "new", "rotation", "corner", "new"]
REPEAT_DAYS = 21

LAPSED_DAYS = 180
MIN_ALBUM_HOURS = 3
MIN_ALBUM_TRACKS = 3
CANDIDATES = 30

# An album counts as explored once it's had this much listening.
EXPLORED_MINUTES = 20
CORNER_MIN_HOURS = 5
CORNER_POOL = 40
CORNER_ARTISTS = 5
GENRE_ARTISTS = 10
GENRE_POOL = 5
UNKNOWN_ARTIST_MINUTES = 60

FAN_ARTISTS = 20
FAN_YEARS = 2
NEW_DAYS = 45
EP_TRACKS = 4

EDITION = re.compile(r"\s*(\(|\[| - ).*$")
SKIP_TITLES = re.compile(r"\b(live|greatest hits|best of|remix(es)?|commentary|karaoke)\b", re.I)


def load_snapshot() -> dict:
    body = boto3.client("s3").get_object(Bucket=os.environ["SPOTIFY_BUCKET"], Key=SNAPSHOT_KEY)["Body"].read()
    # S3 hands back the stored bytes, gzipped, whatever ContentEncoding says.
    return json.loads(gzip.decompress(body))


def utc_stamp(day: date) -> str:
    start = datetime.combine(day, time.min, tzinfo=config.TIMEZONE).astimezone(timezone.utc)
    return start.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def top(totals: dict[str, int]) -> str:
    return max(totals, key=lambda key: (totals[key], key)) if totals else ""


def base_title(name: str) -> str:
    """"Currents (Deluxe)" and "Currents - Remastered" are both "currents"."""
    return EDITION.sub("", name).strip().lower() or name.lower()


def pick_key(title: str, artist: str) -> tuple[str, str]:
    return base_title(title), artist.lower()


def hours(ms: int) -> int:
    return max(1, round(ms / MS_PER_HOUR))


def names(items: list[str]) -> str:
    return items[0] if len(items) == 1 else f"{', '.join(items[:-1])} and {items[-1]}"


def yesterday(snapshot: dict, today: date) -> dict:
    start, end = utc_stamp(today - timedelta(days=1)), utc_stamp(today)
    played, artists, songs = 0, defaultdict(int), defaultdict(int)
    for played_at, track_index, duration, *_ in snapshot["listens"]:
        if start <= played_at < end:
            _, name, _, track_artists, *_ = snapshot["tracks"][track_index]
            played += duration
            artists[track_artists[0]] += duration
            songs[name] += duration
    return {"minutes": round(played / 60000), "topArtist": top(artists), "topSong": top(songs)}


def history(snapshot: dict, today: date) -> dict:
    """Listening by album and by lead artist."""
    recent_cutoff = utc_stamp(today - timedelta(days=365 * FAN_YEARS))
    albums: dict = defaultdict(lambda: {"played": 0, "last": "", "tracks": defaultdict(int), "years": defaultdict(int)})
    artists: dict = defaultdict(lambda: {"played": 0, "recent": 0, "albums": defaultdict(int), "tracks": defaultdict(int)})
    for played_at, track_index, duration, *_ in snapshot["listens"]:
        track_id, _, album, track_artists, *_ = snapshot["tracks"][track_index]
        artist = track_artists[0]
        entry = albums[(album, artist)]
        entry["played"] += duration
        entry["last"] = max(entry["last"], played_at)
        entry["tracks"][track_id] += duration
        entry["years"][played_at[:4]] += duration
        if artist.startswith("Unknown"):
            continue
        fan = artists[artist]
        fan["played"] += duration
        fan["recent"] += duration if played_at >= recent_cutoff else 0
        fan["albums"][album] += duration
        fan["tracks"][track_id] += duration
    return {"albums": albums, "artists": artists}


def album_played(fan: dict, title: str) -> int:
    base = base_title(title)
    return sum(ms for album, ms in fan["albums"].items() if base_title(album) == base)


def rotation(stats: dict, today: date) -> list[dict]:
    """Albums played a lot in the past and not lately, biggest first."""
    cutoff = utc_stamp(today - timedelta(days=LAPSED_DAYS))
    lapsed = sorted(
        (
            (key, entry)
            for key, entry in stats["albums"].items()
            if entry["last"] < cutoff
            and entry["played"] >= MIN_ALBUM_HOURS * MS_PER_HOUR
            and len(entry["tracks"]) >= MIN_ALBUM_TRACKS
            and not key[0].startswith("Unknown")
        ),
        key=lambda item: (-item[1]["played"], item[0]),
    )[:CANDIDATES]
    picks = []
    for (album, artist), entry in lapsed:
        last = datetime.fromisoformat(entry["last"].replace("Z", "+00:00"))
        picks.append(
            {
                "kind": "Back in rotation",
                "title": album,
                "artist": artist,
                "why": f"You played it for {hours(entry['played'])} hours, mostly in {top(entry['years'])}, and not since {last:%B %Y}.",
                "url": f"https://open.spotify.com/track/{top(entry['tracks'])}",
            }
        )
    return picks


class Artists:
    """Spotify ids for snapshot artists, found through each one's most-played track."""

    def __init__(self, spotify, stats: dict) -> None:
        self.spotify, self.stats, self.ids = spotify, stats, {}

    def id(self, name: str) -> str:
        if name not in self.ids:
            self.ids[name] = self.spotify.track_artist(top(self.stats["artists"][name]["tracks"]))["id"]
        return self.ids[name]


def album_url(album_id: str) -> str:
    return f"https://open.spotify.com/album/{album_id}"


def artist_corners(stats: dict, spotify, artists: Artists, rng: random.Random) -> list[dict]:
    """Albums you've barely played by artists whose other albums you know well."""
    explored = EXPLORED_MINUTES * MS_PER_MINUTE
    pool = [
        name
        for name, fan in sorted(stats["artists"].items(), key=lambda item: -item[1]["played"])
        if fan["played"] >= CORNER_MIN_HOURS * MS_PER_HOUR
        and len({base_title(album) for album, ms in fan["albums"].items() if ms >= explored}) >= 2
    ][:CORNER_POOL]
    picks = []
    for name in rng.sample(pool, min(CORNER_ARTISTS, len(pool))):
        fan = stats["artists"][name]
        unplayed, seen = [], set()
        for album in spotify.discography(artists.id(name), name):
            base = base_title(album["name"])
            if album["type"] != "album" or base in seen or SKIP_TITLES.search(album["name"]):
                continue
            seen.add(base)
            if album_played(fan, album["name"]) < explored:
                unplayed.append(album)
        if not unplayed:
            continue
        album = rng.choice(unplayed)
        known = sorted(fan["albums"], key=lambda title: -fan["albums"][title])[:3]
        picks.append(
            {
                "kind": "Unexplored corner",
                "title": album["name"],
                "artist": name,
                "why": f"You've spent {hours(fan['played'])} hours with {name}, mostly on {names(known)}, but barely touched this one.",
                "url": album_url(album["id"]),
            }
        )
    return picks


def genre_corners(stats: dict, spotify, artists: Artists, rng: random.Random) -> list[dict]:
    """Artists you've barely played in the genres you play most."""
    leaders = sorted(stats["artists"], key=lambda name: -stats["artists"][name]["played"])[:GENRE_ARTISTS]
    weight: dict[str, int] = defaultdict(int)
    fans: dict[str, list[str]] = defaultdict(list)
    for name in leaders:
        for genre in spotify.genres(artists.id(name)):
            weight[genre] += stats["artists"][name]["played"]
            fans[genre].append(name)
    genres = sorted(weight, key=lambda genre: (-weight[genre], genre))[:GENRE_POOL]
    rng.shuffle(genres)
    known = {name.lower(): fan["played"] for name, fan in stats["artists"].items()}
    picks = []
    for genre in genres:
        for found in spotify.genre_artists(genre):
            if known.get(found["name"].lower(), 0) >= UNKNOWN_ARTIST_MINUTES * MS_PER_MINUTE:
                continue
            albums = [
                album
                for album in spotify.discography(found["id"], found["name"])
                if album["type"] == "album" and not SKIP_TITLES.search(album["name"])
            ]
            if not albums:
                continue
            album = albums[0]
            picks.append(
                {
                    "kind": "Unexplored corner",
                    "title": album["name"],
                    "artist": found["name"],
                    "why": f"You play a lot of {genre}, mostly {names(fans[genre][:2])}, and almost none of {found['name']}.",
                    "url": album_url(album["id"]),
                }
            )
            break
    return picks


def released(text: str) -> date | None:
    try:
        return date.fromisoformat(text)
    except ValueError:
        return None  # Year or month precision only, so not a recent release we can date.


def new_releases(stats: dict, spotify, artists: Artists, today: date) -> list[dict]:
    """Albums and EPs out in the last few weeks from the artists you play most, newest first."""
    fans = sorted(
        (name for name, fan in stats["artists"].items() if fan["recent"] > 0),
        key=lambda name: -stats["artists"][name]["recent"],
    )[:FAN_ARTISTS]
    found = []
    for name in fans:
        fan = stats["artists"][name]
        for album in spotify.discography(artists.id(name), name):
            day = released(album["released"])
            if not day or not today - timedelta(days=NEW_DAYS) <= day <= today:
                continue
            if album["type"] != "album" and album["tracks"] < EP_TRACKS:
                continue
            if album_played(fan, album["name"]) >= EXPLORED_MINUTES * MS_PER_MINUTE:
                continue
            label = "album" if album["type"] == "album" else "EP"
            found.append(
                (
                    day,
                    {
                        "kind": "New release",
                        "title": album["name"],
                        "artist": name,
                        "why": f"A new {label} out {day:%B} {day.day}. You've played {name} for {hours(fan['played'])} hours.",
                        "url": album_url(album["id"]),
                    },
                )
            )
    found.sort(key=lambda item: item[0], reverse=True)
    return [pick for _, pick in found]


def safely(label: str, find: Callable[[], list[dict]]) -> list[dict]:
    try:
        return find()
    except Exception:
        logger.exception("Finding %s failed", label)
        return []


def mix(pools: dict[str, list[dict]], skip: set[tuple[str, str]]) -> list[dict]:
    """Up to SUGGESTIONS picks in MIX order, one per artist, none suggested lately."""
    queues = {kind: list(picks) for kind, picks in pools.items()}
    used, artists, chosen = set(skip), set(), []

    def take(kind: str) -> bool:
        queue = queues.get(kind, [])
        while queue:
            pick = queue.pop(0)
            key = pick_key(pick["title"], pick["artist"])
            if key in used or pick["artist"].lower() in artists:
                continue
            used.add(key)
            artists.add(pick["artist"].lower())
            chosen.append(pick)
            return True
        return False

    for kind in MIX:
        if len(chosen) < SUGGESTIONS and not take(kind):
            for other in MIX:
                if take(other):
                    break
    while len(chosen) < SUGGESTIONS and any(take(kind) for kind in dict.fromkeys(MIX)):
        pass
    return chosen


def soundtracks(snapshot: dict, today: date, spotify=None, recent: set[tuple[str, str]] = frozenset()) -> list[dict]:
    stats = history(snapshot, today)
    rng = random.Random(today.toordinal())
    back = rotation(stats, today)
    rng.shuffle(back)
    pools = {"rotation": back}
    if spotify is not None:
        artists = Artists(spotify, stats)
        corners = safely("artist corners", lambda: artist_corners(stats, spotify, artists, rng))
        by_genre = safely("genre corners", lambda: genre_corners(stats, spotify, artists, rng))
        # Alternate the two kinds of corner so a day gets one of each when it can.
        pools["corner"] = [pick for index in range(max(len(corners), len(by_genre))) for pick in (corners[index : index + 1] + by_genre[index : index + 1])]
        pools["new"] = safely("new releases", lambda: new_releases(stats, spotify, artists, today))
    picks = mix(pools, set(recent))
    if not picks:
        raise ValueError("nothing to suggest from the listening history")
    return picks


def recently_suggested(today: date) -> set[tuple[str, str]]:
    keys = set()
    for brief in store.since((today - timedelta(days=REPEAT_DAYS)).isoformat()):
        if brief.get("date") == today.isoformat():
            continue  # A rerun of today keeps today's picks.
        listening = brief.get("listening") or {}
        for pick in listening.get("soundtracks") or [listening.get("soundtrack") or {}]:
            if pick.get("title") and pick.get("artist"):
                keys.add(pick_key(pick["title"], pick["artist"]))
    return keys


def fetch(today: date) -> dict:
    snapshot = load_snapshot()
    spotify = None
    if not os.environ.get("SPOTIFY_REFRESH_TOKEN"):
        logger.warning("No Spotify credentials; suggesting albums back in rotation only")
    else:
        try:
            spotify = Spotify()
        except Exception:
            logger.exception("Connecting to Spotify failed; suggesting albums back in rotation only")
    recent: set[tuple[str, str]] = set()
    try:
        recent = recently_suggested(today)
    except Exception:
        logger.exception("Reading recent suggestions failed")
    return {"yesterday": yesterday(snapshot, today), "soundtracks": soundtracks(snapshot, today, spotify, recent)}
