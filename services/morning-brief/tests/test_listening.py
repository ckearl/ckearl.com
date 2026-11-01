from datetime import date

import pytest

from brief import listening

HOUR = listening.MS_PER_HOUR


def snapshot(*listens):
    return {
        "tracks": [
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
    assert listening.yesterday(data, date(2026, 11, 2)) == {"minutes": 4, "topArtist": "Other", "topSong": "New Song"}


def test_yesterday_with_no_listening():
    assert listening.yesterday(snapshot(), date(2026, 11, 2))["minutes"] == 0


def test_soundtrack_picks_a_lapsed_album_and_explains_it():
    data = snapshot(
        ("2021-03-01T00:00:00.000Z", 0, 2 * HOUR),
        ("2021-04-01T00:00:00.000Z", 1, 2 * HOUR),
        ("2022-02-01T00:00:00.000Z", 2, HOUR),
        ("2026-10-30T00:00:00.000Z", 3, 9 * HOUR),
    )
    pick = listening.soundtrack(data, date(2026, 11, 2))
    assert pick["title"] == "Old Album"
    assert pick["artist"] == "Band"
    assert pick["why"] == "You played it for 5 hours, mostly in 2021, and not since February 2022."
    assert pick["url"] == "https://open.spotify.com/track/t2"


def test_soundtrack_skips_recent_and_barely_played_albums():
    data = snapshot(
        ("2026-10-30T00:00:00.000Z", 3, 9 * HOUR),
        ("2021-01-01T00:00:00.000Z", 4, 9 * HOUR),
    )
    with pytest.raises(ValueError):
        listening.soundtrack(data, date(2026, 11, 2))
