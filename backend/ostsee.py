"""Ostsee-Freiwasser-Check (Warnemünde) für die Schwimmplanung.

Holt Wassertemperatur (Open-Meteo Marine API) und Wind in Knoten inkl.
Richtung (Open-Meteo Forecast API) für den Badespot und baut daraus einen
kompakten Prompt-Block: pro Tag Wassertemperatur, bestes Schwimmfenster und
ob Freiwasserschwimmen nach den Regeln des Athleten möglich ist.

Regeln des Athleten:
- Wassertemperatur über 20 °C
- Wind ablandig (in Warnemünde: aus Süd, Land liegt südlich) ODER schwach
  (max. 5 kn); ablandiger Wind wird aus Sicherheitsgründen bei 15 kn gedeckelt.

Der Block wird nur in den warmen Monaten (Mai-Oktober) erzeugt; außerhalb —
und bei jedem Fehler — liefert get_ostsee_block() einen leeren String.

Spot-Fallback: Warnemünde Strand (54.18, 12.08).
Konfigurierbar via athlete_config keys  ostsee_lat / ostsee_lon.
"""
from __future__ import annotations

import datetime as dt
import time
from typing import Any

import requests

from .db import database as db

DEFAULT_LAT = 54.18
DEFAULT_LON = 12.08

SWIM_MONTHS = range(5, 11)          # Mai bis Oktober
MIN_WATER_TEMP_C = 20.0
MAX_WIND_KN = 5.0                   # "wenig Wind" laut Athlet
MAX_OFFSHORE_WIND_KN = 15.0         # Sicherheitsdeckel bei ablandigem Wind
OFFSHORE_FROM_DEG = 120.0           # ablandig in Warnemünde: Wind aus SO bis SW
OFFSHORE_TO_DEG = 240.0
DAY_START_H = 8                     # betrachtetes Tagesfenster
DAY_END_H = 20
MIN_WINDOW_H = 2                    # so lang muss ein Schwimmfenster mindestens sein

MARINE_URL = "https://marine-api.open-meteo.com/v1/marine"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

CACHE_MAX_AGE_S = 30 * 60
_cache: dict[str, Any] = {"ts": 0.0, "block": None}

_COMPASS = ["N", "NO", "NO", "O", "O", "SO", "SO", "S",
            "S", "SW", "SW", "W", "W", "NW", "NW", "N"]

_WEEKDAYS = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]


def _compass(deg: float) -> str:
    return _COMPASS[int((deg % 360) / 22.5)]


def _get_location() -> tuple[float, float]:
    try:
        lat = float(db.get_athlete_config("ostsee_lat", str(DEFAULT_LAT)))
        lon = float(db.get_athlete_config("ostsee_lon", str(DEFAULT_LON)))
        return lat, lon
    except Exception:
        return DEFAULT_LAT, DEFAULT_LON


def _is_offshore(deg: float) -> bool:
    return OFFSHORE_FROM_DEG <= (deg % 360) <= OFFSHORE_TO_DEG


def _hour_swimmable(speed_kn: float, direction_deg: float) -> bool:
    if speed_kn <= MAX_WIND_KN:
        return True
    return _is_offshore(direction_deg) and speed_kn <= MAX_OFFSHORE_WIND_KN


def _fetch(lat: float, lon: float) -> tuple[dict[str, Any], dict[str, Any]]:
    marine = requests.get(MARINE_URL, params={
        "latitude": lat, "longitude": lon,
        "hourly": "sea_surface_temperature",
        "timezone": "auto", "forecast_days": 7,
    }, timeout=10)
    marine.raise_for_status()
    wind = requests.get(FORECAST_URL, params={
        "latitude": lat, "longitude": lon,
        "hourly": "windspeed_10m,winddirection_10m",
        "wind_speed_unit": "kn",
        "timezone": "auto", "forecast_days": 7,
    }, timeout=10)
    wind.raise_for_status()
    return marine.json(), wind.json()


def _by_date_hour(hourly: dict[str, Any], key: str) -> dict[str, dict[int, float]]:
    """hourly-Arrays der API → {date: {hour: value}}."""
    out: dict[str, dict[int, float]] = {}
    for t, v in zip(hourly["time"], hourly[key]):
        if v is None:
            continue
        date, hh = t.split("T")
        out.setdefault(date, {})[int(hh[:2])] = float(v)
    return out


def _best_window(speeds: dict[int, float], dirs: dict[int, float]) -> tuple[int, int] | None:
    """Längstes zusammenhängendes schwimmbares Fenster im Tagesbereich; None wenn < MIN_WINDOW_H."""
    best: tuple[int, int] | None = None
    start: int | None = None
    for h in range(DAY_START_H, DAY_END_H + 1):
        ok = h in speeds and h in dirs and _hour_swimmable(speeds[h], dirs[h])
        if ok and start is None:
            start = h
        if (not ok or h == DAY_END_H) and start is not None:
            end = h if ok else h - 1
            if end - start >= MIN_WINDOW_H and (best is None or end - start > best[1] - best[0]):
                best = (start, end)
            start = None
    return best


def _build_day_line(date_str: str, sst: float | None,
                    speeds: dict[int, float], dirs: dict[int, float]) -> str:
    d = dt.date.fromisoformat(date_str)
    label = f"{_WEEKDAYS[d.weekday()]} {d.strftime('%d.%m.')}"
    if sst is None:
        return f"{label}: keine Wasserdaten"

    window = _best_window(speeds, dirs)
    warm = sst >= MIN_WATER_TEMP_C
    if warm and window:
        s, e = window
        w_speeds = [speeds[h] for h in range(s, e + 1)]
        w_dirs = [dirs[h] for h in range(s, e + 1)]
        mean_dir = sum(w_dirs) / len(w_dirs)
        tags = []
        if _is_offshore(mean_dir):
            tags.append("ablandig")
        if d.weekday() >= 5:
            tags.append("Wochenende")
        tag_str = f", {', '.join(tags)}" if tags else ""
        return (f"{label}: ✓ möglich — Wasser {sst:.1f}°C, Fenster {s}-{e} Uhr, "
                f"Wind {min(w_speeds):.0f}-{max(w_speeds):.0f} kn aus "
                f"{_compass(mean_dir)}{tag_str}")
    reasons = []
    if not warm:
        reasons.append(f"Wasser nur {sst:.1f}°C")
    if not window:
        day_speeds = [speeds[h] for h in range(DAY_START_H, DAY_END_H + 1) if h in speeds]
        if day_speeds:
            reasons.append(f"Wind {min(day_speeds):.0f}-{max(day_speeds):.0f} kn, kein passendes Fenster")
    return f"{label}: ✗ ({'; '.join(reasons) or 'Bedingungen passen nicht'})"


def get_ostsee_block() -> str:
    """Prompt-Block mit den Ostsee-Bedingungen; leerer String bei Fehlern
    oder außerhalb der Saison (Mai-Oktober)."""
    if dt.date.today().month not in SWIM_MONTHS:
        return ""

    if _cache["block"] is not None and time.time() - _cache["ts"] < CACHE_MAX_AGE_S:
        return _cache["block"]

    try:
        lat, lon = _get_location()
        marine, wind = _fetch(lat, lon)
        sst_by_day = _by_date_hour(marine["hourly"], "sea_surface_temperature")
        speed_by_day = _by_date_hour(wind["hourly"], "windspeed_10m")
        dir_by_day = _by_date_hour(wind["hourly"], "winddirection_10m")
    except Exception:
        return _cache["block"] or ""

    lines = ["--- OSTSEE-FREIWASSER (Warnemünde, nächste 7 Tage) ---"]
    lines.append(
        "Kriterien des Athleten: Wasser > 20°C UND Wind ablandig (aus S, hier "
        "max. 15 kn Sicherheitsdeckel) ODER Wind ≤ 5 kn. Fenster = "
        "zusammenhängende Stunden mit passendem Wind (8-20 Uhr, min. 2 h):"
    )
    for date_str in sorted(speed_by_day):
        sst_hours = sst_by_day.get(date_str, {})
        # Nachmittagswert (14 Uhr) als repräsentative Badetemperatur
        sst = sst_hours.get(14) or (max(sst_hours.values()) if sst_hours else None)
        lines.append(_build_day_line(date_str, sst,
                                     speed_by_day[date_str],
                                     dir_by_day.get(date_str, {})))
    lines.append(
        "(Ostsee-Einheiten inkl. Fahrzeit als Gesamtblock planen und bevorzugt "
        "auf das Wochenende legen — siehe Vorlieben des Athleten.)"
    )

    block = "\n".join(lines)
    _cache.update(ts=time.time(), block=block)
    return block
