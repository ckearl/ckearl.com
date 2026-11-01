"""English word from Wiktionary, Korean word from the bundled Hanja Chain list."""

import html
import json
import re
from datetime import date
from pathlib import Path

from defusedxml import ElementTree

from brief.http import get_text

FEED = "https://en.wiktionary.org/w/api.php?action=featuredfeed&feed=wotd&feedformat=rss"
KOREAN_WORDS = Path(__file__).parent.parent / "data" / "korean_words.json"
PARTS_OF_SPEECH = {"n": "noun", "v": "verb", "adj": "adjective", "adv": "adverb", "prep": "preposition", "interj": "interjection"}


def strip_tags(text: str) -> str:
    return " ".join(html.unescape(re.sub(r"<[^>]+>", "", text)).split())


def parse_english(xml: str, today: date) -> dict:
    items = list(ElementTree.fromstring(xml).iter("item"))
    title = f"Word of the day for {today.strftime('%B')} {today.day}"
    item = next((entry for entry in items if entry.findtext("title") == title), items[-1])
    body = item.findtext("description")

    word = re.search(r'id="WOTD-rss-title">(.*?)</span>', body, re.S)
    part = re.search(r"WOTD-rss-title.*?</b>\s*<i>(.*?)</i>", body, re.S)
    section = body[body.find('id="WOTD-rss-description"') :]
    definition = re.search(r"<li>(.*?)(?:</li>|<ol|<dl|<ul)", section, re.S)
    if not word or not definition:
        raise ValueError("Unexpected Wiktionary format")

    label = strip_tags(part.group(1)) if part else ""
    return {
        "word": strip_tags(word.group(1)),
        "partOfSpeech": PARTS_OF_SPEECH.get(label, label),
        "definition": strip_tags(definition.group(1)),
    }


def korean_for(today: date) -> dict:
    words = json.loads(KOREAN_WORDS.read_text(encoding="utf-8"))
    return words[today.toordinal() % len(words)]


def fetch(today: date) -> dict:
    return {"english": parse_english(get_text(FEED), today), "korean": korean_for(today)}
