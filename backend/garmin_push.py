"""Push structured workouts to Garmin Connect (workout-service).

The coach turns a planned workout into Garmin's workout JSON, uploads it
(POST /workout-service/workout), schedules it on the target date
(POST /workout-service/schedule/{workoutId}) and remembers the Garmin IDs on
the planned_workouts row. The watch picks the workout up on its next Garmin
Connect sync (Training > Workouts / calendar).

Reuses the authenticated client from garmin_sync (Keychain credentials +
persisted OAuth tokens in ~/.garminconnect).
"""
from __future__ import annotations

import datetime as dt
import json
from typing import Any

from .db import database as db
from .garmin_sync import _client

# Numeric bounds behind coach_prompt.HR_ZONES — keep the two in sync.
HR_ZONE_BOUNDS: dict[str, tuple[int, int]] = {
    "Z1": (90, 120),
    "Z2": (120, 140),
    "Z3": (140, 160),
    "Z4": (160, 180),
    "Z5": (180, 200),
}

# workout-service sport types (NOT the activity-service ones: swimming is 4
# here; 3 gets normalized to "other" on upload).
_SPORT_TYPES: dict[str, dict[str, Any]] = {
    "run": {"sportTypeId": 1, "sportTypeKey": "running"},
    "bike": {"sportTypeId": 2, "sportTypeKey": "cycling"},
    "swim": {"sportTypeId": 4, "sportTypeKey": "swimming"},
    "strength": {"sportTypeId": 5, "sportTypeKey": "strength_training"},
    "other": {"sportTypeId": 3, "sportTypeKey": "other"},
}

_STEP_TYPES: dict[str, dict[str, Any]] = {
    "warmup": {"stepTypeId": 1, "stepTypeKey": "warmup"},
    "cooldown": {"stepTypeId": 2, "stepTypeKey": "cooldown"},
    "interval": {"stepTypeId": 3, "stepTypeKey": "interval"},
    "recovery": {"stepTypeId": 4, "stepTypeKey": "recovery"},
    "rest": {"stepTypeId": 5, "stepTypeKey": "rest"},
    "repeat": {"stepTypeId": 6, "stepTypeKey": "repeat"},
}

_NO_TARGET = {"workoutTargetTypeId": 1, "workoutTargetTypeKey": "no.target", "displayOrder": 1}


def _parse_pace(p: str | float) -> float:
    """'5:30' (min/km) or minutes-per-km float -> speed in m/s."""
    if isinstance(p, str):
        parts = p.strip().split(":")
        sec_per_km = int(parts[0]) * 60 + (int(parts[1]) if len(parts) > 1 else 0)
    else:
        sec_per_km = float(p) * 60.0
    if sec_per_km <= 0:
        raise ValueError(f"invalid pace: {p!r}")
    return 1000.0 / sec_per_km


def _target_for(step: dict[str, Any]) -> dict[str, Any]:
    """Map a simple step spec to a Garmin target block (HR zone / pace / power)."""
    zone = (step.get("zone") or "").upper().strip()
    if zone in HR_ZONE_BOUNDS:
        low, high = HR_ZONE_BOUNDS[zone]
        return {
            "targetType": {"workoutTargetTypeId": 4, "workoutTargetTypeKey": "heart.rate.zone", "displayOrder": 4},
            "targetValueOne": low,
            "targetValueTwo": high,
        }
    if step.get("pace_slow") and step.get("pace_fast"):
        # speed targets are m/s, low value first
        v1 = _parse_pace(step["pace_slow"])
        v2 = _parse_pace(step["pace_fast"])
        return {
            "targetType": {"workoutTargetTypeId": 5, "workoutTargetTypeKey": "speed.zone", "displayOrder": 5},
            "targetValueOne": min(v1, v2),
            "targetValueTwo": max(v1, v2),
        }
    if step.get("power_low") and step.get("power_high"):
        return {
            "targetType": {"workoutTargetTypeId": 2, "workoutTargetTypeKey": "power.zone", "displayOrder": 2},
            "targetValueOne": float(step["power_low"]),
            "targetValueTwo": float(step["power_high"]),
        }
    return {"targetType": dict(_NO_TARGET)}


def _end_condition(step: dict[str, Any]) -> tuple[dict[str, Any], float]:
    if step.get("distance_m"):
        return (
            {"conditionTypeId": 1, "conditionTypeKey": "distance", "displayOrder": 1, "displayable": True},
            float(step["distance_m"]),
        )
    minutes = step.get("duration_min") or 10
    return (
        {"conditionTypeId": 2, "conditionTypeKey": "time", "displayOrder": 2, "displayable": True},
        round(float(minutes) * 60.0, 1),
    )


class _StepCounter:
    def __init__(self) -> None:
        self.n = 0

    def next(self) -> int:
        self.n += 1
        return self.n


def _build_step(step: dict[str, Any], counter: _StepCounter, default_type: str) -> dict[str, Any]:
    """One simple step spec -> ExecutableStepDTO or RepeatGroupDTO."""
    repeats = int(step.get("repeats") or 1)
    inner_steps = step.get("steps")

    if repeats > 1 or (inner_steps and isinstance(inner_steps, list)):
        order = counter.next()
        children_spec = inner_steps or [{k: v for k, v in step.items() if k not in ("repeats", "steps")}]
        children = [_build_step(s, counter, "interval") for s in children_spec]
        return {
            "type": "RepeatGroupDTO",
            "stepOrder": order,
            "stepType": {**_STEP_TYPES["repeat"], "displayOrder": 6},
            "numberOfIterations": max(repeats, 1),
            "smartRepeat": False,
            "endCondition": {"conditionTypeId": 7, "conditionTypeKey": "iterations", "displayOrder": 7, "displayable": False},
            "endConditionValue": float(max(repeats, 1)),
            "workoutSteps": children,
        }

    kind = (step.get("step_type") or default_type or "interval").lower()
    st = _STEP_TYPES.get(kind, _STEP_TYPES["interval"])
    cond, cond_value = _end_condition(step)
    dto: dict[str, Any] = {
        "type": "ExecutableStepDTO",
        "stepOrder": counter.next(),
        "stepType": {**st, "displayOrder": st["stepTypeId"]},
        "endCondition": cond,
        "endConditionValue": cond_value,
        **_target_for(step),
    }
    desc = step.get("note") or step.get("description")
    if desc:
        dto["description"] = str(desc)[:512]
    return dto


def build_workout_json(sport: str, title: str, steps: list[dict[str, Any]],
                       description: str | None = None,
                       pool_length_m: float = 25.0) -> dict[str, Any]:
    """Build Garmin workout-service JSON from a simple step list.

    Step spec (all optional except one of duration_min/distance_m):
      step_type: warmup|interval|recovery|rest|cooldown
      duration_min | distance_m, zone (Z1-Z5), pace_fast/pace_slow ('4:45' min/km),
      power_low/power_high (W), note, repeats (int), steps (nested, for repeats)
    """
    sport_key = sport.lower().strip()
    sport_type = dict(_SPORT_TYPES.get(sport_key, _SPORT_TYPES["other"]))
    counter = _StepCounter()

    dtos: list[dict[str, Any]] = []
    for i, s in enumerate(steps):
        default = "warmup" if i == 0 and len(steps) > 1 else (
            "cooldown" if i == len(steps) - 1 and len(steps) > 1 else "interval")
        dtos.append(_build_step(s, counter, default))
    if not dtos:
        raise ValueError("workout needs at least one step")

    def _sum_secs(items: list[dict[str, Any]]) -> float:
        total = 0.0
        for d in items:
            if d.get("type") == "RepeatGroupDTO":
                total += d.get("numberOfIterations", 1) * _sum_secs(d["workoutSteps"])
            elif (d.get("endCondition") or {}).get("conditionTypeKey") == "time":
                total += d.get("endConditionValue") or 0.0
            elif (d.get("endCondition") or {}).get("conditionTypeKey") == "distance":
                total += (d.get("endConditionValue") or 0.0) / 2.0  # rough: ~2 m/s
        return total

    workout: dict[str, Any] = {
        "workoutName": title,
        "sportType": sport_type,
        "estimatedDurationInSecs": int(_sum_secs(dtos)) or 600,
        "workoutSegments": [{
            "segmentOrder": 1,
            "sportType": dict(sport_type),
            "workoutSteps": dtos,
        }],
    }
    if description:
        workout["description"] = description[:1024]
    if sport_key == "swim":
        workout["poolLength"] = pool_length_m
        workout["poolLengthUnit"] = {"unitId": 1, "unitKey": "meter", "factor": 100.0}
    return workout


# ---------------------------------------------------------------------------
# DB plumbing: remember Garmin IDs on the planned workout row.
# ---------------------------------------------------------------------------

def _ensure_columns() -> None:
    """Add garmin_workout_id / garmin_schedule_id to planned_workouts if missing.

    schema.sql only creates tables when absent, so existing DBs need this
    runtime ALTER (idempotent via PRAGMA check)."""
    with db.get_conn() as conn:
        cols = {r["name"] for r in conn.execute("PRAGMA table_info(planned_workouts)")}
        if "garmin_workout_id" not in cols:
            conn.execute("ALTER TABLE planned_workouts ADD COLUMN garmin_workout_id TEXT")
        if "garmin_schedule_id" not in cols:
            conn.execute("ALTER TABLE planned_workouts ADD COLUMN garmin_schedule_id TEXT")


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def push_workout(sport: str, title: str, date: str,
                 steps: list[dict[str, Any]],
                 description: str | None = None,
                 planned_workout_id: int | None = None,
                 pool_length_m: float = 25.0) -> dict[str, Any]:
    """Upload a structured workout to Garmin Connect and schedule it on `date`.

    Returns {"garmin_workout_id", "garmin_schedule_id", "scheduled": bool}.
    Raises RuntimeError with a readable message on auth/API failure.
    """
    dt.date.fromisoformat(date)  # validate early
    payload = build_workout_json(sport, title, steps, description, pool_length_m)

    client = _client()
    try:
        created = client.upload_workout(payload)
    except Exception as e:  # noqa: BLE001
        raise RuntimeError(f"Garmin workout upload failed: {e}") from e
    workout_id = created.get("workoutId")
    if not workout_id:
        raise RuntimeError(f"Garmin returned no workoutId: {json.dumps(created)[:400]}")

    schedule_id: str | None = None
    scheduled = False
    try:
        sched = client.schedule_workout(workout_id, date)
        schedule_id = str(sched.get("workoutScheduleId") or sched.get("id") or "") or None
        scheduled = True
    except Exception as e:  # noqa: BLE001
        # Workout exists in the library even if scheduling failed — report both.
        return {
            "garmin_workout_id": str(workout_id),
            "garmin_schedule_id": None,
            "scheduled": False,
            "schedule_error": str(e),
        }
    finally:
        if planned_workout_id is not None:
            _ensure_columns()
            db.update_workout(planned_workout_id, {
                "garmin_workout_id": str(workout_id),
                "garmin_schedule_id": schedule_id,
            })

    return {
        "garmin_workout_id": str(workout_id),
        "garmin_schedule_id": schedule_id,
        "scheduled": scheduled,
    }


def push_planned_workout(planned_workout_id: int) -> dict[str, Any]:
    """Push an existing planned_workouts row to Garmin Connect.

    Uses structured_steps JSON when present; otherwise builds a single steady
    step from duration_min + target_zone. Replaces a previously pushed version
    (unschedule + delete) so the calendar never shows duplicates.
    """
    rows = [w for w in db.get_plan("0000-01-01", "9999-12-31") if w["id"] == planned_workout_id]
    if not rows:
        raise RuntimeError(f"Geplante Einheit {planned_workout_id} nicht gefunden.")
    w = rows[0]

    if w["sport"] not in _SPORT_TYPES:
        raise RuntimeError(
            f"Sport '{w['sport']}' kann nicht als Garmin-Workout gepusht werden "
            f"(unterstützt: {', '.join(k for k in _SPORT_TYPES if k != 'other')})."
        )

    steps: list[dict[str, Any]] = []
    if w.get("structured_steps"):
        try:
            raw = json.loads(w["structured_steps"])
            if isinstance(raw, list):
                steps = raw
        except (ValueError, TypeError):
            steps = []
    if not steps:
        steps = [{
            "step_type": "interval",
            "duration_min": w.get("duration_min") or 60,
            "zone": (w.get("target_zone") or "").split("-")[0],
            "note": (w.get("content") or "")[:200] or None,
        }]

    # drop a stale previous push of this row (best effort)
    _ensure_columns()
    if w.get("garmin_workout_id"):
        remove_pushed_workout(planned_workout_id, missing_ok=True)

    title = w.get("title") or f"{w['sport'].capitalize()} {w['date']}"
    return push_workout(
        sport=w["sport"], title=title, date=w["date"], steps=steps,
        description=w.get("content"), planned_workout_id=planned_workout_id,
    )


def remove_pushed_workout(planned_workout_id: int, missing_ok: bool = False) -> dict[str, Any]:
    """Unschedule + delete the Garmin copy of a previously pushed workout."""
    _ensure_columns()
    with db.get_conn() as conn:
        row = conn.execute(
            "SELECT garmin_workout_id, garmin_schedule_id FROM planned_workouts WHERE id=?",
            (planned_workout_id,),
        ).fetchone()
    if not row or not row["garmin_workout_id"]:
        if missing_ok:
            return {"removed": False, "reason": "kein Garmin-Workout hinterlegt"}
        raise RuntimeError(f"Einheit {planned_workout_id} hat kein gepushtes Garmin-Workout.")

    client = _client()
    for fn in (
        (lambda: client.unschedule_workout(row["garmin_schedule_id"])) if row["garmin_schedule_id"] else None,
        lambda: client.delete_workout(row["garmin_workout_id"]),
    ):
        if fn is None:
            continue
        try:
            fn()
        except Exception:  # noqa: BLE001 — already gone on Garmin's side is fine
            pass
    db.update_workout(planned_workout_id, {"garmin_workout_id": None, "garmin_schedule_id": None})
    return {"removed": True}
