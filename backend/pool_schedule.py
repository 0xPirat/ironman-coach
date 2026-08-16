"""Öffnungszeiten Schwimmhalle Neptun Rostock für die Schwimmplanung des Coaches.

Quelle: Offizielle Seite der Hansestadt Rostock,
https://rathaus.rostock.de/de/kultur_freizeit_sport/sport/hallenschwimmbad/249778
(abgerufen am 2026-07-05). Öffentliches Schwimmen findet nur in der
25-Meter-Halle statt ("50-Meter-Halle: kein öffentliches Schwimmen").
Sommerpause 2026: 11.07.2026 bis einschließlich 23.08.2026 komplett geschlossen
(https://rathaus.rostock.de/de/rathaus/aktuelles_medien/jaehrliche_sommerpausen_in_schwimmbaedern/367350).

Die Zeiten sind via athlete_config überschreibbar (Key: pool_schedule_json),
damit geänderte Schwimmzeiten ohne Codeänderung gepflegt werden können.
Erwartetes JSON-Format (gleiches Schema wie DEFAULT_SCHEDULE):
    {"Montag": ["06:00-07:30", "18:00-20:00"], ...,
     "hinweise": ["..."], "geschlossen": ["2026-07-11/2026-08-23"]}
"""
from __future__ import annotations

import datetime as dt
import json

from .db import database as db

POOL_NAME = "Schwimmhalle Neptun Rostock (Kopernikusstraße 17, 18057 Rostock)"

# Öffentliches Schwimmen, 25-m-Halle. Stand: 2026-07-05.
DEFAULT_SCHEDULE: dict[str, list[str]] = {
    "Montag": ["06:00-07:30", "18:00-20:00"],
    "Dienstag": ["19:00-22:00"],
    "Mittwoch": ["06:00-07:30", "20:00-22:00"],
    "Donnerstag": ["12:00-14:00"],  # 20-22 Uhr entfällt: nur Frauenschwimmen
    "Freitag": ["06:00-07:30", "13:00-15:00"],
    "Samstag": ["08:00-12:00", "14:00-18:00"],
    "Sonntag": ["08:00-12:00", "13:00-15:00"],
}

DEFAULT_NOTES: list[str] = [
    "Einlass nur bis 60 Minuten vor Ende des jeweiligen Zeitfensters.",
    "Nur die 25-m-Halle ist öffentlich; die 50-m-Halle ist Vereinen/Schulen vorbehalten.",
    "Do 20:00-22:00 Uhr ist Frauenschwimmen (nicht eingeplant).",
    "Zeiten können durch Veranstaltungen kurzfristig abweichen.",
]

# Komplette Schließzeiten als "YYYY-MM-DD/YYYY-MM-DD" (inklusive).
DEFAULT_CLOSURES: list[str] = [
    "2026-07-11/2026-08-23",  # jährliche Sommerpause
]


def _load_schedule() -> tuple[dict[str, list[str]], list[str], list[str]]:
    """DB-Override lesen, sonst Defaults. Fehler -> Defaults."""
    try:
        raw = db.get_athlete_config("pool_schedule_json")
        if raw:
            data = json.loads(raw)
            notes = data.pop("hinweise", DEFAULT_NOTES)
            closures = data.pop("geschlossen", DEFAULT_CLOSURES)
            if data:
                return data, notes, closures
    except Exception:
        pass
    return DEFAULT_SCHEDULE, DEFAULT_NOTES, DEFAULT_CLOSURES


def _active_closures(closures: list[str], today: dt.date) -> list[tuple[dt.date, dt.date]]:
    """Nur Schließzeiten, die noch nicht vorbei sind."""
    out = []
    for c in closures:
        try:
            start_s, end_s = c.split("/")
            start = dt.date.fromisoformat(start_s)
            end = dt.date.fromisoformat(end_s)
            if end >= today:
                out.append((start, end))
        except Exception:
            continue
    return out


def get_pool_schedule_block() -> str:
    """Prompt-Block mit den Schwimmzeiten; leerer String bei Fehlern."""
    try:
        schedule, notes, closures = _load_schedule()
        today = dt.date.today()

        lines = [f"--- SCHWIMMHALLE ({POOL_NAME}) ---"]
        lines.append(
            "Öffentliche Schwimmzeiten (NUR in diese Fenster Schwimmeinheiten "
            "planen; plane inkl. Umziehen/Duschen ±20min Puffer, d.h. die "
            "reine Wasserzeit muss deutlich ins Fenster passen):"
        )
        for day, windows in schedule.items():
            lines.append(f"- {day}: {', '.join(windows) if windows else 'geschlossen'}")

        for start, end in _active_closures(closures, today):
            if start <= today <= end:
                lines.append(
                    f"ACHTUNG: Die Halle ist AKTUELL GESCHLOSSEN "
                    f"({start.strftime('%d.%m.%Y')} bis {end.strftime('%d.%m.%Y')}, Sommerpause). "
                    "Plane bis dahin Freiwasser-Alternativen (z. B. Ostsee/Warnemünde, "
                    "wetterabhängig) oder verschiebe Schwimm-Schwerpunkte."
                )
            else:
                lines.append(
                    f"Geplante Schließzeit: {start.strftime('%d.%m.%Y')} bis "
                    f"{end.strftime('%d.%m.%Y')} — Schwimmeinheiten in diesem "
                    "Zeitraum NICHT in der Halle planen."
                )

        for n in notes:
            lines.append(f"({n})")
        return "\n".join(lines)
    except Exception:
        return ""
