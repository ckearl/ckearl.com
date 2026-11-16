"""Weather from NWS, plus air quality and sunrise from Open-Meteo."""

import logging
from datetime import date, datetime

import requests

from brief import config, work
from brief.http import get_json

logger = logging.getLogger(__name__)

# (label, start, end). The first listed slot wins a tie. "After work" starts 15 minutes after the work day.
WEEKEND_SLOTS = [("Morning", "08:00", "09:00"), ("Midday", "12:00", "13:00"), ("Afternoon", "16:00", "17:00")]
SLOT_MINUTES = 60


def to_minutes(clock: str) -> int:
    hours, minutes = clock.split(":")
    return int(hours) * 60 + int(minutes)


def to_clock(total: int) -> str:
    return f"{total // 60:02d}:{total % 60:02d}"


def display(start: str, end: str) -> str:
    def part(clock: str) -> str:
        hours, minutes = divmod(to_minutes(clock), 60)
        return f"{hours % 12 or 12}:{minutes:02d}"

    return f"{part(start)}–{part(end)} {'AM' if to_minutes(end) <= 12 * 60 else 'PM'}"


def training_slots(today: date) -> list[tuple[str, str, str]]:
    """Weekday slots work around the work day. Days off use daytime slots, since there's no "after work"."""
    days, _start, end = work.usual_hours()
    if today.weekday() not in days:
        return WEEKEND_SLOTS
    after = to_minutes(end) + 15
    return [
        ("After work", to_clock(after), to_clock(after + SLOT_MINUTES)),
        ("Early morning", "06:00", "07:00"),
        ("Night", "20:00", "21:00"),
    ]


def busy_times(schedule: list[dict]) -> list[tuple[int, int]]:
    """Timed events that are his or shared. Her events and all-day entries don't block a workout."""
    return [
        (to_minutes(item["start"]), to_minutes(item["end"]))
        for item in schedule
        if not item.get("allDay") and item.get("owner", "mine") != "hers"
    ]


def wind_mph(text: str) -> int:
    numbers = [int(part) for part in text.split() if part.isdigit()]
    return max(numbers, default=0)


def short_time(value: str) -> str:
    moment = datetime.fromisoformat(value)
    return f"{moment.hour % 12 or 12}:{moment.minute:02d} {'AM' if moment.hour < 12 else 'PM'}"


def aqi_label(aqi: float | None) -> str:
    if aqi is None:
        return "unknown"
    if aqi <= 50:
        return "good"
    if aqi <= 100:
        return "moderate"
    if aqi <= 150:
        return "unhealthy for sensitive groups"
    return "unhealthy"


def clothing_plan(low: int, high: int, rain: int) -> str:
    if rain >= 40:
        return "Take a rain jacket."
    if low <= 32:
        return "Gloves for an early run, and a warm layer for the morning."
    if high >= 90:
        return "Train early or late, and carry water."
    if low <= 50:
        return "A light jacket covers the cooler hours."
    return "No jacket needed."


def slot_penalty(temperature: int, wind: int, rain: int, aqi: float | None) -> int:
    penalty = 0
    if rain >= 40:
        penalty += 3
    if aqi is not None and aqi > 100:
        penalty += 3
    if wind >= 20:
        penalty += 2
    if temperature < 25 or temperature > 85:
        penalty += 2
    return penalty


def training_windows(hourly: list[dict], aqi_by_hour: dict[str, float], today: date, schedule: list[dict] | None = None) -> list[dict]:
    by_hour = {
        period["startTime"][:13]: period for period in hourly if period["startTime"][:10] == today.isoformat()
    }
    busy = busy_times(schedule or [])
    windows = []
    for rank, (label, start, end) in enumerate(training_slots(today)):
        if any(to_minutes(start) < busy_end and busy_start < to_minutes(end) for busy_start, busy_end in busy):
            continue
        key = f"{today.isoformat()}T{start[:2]}"
        period = by_hour.get(key)
        if not period:
            continue
        wind = wind_mph(period["windSpeed"])
        rain = (period.get("probabilityOfPrecipitation") or {}).get("value") or 0
        aqi = aqi_by_hour.get(key)
        windows.append(
            {
                "label": label,
                "time": display(start, end),
                "start": start,
                "end": end,
                "conditions": f"{period['temperature']}°, wind {wind} mph, {rain}% rain, air {aqi_label(aqi)}",
                "penalty": slot_penalty(period["temperature"], wind, rain, aqi),
                "rank": rank,
            }
        )
    if windows:
        best = min(windows, key=lambda window: (window["penalty"], window["rank"]))
        best["best"] = True
    for window in windows:
        del window["penalty"], window["rank"]
    return sorted(windows, key=lambda window: window["start"])


def build(forecast: dict, hourly: dict, alerts: dict, air: dict, sun: dict | None, today: date, schedule: list[dict] | None = None) -> dict:
    periods = forecast["properties"]["periods"]
    hours = hourly["properties"]["periods"]
    now = hours[0]
    high = next(period["temperature"] for period in periods if period["isDaytime"])
    low = next(period["temperature"] for period in periods if not period["isDaytime"])
    rain = (periods[0].get("probabilityOfPrecipitation") or {}).get("value") or 0
    aqi = air["current"].get("us_aqi")
    aqi_by_hour = dict(
        (time[:13], value) for time, value in zip(air["hourly"]["time"], air["hourly"]["us_aqi"])
    )

    brief = {
        "now": f"{now['temperature']}°",
        "high": f"{high}°",
        "low": f"{low}°",
        "conditions": now["shortForecast"],
        "details": (
            f"{rain}% rain, wind {now['windDirection']} {wind_mph(now['windSpeed'])} mph, "
            f"air quality {aqi_label(aqi)} (AQI {round(aqi) if aqi is not None else 'unknown'})."
            + (f" Sunrise {short_time(sun['daily']['sunrise'][0])}, sunset {short_time(sun['daily']['sunset'][0])}." if sun else "")
        ),
        "plan": clothing_plan(low, high, rain),
        "trainingWindows": training_windows(hours, aqi_by_hour, today, schedule),
    }
    active = [feature["properties"]["headline"] for feature in alerts.get("features", [])]
    if active:
        brief["alert"] = active[0]
    return brief


def fetch(today: date, schedule: list[dict] | None = None) -> dict:
    point = get_json(f"https://api.weather.gov/points/{config.LATITUDE},{config.LONGITUDE}")["properties"]
    location = {"latitude": config.LATITUDE, "longitude": config.LONGITUDE, "timezone": "America/Denver"}
    return build(
        get_json(point["forecast"]),
        get_json(point["forecastHourly"]),
        get_json(f"https://api.weather.gov/alerts/active?point={config.LATITUDE},{config.LONGITUDE}"),
        get_json(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            {**location, "current": "us_aqi", "hourly": "us_aqi", "forecast_days": 2},
        ),
        sun_times(location),
        today,
        schedule,
    )


def sun_times(location: dict) -> dict | None:
    """Sunrise and sunset are a nice extra, so an outage leaves them out instead of failing the window."""
    try:
        return get_json("https://api.open-meteo.com/v1/forecast", {**location, "daily": "sunrise,sunset", "forecast_days": 1})
    except requests.RequestException:
        logger.warning("Sunrise and sunset unavailable", exc_info=True)
        return None
