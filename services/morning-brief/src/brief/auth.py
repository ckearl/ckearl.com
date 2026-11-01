"""Page login. The password is exchanged for an expiring signed token, and only the token
is saved in the browser. The password's SHA-256 is stored, which is safe because it's a
long random value. Switch to a slow hash if it's ever replaced with a human-chosen one."""

import hashlib
import hmac
import os
import time

TOKEN_DAYS = 30


def password_matches(password: str) -> bool:
    expected = os.environ.get("BRIEF_PASSWORD_HASH")
    if not expected or not password or not isinstance(password, str):
        return False
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), expected)


def signature(expires: str, secret: str) -> str:
    return hmac.new(secret.encode(), expires.encode(), hashlib.sha256).hexdigest()


def issue_token(now: float | None = None) -> str:
    expires = str(int(now if now is not None else time.time()) + TOKEN_DAYS * 24 * 60 * 60)
    return f"{expires}.{signature(expires, os.environ['BRIEF_TOKEN_SECRET'])}"


def authorized(event: dict, now: float | None = None) -> bool:
    secret = os.environ.get("BRIEF_TOKEN_SECRET")
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    scheme, _, token = (headers.get("authorization") or "").partition(" ")
    expires, _, signed = token.partition(".")
    if not secret or scheme != "Bearer" or not expires.isdigit():
        return False
    if not hmac.compare_digest(signature(expires, secret), signed):
        return False
    return int(expires) > (now if now is not None else time.time())
