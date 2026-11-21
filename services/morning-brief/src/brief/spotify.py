"""The Spotify Web API, read-only, for discographies and new releases.

Uses the spotify_stats app's client and refresh token. Development-mode apps get small pages
(10 items at most) and some endpoints are gone, so every call pages by 10 and the discography
falls back to search when the artist-albums endpoint refuses.
"""

import os

import requests

from brief.http import TIMEOUT

API = "https://api.spotify.com/v1"
TOKEN_URL = "https://accounts.spotify.com/api/token"
PAGE = 10
MAX_PAGES = 5


class Spotify:
    def __init__(self) -> None:
        response = requests.post(
            TOKEN_URL,
            data={"grant_type": "refresh_token", "refresh_token": os.environ["SPOTIFY_REFRESH_TOKEN"]},
            auth=(os.environ["SPOTIFY_CLIENT_ID"], os.environ["SPOTIFY_CLIENT_SECRET"]),
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {response.json()['access_token']}"

    def _get(self, path: str, params: dict | None = None) -> dict:
        response = self.session.get(f"{API}{path}", params=params, timeout=TIMEOUT)
        response.raise_for_status()
        return response.json()

    def _pages(self, path: str, params: dict, key: str | None = None) -> list[dict]:
        items: list[dict] = []
        for page in range(MAX_PAGES):
            body = self._get(path, {**params, "limit": PAGE, "offset": page * PAGE})
            block = body[key] if key else body
            items += [item for item in block.get("items") or [] if item]
            if not block.get("next"):
                break
        return items

    def track_artist(self, track_id: str) -> dict:
        """The track's first artist as {"id", "name"}, plus its album id."""
        track = self._get(f"/tracks/{track_id}")
        return {"id": track["artists"][0]["id"], "name": track["artists"][0]["name"], "album": track["album"]["id"]}

    def genres(self, artist_id: str) -> list[str]:
        return self._get(f"/artists/{artist_id}").get("genres") or []

    def discography(self, artist_id: str, name: str) -> list[dict]:
        """Albums and EPs led by this artist: {"id", "name", "type", "tracks", "released"}."""
        try:
            items = self._pages(f"/artists/{artist_id}/albums", {"include_groups": "album,single"})
        except requests.HTTPError as error:
            if error.response is None or error.response.status_code not in (400, 403, 404):
                raise
            items = self._pages("/search", {"q": f'artist:"{name}"', "type": "album"}, "albums")
        return [
            {
                "id": item["id"],
                "name": item["name"],
                "type": item.get("album_type", "album"),
                "tracks": item.get("total_tracks") or 0,
                "released": item.get("release_date") or "",
            }
            for item in items
            if item.get("artists") and item["artists"][0]["id"] == artist_id
        ]

    def genre_artists(self, genre: str) -> list[dict]:
        body = self._get("/search", {"q": f'genre:"{genre}"', "type": "artist", "limit": PAGE})
        return [{"id": item["id"], "name": item["name"]} for item in body["artists"]["items"] if item]
