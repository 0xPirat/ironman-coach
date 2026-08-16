"""Dependency-free helpers for the explicitly enabled mobile API."""

from __future__ import annotations

import secrets


TOKEN_ENV = "IRONMAN_MOBILE_TOKEN"
MIN_TOKEN_LENGTH = 32


def validate_mobile_token(token: str | None) -> str:
    """Return a valid token or raise without including it in the error."""
    value = (token or "").strip()
    if len(value) < MIN_TOKEN_LENGTH:
        raise ValueError(
            f"{TOKEN_ENV} muss mindestens {MIN_TOKEN_LENGTH} Zeichen lang sein."
        )
    return value


def bearer_is_valid(authorization: str | None, expected_token: str) -> bool:
    """Compare an HTTP Bearer credential in constant time."""
    if not authorization or not authorization.startswith("Bearer "):
        return False
    supplied = authorization.removeprefix("Bearer ").strip()
    return bool(supplied) and secrets.compare_digest(supplied, expected_token)
