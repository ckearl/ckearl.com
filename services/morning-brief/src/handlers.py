import json
import logging
import os

from brief import assemble, auth, store

logging.getLogger().setLevel(logging.INFO)


def generate(_event, _context):
    brief = assemble.build()
    store.save(brief)
    return {"date": brief["date"], "sources": brief["sources"]}


def cors_headers(event: dict) -> dict:
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    origin = headers.get("origin", "")
    allowed = os.environ.get("ALLOWED_ORIGINS", "").split(",")
    return {
        "Access-Control-Allow-Origin": origin if origin in allowed else allowed[0],
        "Access-Control-Allow-Headers": "X-Brief-Password",
        "Access-Control-Allow-Methods": "GET,OPTIONS",
        "Vary": "Origin",
    }


def respond(event: dict, status: int, body: dict) -> dict:
    return {
        "statusCode": status,
        "headers": {"Content-Type": "application/json", "Cache-Control": "no-store", **cors_headers(event)},
        "body": json.dumps(body, ensure_ascii=False),
    }


def today(event, _context):
    if not auth.authorized(event):
        return respond(event, 401, {"error": "unauthorized"})
    brief = store.latest()
    if brief is None:
        return respond(event, 404, {"error": "no brief yet"})
    return respond(event, 200, brief)
