"""Authentication helpers (stdlib only).

- Password hashing: PBKDF2-HMAC-SHA256 with a random salt.
- Token: an HS256-style JWT implemented with ``hmac``/``hashlib`` so no
  third-party dependency is required.
"""
import base64
import hashlib
import hmac
import json
import os
import time
from datetime import timedelta
from typing import Optional

from ..core.config import get_settings

PBKDF2_ITERATIONS = 200_000
TOKEN_ALGO = "HS256"
TOKEN_LIFETIME = timedelta(days=7)


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def _secret() -> str:
    return get_settings().SECRET_KEY


# ---------------------------------------------------------------------------
# Password hashing
# ---------------------------------------------------------------------------

def hash_password(password: str) -> str:
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS
    )
    return (
        f"pbkdf2_sha256${PBKDF2_ITERATIONS}"
        f"${_b64url(salt)}${_b64url(digest)}"
    )


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations_str, salt_b64, digest_b64 = stored.split("$")
        iterations = int(iterations_str)
        salt = _b64url_decode(salt_b64)
        expected = _b64url_decode(digest_b64)
    except (ValueError, TypeError):
        return False

    actual = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, iterations
    )
    return hmac.compare_digest(actual, expected)


# ---------------------------------------------------------------------------
# Token create / verify
# ---------------------------------------------------------------------------

def create_token(customer_id: str, email: str) -> str:
    now = int(time.time())
    payload = {
        "sub": customer_id,
        "email": email,
        "iat": now,
        "exp": now + int(TOKEN_LIFETIME.total_seconds()),
    }
    header = {"alg": TOKEN_ALGO, "typ": "JWT"}

    encoded_header = _b64url(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    encoded_payload = _b64url(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{encoded_header}.{encoded_payload}"

    signature = hmac.new(
        _secret().encode("utf-8"), signing_input.encode("utf-8"), hashlib.sha256
    ).digest()

    return f"{signing_input}.{_b64url(signature)}"


def decode_token(token: str) -> Optional[str]:
    """Return the customer id from a valid token, or ``None``."""
    parts = token.split(".")
    if len(parts) != 3:
        return None

    signed_part, signature_b64 = ".".join(parts[:2]), parts[2]

    expected = hmac.new(
        _secret().encode("utf-8"), signed_part.encode("utf-8"), hashlib.sha256
    ).digest()
    provided = _b64url_decode(signature_b64)

    if not hmac.compare_digest(expected, provided):
        return None

    try:
        payload = json.loads(_b64url_decode(parts[1]))
    except (ValueError, json.JSONDecodeError):
        return None

    exp = payload.get("exp")
    if not exp or int(exp) < int(time.time()):
        return None

    return str(payload.get("sub") or "") or None