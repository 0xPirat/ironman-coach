"""Secure credential storage via the operating-system vault (using `keyring`).

NEVER store secrets in plaintext. Garmin credentials and (optionally) a
long-lived Claude OAuth token live in Keychain/Credential Manager under the service
name `ironman-coach`.
"""
from __future__ import annotations

import keyring

SERVICE = "ironman-coach"

# Keys
GARMIN_EMAIL = "garmin_email"
GARMIN_PASSWORD = "garmin_password"
CLAUDE_OAUTH_TOKEN = "claude_oauth_token"  # optional, from `claude setup-token`


def set_secret(key: str, value: str) -> None:
    keyring.set_password(SERVICE, key, value)


def get_secret(key: str) -> str | None:
    return keyring.get_password(SERVICE, key)


def delete_secret(key: str) -> None:
    try:
        keyring.delete_password(SERVICE, key)
    except keyring.errors.PasswordDeleteError:
        pass


# Convenience -----------------------------------------------------------------

def set_garmin_credentials(email: str, password: str) -> None:
    set_secret(GARMIN_EMAIL, email)
    set_secret(GARMIN_PASSWORD, password)


def get_garmin_credentials() -> tuple[str | None, str | None]:
    return get_secret(GARMIN_EMAIL), get_secret(GARMIN_PASSWORD)


def get_claude_oauth_token() -> str | None:
    """Optional long-lived token from `claude setup-token`.

    If present, the coach agent exports it as CLAUDE_CODE_OAUTH_TOKEN for the
    bundled `claude` CLI. If absent, the CLI falls back to the interactive
    Keychain login created by `claude /login` (see AUTH_FINDINGS.md).
    """
    return get_secret(CLAUDE_OAUTH_TOKEN)


if __name__ == "__main__":
    # Tiny CLI to set Garmin creds interactively without putting them in shell history.
    import getpass

    print("Store Garmin credentials in the secure system vault (service 'ironman-coach').")
    email = input("Garmin email: ").strip()
    password = getpass.getpass("Garmin password: ")
    set_garmin_credentials(email, password)
    print("Stored. Verify with: python -c \"from backend.credentials import get_garmin_credentials as g; print(g()[0])\"")
