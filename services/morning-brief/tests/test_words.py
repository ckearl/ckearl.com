from datetime import date, timedelta
from pathlib import Path

from brief import words

FEED = (Path(__file__).parent / "fixtures" / "wotd.xml").read_text(encoding="utf-8")


def test_parses_a_real_wiktionary_item():
    english = words.parse_english(FEED, date(2026, 10, 31))
    assert english["word"] == "walking corpse syndrome"
    assert english["partOfSpeech"] == "noun"
    assert len(english["definition"]) > 20
    assert "<" not in english["definition"]


def test_falls_back_to_the_newest_item():
    assert words.parse_english(FEED, date(2027, 1, 1))["word"] == "walking corpse syndrome"


def test_korean_word_has_every_field():
    word = words.korean_for(date(2026, 11, 2))
    assert set(word) == {"word", "hanja", "meaning", "chain"}


def test_korean_word_is_stable_and_changes_daily():
    day = date(2026, 11, 2)
    assert words.korean_for(day) == words.korean_for(day)
    assert words.korean_for(day) != words.korean_for(day + timedelta(days=1))
