"""Apple-Kalender (Kalender.app) als lokale Termin-Quelle via EventKit (pyobjc).

Liest Busy-Slots direkt aus dem macOS-Kalender — keine URL nötig. Wird von
backend/gcal.py als Quelle "apple" verwendet (siehe dort: calendar_source).

Berechtigung (TCC):
  EventKit verlangt Kalender-Vollzugriff. Der Berechtigungs-Dialog erscheint
  beim ERSTEN Zugriff und hängt am aufrufenden Prozess (Terminal bzw. der
  LaunchAgent-Python-Prozess). Einmalig im Terminal ausführen und den Dialog
  mit "Erlauben" bestätigen:

      cd /Users/johannesbenedict/Desktop/ironman-coach
      PYTHONPATH=$PWD .venv/bin/python -m backend.apple_cal

  Falls kein Dialog erscheint oder der Sidecar (LaunchAgent) trotzdem keinen
  Zugriff hat: Systemeinstellungen → Datenschutz & Sicherheit → Kalender →
  dort das Terminal bzw. Python auf "Vollzugriff" stellen und den Sidecar
  neu starten.

Optionaler Kalender-Filter: athlete_config-Key `apple_cal_names` =
kommagetrennte Kalendernamen (z.B. "Privat,Uni"). Ohne Key: alle Kalender.

Bei verweigertem Zugriff: RuntimeError + Log-Zeile; gcal.py degradiert dann
auf die ICS-Quelle bzw. einen leeren Prompt-Block.
"""
from __future__ import annotations

import datetime as dt
import logging
import threading
import time
from typing import Any

from .db import database as db

log = logging.getLogger(__name__)

# EKAuthorizationStatus (macOS 14+: 3 = fullAccess, 4 = writeOnly)
_STATUS_NOT_DETERMINED = 0
_STATUS_RESTRICTED = 1
_STATUS_DENIED = 2
_STATUS_FULL_ACCESS = 3

_CFG_CAL_NAMES = "apple_cal_names"

# EKEventAvailability: Free=1 (blockiert keine Trainingszeit)
_AVAILABILITY_FREE = 1

_store = None


def _event_store():
    global _store
    if _store is None:
        import EventKit
        _store = EventKit.EKEventStore.alloc().init()
    return _store


def authorization_status() -> int:
    import EventKit
    return int(EventKit.EKEventStore.authorizationStatusForEntityType_(
        EventKit.EKEntityTypeEvent))


def request_access(timeout_s: float = 20.0) -> bool:
    """Ensure full calendar access; triggers the TCC dialog on first run.

    Pumps the runloop while waiting so the completion handler can fire when
    called from a plain (non-app) Python process."""
    import EventKit
    import Foundation

    status = authorization_status()
    if status == _STATUS_FULL_ACCESS:
        return True
    if status in (_STATUS_RESTRICTED, _STATUS_DENIED):
        log.warning("Apple-Kalender: Zugriff verweigert (TCC-Status %s). "
                    "Systemeinstellungen → Datenschutz → Kalender.", status)
        return False

    done = threading.Event()
    result: dict[str, bool] = {}

    def _cb(granted, error):  # noqa: ANN001 — ObjC completion signature
        result["granted"] = bool(granted)
        if error:
            log.warning("Apple-Kalender: EventKit-Fehler bei Zugriffsanfrage: %s", error)
        done.set()

    store = _event_store()
    if hasattr(store, "requestFullAccessToEventsWithCompletion_"):  # macOS 14+
        store.requestFullAccessToEventsWithCompletion_(_cb)
    else:  # pre-macOS-14 fallback
        store.requestAccessToEntityType_completion_(EventKit.EKEntityTypeEvent, _cb)

    deadline = time.time() + timeout_s
    while not done.is_set() and time.time() < deadline:
        Foundation.NSRunLoop.currentRunLoop().runMode_beforeDate_(
            Foundation.NSDefaultRunLoopMode,
            Foundation.NSDate.dateWithTimeIntervalSinceNow_(0.1),
        )
    if not done.is_set():
        log.warning("Apple-Kalender: Berechtigungs-Dialog nicht beantwortet "
                    "(Timeout %ss).", timeout_s)
        return False
    granted = result.get("granted", False)
    if not granted:
        log.warning(
            "Apple-Kalender: Zugriff nicht erteilt. Erschien KEIN Dialog, war es "
            "eine stille Ablehnung (Prozess ohne Calendar-Usage-Description) — "
            "einmalig aus Terminal.app ausführen: "
            "PYTHONPATH=$PWD .venv/bin/python -m backend.apple_cal")
    return granted


def _selected_calendars(store) -> Any:
    """None = all calendars; otherwise the EKCalendars matching the filter."""
    import EventKit
    try:
        raw = db.get_athlete_config(_CFG_CAL_NAMES)
    except Exception:  # noqa: BLE001
        raw = None
    if not raw:
        return None
    wanted = {n.strip() for n in raw.split(",") if n.strip()}
    cals = store.calendarsForEntityType_(EventKit.EKEntityTypeEvent)
    picked = [c for c in cals if str(c.title()) in wanted]
    return picked or None


def get_busy_days(start: dt.date, days: int) -> list[dict[str, Any]]:
    """Per-day busy slots from the Mac calendar — same shape as gcal's ICS parser.

    Raises RuntimeError when calendar access is not granted."""
    import Foundation

    if not request_access():
        raise RuntimeError(
            "Kein Zugriff auf den Apple-Kalender (TCC). Einmalig ausführen: "
            "PYTHONPATH=$PWD .venv/bin/python -m backend.apple_cal"
        )

    store = _event_store()
    end = start + dt.timedelta(days=days)
    local_tz = dt.datetime.now().astimezone().tzinfo
    start_dt = dt.datetime.combine(start, dt.time.min, tzinfo=local_tz)
    end_dt = dt.datetime.combine(end, dt.time.min, tzinfo=local_tz)

    ns_start = Foundation.NSDate.dateWithTimeIntervalSince1970_(start_dt.timestamp())
    ns_end = Foundation.NSDate.dateWithTimeIntervalSince1970_(end_dt.timestamp())
    pred = store.predicateForEventsWithStartDate_endDate_calendars_(
        ns_start, ns_end, _selected_calendars(store))
    events = store.eventsMatchingPredicate_(pred) or []

    by_day: dict[str, list[dict[str, Any]]] = {}
    for ev in events:
        try:
            if int(ev.availability()) == _AVAILABILITY_FREE:
                continue  # analog TRANSPARENT bei ICS: blockiert nichts
        except Exception:  # noqa: BLE001 — availability not supported
            pass
        title = str(ev.title() or "Termin")
        s_local = dt.datetime.fromtimestamp(ev.startDate().timeIntervalSince1970(), tz=local_tz)
        e_local = dt.datetime.fromtimestamp(ev.endDate().timeIntervalSince1970(), tz=local_tz)

        if ev.isAllDay():
            d = max(s_local.date(), start)
            last = min(e_local.date(), end - dt.timedelta(days=1))
            while d <= last:
                by_day.setdefault(d.isoformat(), []).append(
                    {"start": None, "end": None, "title": title, "all_day": True})
                d += dt.timedelta(days=1)
        else:
            key = s_local.date().isoformat()
            if start.isoformat() <= key < end.isoformat():
                by_day.setdefault(key, []).append({
                    "start": s_local.strftime("%H:%M"),
                    "end": e_local.strftime("%H:%M"),
                    "title": title,
                    "all_day": False,
                })

    weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    result = []
    for i in range(days):
        d = start + dt.timedelta(days=i)
        slots = sorted(
            by_day.get(d.isoformat(), []),
            key=lambda s: (not s["all_day"] and 1 or 0, s["start"] or ""),
        )
        result.append({"date": d.isoformat(), "weekday": weekdays[d.weekday()], "busy": slots})
    return result


if __name__ == "__main__":
    # One-time interactive grant + live smoke test (run from a terminal so the
    # TCC dialog can appear).
    logging.basicConfig(level=logging.INFO)
    print("Apple-Kalender-Zugriff anfordern (TCC-Status vorher: "
          f"{authorization_status()}) …")
    if not request_access(timeout_s=120):
        raise SystemExit(
            "Zugriff nicht erteilt. Systemeinstellungen → Datenschutz & "
            "Sicherheit → Kalender → Terminal/Python erlauben, dann erneut ausführen.")
    today = dt.date.today()
    for day in get_busy_days(today, 7):
        slots = day["busy"]
        desc = ", ".join(
            ("ganztägig" if s["all_day"] else f"{s['start']}-{s['end']}") + f" ({s['title']})"
            for s in slots
        ) or "frei"
        print(f"{day['weekday']} {day['date']}: {desc}")
    print("OK — Apple-Kalender-Quelle funktioniert.")
