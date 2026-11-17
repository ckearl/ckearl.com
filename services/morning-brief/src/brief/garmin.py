"""Workouts, sleep and HRV from Garmin's official Personal API. Read-only: every call is a GET.
The key comes from Garmin Connect, Settings, Personal API, and is traded for a short-lived token.
Paths follow Garmin's client, github.com/garmin/connect-personal-api-python."""

import os
from datetime import date, datetime, timedelta

import requests

from brief.http import TIMEOUT

BASE_URL = "https://personal.connectapi.garmin.com"
TOKEN_PATH = "/personalapitoken-service/personal-api/personal-api-key/token"
HISTORY_DAYS = 35
METERS_PER_MILE = 1609.344

KINDS = {
    "running": "run",
    "trail_running": "run",
    "treadmill_running": "run",
    "track_running": "run",
    "indoor_running": "run",
    "lap_swimming": "swim",
    "open_water_swimming": "swim",
    "swimming": "swim",
    "strength_training": "strength",
    # Record calisthenics on the watch as HIIT and it counts without a check mark.
    "hiit": "calisthenics",
}


def token() -> str:
    response = requests.post(
        BASE_URL + TOKEN_PATH,
        headers={"Accept": "*/*", "Authorization": f"ApiKey {os.environ['GARMIN_API_KEY']}"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.text.strip()


def get(path: str, access: str, params: dict | None = None):
    response = requests.get(
        BASE_URL + path,
        params=params,
        headers={"Accept": "application/json", "Authorization": f"Bearer {access}"},
        timeout=TIMEOUT,
    )
    response.raise_for_status()
    return response.json() if response.text else None


def to_activity(raw: dict) -> dict:
    type_key = (raw.get("activityType") or {}).get("typeKey", "other")
    return {
        "date": raw["startTimeLocal"][:10],
        "kind": KINDS.get(type_key, "other"),
        "type": type_key,
        "miles": round((raw.get("distance") or 0) / METERS_PER_MILE, 2),
        "minutes": round((raw.get("duration") or 0) / 60),
        "effect": raw.get("aerobicTrainingEffect") or 0,
    }


def to_sleep(rows) -> dict[str, float]:
    return {
        row["calendarDate"]: round(row["sleepTimeSeconds"] / 3600, 1)
        for row in rows or []
        if row.get("sleepTimeSeconds")
    }


def to_hrv(payload) -> dict[str, dict]:
    nights = {}
    for row in (payload or {}).get("hrvSummaries", []):
        low = (row.get("baseline") or {}).get("lowUpper")
        if row.get("lastNightAvg") and low:
            nights[row["calendarDate"]] = {"last": row["lastNightAvg"], "low": low}
    return nights


def fetch(today: date) -> dict:
    access = token()
    start = (today - timedelta(days=HISTORY_DAYS)).isoformat()
    end = today.isoformat()
    raw = get(
        "/activitylist-service/activities/search/activities",
        access,
        {"start": 0, "limit": 100, "startDate": start, "endDate": end},
    )
    recent = (today - timedelta(days=6)).isoformat()
    return {
        "activities": [to_activity(item) for item in raw or []],
        "sleep": to_sleep(get("/sleep-service/sleep/dailySleepSummariesByDate", access, {"startDate": recent, "endDate": end})),
        "hrv": to_hrv(get(f"/hrv-service/hrv/daily/{recent}/{end}", access)),
        "fetchedAt": datetime.now().isoformat(),
    }
