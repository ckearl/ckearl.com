import json
from datetime import date, timedelta

import pytest

from brief import training

MONDAY = date(2026, 11, 9)


@pytest.fixture(autouse=True)
def settings(monkeypatch):
    monkeypatch.setenv("TRAINING_EASY_PACE", "8:30-8:45")
    monkeypatch.setenv("TRAINING_BASE_MILES", "7.5")


def run(day, miles, effect=2.5):
    return {"date": day.isoformat(), "kind": "run", "type": "running", "miles": miles, "minutes": 40, "effect": effect}


def history(weekly_miles, before=MONDAY):
    """Two runs a week for the four weeks before `before`."""
    runs = []
    for week in range(1, 5):
        start = before - timedelta(days=7 * week)
        runs += [run(start + timedelta(days=1), weekly_miles / 2), run(start + timedelta(days=5), weekly_miles / 2)]
    return runs


def event(title, day):
    return {"title": title, "calendar": "personal", "owner": "mine", "start": "19:00", "end": "21:00"}


def kinds(week, day):
    return [item.get("type", item["kind"]) for item in week["days"][day]]


def test_parse_goal_checks_kind_and_date():
    today = date(2026, 11, 12)
    goal = training.parse_goal(json.dumps({"name": " St. George ", "kind": "half", "date": "2027-03-06"}), today)
    assert goal == {"name": "St. George", "kind": "half", "date": "2027-03-06"}
    assert training.parse_goal('{"clear": true}', today) is None
    for bad in ({"kind": "ultra", "date": "2027-03-06"}, {"kind": "half", "date": "2026-11-01"}, {"kind": "half", "date": "soon"}):
        with pytest.raises(ValueError):
            training.parse_goal(json.dumps(bad), today)


def test_base_is_the_four_week_average_and_ignores_this_week():
    activities = history(8) + [run(MONDAY, 20)]
    assert training.base_miles(activities, MONDAY) == 8


def test_without_garmin_it_uses_the_saved_mileage():
    week = training.plan_week(MONDAY, None, [], {})
    assert week["base"] == 7.5
    assert week["measured"] is False


def test_fitness_week_grows_about_ten_percent_with_no_hard_running():
    week = training.plan_week(MONDAY, None, history(8), {})
    assert week["phase"] == "build"
    assert week["target"] == 9
    run_types = [item["type"] for items in week["days"].values() for item in items if item["kind"] == "run"]
    assert "quality" not in run_types
    assert run_types.count("long") == 1


def test_weekly_miles_add_up_to_the_target():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    week = training.plan_week(MONDAY, goal, history(16), {})
    total = sum(item["miles"] for items in week["days"].values() for item in items if item["kind"] == "run")
    assert abs(total - week["target"]) <= 1.5


def test_a_goal_adds_one_quality_run_away_from_other_hard_days():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    calendar = {MONDAY + timedelta(days=1): [event("Basketball", MONDAY)]}
    week = training.plan_week(MONDAY, goal, history(12), calendar)
    hard = sorted(index for index, day in enumerate(week["days"]) if any(item["hard"] for item in week["days"][day]))
    assert [b - a for a, b in zip(hard, hard[1:])] == [b - a for a, b in zip(hard, hard[1:]) if b - a > 1]
    quality = [day for day in week["days"] if "quality" in kinds(week, day)]
    assert len(quality) == 1


def test_sports_on_the_calendar_take_the_day_and_block_running():
    tuesday = MONDAY + timedelta(days=1)
    week = training.plan_week(MONDAY, None, history(8), {tuesday: [event("Pickup basketball", tuesday)]})
    assert kinds(week, tuesday) == ["sport", "calisthenics"]
    assert week["sports"] == {1: "Pickup basketball"}


def test_her_sports_dont_count():
    tuesday = MONDAY + timedelta(days=1)
    item = event("Soccer", tuesday) | {"owner": "hers"}
    assert training.plan_week(MONDAY, None, history(8), {tuesday: [item]})["sports"] == {}


def test_long_run_moves_off_saturday_when_a_game_is_on_it():
    saturday = MONDAY + timedelta(days=5)
    week = training.plan_week(MONDAY, None, history(8), {saturday: [event("Soccer game", saturday)]})
    assert "long" in kinds(week, MONDAY + timedelta(days=4))


def test_sunday_stays_free():
    week = training.plan_week(MONDAY, {"name": "Half", "kind": "half", "date": "2027-03-06"}, history(20), {})
    assert kinds(week, MONDAY + timedelta(days=6)) == ["calisthenics"]


def test_strength_twice_and_one_swim_a_week():
    week = training.plan_week(MONDAY, None, history(8), {})
    assert (week["strength"], week["swims"]) == (2, 1)
    strength = [index for index, day in enumerate(week["days"]) for kind in kinds(week, day) if kind in ("push", "full")]
    assert strength[1] - strength[0] > 1


def test_gym_days_are_one_push_and_one_full_body_away_from_runs():
    week = training.plan_week(MONDAY, None, history(8), {})
    gym = {day: kind for day in week["days"] for kind in kinds(week, day) if kind in ("push", "full")}
    assert sorted(gym.values()) == ["full", "push"]
    for day in gym:
        assert not {"easy", "long", "quality", "swim"} & set(kinds(week, day))


def test_calisthenics_is_daily_on_its_own_or_after_an_easy_run():
    week = training.plan_week(MONDAY, None, history(8), {})
    for day, items in week["days"].items():
        calisthenics = next(item for item in items if item["kind"] == "calisthenics")
        after_run = "easy" in kinds(week, day)
        assert calisthenics["title"] == ("Calisthenics, after the run" if after_run else "Calisthenics, morning")
        if "push" in kinds(week, day):
            assert "squats" in calisthenics["detail"]


def test_swim_goal_swims_three_times():
    week = training.plan_week(MONDAY, {"name": "Swim", "kind": "swim", "date": "2027-03-06"}, history(8), {})
    assert week["swims"] == 3


def test_recovery_week_every_fourth_week_before_the_taper():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}  # race week starts Mar 1
    weeks = {start: training.phase(goal, start)[0] for start in (date(2027, 3, 1) - timedelta(days=7 * n) for n in range(8))}
    assert [weeks[start] for start in sorted(weeks, reverse=True)] == ["race", "taper", "build", "build", "build", "recovery", "build", "build"]


def test_taper_and_race_week():
    goal = {"name": "Turkey Trot", "kind": "5k", "date": "2026-11-26"}
    race_week = training.plan_week(date(2026, 11, 23), goal, history(12, date(2026, 11, 23)), {})
    thursday = date(2026, 11, 26)
    assert kinds(race_week, thursday) == ["race"]
    assert race_week["days"][thursday][0]["title"] == "Race day: Turkey Trot"
    assert race_week["strength"] == 0
    for day in (thursday - timedelta(days=1), thursday + timedelta(days=1)):
        assert "easy" not in kinds(race_week, day)


def test_tempo_pace_is_a_minute_faster_than_easy():
    item = training.run_item("quality", 4, (510, 525), 2)
    assert item["title"] == "Tempo run, 4 miles"
    assert "7:30–7:45" in item["detail"]


def plan_for(today, goal=None, activities=None, sleep=None, hrv=None, calendar=None):
    data = {"activities": activities or [], "sleep": sleep or {}, "hrv": hrv or {}}
    return training.build(today, goal, data, calendar or {})


def test_missed_run_is_dropped_not_crammed():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    week = training.plan_week(MONDAY, goal, history(12), {})
    run_day = next(day for day in week["days"] if "easy" in kinds(week, day) and day.weekday() < 5)
    result = plan_for(run_day + timedelta(days=1), goal, history(12))
    assert "Yesterday's run didn't happen" in result["why"]


def test_short_sleep_on_three_nights_turns_a_hard_session_easy():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    week = training.plan_week(MONDAY, goal, history(12), {})
    quality_day = next(day for day in week["days"] if "quality" in kinds(week, day))
    sleep = {(quality_day - timedelta(days=back)).isoformat(): 5.5 for back in range(3)}
    result = plan_for(quality_day, goal, history(12), sleep=sleep)
    assert result["today"][0]["title"].startswith("Easy run")
    assert "sleep averaged 5.5 hours" in result["why"].lower()


def test_sleep_rule_needs_all_three_nights():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    week = training.plan_week(MONDAY, goal, history(12), {})
    quality_day = next(day for day in week["days"] if "quality" in kinds(week, day))
    sleep = {quality_day.isoformat(): 4.0, (quality_day - timedelta(days=1)).isoformat(): 4.0}
    result = plan_for(quality_day, goal, history(12), sleep=sleep)
    assert not result["today"][0]["title"].startswith("Easy run")


def test_low_hrv_turns_the_long_run_into_a_shorter_easy_one():
    saturday = MONDAY + timedelta(days=5)
    result = plan_for(saturday, None, history(8), hrv={saturday.isoformat(): {"last": 60, "low": 77}})
    assert result["today"][0]["title"].startswith("Easy run")
    assert "HRV was 60" in result["why"]


def test_unplanned_hard_effort_yesterday_softens_today():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    week = training.plan_week(MONDAY, goal, history(12), {})
    quality_day = next(day for day in week["days"] if "quality" in kinds(week, day))
    yesterday = quality_day - timedelta(days=1)
    activities = history(12) + [{"date": yesterday.isoformat(), "kind": "other", "type": "basketball", "miles": 0, "minutes": 90, "effect": 4.1}]
    if "easy" in kinds(week, yesterday):
        activities.append(run(yesterday, 3))
    result = plan_for(quality_day, goal, activities)
    assert result["today"][0]["title"].startswith("Easy run")
    assert "training effect 4.1" in result["why"]


def test_build_shapes_the_page_section():
    wednesday = MONDAY + timedelta(days=2)
    activities = history(8) + [run(MONDAY, 3)]
    result = plan_for(wednesday, {"name": "St. George", "kind": "half", "date": "2027-03-06"}, activities)
    assert result["focus"] == "St. George (Half marathon), Mar 6, in 16 weeks"
    assert result["week"][0] == {"label": "Miles", "done": 3, "target": result["week"][0]["target"]}
    assert [day["day"] for day in result["plan"]] == ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    assert result["plan"][2]["today"] is True
    assert result["today"][-1]["title"].startswith("Calisthenics")
    assert result["today"][-1]["minutes"] == 15
    assert result["goal"]["kind"] == "half"


def test_fitness_focus_invites_an_event():
    assert plan_for(MONDAY + timedelta(days=2))["focus"] == "General fitness. Add an event to train toward it."


def test_long_run_is_longer_than_the_easy_one_at_low_mileage():
    week = training.plan_week(MONDAY, None, history(4), {})
    runs = {item["type"]: item["miles"] for items in week["days"].values() for item in items if item["kind"] == "run"}
    assert runs["long"] > runs["easy"]


def test_summary_doesnt_claim_ten_percent_when_the_floor_sets_the_target():
    result = plan_for(MONDAY + timedelta(days=2), None, history(4))
    assert "a gentle start" in result["why"]
    assert "10%" not in result["why"]


def test_parse_mark_checks_kind_and_date():
    today = date(2026, 11, 12)
    assert training.parse_mark(json.dumps({"date": "2026-11-12", "kind": "calisthenics", "done": True}), today) == {
        "date": "2026-11-12",
        "kind": "calisthenics",
        "done": True,
    }
    for body in (
        {"date": "2026-11-12", "kind": "nap", "done": True},
        {"date": "2026-11-13", "kind": "run", "done": True},
        {"date": "2026-11-01", "kind": "run", "done": True},
        {"date": "2026-11-12", "kind": "run", "done": "yes"},
    ):
        with pytest.raises(ValueError):
            training.parse_mark(json.dumps(body), today)


def test_save_mark_adds_and_removes_one_day(monkeypatch):
    stored = {"marks": [{"date": "2026-09-01", "kind": "run"}, {"date": "2026-11-11", "kind": "calisthenics"}]}
    saved = []
    monkeypatch.setattr(training.store, "latest_pushed", lambda kind: stored)
    monkeypatch.setattr(training.store, "save_pushed", lambda kind, body: saved.append((kind, body)))
    training.save_mark({"date": "2026-11-12", "kind": "strength", "done": True}, date(2026, 11, 12))
    training.save_mark({"date": "2026-11-11", "kind": "calisthenics", "done": False}, date(2026, 11, 12))
    assert saved[0] == ("done", {"marks": [{"date": "2026-11-11", "kind": "calisthenics"}, {"date": "2026-11-12", "kind": "strength"}]})
    assert saved[1] == ("done", {"marks": []})


def test_check_marks_count_this_week_and_mark_today_done():
    wednesday = MONDAY + timedelta(days=2)
    week = training.plan_week(MONDAY, None, history(8), {})
    run_day = next(day for day in week["days"] if "easy" in kinds(week, day) and day < wednesday)
    run_miles = next(item["miles"] for item in week["days"][run_day] if item["kind"] == "run")
    data = {
        "activities": history(8),
        "marks": [
            {"date": run_day.isoformat(), "kind": "run"},
            {"date": MONDAY.isoformat(), "kind": "calisthenics"},
            {"date": wednesday.isoformat(), "kind": "calisthenics"},
        ],
    }
    result = training.build(wednesday, None, data, {})
    meters = {meter["label"]: meter for meter in result["week"]}
    assert meters["Runs"]["done"] == 1
    assert meters["Miles"]["done"] == run_miles
    assert meters["Calisthenics"] == {"label": "Calisthenics", "done": 2, "target": 7}
    calisthenics = next(item for item in result["today"] if item["kind"] == "calisthenics")
    assert calisthenics["done"] is True


def test_a_checked_run_isnt_called_missed():
    goal = {"name": "Half", "kind": "half", "date": "2027-03-06"}
    week = training.plan_week(MONDAY, goal, history(12), {})
    run_day = next(day for day in week["days"] if "easy" in kinds(week, day) and day.weekday() < 5)
    data = {"activities": history(12), "marks": [{"date": run_day.isoformat(), "kind": "run"}]}
    result = training.build(run_day + timedelta(days=1), goal, data, {})
    assert "didn't happen" not in result["why"]


def test_next_gym_day_names_the_session():
    week = training.plan_week(MONDAY, None, history(8), {})
    first_gym = min(day for day in week["days"] if {"push", "full"} & set(kinds(week, day)))
    result = plan_for(first_gym - timedelta(days=1), None, history(8))
    assert result["gymNext"] == "Tomorrow: gym, push day"
