from datetime import date

from brief import weather

TODAY = date(2026, 11, 2)


def hour(clock, temperature=50, wind="5 mph", rain=0):
    return {
        "startTime": f"2026-11-02T{clock:02d}:00:00-07:00",
        "temperature": temperature,
        "windSpeed": wind,
        "windDirection": "NW",
        "shortForecast": "Clear",
        "probabilityOfPrecipitation": {"value": rain},
    }


def test_wind_uses_the_top_of_a_range():
    assert weather.wind_mph("5 to 15 mph") == 15


def test_prefers_after_work_when_slots_tie():
    windows = weather.training_windows([hour(6), hour(17), hour(20)], {}, TODAY)
    assert [window["label"] for window in windows if window.get("best")] == ["After work"]


def test_avoids_rain_in_the_preferred_slot():
    windows = weather.training_windows([hour(6), hour(17, rain=80), hour(20)], {}, TODAY)
    assert [window["label"] for window in windows if window.get("best")] == ["Early morning"]


def test_bad_air_moves_the_recommendation():
    aqi = {"2026-11-02T17": 160, "2026-11-02T06": 40, "2026-11-02T20": 170}
    windows = weather.training_windows([hour(6), hour(17), hour(20)], aqi, TODAY)
    assert [window["label"] for window in windows if window.get("best")] == ["Early morning"]


def test_exactly_one_best_window_and_no_internal_fields():
    windows = weather.training_windows([hour(6), hour(17), hour(20)], {}, TODAY)
    assert sum(1 for window in windows if window.get("best")) == 1
    assert all("penalty" not in window for window in windows)


def test_only_today_counts():
    tomorrow = {**hour(17), "startTime": "2026-11-03T17:00:00-07:00"}
    assert weather.training_windows([tomorrow], {}, TODAY) == []


def test_clothing_plan():
    assert "rain" in weather.clothing_plan(50, 60, 60).lower()
    assert "Gloves" in weather.clothing_plan(30, 50, 0)


def test_build_reports_an_active_alert():
    forecast = {
        "properties": {
            "periods": [
                {"isDaytime": True, "temperature": 52, "probabilityOfPrecipitation": {"value": 5}},
                {"isDaytime": False, "temperature": 31},
            ]
        }
    }
    brief = weather.build(
        forecast,
        {"properties": {"periods": [hour(6), hour(17), hour(20)]}},
        {"features": [{"properties": {"headline": "Winter Storm Warning"}}]},
        {"current": {"us_aqi": 41}, "hourly": {"time": [], "us_aqi": []}},
        {"daily": {"sunrise": ["2026-11-02T07:10"], "sunset": ["2026-11-02T17:32"]}},
        TODAY,
    )
    assert brief["alert"] == "Winter Storm Warning"
    assert brief["high"] == "52°" and brief["low"] == "31°"
    assert "AQI 41" in brief["details"] and "7:10 AM" in brief["details"]
