#!/usr/bin/env python3
"""Makes a YouTube Data API key for score highlights, once, and saves it to .env as YOUTUBE_API_KEY.

Signs in with the Google client already in .env (from connect_google.py), asking for Google Cloud
access for this run only. No refresh token is kept. In that client's Cloud project it turns on the
YouTube Data API and the API Keys API, then makes a key that only works for YouTube. Running it
again reuses the same key. Nothing secret is printed.

Google may warn that the app isn't verified, because Cloud access is a sensitive permission. It's
your own app: choose Advanced, then continue.

Usage: python3 scripts/connect_youtube.py
"""

import json
import sys
import time
import urllib.error
import urllib.request

from connect_google import saved_client, set_env, sign_in

SCOPE = "https://www.googleapis.com/auth/cloud-platform"
SERVICES = ("apikeys.googleapis.com", "youtube.googleapis.com")
KEY_ID = "morning-brief-youtube"
WAIT_SECONDS = 120


def call(token: str, method: str, url: str, body: dict | None = None) -> dict:
    request = urllib.request.Request(
        url,
        method=method,
        data=json.dumps(body).encode() if body is not None else None,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request) as response:
        return json.load(response)


def finish(token: str, base: str, operation: dict) -> dict:
    """Waits for a long-running Google Cloud operation and returns its result."""
    deadline = time.monotonic() + WAIT_SECONDS
    while not operation.get("done"):
        if time.monotonic() > deadline:
            sys.exit(f"Google Cloud is still working on {operation['name']}. Run this again in a minute.")
        time.sleep(2)
        operation = call(token, "GET", f"{base}/{operation['name']}")
    if "error" in operation:
        sys.exit(f"Google Cloud refused: {operation['error'].get('message', operation['error'])}")
    return operation.get("response", {})


def error_message(error: urllib.error.HTTPError) -> str:
    try:
        return json.loads(error.read())["error"]["message"]
    except Exception:
        return f"HTTP {error.code}"


def main() -> None:
    if len(sys.argv) > 1:
        sys.exit(__doc__)
    client = saved_client()
    # A Desktop client's ID starts with its Cloud project's number.
    project = client["client_id"].split("-", 1)[0]
    if not project.isdigit():
        sys.exit("Couldn't read the Cloud project from GOOGLE_CLIENT_ID.")

    token = sign_in(client, SCOPE, offline=False)["access_token"]

    try:
        for service in SERVICES:
            print(f"Turning on {service}...")
            base = "https://serviceusage.googleapis.com/v1"
            finish(token, base, call(token, "POST", f"{base}/projects/{project}/services/{service}:enable", {}))

        keys = f"https://apikeys.googleapis.com/v2/projects/{project}/locations/global/keys"
        name = f"projects/{project}/locations/global/keys/{KEY_ID}"
        print("Making a key that only works for YouTube...")
        body = {"displayName": "Morning brief YouTube", "restrictions": {"apiTargets": [{"service": "youtube.googleapis.com"}]}}
        try:
            name = finish(token, "https://apikeys.googleapis.com/v2", call(token, "POST", f"{keys}?keyId={KEY_ID}", body))["name"]
        except urllib.error.HTTPError as error:
            if error.code != 409:
                raise
            print("The key already exists; reusing it.")
        key = call(token, "GET", f"https://apikeys.googleapis.com/v2/{name}/keyString")["keyString"]
    except urllib.error.HTTPError as error:
        sys.exit(f"Google Cloud refused: {error_message(error)}")

    set_env({"YOUTUBE_API_KEY": key})
    print("Saved YOUTUBE_API_KEY to services/morning-brief/.env. Deploy with scripts/deploy.sh to use it.")


if __name__ == "__main__":
    main()
