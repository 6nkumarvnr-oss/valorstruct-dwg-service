from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import secrets
import time
from datetime import timedelta

JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
ACCESS_MINUTES = int(os.getenv("JWT_ACCESS_MINUTES", "30"))
REFRESH_DAYS = int(os.getenv("JWT_REFRESH_DAYS", "7"))


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, password_hash: str) -> bool:
    try:
        salt, digest_hex = password_hash.split("$", 1)
    except ValueError:
        return False
    candidate = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000).hex()
    return hmac.compare_digest(candidate, digest_hex)


def _sign(payload: dict) -> str:
    body = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    body_b64 = _b64url_encode(body)
    sig = hmac.new(JWT_SECRET.encode("utf-8"), body_b64.encode("utf-8"), hashlib.sha256).digest()
    sig_b64 = _b64url_encode(sig)
    return f"{body_b64}.{sig_b64}"


def _verify(token: str) -> dict:
    try:
        body_b64, sig_b64 = token.split(".", 1)
    except ValueError as exc:
        raise ValueError("invalid token format") from exc

    expected_sig = hmac.new(JWT_SECRET.encode("utf-8"), body_b64.encode("utf-8"), hashlib.sha256).digest()
    actual_sig = _b64url_decode(sig_b64)
    if not hmac.compare_digest(expected_sig, actual_sig):
        raise ValueError("invalid token signature")

    payload = json.loads(_b64url_decode(body_b64).decode("utf-8"))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("token expired")
    return payload


def create_access_token(*, user_id: str, email: str, role: str) -> str:
    exp = int((time.time() + timedelta(minutes=ACCESS_MINUTES).total_seconds()))
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "access",
        "exp": exp,
        "iat": int(time.time()),
    }
    return _sign(payload)


def create_refresh_token(*, user_id: str, email: str, role: str) -> str:
    exp = int((time.time() + timedelta(days=REFRESH_DAYS).total_seconds()))
    payload = {
        "sub": user_id,
        "email": email,
        "role": role,
        "type": "refresh",
        "exp": exp,
        "iat": int(time.time()),
    }
    return _sign(payload)


def decode_token(token: str) -> dict:
    return _verify(token)
