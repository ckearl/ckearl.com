import json
from datetime import date
from types import SimpleNamespace

import pytest

from brief import claude

TODAY = date(2026, 11, 2)


def sample_brief():
    return {
        "todos": {"list": "to do", "items": [{"title": "Oil change", "due": "2026-11-02"}, {"title": "Buy stamps"}]},
        "news": [
            {"label": "Utah", "stories": [{"text": "Local story", "source": "KSL", "url": "https://example.com/a"}]},
            {
                "label": "World",
                "stories": [
                    {"text": "World one", "source": "BBC", "url": "https://example.com/b"},
                    {"text": "World two", "source": "NPR", "url": "https://example.com/c"},
                ],
            },
        ],
    }


def reply(text, stop_reason="end_turn"):
    return SimpleNamespace(
        stop_reason=stop_reason,
        usage=SimpleNamespace(input_tokens=10, output_tokens=5),
        content=[SimpleNamespace(type="text", text=text)],
    )


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.sent = None
        self.beta = self
        self.messages = self

    def create(self, **request):
        self.sent = request
        return self.response


def block(kind, title, start, minutes, reason="Fits.", reminder_id=-1):
    return {"kind": kind, "title": title, "start": start, "minutes": minutes, "reminder_id": reminder_id, "reason": reason}


def judgment(**overrides):
    return {
        "day_plan": [block("todo", "", "17:30", 15, "It fits after work.", reminder_id=1)],
        "top_stories": [{"story_id": 2, "why": "It matters."}],
        "sports_line": "The Jazz lost.",
        **overrides,
    }


def test_fetch_sends_ids_and_returns_the_answer(monkeypatch):
    fake = FakeClient(reply(json.dumps(judgment())))
    monkeypatch.setattr(claude, "client", lambda: fake)

    assert claude.fetch(sample_brief(), TODAY) == judgment()

    data = json.loads(fake.sent["messages"][0]["content"].removeprefix("<data>\n").removesuffix("\n</data>"))
    assert data["today"] == "Monday, 2026-11-02"
    assert data["reminders"] == [{"id": 0, "title": "Oil change", "due": "2026-11-02"}, {"id": 1, "title": "Buy stamps"}]
    assert data["stories"][2] == {"id": 2, "headline": "World two", "source": "NPR"}
    assert "url" not in data["stories"][0]


def test_fetch_rejects_an_early_stop(monkeypatch):
    monkeypatch.setattr(claude, "client", lambda: FakeClient(reply("", stop_reason="refusal")))

    with pytest.raises(ValueError):
        claude.fetch(sample_brief(), TODAY)


def test_merge_uses_the_original_reminder_title():
    brief = {**sample_brief(), "judgment": judgment()}

    claude.merge(brief)

    assert brief["suggestions"] == [{"start": "17:30", "end": "17:45", "title": "Buy stamps", "kind": "todo", "why": "It fits after work."}]
    assert "judgment" not in brief


def test_merge_drops_unknown_and_repeated_reminders():
    picks = [
        block("todo", "", "07:00", 5, "Unknown", reminder_id=9),
        block("todo", "", "07:10", 5, "Unknown", reminder_id=-1),
        block("todo", "", "07:20", 5, "First", reminder_id=0),
        block("todo", "", "07:30", 5, "Repeat", reminder_id=0),
    ]
    brief = {**sample_brief(), "judgment": judgment(day_plan=picks)}

    claude.merge(brief)

    assert [item["why"] for item in brief["suggestions"]] == ["First"]


def test_merge_drops_blocks_that_overlap_his_events_or_each_other():
    schedule = [
        {"title": "Work", "owner": "mine", "start": "08:00", "end": "17:00"},
        {"title": "Her class", "owner": "hers", "start": "18:00", "end": "19:00"},
        {"title": "Birthday", "owner": "shared", "start": "00:00", "end": "23:59", "allDay": True},
    ]
    picks = [
        block("workout", "Easy run", "16:30", 45),
        block("dinner", "Cook tacos", "18:00", 40),
        block("chores", "Chores", "18:20", 20),
        block("reading", "Read", "21:00", 30),
    ]
    brief = {**sample_brief(), "schedule": schedule, "judgment": judgment(day_plan=picks)}

    claude.merge(brief)

    assert [(item["title"], item["start"], item["end"]) for item in brief["suggestions"]] == [
        ("Cook tacos", "18:00", "18:40"),
        ("Read", "21:00", "21:30"),
    ]


def test_merge_drops_blocks_outside_the_waking_day_or_with_bad_times():
    picks = [
        block("music", "Guitar", "05:30", 20),
        block("reading", "Read", "22:15", 30),
        block("music", "Piano", "7pm", 20),
        block("chores", "Chores", "12:00", 0),
        block("dance", "Dance", "13:00", 20),
        block("music", "  ", "14:00", 20),
        block("music", "Piano", "19:00", 25),
    ]
    brief = {**sample_brief(), "judgment": judgment(day_plan=picks)}

    claude.merge(brief)

    assert [item["title"] for item in brief["suggestions"]] == ["Piano"]


def test_fetch_sends_training_and_meals(monkeypatch):
    fake = FakeClient(reply(json.dumps(judgment())))
    monkeypatch.setattr(claude, "client", lambda: fake)
    brief = {**sample_brief(), "training": {"focus": "General fitness", "today": [{"title": "Easy run", "detail": "3 mi"}], "why": "Base.", "week": []}, "meals": [{"date": "2026-11-02", "day": "Mon", "dinner": "Tacos"}]}

    claude.fetch(brief, TODAY)

    data = json.loads(fake.sent["messages"][0]["content"].removeprefix("<data>\n").removesuffix("\n</data>"))
    assert data["training"]["today"] == [{"title": "Easy run", "detail": "3 mi"}]
    assert "week" not in data["training"]
    assert data["meals"][0]["dinner"] == "Tacos"
    assert fake.sent["fallbacks"] == "default"


def test_merge_moves_top_stories_first_without_repeating_them():
    brief = {**sample_brief(), "judgment": judgment()}

    claude.merge(brief)

    top, utah, world = brief["news"]
    assert top["label"] == "Top stories"
    assert top["stories"] == [{"text": "World two", "source": "NPR", "url": "https://example.com/c", "why": "It matters."}]
    assert [story["text"] for story in utah["stories"]] == ["Local story"]
    assert [story["text"] for story in world["stories"]] == ["World one"]


def test_merge_removes_a_group_left_empty():
    picks = [{"story_id": 0, "why": "It matters."}]
    brief = {**sample_brief(), "judgment": judgment(top_stories=picks)}

    claude.merge(brief)

    assert [group["label"] for group in brief["news"]] == ["Top stories", "World"]


def test_merge_keeps_the_news_when_no_story_id_is_valid():
    brief = {**sample_brief(), "judgment": judgment(top_stories=[{"story_id": 40, "why": "Unknown"}])}

    claude.merge(brief)

    assert [group["label"] for group in brief["news"]] == ["Utah", "World"]


def test_merge_sets_the_sports_line_only_when_there_is_one():
    brief = {**sample_brief(), "judgment": judgment()}
    claude.merge(brief)
    assert brief["roundup"] == [{"label": "Sports", "text": "The Jazz lost."}]

    quiet = {**sample_brief(), "judgment": judgment(sports_line=" ")}
    claude.merge(quiet)
    assert "roundup" not in quiet


def test_merge_leaves_the_brief_alone_when_claude_failed():
    brief = sample_brief()

    claude.merge(brief)

    assert brief == sample_brief()
