from datetime import date, timedelta
from pathlib import Path
from xml.sax.saxutils import escape

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


def test_skips_a_definition_that_is_only_a_label():
    body = (
        '<span id="WOTD-rss-title">synecdoche</span></b> <i>n</i>'
        '<div id="WOTD-rss-description"><ol><li><span>(</span><a href="/wiki/rhetoric">rhetoric</a><span>)</span>\n'
        "<ol><li><span>(uncountable)</span> The use of a single part of a concept.</li></ol></li></ol></div>"
    )
    xml = f"<rss><channel><item><title>Word</title><description>{escape(body)}</description></item></channel></rss>"
    assert words.parse_english(xml, date(2026, 11, 1))["definition"] == "(uncountable) The use of a single part of a concept."


def test_korean_word_has_every_field():
    word = words.korean_for(date(2026, 11, 2))
    assert set(word) == {"word", "hanja", "meaning", "chain"}


def test_korean_word_is_stable_and_changes_daily():
    day = date(2026, 11, 2)
    assert words.korean_for(day) == words.korean_for(day)
    assert words.korean_for(day) != words.korean_for(day + timedelta(days=1))
