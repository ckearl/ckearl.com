"""Page login. The password is exchanged for an expiring signed token, and only the token
is saved in the browser. The password's SHA-256 is stored, which is safe because it's a
long random value. Switch to a slow hash if it's ever replaced with a human-chosen one."""

import hashlib
import hmac
import os
import time

TOKEN_DAYS = 30


def hash_matches(value: str, expected: str | None) -> bool:
    if not expected or not value or not isinstance(value, str):
        return False
    return hmac.compare_digest(hashlib.sha256(value.encode()).hexdigest(), expected)


def password_matches(password: str) -> bool:
    return hash_matches(password, os.environ.get("BRIEF_PASSWORD_HASH"))


def bearer(event: dict) -> tuple[str, str]:
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    scheme, _, credential = (headers.get("authorization") or "").partition(" ")
    return scheme, credential


def todos_key_matches(event: dict) -> bool:
    """The iPhone Shortcut's own key. It can send the list and nothing else."""
    scheme, key = bearer(event)
    return scheme == "Bearer" and hash_matches(key, os.environ.get("TODOS_KEY_HASH"))


def signature(expires: str, secret: str) -> str:
    return hmac.new(secret.encode(), expires.encode(), hashlib.sha256).hexdigest()


def issue_token(now: float | None = None) -> str:
    expires = str(int(now if now is not None else time.time()) + TOKEN_DAYS * 24 * 60 * 60)
    return f"{expires}.{signature(expires, os.environ['BRIEF_TOKEN_SECRET'])}"


def authorized(event: dict, now: float | None = None) -> bool:
    secret = os.environ.get("BRIEF_TOKEN_SECRET")
    scheme, token = bearer(event)
    expires, _, signed = token.partition(".")
    if not secret or scheme != "Bearer" or not expires.isdigit():
        return False
    if not hmac.compare_digest(signature(expires, secret), signed):
        return False
    return int(expires) > (now if now is not None else time.time())
