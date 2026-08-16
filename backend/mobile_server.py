"""Authenticated, explicitly enabled LAN entry point for mobile clients.

Unlike the normal sidecar this process listens on the LAN. It intentionally
refuses to start without a strong token.
"""

from __future__ import annotations

import argparse
import os

import uvicorn

from .mobile_auth import TOKEN_ENV, validate_mobile_token


def main() -> None:
    parser = argparse.ArgumentParser(description="Ironman Coach Mobile-API")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8766)
    args = parser.parse_args()

    try:
        validate_mobile_token(os.environ.get(TOKEN_ENV))
    except ValueError as exc:
        parser.error(
            f"{exc} Erzeuge z. B. einen Token mit: "
            "python3 -c 'import secrets; print(secrets.token_urlsafe(32))'"
        )

    uvicorn.run("backend.main:app", host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
