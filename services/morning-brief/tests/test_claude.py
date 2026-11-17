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


def block(kind, title, start, minutes, ref=-1):
    return {"kind": kind, "title": title, "start": start, "minutes": minutes, "ref": ref}


def judgment(**overrides):
    return {
        "day_plan": [block("todo", "", "17:30", 15, ref=1)],
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

    assert brief["suggestions"] == [{"start": "17:30", "end": "17:45", "title": "Buy stamps", "kind": "todo"}]
    assert "judgment" not in brief


def test_merge_drops_unknown_and_repeated_reminders():
    picks = [
        block("todo", "", "07:00", 5, ref=9),
        block("todo", "", "07:10", 5, ref=-1),
        block("todo", "", "07:20", 5, ref=0),
        block("todo", "", "07:30", 5, ref=0),
    ]
    brief = {**sample_brief(), "judgment": judgment(day_plan=picks)}

    claude.merge(brief)

    assert [(item["title"], item["start"]) for item in brief["suggestions"]] == [("Oil change", "07:20")]


def test_merge_keeps_at_most_two_reminders():
    items = [{"title": f"Task {number}"} for number in range(4)]
    picks = [block("todo", "", f"1{number}:00", 15, ref=number) for number in range(4)]
    brief = {**sample_brief(), "todos": {"list": "to do", "items": items}, "judgment": judgment(day_plan=picks)}

    claude.merge(brief)

    assert [item["title"] for item in brief["suggestions"]] == ["Task 0", "Task 1"]


def test_merge_gives_a_reminder_the_time_its_notes_ask_for():
    items = [{"title": "Empty recycling", "notes": "25 min, drive to the recycling center"}]
    brief = {**sample_brief(), "todos": {"list": "to do", "items": items}, "judgment": judgment(day_plan=[block("todo", "", "18:00", 5, ref=0)])}

    claude.merge(brief)

    assert (brief["suggestions"][0]["start"], brief["suggestions"][0]["end"]) == ("18:00", "18:25")


def test_merge_titles_workouts_from_the_plan_and_adds_gym_travel():
    workouts = [
        {"kind": "calisthenics", "title": "Calisthenics, morning", "detail": "", "minutes": 15},
        {"kind": "strength", "title": "Strength, push day", "detail": "", "minutes": 45, "away": True},
        {"kind": "run", "title": "Easy run, 3 miles", "detail": "", "minutes": 30, "done": True},
    ]
    picks = [
        block("workout", "Morning set", "06:30", 15, ref=0),
        block("workout", "Gym", "17:30", 45, ref=1),
        block("workout", "Run", "19:00", 30, ref=2),
        block("workout", "Again", "21:00", 15, ref=0),
    ]
    brief = {**sample_brief(), "training": {"today": workouts}, "judgment": judgment(day_plan=picks)}

    claude.merge(brief)

    assert [(item["title"], item["start"], item["end"]) for item in brief["suggestions"]] == [
        ("Calisthenics, morning", "06:30", "06:45"),
        ("Strength, push day", "17:30", "18:45"),
    ]


def test_merge_drops_blocks_that_overlap_his_events_or_each_other():
    schedule = [
        {"title": "Work", "owner": "mine", "start": "08:00", "end": "17:00"},
        {"title": "Her class", "owner": "hers", "start": "18:00", "end": "19:00"},
        {"title": "Birthday", "owner": "shared", "start": "00:00", "end": "23:59", "allDay": True},
    ]
    picks = [
        block("music", "Guitar", "16:30", 45),
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
    today = [{"kind": "run", "title": "Easy run", "detail": "3 mi", "minutes": 30}, {"kind": "strength", "title": "Gym", "detail": "Lift", "minutes": 45, "away": True, "done": True}]
    brief = {**sample_brief(), "training": {"focus": "General fitness", "today": today, "why": "Base.", "week": []}, "meals": [{"date": "2026-11-02", "day": "Mon", "dinner": "Tacos"}]}
    brief["todos"]["items"][1]["notes"] = "About 1 hour"

    claude.fetch(brief, TODAY)

    data = json.loads(fake.sent["messages"][0]["content"].removeprefix("<data>\n").removesuffix("\n</data>"))
    assert data["training"]["today"] == [{"id": 0, "title": "Easy run", "minutes": 30}, {"id": 1, "title": "Gym", "minutes": 45, "away": True, "done": True}]
    assert data["reminders"][1] == {"id": 1, "title": "Buy stamps", "notes": "About 1 hour", "minutes": 60}
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
