from datetime import date

from brief import routine

MONDAY = date(2026, 11, 16)
SATURDAY = date(2026, 11, 21)


def test_morning_help_holds_weekday_mornings(monkeypatch):
    monkeypatch.delenv("MORNING_HELP", raising=False)
    assert routine.morning_help(MONDAY) == {"title": "Morning help", "calendar": "routine", "owner": "mine", "start": "07:00", "end": "07:40"}
    assert routine.morning_help(SATURDAY) is None


def test_morning_help_follows_the_setting(monkeypatch):
    monkeypatch.setenv("MORNING_HELP", "Mon-Sat,07:30-08:10")
    assert routine.morning_help(SATURDAY)["start"] == "07:30"


def test_merge_adds_it_to_the_schedule_in_order(monkeypatch):
    monkeypatch.delenv("MORNING_HELP", raising=False)
    brief = {"schedule": [{"title": "Work", "start": "08:00", "end": "17:00"}, {"title": "Gym", "start": "06:00", "end": "06:45"}]}
    routine.merge(brief, MONDAY)
    assert [item["title"] for item in brief["schedule"]] == ["Gym", "Morning help", "Work"]
