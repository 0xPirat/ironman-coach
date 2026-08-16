"""Garmin Connect sync for the Forerunner 965.

Pulls the last N days of wellness metrics + activities into SQLite using
`python-garminconnect`. Credentials come from the macOS Keychain — never
plaintext. Network egress only to Garmin; nothing is exposed inbound.

This module degrades gracefully: if garminconnect isn't installed or login
fails, sync raises a clear error the API layer turns into a 4xx/5xx, but the
rest of the app keeps working with whatever is already in the DB.
"""
from __future__ import annotations

import datetime as dt
import json
import logging
import os
from typing import Any

from .credentials import get_garmin_credentials
from .db import database as db

log = logging.getLogger(__name__)

# Garmin OAuth tokens (valid ~1 year) persisted here so a sync doesn't need a
# full SSO login every time — logins are slow and rate-limited (HTTP 429).
TOKEN_STORE = os.path.expanduser("~/.garminconnect")

# Garmin sport-type strings -> our normalized sports.
_SPORT_MAP = {
    "running": "run",
    "trail_running": "run",
    "treadmill_running": "run",
    "cycling": "bike",
    "road_biking": "bike",
    "indoor_cycling": "bike",
    "virtual_ride": "bike",
    "lap_swimming": "swim",
    "open_water_swimming": "swim",
    "swimming": "swim",
    "strength_training": "strength",
    "fitness_equipment": "strength",
}


def _normalize_sport(garmin_type: str | None) -> str:
    if not garmin_type:
        return "other"
    return _SPORT_MAP.get(garmin_type.lower(), "other")


def _client():
    """Authenticate and return a Garmin client.

    Imported lazily so the backend imports cleanly even if garminconnect is
    not yet installed.
    """
    try:
        from garminconnect import Garmin
    except ImportError as e:  # pragma: no cover
        raise RuntimeError(
            "python-garminconnect not installed. `pip install garminconnect`."
        ) from e

    email, password = get_garmin_credentials()
    if not email or not password:
        raise RuntimeError(
            "No Garmin credentials in Keychain. Run `python -m backend.credentials` "
            "to store them."
        )
    client = Garmin(email, password)
    # login(tokenstore) resumes saved tokens when valid (fast, no SSO
    # round-trip, immune to login rate limits); otherwise it does a full
    # credential login and persists fresh tokens to the store itself.
    client.login(TOKEN_STORE)
    return client


def _safe(d: dict[str, Any] | None, *keys: str) -> Any:
    """Return the first present, non-None key from a dict."""
    if not d:
        return None
    for k in keys:
        if d.get(k) is not None:
            return d[k]
    return None


def sync_metrics_for_day(client, day: dt.date) -> dict[str, Any]:
    """Pull wellness metrics for a single day and upsert into daily_metrics."""
    ds = day.isoformat()
    record: dict[str, Any] = {"date": ds}

    # Each call is wrapped: Garmin endpoints occasionally 404 for days with no data.
    # A gap and a broken endpoint look identical from the outside, so log the
    # exception — silently swallowing it hides real outages behind "no data".
    def _try(fn, name: str):
        try:
            return fn()
        except Exception as e:  # noqa: BLE001 — tolerate per-endpoint gaps
            log.warning("Garmin %s failed for %s: %s: %s", name, ds, type(e).__name__, e)
            return None

    rhr = _try(lambda: client.get_rhr_day(ds), "rhr")
    if rhr:
        metrics = (rhr.get("allMetrics", {}) or {}).get("metricsMap", {})
        rhr_vals = metrics.get("WELLNESS_RESTING_HEART_RATE")
        if rhr_vals:
            record["rhr"] = _safe(rhr_vals[0], "value")

    hrv = _try(lambda: client.get_hrv_data(ds), "hrv")
    if hrv and hrv.get("hrvSummary"):
        summ = hrv["hrvSummary"]
        record["hrv"] = _safe(summ, "lastNightAvg", "weeklyAvg")
        record["hrv_status"] = _safe(summ, "status")

    sleep = _try(lambda: client.get_sleep_data(ds), "sleep")
    if sleep:
        daily = sleep.get("dailySleepDTO", {}) or {}
        secs = _safe(daily, "sleepTimeSeconds")
        if secs:
            record["sleep_hours"] = round(secs / 3600.0, 2)
        scores = daily.get("sleepScores", {}) or {}
        record["sleep_score"] = _safe(scores.get("overall", {}), "value")
        record["sleep_quality"] = _safe(scores.get("overall", {}), "qualifierKey")

    bb = _try(lambda: client.get_body_battery(ds, ds), "body_battery")
    if bb and isinstance(bb, list) and bb:
        levels = bb[0].get("bodyBatteryValuesArray") or []
        vals = [p[1] for p in levels if len(p) > 1 and p[1] is not None]
        if vals:
            record["body_battery"] = max(vals)
            record["body_battery_low"] = min(vals)

    tr = _try(lambda: client.get_training_readiness(ds), "training_readiness")
    if tr and isinstance(tr, list) and tr:
        record["training_readiness"] = _safe(tr[0], "score")

    ts = _try(lambda: client.get_training_status(ds), "training_status")
    if ts:
        most_recent = ts.get("mostRecentTrainingStatus", {}) or {}
        latest = (most_recent.get("latestTrainingStatusData") or {})
        for _, v in latest.items():
            record["training_status"] = _safe(v, "trainingStatusFeedbackPhrase", "trainingStatus")
            record["training_load"] = _safe(v, "loadTunnelMin", "weeklyTrainingLoad")
            break
        vo2 = ts.get("mostRecentVO2Max", {}) or {}
        generic = (vo2.get("generic") or {})
        record["vo2max"] = _safe(generic, "vo2MaxValue")

    stress = _try(lambda: client.get_stress_data(ds), "stress")
    if stress:
        record["stress"] = _safe(stress, "avgStressLevel")

    # Decide "did Garmin actually give us anything" BEFORE adding raw_json —
    # that field is set unconditionally and would otherwise count itself, making
    # every day look like a success even when the watch delivered nothing.
    has_data = _has_wellness(record)

    record["raw_json"] = json.dumps(
        {"rhr": bool(rhr), "hrv": bool(hrv), "sleep": bool(sleep)}, ensure_ascii=False
    )

    if has_data:
        db.upsert("daily_metrics", ["date"], record)
    else:
        log.info("Garmin: keine Wellness-Daten für %s", ds)
    return record


def sync_activities(client, start: dt.date, end: dt.date) -> int:
    """Pull activities in [start, end] and upsert into activities."""
    try:
        acts = client.get_activities_by_date(start.isoformat(), end.isoformat())
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Garmin activities fetch failed: {e}") from e

    count = 0
    for a in acts or []:
        start_iso = a.get("startTimeLocal") or a.get("startTimeGMT")
        day = (start_iso or "")[:10] or end.isoformat()
        rec = {
            "garmin_id": str(a.get("activityId")),
            "date": day,
            "start_time": start_iso,
            "sport": _normalize_sport(((a.get("activityType") or {}).get("typeKey"))),
            "title": a.get("activityName"),
            "duration_min": round((a.get("duration") or 0) / 60.0, 1) or None,
            "distance_km": round((a.get("distance") or 0) / 1000.0, 2) or None,
            "avg_hr": a.get("averageHR"),
            "max_hr": a.get("maxHR"),
            "avg_power": a.get("avgPower"),
            "elevation_gain_m": a.get("elevationGain"),
            "calories": a.get("calories"),
            "training_load": a.get("activityTrainingLoad"),
            "raw_json": json.dumps(a, ensure_ascii=False),
        }
        db.upsert("activities", ["garmin_id"], {k: v for k, v in rec.items() if v is not None})
        count += 1
    return count


def _has_wellness(rec: dict[str, Any]) -> bool:
    """True when Garmin returned at least one real measurement for the day.

    `date` is ours and `raw_json` is written unconditionally, so neither counts.
    Presence of a key isn't enough either: on a day the watch never uploaded,
    Garmin still answers with an envelope, and keys like sleep_score, vo2max and
    stress get set to None — so only non-None values count as data.
    """
    return any(
        v is not None for k, v in rec.items() if k not in ("date", "raw_json")
    )


def sync_last_n_days(days: int = 14) -> dict[str, Any]:
    """Top-level sync entry point. Returns a small summary dict."""
    db.init_db()
    client = _client()
    today = dt.date.today()
    start = today - dt.timedelta(days=days)

    metric_days = 0
    empty_days: list[str] = []
    for i in range(days + 1):
        d = start + dt.timedelta(days=i)
        rec = sync_metrics_for_day(client, d)
        if _has_wellness(rec):
            metric_days += 1
        else:
            empty_days.append(d.isoformat())

    act_count = sync_activities(client, start, today)
    recompute_pmc(days_back=120)  # keep CTL/ATL/TSB fresh after a sync

    upload = None
    try:
        ms = (client.get_device_last_used() or {}).get("lastUsedDeviceUploadTime")
        if ms:
            upload = dt.datetime.fromtimestamp(ms / 1000).isoformat(timespec="seconds")
    except Exception as e:  # noqa: BLE001 — purely informational
        log.warning("Garmin device_last_used failed: %s: %s", type(e).__name__, e)

    if empty_days:
        log.warning(
            "Garmin: %d von %d Tagen ohne Wellness-Daten (%s) — letzter Uhren-Upload: %s",
            len(empty_days), days + 1, ", ".join(empty_days), upload or "unbekannt",
        )

    return {
        "synced_days": days,
        "metric_days_with_data": metric_days,
        "days_without_data": empty_days,
        "last_device_upload": upload,
        "activities_upserted": act_count,
        "from": start.isoformat(),
        "to": today.isoformat(),
    }


# ---------------------------------------------------------------------------
# Performance Management Chart (CTL/ATL/TSB) — computed from activity load/TSS.
# CTL = 42-day EWMA, ATL = 7-day EWMA, TSB = CTL(yesterday) - ATL(yesterday).
# Uses training_load as the daily stress proxy when TSS isn't present.
# ---------------------------------------------------------------------------

def recompute_pmc(days_back: int = 120) -> None:
    today = dt.date.today()
    start = today - dt.timedelta(days=days_back)
    acts = db.get_activities(start.isoformat(), today.isoformat())

    # daily load total
    daily_load: dict[str, float] = {}
    for a in acts:
        load = a.get("tss") or a.get("training_load") or 0.0
        daily_load[a["date"]] = daily_load.get(a["date"], 0.0) + float(load or 0.0)

    ctl = atl = 0.0
    ctl_k = 2.0 / (42 + 1)
    atl_k = 2.0 / (7 + 1)
    for i in range(days_back + 1):
        d = (start + dt.timedelta(days=i)).isoformat()
        load = daily_load.get(d, 0.0)
        tsb = ctl - atl  # form is yesterday's fitness minus fatigue
        ctl = ctl + ctl_k * (load - ctl)
        atl = atl + atl_k * (load - atl)
        db.upsert(
            "daily_metrics", ["date"],
            {"date": d, "ctl": round(ctl, 1), "atl": round(atl, 1), "tsb": round(tsb, 1)},
        )


if __name__ == "__main__":
    print(json.dumps(sync_last_n_days(14), indent=2))
