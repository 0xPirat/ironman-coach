"""Kalender-Integration: Apple-Kalender (lokal, EventKit) und/oder Google iCal-URL.

Der Coach sieht damit, WANN der Athlet belegt ist, und legt Trainings nur in
freie Fenster. Es wird nur GELESEN — nie in den Kalender geschrieben.

Quellen-Auswahl via athlete_config-Key `calendar_source`:
  - "auto"  (Default): Apple-Kalender wenn Zugriff erteilt, sonst iCal-URL,
             sonst leer (kein Kalender-Block im Prompt).
  - "apple": nur Kalender.app via EventKit (siehe backend/apple_cal.py —
             dort steht auch, wie man die Kalender-Berechtigung erteilt).
  - "ics":   nur die private Google-iCal-URL.

Setup Apple-Kalender (empfohlen, keine URL-Kopiererei) — einmalig im Terminal
ausführen und den Berechtigungs-Dialog bestätigen:
      PYTHONPATH=$PWD .venv/bin/python -m backend.apple_cal

Setup Google-iCal (alternativ / als Fallback):
  1. Google Calendar im Browser öffnen → Zahnrad → Einstellungen →
     links den eigenen Kalender wählen → "Kalender integrieren" →
     "Privatadresse im iCal-Format" kopieren (endet auf `/basic.ics`).
  2. URL im macOS Keychain hinterlegen (nie plaintext):
       PYTHONPATH=$PWD .venv/bin/python -m backend.gcal
     (fragt interaktiv nach der URL; Service `ironman-coach`, Key `gcal_ics_url`)

Danach: der Kalender-Block erscheint automatisch im System-Prompt des Coaches,
das Coach-Tool `get_calendar` und `GET /calendar` liefern die Busy-Slots —
unabhängig von der aktiven Quelle immer in derselben Struktur ("source" im
Ergebnis zeigt, welche Quelle geliefert hat).

Caching: athlete_config key `gcal_cache` (JSON), max. 30 min alt; bei
Fehlern wird der letzte Stand mit stale=True serviert. Ohne konfigurierte
Quelle degradiert alles leise (leerer Prompt-Block).
"""
from __future__ import annotations

import datetime as dt
import json
from typing import Any

import requests

from .db import database as db

# Keychain key (service "ironman-coach", see backend/credentials.py)
GCAL_ICS_URL_KEY = "gcal_ics_url"

# athlete_config keys
_CFG_URL_KEY = "gcal_ics_url"       # fallback storage if Keychain unavailable
_CFG_CACHE_KEY = "gcal_cache"
_CFG_SOURCE_KEY = "calendar_source"  # "apple" | "ics" | "auto" (default)

CACHE_MAX_AGE_S = 30 * 60
DEFAULT_DAYS = 7

_WEEKDAYS_DE = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def get_ics_url() -> str | None:
    """Resolve the private iCal URL: env → Keychain → athlete_config."""
    import os
    url = os.environ.get("GCAL_ICS_URL")
    if url:
        return url.strip()
    try:
        from .credentials import get_secret
        url = get_secret(GCAL_ICS_URL_KEY)
        if url:
            return url.strip()
    except Exception:  # noqa: BLE001 — keyring unavailable (e.g. headless test)
        pass
    try:
        url = db.get_athlete_config(_CFG_URL_KEY)
        return url.strip() if url else None
    except Exception:  # noqa: BLE001
        return None


def _fetch_ics(url: str) -> bytes:
    if url.startswith("file://"):  # local file — used by tests
        from urllib.request import url2pathname
        from urllib.parse import urlparse
        return open(url2pathname(urlparse(url).path), "rb").read()
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    return resp.content


def _parse_busy_days(ics_bytes: bytes, start: dt.date, days: int) -> list[dict[str, Any]]:
    """Expand events (incl. recurrences) into per-day busy slots, local time."""
    import icalendar
    import recurring_ical_events

    cal = icalendar.Calendar.from_ical(ics_bytes)
    end = start + dt.timedelta(days=days)
    events = recurring_ical_events.of(cal).between(start, end)

    by_day: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        summary = str(ev.get("SUMMARY", "Termin"))
        # Transparent events ("frei" in Google) don't block training time.
        if str(ev.get("TRANSP", "OPAQUE")).upper() == "TRANSPARENT":
            continue
        dtstart = ev["DTSTART"].dt
        dtend = ev["DTEND"].dt if "DTEND" in ev else dtstart

        if isinstance(dtstart, dt.datetime):
            s_local = dtstart.astimezone()
            e_local = dtend.astimezone() if isinstance(dtend, dt.datetime) else s_local
            day_key = s_local.date().isoformat()
            slot = {
                "start": s_local.strftime("%H:%M"),
                "end": e_local.strftime("%H:%M"),
                "title": summary,
                "all_day": False,
            }
        else:  # all-day event (date, not datetime)
            day_key = dtstart.isoformat()
            slot = {"start": None, "end": None, "title": summary, "all_day": True}

        if start.isoformat() <= day_key < end.isoformat():
            by_day.setdefault(day_key, []).append(slot)

    result = []
    for i in range(days):
        d = start + dt.timedelta(days=i)
        key = d.isoformat()
        slots = sorted(
            by_day.get(key, []),
            key=lambda s: (not s["all_day"] and 1 or 0, s["start"] or ""),
        )
        result.append({"date": key, "weekday": _WEEKDAYS_DE[d.weekday()], "busy": slots})
    return result


def _read_cache(max_age_s: int | None = CACHE_MAX_AGE_S) -> dict[str, Any] | None:
    try:
        raw = db.get_athlete_config(_CFG_CACHE_KEY)
        if not raw:
            return None
        data = json.loads(raw)
        if max_age_s is not None:
            fetched = dt.datetime.fromisoformat(data["fetched_at"])
            if (dt.datetime.utcnow() - fetched).total_seconds() > max_age_s:
                return None
        return data
    except Exception:  # noqa: BLE001
        return None


def _write_cache(data: dict[str, Any]) -> None:
    try:
        db.set_athlete_config(_CFG_CACHE_KEY, json.dumps(data, ensure_ascii=False))
    except Exception:  # noqa: BLE001
        pass


def _get_source() -> str:
    try:
        src = (db.get_athlete_config(_CFG_SOURCE_KEY, "auto") or "auto").strip().lower()
    except Exception:  # noqa: BLE001
        return "auto"
    return src if src in ("apple", "ics", "auto") else "auto"


def _fetch_busy_days(source: str, start: dt.date, days: int) -> tuple[list[dict[str, Any]], str]:
    """Return (busy_days, used_source); raises if no source delivers."""
    errors: list[str] = []
    if source in ("apple", "auto"):
        try:
            from .apple_cal import get_busy_days
            return get_busy_days(start, days), "apple"
        except Exception as exc:  # noqa: BLE001 — no access / pyobjc missing
            errors.append(f"apple: {exc}")
            if source == "apple":
                raise
    if source in ("ics", "auto"):
        url = get_ics_url()
        if not url:
            errors.append(
                "ics: keine iCal-URL hinterlegt (Setup: "
                "PYTHONPATH=$PWD .venv/bin/python -m backend.gcal)")
        else:
            return _parse_busy_days(_fetch_ics(url), start, days), "ics"
    raise RuntimeError("Keine Kalender-Quelle verfügbar — " + "; ".join(errors))


def get_calendar_summary(days: int = DEFAULT_DAYS,
                         force_refresh: bool = False) -> dict[str, Any]:
    """Busy slots for the next `days` days. Cached ≤30 min; stale fallback.

    Source per athlete_config `calendar_source` (apple|ics|auto).
    Raises RuntimeError if no source is configured/accessible.
    """
    if not force_refresh:
        cached = _read_cache()
        if cached is not None and cached.get("days_requested", DEFAULT_DAYS) >= days:
            return cached

    today = dt.date.today()
    try:
        busy_days, used_source = _fetch_busy_days(_get_source(), today, days)
    except Exception:  # noqa: BLE001 — source hiccup: serve stale cache
        stale = _read_cache(max_age_s=None)
        if stale is not None:
            stale["stale"] = True
            return stale
        raise

    summary: dict[str, Any] = {
        "fetched_at": dt.datetime.utcnow().isoformat(),
        "stale": False,
        "days_requested": days,
        "source": used_source,
        "days": busy_days,
    }
    _write_cache(summary)
    return summary


def build_calendar_block(days: int = DEFAULT_DAYS) -> str:
    """Compact German prompt section; empty string if unconfigured/broken."""
    try:
        summary = get_calendar_summary(days=days)
    except Exception:  # noqa: BLE001 — graceful degradation
        return ""

    src_label = {"apple": "Apple-Kalender", "ics": "Google Kalender"}.get(
        summary.get("source", ""), "Kalender")
    lines = [f"--- KALENDER / VERFÜGBARKEIT (nächste 7 Tage, {src_label}) ---"]
    for day in summary.get("days", []):
        slots = day.get("busy", [])
        if not slots:
            desc = "frei (keine Termine)"
        else:
            parts = []
            for s in slots:
                if s.get("all_day"):
                    parts.append(f"ganztägig ({s['title']})")
                else:
                    parts.append(f"{s['start']}-{s['end']} ({s['title']})")
            desc = "belegt: " + ", ".join(parts)
        lines.append(f"{day['weekday']} {day['date']}: {desc}")
    if summary.get("stale"):
        lines.append("(Achtung: Kalenderdaten evtl. veraltet — letzter Cache-Stand.)")
    lines.append(
        "(Plane Trainings NUR in freie Zeitfenster — nie überlappend mit Terminen. "
        "Lass realistisch Puffer für Anfahrt/Umziehen. Bei ganztägigen Terminen "
        "nachfragen, ob und wann Training möglich ist.)"
    )
    return "\n".join(lines)


if __name__ == "__main__":
    # Tiny CLI: store the private iCal URL in the macOS Keychain.
    import getpass

    print("Private Google-Kalender-URL (iCal) im macOS Keychain hinterlegen.")
    print("Google Calendar → Einstellungen → Kalender integrieren → "
          "'Privatadresse im iCal-Format'.")
    url = getpass.getpass("iCal-URL (Eingabe bleibt unsichtbar): ").strip()
    if not url:
        raise SystemExit("Keine URL eingegeben — abgebrochen.")
    from .credentials import set_secret
    set_secret(GCAL_ICS_URL_KEY, url)
    print("Gespeichert (Service 'ironman-coach', Key 'gcal_ics_url').")
    print("Test: PYTHONPATH=$PWD .venv/bin/python -c "
          "\"from backend.gcal import build_calendar_block; print(build_calendar_block())\"")
