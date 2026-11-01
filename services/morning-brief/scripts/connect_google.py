#!/usr/bin/env python3
"""Connects Google Calendar with read-only access, once.

Opens Google's sign-in page, catches the redirect on 127.0.0.1, and writes the client ID,
client secret and refresh token into .env. Nothing secret is printed.

Usage: python3 scripts/connect_google.py ~/Downloads/client_secret_XXXX.json
"""

import base64
import hashlib
import json
import re
import secrets
import sys
import urllib.parse
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
SCOPE = "https://www.googleapis.com/auth/calendar.readonly"
ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


class Callback(BaseHTTPRequestHandler):
    query: dict = {}

    def do_GET(self):
        Callback.query = {k: v[0] for k, v in urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query).items()}
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Done. You can close this tab and go back to the terminal.")

    def log_message(self, *_args):
        pass


def set_env(values: dict) -> None:
    text = ENV_PATH.read_text()
    for key, value in values.items():
        line = f"{key}={value}"
        text, found = re.subn(rf"^{key}=.*$", lambda _match: line, text, flags=re.M)
        if not found:
            text = text.rstrip("\n") + f"\n{line}\n"
    ENV_PATH.write_text(text)
    ENV_PATH.chmod(0o600)


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    client = json.loads(Path(sys.argv[1]).expanduser().read_text())["installed"]

    server = HTTPServer(("127.0.0.1", 0), Callback)
    redirect_uri = f"http://127.0.0.1:{server.server_port}"
    state = secrets.token_urlsafe(24)
    verifier = secrets.token_urlsafe(64)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).rstrip(b"=").decode()
    url = AUTH_URL + "?" + urllib.parse.urlencode(
        {
            "client_id": client["client_id"],
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": SCOPE,
            "access_type": "offline",
            "prompt": "consent",
            "state": state,
            "code_challenge": challenge,
            "code_challenge_method": "S256",
        }
    )
    print("Opening Google sign-in in your browser. If it doesn't open, use this link:\n" + url)
    webbrowser.open(url)
    server.handle_request()

    query = Callback.query
    if query.get("state") != state or "code" not in query:
        sys.exit(f"Sign-in didn't finish: {query.get('error', 'unexpected response')}")

    body = urllib.parse.urlencode(
        {
            "client_id": client["client_id"],
            "client_secret": client["client_secret"],
            "code": query["code"],
            "code_verifier": verifier,
            "grant_type": "authorization_code",
            "redirect_uri": redirect_uri,
        }
    ).encode()
    with urllib.request.urlopen(urllib.request.Request(TOKEN_URL, data=body)) as response:
        tokens = json.load(response)
    if "refresh_token" not in tokens:
        sys.exit("Google didn't return a refresh token. Remove the app's access in your Google account and retry.")

    set_env(
        {
            "GOOGLE_CLIENT_ID": client["client_id"],
            "GOOGLE_CLIENT_SECRET": client["client_secret"],
            "GOOGLE_REFRESH_TOKEN": tokens["refresh_token"],
        }
    )
    print("Connected. Saved to services/morning-brief/.env. You can delete the downloaded client_secret file.")


if __name__ == "__main__":
    main()
