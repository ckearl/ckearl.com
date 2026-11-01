"""HTTP for the data sources."""

import requests

# ESPN rejects unusual User-Agent strings with a 403.
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ckearl.com)"}
TIMEOUT = 12


def get(url: str, params: dict | None = None) -> requests.Response:
    response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response


def get_json(url: str, params: dict | None = None) -> dict:
    return get(url, params).json()


def get_text(url: str) -> str:
    return get(url).text
