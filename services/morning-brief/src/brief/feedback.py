"""What happened to suggested times: marked done or skipped on the page. The last four weeks are
summed up by kind for Claude, so the plan leans toward the times things actually get done and away
from what keeps getting skipped."""

import json
import re
from datetime import date, timedelta

from brief import store

OUTCOMES = ("done", "skipped")
KEEP_DAYS = 28
MAX_ENTRIES = 400
MAX_TITLE = 80
CLOCK = re.compile(r"([01]\d|2[0-3]):[0-5]\d")


def parse(body: str, today: date) -> dict:
    """{"date", "kind", "title", "start", "outcome"}, where outcome is done, skipped or clear."""
    payload = json.loads(body)
    if not isinstance(payload, dict):
        raise ValueError("Expected an object")
    if payload.get("outcome") not in (*OUTCOMES, "clear"):
        raise ValueError("Outcome must be done, skipped or clear")
    if payload.get("date") != today.isoformat():
        raise ValueError("Only today's suggestions can be marked")
    title, kind, start = payload.get("title"), payload.get("kind"), payload.get("start")
    if not isinstance(title, str) or not title.strip() or not isinstance(kind, str) or not isinstance(start, str) or not CLOCK.fullmatch(start):
        raise ValueError("Expected the suggestion's kind, title and start")
    return {"date": today.isoformat(), "kind": kind[:20], "title": title.strip()[:MAX_TITLE], "start": start, "outcome": payload["outcome"]}


def save(entry: dict, today: date) -> None:
    oldest = (today - timedelta(days=KEEP_DAYS)).isoformat()
    key = (entry["date"], entry["title"], entry["start"])
    saved = (store.latest_pushed("feedback") or {}).get("entries", [])
    entries = [item for item in saved if item["date"] >= oldest and (item["date"], item["title"], item["start"]) != key]
    if entry["outcome"] != "clear":
        entries.append(entry)
    store.save_pushed("feedback", {"entries": entries[-MAX_ENTRIES:]})


def habits(today: date) -> dict[str, dict]:
    """By kind: how often it was done or skipped before today, and at what times."""
    oldest = (today - timedelta(days=KEEP_DAYS)).isoformat()
    summary: dict[str, dict] = {}
    for item in (store.latest_pushed("feedback") or {}).get("entries", []):
        if not oldest <= item["date"] < today.isoformat():
            continue
        kind = summary.setdefault(item["kind"], {"done": 0, "skipped": 0, "doneAt": [], "skippedAt": []})
        kind[item["outcome"]] += 1
        kind[f"{item['outcome']}At"].append(item["start"])
    for kind in summary.values():
        kind["doneAt"].sort()
        kind["skippedAt"].sort()
    return summary


def apply(suggestions: list[dict], entry: dict) -> list[dict]:
    """Today's suggestions with this one's outcome set, or cleared."""
    marked = []
    for item in suggestions:
        if (item["title"], item["start"]) == (entry["title"], entry["start"]):
            item = {key: value for key, value in item.items() if key != "outcome"}
            if entry["outcome"] != "clear":
                item["outcome"] = entry["outcome"]
        marked.append(item)
    return marked
