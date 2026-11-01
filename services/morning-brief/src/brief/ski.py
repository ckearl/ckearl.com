"""Ski report. Shows only in season when a big storm is forecast for the Cottonwoods.
Calendar ski days will also trigger it once calendars are connected."""

from datetime import date, datetime, timedelta, timezone

from brief import config
from brief.http import get_json

MM_PER_INCH = 25.4


def in_season(today: date) -> bool:
    return today.month in config.SKI_MONTHS


def forecast_inches(grid: dict, now: datetime) -> float:
    """Snow forecast to fall in the next three days."""
    end = now + timedelta(days=config.SKI_WINDOW_DAYS)
    total = 0.0
    for period in grid["properties"]["snowfallAmount"]["values"]:
        start = datetime.fromisoformat(period["validTime"].split("/")[0])
        if now <= start < end:
            total += period["value"] or 0
    return total / MM_PER_INCH


def gained(depths: list[float], days: int) -> float:
    return max(0, depths[-1] - depths[max(0, len(depths) - 1 - days)])


def station_row(name: str, values: list[dict]) -> dict:
    depths = [item["value"] for item in values if item.get("value") is not None]
    if not depths:
        return {"name": name, "base": "n/a", "new24h": "n/a", "new48h": "n/a"}
    return {
        "name": name,
        "base": f'{depths[-1]:.0f}"',
        "new24h": f'{gained(depths, 1):.0f}"',
        "new48h": f'{gained(depths, 2):.0f}"',
    }


def resort_rows(data: list[dict]) -> list[dict]:
    by_station = {station["stationTriplet"]: station["data"][0]["values"] for station in data if station.get("data")}
    return [station_row(name, by_station.get(station, [])) for name, station in config.SKI_STATIONS]


def build(inches: float, data: list[dict], now: datetime) -> dict:
    last_day = now + timedelta(days=config.SKI_WINDOW_DAYS)
    return {
        "summary": f"About {inches:.0f} inches of snow is forecast for the Cottonwoods by {last_day:%A}.",
        "take": "Worth watching. Numbers are from nearby snow stations, so check lift status with the resort.",
        "resorts": resort_rows(data),
    }


def fetch(now: datetime) -> dict | None:
    if not in_season(now.date()):
        return None
    point = get_json(f"https://api.weather.gov/points/{config.SKI_LATITUDE},{config.SKI_LONGITUDE}")["properties"]
    inches = forecast_inches(get_json(point["forecastGridData"]), now.astimezone(timezone.utc))
    if inches < config.SKI_STORM_INCHES:
        return None
    today = now.date()
    data = get_json(
        "https://wcc.sc.egov.usda.gov/awdbRestApi/services/v1/data",
        {
            "stationTriplets": ",".join(station for _, station in config.SKI_STATIONS),
            "elements": "SNWD",
            "duration": "DAILY",
            "beginDate": (today - timedelta(days=3)).isoformat(),
            "endDate": today.isoformat(),
        },
    )
    return build(inches, data, now)
