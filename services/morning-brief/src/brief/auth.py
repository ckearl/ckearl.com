"""Password check for API requests. Only the SHA-256 of the password is stored."""

import hashlib
import hmac
import os


def authorized(event: dict) -> bool:
    expected = os.environ.get("BRIEF_PASSWORD_HASH")
    headers = {key.lower(): value for key, value in (event.get("headers") or {}).items()}
    password = headers.get("x-brief-password")
    if not expected or not password:
        return False
    return hmac.compare_digest(hashlib.sha256(password.encode()).hexdigest(), expected)
