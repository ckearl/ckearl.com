from datetime import date

import pytest

from brief import listening

HOUR = listening.MS_PER_HOUR
TODAY = date(2026, 11, 2)


def snapshot(*listens, tracks=None):
    return {
        "tracks": tracks
        or [
            ["t1", "Song One", "Old Album", ["Band"], 1, None],
            ["t2", "Song Two", "Old Album", ["Band"], 1, None],
            ["t3", "Song Three", "Old Album", ["Band"], 1, None],
            ["t4", "New Song", "New Album", ["Other"], 1, None],
            ["t5", "Short", "Small Album", ["Tiny"], 1, None],
        ],
        "listens": [[when, track, ms, None, None, None, None] for when, track, ms in listens],
    }


def test_yesterday_uses_mountain_time_day_boundaries():
    data = snapshot(
        ("2026-11-01T05:59:00.000Z", 0, 60000),  # 11:59 PM on Oct 31 in Denver
        ("2026-11-01T06:01:00.000Z", 3, 120000),  # 12:01 AM on Nov 1
        ("2026-11-01T20:00:00.000Z", 3, 60000),
        ("2026-11-01T20:30:00.000Z", 0, 60000),
        ("2026-11-02T07:01:00.000Z", 0, 60000),  # Nov 2, after clocks change
    )
    assert listening.yesterday(data, TODAY) == {"minutes": 4, "topArtist": "Other", "topSong": "New Song"}


def test_yesterday_with_no_listening():
    assert listening.yesterday(snapshot(), TODAY)["minutes"] == 0


def test_rotation_picks_a_lapsed_album_and_explains_it():
    data = snapshot(
        ("2021-03-01T00:00:00.000Z", 0, 2 * HOUR),
        ("2021-04-01T00:00:00.000Z", 1, 2 * HOUR),
        ("2022-02-01T00:00:00.000Z", 2, HOUR),
        ("2026-10-30T00:00:00.000Z", 3, 9 * HOUR),
    )
    [pick] = listening.soundtracks(data, TODAY)
    assert pick == {
        "kind": "Back in rotation",
        "title": "Old Album",
        "artist": "Band",
        "why": "You played it for 5 hours, mostly in 2021, and not since February 2022.",
        "url": "https://open.spotify.com/track/t2",
    }


def test_rotation_skips_recent_and_barely_played_albums():
    data = snapshot(
        ("2026-10-30T00:00:00.000Z", 3, 9 * HOUR),
        ("2021-01-01T00:00:00.000Z", 4, 9 * HOUR),
    )
    with pytest.raises(ValueError):
        listening.soundtracks(data, TODAY)


def test_base_title_ignores_editions():
    assert listening.base_title("Currents (Deluxe)") == "currents"
    assert listening.base_title("Currents - 2025 Remaster") == "currents"
    assert listening.base_title("Currents") == "currents"


class FakeSpotify:
    """Artists by lead track id: Band (b) and Other (o). Genre search finds Stranger (s)."""

    def __init__(self, albums, genres=None, genre_artists=None):
        self.albums, self.by_genre, self.found = albums, genres or {}, genre_artists or []

    def track_artist(self, track_id):
        return {"id": {"t1": "b", "t2": "b", "t3": "b", "t6": "b", "t4": "o", "t5": "l"}[track_id], "name": "", "album": ""}

    def discography(self, artist_id, _name):
        return self.albums.get(artist_id, [])

    def genres(self, artist_id):
        return self.by_genre.get(artist_id, [])

    def genre_artists(self, _genre):
        return self.found


def album(album_id, name, released="2015-01-01", kind="album", tracks=10):
    return {"id": album_id, "name": name, "type": kind, "tracks": tracks, "released": released}


TRACKS = [
    ["t1", "One", "Album A", ["Band"], 1, None],
    ["t2", "Two", "Album B (Deluxe)", ["Band"], 1, None],
    ["t3", "Three", "Album E", ["Band"], 1, None],
    ["t4", "Four", "Other Album", ["Other"], 1, None],
    ["t5", "Five", "Old Favorite", ["Lapsed"], 1, None],
    ["t6", "Six", "Album C", ["Band"], 1, None],
]


def fan_snapshot():
    return snapshot(
        ("2026-09-01T00:00:00.000Z", 0, 3 * HOUR),
        ("2026-09-02T00:00:00.000Z", 1, 3 * HOUR),
        ("2026-09-03T00:00:00.000Z", 2, 3 * HOUR),
        ("2026-09-04T00:00:00.000Z", 5, 5 * listening.MS_PER_MINUTE),  # A taste of Album C
        ("2026-10-01T00:00:00.000Z", 3, 2 * HOUR),
        ("2020-01-01T00:00:00.000Z", 4, 4 * HOUR),
        ("2020-01-02T00:00:00.000Z", 4, 4 * HOUR),
        tracks=TRACKS,
    )


def test_corner_suggests_an_album_the_artist_has_that_you_barely_played():
    spotify = FakeSpotify(
        {
            "b": [
                album("a", "Album A"),
                album("bb", "Album B"),
                album("c", "Album C"),
                album("e", "Album E"),
                album("live", "Live at the Hall"),
                album("single", "A Single", kind="single", tracks=1),
            ]
        }
    )
    stats = listening.history(fan_snapshot(), TODAY)
    picks = listening.artist_corners(stats, spotify, listening.Artists(spotify, stats), listening.random.Random(1))
    assert [pick["title"] for pick in picks] == ["Album C"]
    assert picks[0]["url"] == "https://open.spotify.com/album/c"
    assert picks[0]["why"].startswith("You've spent 9 hours with Band, mostly on ")


def test_genre_corner_finds_an_artist_you_barely_know_in_your_main_genre():
    spotify = FakeSpotify(
        {"s": [album("s1", "Stranger Debut")], "b": []},
        genres={"b": ["shoegaze"], "o": ["shoegaze", "dream pop"]},
        genre_artists=[{"id": "b", "name": "Band"}, {"id": "s", "name": "Stranger"}],
    )
    stats = listening.history(fan_snapshot(), TODAY)
    picks = listening.genre_corners(stats, spotify, listening.Artists(spotify, stats), listening.random.Random(1))
    assert picks[0]["artist"] == "Stranger"
    assert picks[0]["title"] == "Stranger Debut"
    assert picks[0]["why"].startswith(("You play a lot of shoegaze", "You play a lot of dream pop"))


def test_new_releases_are_recent_unplayed_albums_or_eps_from_artists_you_play():
    spotify = FakeSpotify(
        {
            "b": [
                album("n1", "Fresh LP", released="2026-10-20"),
                album("n2", "Fresh EP", released="2026-10-28", kind="single", tracks=5),
                album("n3", "Fresh Single", released="2026-10-30", kind="single", tracks=1),
                album("n4", "Album A (Anniversary)", released="2026-10-29"),  # already played
                album("n5", "Too Old", released="2026-06-01"),
                album("n6", "Year Only", released="2026"),
            ]
        }
    )
    stats = listening.history(fan_snapshot(), TODAY)
    picks = listening.new_releases(stats, spotify, listening.Artists(spotify, stats), TODAY)
    assert [pick["title"] for pick in picks] == ["Fresh EP", "Fresh LP"]
    assert picks[0]["why"] == "A new EP out October 28. You've played Band for 9 hours."


def pick(kind, title, artist):
    return {"kind": kind, "title": title, "artist": artist, "why": "", "url": ""}


def test_mix_follows_the_order_one_per_artist_and_skips_recent_suggestions():
    pools = {
        "corner": [pick("c", "C1", "A"), pick("c", "C2", "B")],
        "new": [pick("n", "N1", "A"), pick("n", "N2", "C"), pick("n", "N3", "D")],
        "rotation": [pick("r", "R1", "E"), pick("r", "R2", "F"), pick("r", "R3", "G")],
    }
    chosen = listening.mix(pools, {("c2", "b")})
    assert [item["title"] for item in chosen] == ["C1", "N2", "R1", "N3", "R2"]


def test_mix_fills_from_other_kinds_when_one_runs_short():
    pools = {"rotation": [pick("r", f"R{n}", f"Artist {n}") for n in range(8)]}
    assert len(listening.mix(pools, set())) == 5


def test_soundtracks_survive_a_failing_spotify_source(monkeypatch):
    monkeypatch.setattr(listening, "MIN_ALBUM_TRACKS", 1)

    class Broken(FakeSpotify):
        def genres(self, artist_id):
            raise RuntimeError("gone")

    spotify = Broken({"b": [album("c", "Album C")]})
    picks = listening.soundtracks(fan_snapshot(), TODAY, spotify)
    kinds = [item["kind"] for item in picks]
    assert kinds == ["Unexplored corner", "Back in rotation"]


def test_soundtracks_are_the_same_for_a_rerun_of_the_day():
    spotify = FakeSpotify({"b": [album("c", "Album C"), album("n", "New", released="2026-10-30")]})
    first = listening.soundtracks(fan_snapshot(), TODAY, spotify)
    assert first == listening.soundtracks(fan_snapshot(), TODAY, spotify)


def test_recently_suggested_reads_both_brief_shapes(monkeypatch):
    briefs = [
        {"date": "2026-10-20", "listening": {"soundtrack": {"title": "Old (Deluxe)", "artist": "X"}}},
        {"date": "2026-11-01", "listening": {"soundtracks": [{"title": "New", "artist": "Y"}]}},
        {"date": "2026-11-02", "listening": {"soundtracks": [{"title": "Today", "artist": "Z"}]}},
    ]
    monkeypatch.setattr(listening.store, "since", lambda _day: briefs)
    assert listening.recently_suggested(TODAY) == {("old", "x"), ("new", "y")}
