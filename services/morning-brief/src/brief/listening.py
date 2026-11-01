"""Yesterday's listening and a lapsed album, from the spotify_stats snapshot in S3."""

import gzip
import json
import os
from collections import defaultdict
from datetime import date, datetime, time, timedelta, timezone

import boto3

from brief import config

SNAPSHOT_KEY = "data/snapshot.json"
LAPSED_DAYS = 180
MIN_ALBUM_HOURS = 3
MIN_ALBUM_TRACKS = 3
CANDIDATES = 30
MS_PER_HOUR = 60 * 60 * 1000


def load_snapshot() -> dict:
    body = boto3.client("s3").get_object(Bucket=os.environ["SPOTIFY_BUCKET"], Key=SNAPSHOT_KEY)["Body"].read()
    # S3 hands back the stored bytes, gzipped, whatever ContentEncoding says.
    return json.loads(gzip.decompress(body))


def utc_stamp(day: date) -> str:
    start = datetime.combine(day, time.min, tzinfo=config.TIMEZONE).astimezone(timezone.utc)
    return start.strftime("%Y-%m-%dT%H:%M:%S.000Z")


def top(totals: dict[str, int]) -> str:
    return max(totals, key=lambda key: (totals[key], key)) if totals else ""


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


def soundtrack(snapshot: dict, today: date) -> dict:
    """An album played a lot in the past and not lately. Rotates daily through the biggest."""
    albums: dict = defaultdict(
        lambda: {"played": 0, "last": "", "tracks": defaultdict(int), "years": defaultdict(int)}
    )
    for played_at, track_index, duration, *_ in snapshot["listens"]:
        track_id, _, album, artists, *_ = snapshot["tracks"][track_index]
        entry = albums[(album, artists[0])]
        entry["played"] += duration
        entry["last"] = max(entry["last"], played_at)
        entry["tracks"][track_id] += duration
        entry["years"][played_at[:4]] += duration

    cutoff = utc_stamp(today - timedelta(days=LAPSED_DAYS))
    lapsed = sorted(
        (
            (key, entry)
            for key, entry in albums.items()
            if entry["last"] < cutoff
            and entry["played"] >= MIN_ALBUM_HOURS * MS_PER_HOUR
            and len(entry["tracks"]) >= MIN_ALBUM_TRACKS
            and not key[0].startswith("Unknown")
        ),
        key=lambda item: (-item[1]["played"], item[0]),
    )[:CANDIDATES]
    if not lapsed:
        raise ValueError("no lapsed album in the listening history")

    (album, artist), entry = lapsed[today.toordinal() % len(lapsed)]
    hours = round(entry["played"] / MS_PER_HOUR)
    last = datetime.fromisoformat(entry["last"].replace("Z", "+00:00"))
    return {
        "kind": "Back in rotation",
        "title": album,
        "artist": artist,
        "why": f"You played it for {hours} hours, mostly in {top(entry['years'])}, and not since {last:%B %Y}.",
        "url": f"https://open.spotify.com/track/{top(entry['tracks'])}",
    }


def fetch(today: date) -> dict:
    snapshot = load_snapshot()
    return {"yesterday": yesterday(snapshot, today), "soundtrack": soundtrack(snapshot, today)}
