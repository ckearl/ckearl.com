"""Weather from NWS, plus air quality and sunrise from Open-Meteo."""

from datetime import date, datetime

from brief import config
from brief.http import get_json

# (label, display time, hour used for the forecast)
TRAINING_SLOTS = [
    ("Early morning", "6:00–7:00 AM", 6),
    ("After work", "5:15–6:15 PM", 17),
    ("Night", "8:00–9:00 PM", 20),
]
PREFERRED_SLOT = "After work"


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


def training_windows(hourly: list[dict], aqi_by_hour: dict[str, float], today: date) -> list[dict]:
    by_hour = {
        period["startTime"][:13]: period for period in hourly if period["startTime"][:10] == today.isoformat()
    }
    windows = []
    for label, display, hour in TRAINING_SLOTS:
        key = f"{today.isoformat()}T{hour:02d}"
        period = by_hour.get(key)
        if not period:
            continue
        wind = wind_mph(period["windSpeed"])
        rain = (period.get("probabilityOfPrecipitation") or {}).get("value") or 0
        aqi = aqi_by_hour.get(key)
        windows.append(
            {
                "label": label,
                "time": display,
                "conditions": f"{period['temperature']}°, wind {wind} mph, {rain}% rain, air {aqi_label(aqi)}",
                "penalty": slot_penalty(period["temperature"], wind, rain, aqi),
            }
        )
    if windows:
        best = min(windows, key=lambda window: (window["penalty"], window["label"] != PREFERRED_SLOT))
        best["best"] = True
    for window in windows:
        del window["penalty"]
    return windows


def build(forecast: dict, hourly: dict, alerts: dict, air: dict, sun: dict, today: date) -> dict:
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
            f"air quality {aqi_label(aqi)} (AQI {round(aqi) if aqi is not None else 'unknown'}). "
            f"Sunrise {short_time(sun['daily']['sunrise'][0])}, sunset {short_time(sun['daily']['sunset'][0])}."
        ),
        "plan": clothing_plan(low, high, rain),
        "trainingWindows": training_windows(hours, aqi_by_hour, today),
    }
    active = [feature["properties"]["headline"] for feature in alerts.get("features", [])]
    if active:
        brief["alert"] = active[0]
    return brief


def fetch(today: date) -> dict:
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
        get_json(
            "https://api.open-meteo.com/v1/forecast",
            {**location, "daily": "sunrise,sunset", "forecast_days": 1},
        ),
        today,
    )
