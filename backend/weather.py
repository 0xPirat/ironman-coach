"""Open-Meteo weather integration — no API key required.

Fetches a 7-day daily forecast + current-hour conditions for the athlete's
location.  Results are cached in the DB (table: weather_cache) for up to 30
minutes; if the API is unreachable the last cached forecast is served with
a `stale` flag instead of failing.

Standort-Fallback: Rostock (54.0924, 12.0991).
Konfigurierbar via athlete_config keys  weather_lat / weather_lon.
"""
from __future__ import annotations

import datetime as dt
from typing import Any

import requests

from .db import database as db

# ---------------------------------------------------------------------------
# WMO weather-code → human-readable label (German)
# ---------------------------------------------------------------------------
_WMO_LABELS: dict[int, str] = {
    0: "Sonnig",
    1: "Überwiegend sonnig",
    2: "Teilweise bewölkt",
    3: "Bedeckt",
    45: "Neblig",
    48: "Reifnebel",
    51: "Leichter Nieselregen",
    53: "Nieselregen",
    55: "Starker Nieselregen",
    61: "Leichter Regen",
    63: "Regen",
    65: "Starker Regen",
    71: "Leichter Schnee",
    73: "Schnee",
    75: "Starker Schnee",
    77: "Schneekörner",
    80: "Leichte Regenschauer",
    81: "Regenschauer",
    82: "Starke Regenschauer",
    85: "Schneeschauer",
    86: "Starke Schneeschauer",
    95: "Gewitter",
    96: "Gewitter mit Hagel",
    99: "Gewitter mit starkem Hagel",
}

_THUNDERSTORM_CODES = {95, 96, 99}

DEFAULT_LAT = 54.0924
DEFAULT_LON = 12.0991

# Open-Meteo model runs refresh roughly hourly; 30 min keeps us current
# without hammering the (free, keyless) API.
CACHE_MAX_AGE_S = 30 * 60

OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"


def _wmo_label(code: int) -> str:
    return _WMO_LABELS.get(int(code), f"Wetterlage {code}")


def _is_thunderstorm(code: int) -> bool:
    return int(code) in _THUNDERSTORM_CODES


def _get_location() -> tuple[float, float]:
    try:
        lat = float(db.get_athlete_config("weather_lat", str(DEFAULT_LAT)))
        lon = float(db.get_athlete_config("weather_lon", str(DEFAULT_LON)))
        return lat, lon
    except Exception:
        return DEFAULT_LAT, DEFAULT_LON


def _fetch_from_api(lat: float, lon: float) -> dict[str, Any]:
    """Call Open-Meteo and return the raw JSON response."""
    params = {
        "latitude": lat,
        "longitude": lon,
        "timezone": "auto",
        # Daily variables (7-day forecast)
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "precipitation_probability_max",
            "weathercode",
            "windspeed_10m_max",
            "uv_index_max",
        ],
        # Hourly variables (for current conditions — we pick the matching hour)
        "hourly": [
            "temperature_2m",
            "precipitation",
            "weathercode",
            "windspeed_10m",
        ],
        "forecast_days": 7,
        "wind_speed_unit": "kmh",
    }
    resp = requests.get(OPEN_METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _parse_current(hourly: dict[str, Any], timezone_offset_seconds: int) -> dict[str, Any]:
    """Extract the closest-hour values from the hourly block."""
    # Find the index whose timestamp is closest to now (local time).
    now_utc = dt.datetime.utcnow()
    now_local = now_utc + dt.timedelta(seconds=timezone_offset_seconds)
    target_hour = now_local.replace(minute=0, second=0, microsecond=0)
    iso_target = target_hour.strftime("%Y-%m-%dT%H:%M")

    times: list[str] = hourly["time"]
    try:
        idx = times.index(iso_target)
    except ValueError:
        # Fallback: find the closest index
        idx = min(range(len(times)),
                  key=lambda i: abs(dt.datetime.fromisoformat(times[i]) - target_hour))

    return {
        "temp_c": round(hourly["temperature_2m"][idx], 1),
        "description": _wmo_label(hourly["weathercode"][idx]),
        "code": int(hourly["weathercode"][idx]),
        "wind_kmh": round(hourly["windspeed_10m"][idx], 1),
        "precip_mm": round(hourly["precipitation"][idx], 1),
    }


def _parse_forecast(daily: dict[str, Any]) -> list[dict[str, Any]]:
    """Build the 7-day forecast list."""
    weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    result = []
    for i, date_str in enumerate(daily["time"]):
        code = daily["weathercode"][i]
        precip_prob = daily["precipitation_probability_max"][i] or 0
        wind_max = daily["windspeed_10m_max"][i] or 0.0
        thunder = _is_thunderstorm(code)
        outdoor_suitable = (
            precip_prob < 60
            and wind_max < 50
            and not thunder
        )
        d = dt.date.fromisoformat(date_str)
        result.append({
            "date": date_str,
            "weekday": weekday_names[d.weekday()],
            "desc": _wmo_label(code),
            "code": int(code),
            "temp_max": daily["temperature_2m_max"][i],
            "temp_min": daily["temperature_2m_min"][i],
            "precip_mm": round(daily["precipitation_sum"][i] or 0.0, 1),
            "precip_prob_pct": int(precip_prob),
            "wind_max_kmh": round(wind_max, 1),
            "uv_max": daily["uv_index_max"][i] or 0.0,
            "outdoor_suitable": outdoor_suitable,
        })
    return result


def get_weather_summary(force_refresh: bool = False) -> dict[str, Any]:
    """Return current + 7-day forecast.  Uses DB cache (max 30 min staleness).

    If the API is unreachable, the last cached forecast is returned with
    stale=True rather than raising — an old forecast beats none.
    """
    if not force_refresh:
        cached = db.get_weather_cache(CACHE_MAX_AGE_S)
        if cached is not None:
            return cached

    lat, lon = _get_location()
    try:
        raw = _fetch_from_api(lat, lon)
    except Exception:  # noqa: BLE001 — network/API hiccup: serve stale cache
        stale = db.get_weather_cache(allow_stale=True)
        if stale is not None:
            stale["stale"] = True
            return stale
        raise

    # Open-Meteo returns utc_offset_seconds in the response
    tz_offset = raw.get("utc_offset_seconds", 0)
    now_local = dt.datetime.utcnow() + dt.timedelta(seconds=tz_offset)

    summary: dict[str, Any] = {
        "fetched_at": now_local.strftime("%Y-%m-%dT%H:%M"),
        "stale": False,
        "current": _parse_current(raw["hourly"], tz_offset),
        "forecast": _parse_forecast(raw["daily"]),
    }

    db.save_weather_cache(summary)
    return summary
