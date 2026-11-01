"""Headlines from RSS feeds."""

from defusedxml import ElementTree

from brief import config
from brief.http import get_text

SKIPPED_PREFIXES = ("Have You Seen This?",)


def parse_feed(xml: str, source: str) -> list[dict]:
    stories = []
    for item in ElementTree.fromstring(xml).iter("item"):
        title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        if title and link and not title.startswith(SKIPPED_PREFIXES):
            stories.append({"text": title, "source": source, "url": link})
    return stories


def interleave(feeds: list[list[dict]], limit: int) -> list[dict]:
    picked, seen = [], set()
    for row in range(max(map(len, feeds), default=0)):
        for stories in feeds:
            if row < len(stories) and stories[row]["text"] not in seen:
                seen.add(stories[row]["text"])
                picked.append(stories[row])
                if len(picked) == limit:
                    return picked
    return picked


def fetch() -> list[dict]:
    groups = []
    for group in config.NEWS:
        feeds = []
        for source, url in group["feeds"]:
            try:
                feeds.append(parse_feed(get_text(url), source))
            except Exception:
                # One broken feed shouldn't empty a group with other sources.
                continue
        if feeds:
            groups.append({"label": group["label"], "stories": interleave(feeds, group["limit"])})
    if not groups:
        raise RuntimeError("No news feeds responded")
    return groups
