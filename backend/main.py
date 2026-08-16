"""FastAPI sidecar — localhost by default, authenticated mobile mode opt-in.

Exposes REST for the data views + a streaming chat endpoint that runs the
coaching agent. The normal desktop process binds only to 127.0.0.1. The
separate ``backend.mobile_server`` entry point can expose the same API on a
trusted LAN and requires Bearer authentication. Garmin/Claude calls go outbound
only.

Run standalone for testing:
    cd /Users/johannesbenedict/ironman-coach
    .venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload
"""

from __future__ import annotations

import datetime as dt
import json
import os
from typing import Any

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, SecretStr

from .agent.coach_agent import stream_coach_reply
from .db import database as db
from .mobile_auth import TOKEN_ENV, bearer_is_valid, validate_mobile_token
from .paths import resource_root

app = FastAPI(title="Sport Coach Sidecar", version="0.2.0")


@app.middleware("http")
async def mobile_bearer_auth(request: Request, call_next):
    """Protect every route when the opt-in mobile token is present.

    The normal localhost sidecar does not set IRONMAN_MOBILE_TOKEN and keeps
    its existing behaviour. The separate mobile server validates the token
    before it binds to a LAN interface.
    """
    configured = os.environ.get(TOKEN_ENV)
    if configured is not None:
        try:
            expected = validate_mobile_token(configured)
        except ValueError:
            return JSONResponse(
                status_code=503,
                content={"detail": "Mobile-API ist unsicher konfiguriert."},
            )
        if not bearer_is_valid(request.headers.get("Authorization"), expected):
            return JSONResponse(
                status_code=401,
                content={"detail": "Gültiger Bearer-Token erforderlich."},
                headers={"WWW-Authenticate": "Bearer"},
            )
    return await call_next(request)


@app.on_event("startup")
def _startup() -> None:
    db.init_db()


# ---------------------------------------------------------------------------
# Health / meta
# ---------------------------------------------------------------------------
@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "sport-coach", "date": db.today_str()}


@app.get("/app-info")
def app_info() -> dict[str, Any]:
    research = resource_root() / "research"
    research_files = list(research.rglob("*.md")) if research.exists() else []
    return {
        "version": app.version,
        "platform": __import__("platform").system(),
        "database": str(db.DB_PATH.parent),
        "research_files": len(research_files),
        "research_ready": bool(research_files),
    }


# ---------------------------------------------------------------------------
# Metrics / plan / activities
# ---------------------------------------------------------------------------
def _default_range(start: str | None, end: str | None, days: int = 7) -> tuple[str, str]:
    e = dt.date.fromisoformat(end) if end else dt.date.today()
    s = dt.date.fromisoformat(start) if start else e - dt.timedelta(days=days)
    return s.isoformat(), e.isoformat()


@app.get("/metrics")
def metrics(start: str | None = None, end: str | None = None) -> list[dict[str, Any]]:
    s, e = _default_range(start, end, days=30)
    return db.get_metrics(s, e)


@app.get("/plan")
def plan(start: str | None = None, end: str | None = None) -> list[dict[str, Any]]:
    s, e = _default_range(start, end, days=7)
    return db.get_plan(s, e)


@app.get("/activities")
def activities(start: str | None = None, end: str | None = None) -> list[dict[str, Any]]:
    s, e = _default_range(start, end, days=30)
    return db.get_activities(s, e)


@app.get("/today")
def today(date: str | None = None) -> dict[str, Any]:
    d = date or db.today_str()
    return {
        "date": d,
        "plan": db.get_plan(d, d),
        "metrics": db.get_metrics(d, d),
        "activities": db.get_activities(d, d),
        "checkin": db.get_checkin(d),
        "day_status": db.get_day_status(d),
    }


# ---------------------------------------------------------------------------
# Daily check-in (subjective data)
# ---------------------------------------------------------------------------
class CheckinIn(BaseModel):
    date: str | None = None
    soreness: int | None = None
    pain_location: str | None = None
    pain_level: int | None = None
    motivation: int | None = None
    mental_energy: int | None = None
    available_time: int | None = None
    life_stress: int | None = None
    notes: str | None = None


@app.post("/checkin")
def post_checkin(body: CheckinIn) -> dict[str, Any]:
    data = body.model_dump(exclude_none=True)
    data.setdefault("date", db.today_str())
    db.upsert("daily_checkin", ["date"], data)
    return {"saved": True, "date": data["date"]}


@app.get("/checkin")
def get_checkin(date: str | None = None) -> dict[str, Any]:
    d = date or db.today_str()
    c = db.get_checkin(d)
    if not c:
        raise HTTPException(404, f"Kein Check-in für {d}")
    return c


# ---------------------------------------------------------------------------
# Workout CRUD (also usable from the UI directly, not just the coach)
# ---------------------------------------------------------------------------
class WorkoutIn(BaseModel):
    date: str
    sport: str
    title: str | None = None
    duration_min: int | None = None
    distance_km: float | None = None
    target_zone: str | None = None
    content: str | None = None
    priority: str | None = None
    structured_steps: str | None = None
    status: str | None = None


@app.post("/workouts")
def create_workout(body: WorkoutIn) -> dict[str, Any]:
    wid = db.create_workout(body.model_dump(exclude_none=True))
    return {"id": wid}


@app.patch("/workouts/{workout_id}")
def patch_workout(workout_id: int, body: dict[str, Any]) -> dict[str, Any]:
    if not db.update_workout(workout_id, {k: v for k, v in body.items() if v is not None}):
        raise HTTPException(404, "Workout not found")
    return {"updated": True}


@app.delete("/workouts/{workout_id}")
def remove_workout(workout_id: int) -> dict[str, Any]:
    if not db.delete_workout(workout_id):
        raise HTTPException(404, "Workout not found")
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Athlete Goals
# ---------------------------------------------------------------------------
class GoalIn(BaseModel):
    title: str
    sport: str
    category: str | None = "endurance"
    event_date: str | None = None
    description: str | None = None
    target_metric: str | None = None
    priority: int | None = 2
    status: str | None = "active"


@app.get("/goals")
def list_goals(status: str = "active") -> list[dict[str, Any]]:
    if status == "all":
        return db.get_all_goals()
    return db.get_goals(status)


@app.post("/goals")
def create_goal(body: GoalIn) -> dict[str, Any]:
    data = body.model_dump(exclude_none=True)
    gid = db.create_goal(data)
    return {"id": gid, **data}


@app.patch("/goals/{goal_id}")
def patch_goal(goal_id: int, body: dict[str, Any]) -> dict[str, Any]:
    if not db.update_goal(goal_id, {k: v for k, v in body.items() if v is not None}):
        raise HTTPException(404, "Goal not found")
    return {"updated": True}


@app.delete("/goals/{goal_id}")
def remove_goal(goal_id: int) -> dict[str, Any]:
    if not db.delete_goal(goal_id):
        raise HTTPException(404, "Goal not found")
    return {"deleted": True}


# ---------------------------------------------------------------------------
# Coach Memory
# ---------------------------------------------------------------------------
@app.get("/memory")
def list_memory(min_relevance: int = 1, category: str | None = None,
                limit: int = 50) -> list[dict[str, Any]]:
    return db.get_memories(min_relevance=min_relevance, category=category, limit=limit)


# ---------------------------------------------------------------------------
# Weather
# ---------------------------------------------------------------------------
@app.get("/weather")
def weather(refresh: bool = False) -> dict[str, Any]:
    """Return current weather and 7-day forecast (cached up to 30 min).

    ?refresh=true bypasses the cache and forces a fresh API fetch.
    """
    from .weather import get_weather_summary
    try:
        return get_weather_summary(force_refresh=refresh)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Wetterdaten nicht verfügbar: {exc}")


# ---------------------------------------------------------------------------
# Calendar (Google Calendar via private iCal URL — see backend/gcal.py)
# ---------------------------------------------------------------------------
@app.get("/calendar")
def calendar(days: int = 7, refresh: bool = False) -> dict[str, Any]:
    """Busy slots for the next `days` days (cached up to 30 min).

    ?refresh=true bypasses the cache and forces a fresh ICS fetch.
    """
    from .gcal import get_calendar_summary
    try:
        return get_calendar_summary(days=days, force_refresh=refresh)
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(503, f"Kalenderdaten nicht verfügbar: {exc}")


# ---------------------------------------------------------------------------
# Garmin sync
# ---------------------------------------------------------------------------
@app.post("/sync/garmin")
def sync_garmin(days: int = 14) -> dict[str, Any]:
    # Imported lazily so the sidecar boots even without garminconnect installed.
    from .garmin_sync import sync_last_n_days

    try:
        return sync_last_n_days(days)
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Garmin sync failed: {e}")


# ---------------------------------------------------------------------------
# Garmin workout push
# ---------------------------------------------------------------------------
class GarminPushIn(BaseModel):
    workout_id: int  # planned_workouts.id


@app.post("/garmin/push_workout")
def garmin_push_workout(body: GarminPushIn) -> dict[str, Any]:
    """Push a planned workout to Garmin Connect (library + calendar)."""
    from .garmin_push import push_planned_workout

    try:
        return push_planned_workout(body.workout_id)
    except RuntimeError as e:
        raise HTTPException(400, str(e))
    except Exception as e:  # noqa: BLE001
        raise HTTPException(500, f"Garmin push failed: {e}")


# ---------------------------------------------------------------------------
# Local settings — secrets are written to Keychain / Windows Credential Manager
# ---------------------------------------------------------------------------
class GarminCredentialsIn(BaseModel):
    email: str
    password: SecretStr


class CalendarSettingsIn(BaseModel):
    source: str = "auto"
    ics_url: SecretStr | None = None


@app.get("/settings/status")
def settings_status() -> dict[str, Any]:
    from .credentials import get_garmin_credentials, get_secret
    try:
        garmin_email, garmin_password = get_garmin_credentials()
        calendar_url = get_secret("gcal_ics_url")
    except Exception:  # keyring can be unavailable in headless test environments
        garmin_email = garmin_password = calendar_url = None
    return {
        "garmin_configured": bool(garmin_email and garmin_password),
        "garmin_email": garmin_email or "",
        "calendar_configured": bool(calendar_url),
        "calendar_source": db.get_athlete_config("calendar_source", "auto") or "auto",
    }


@app.post("/settings/garmin")
def save_garmin_settings(body: GarminCredentialsIn) -> dict[str, bool]:
    from .credentials import set_garmin_credentials
    if "@" not in body.email or not body.password.get_secret_value():
        raise HTTPException(400, "Bitte eine gültige E-Mail-Adresse und ein Passwort eingeben.")
    try:
        set_garmin_credentials(body.email.strip(), body.password.get_secret_value())
    except Exception as exc:  # noqa: BLE001
        raise HTTPException(500, f"System-Tresor nicht verfügbar: {exc}")
    return {"saved": True}


@app.post("/settings/calendar")
def save_calendar_settings(body: CalendarSettingsIn) -> dict[str, bool]:
    from .credentials import set_secret
    source = body.source.strip().lower()
    if source not in {"auto", "apple", "ics"}:
        raise HTTPException(400, "Kalenderquelle muss auto, apple oder ics sein.")
    db.set_athlete_config("calendar_source", source)
    if body.ics_url and body.ics_url.get_secret_value().strip():
        set_secret("gcal_ics_url", body.ics_url.get_secret_value().strip())
    return {"saved": True}


# ---------------------------------------------------------------------------
# Chat — streaming coach
# ---------------------------------------------------------------------------
class ChatIn(BaseModel):
    message: str


@app.get("/chat/history")
def chat_history(limit: int = 50) -> list[dict[str, Any]]:
    return db.get_chat_history(limit)


@app.post("/chat")
async def chat(body: ChatIn) -> StreamingResponse:
    """Stream the coach reply as Server-Sent Events (text/event-stream).

    Each event is a JSON line: {"delta": "..."} and a final {"done": true}.
    The full user + assistant turn is persisted to chat_messages.
    """
    user_msg = body.message
    db.save_chat_message("user", user_msg)

    async def event_gen():
        collected: list[str] = []
        try:
            async for chunk in stream_coach_reply(user_msg):
                collected.append(chunk)
                yield f"data: {json.dumps({'delta': chunk}, ensure_ascii=False)}\n\n"
        finally:
            if collected:
                db.save_chat_message("assistant", "".join(collected))
            yield f"data: {json.dumps({'done': True})}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# Keep this mount last so API routes above win over the single-page frontend.
_web_dir = resource_root() / "web"
if _web_dir.exists():
    app.mount("/", StaticFiles(directory=_web_dir, html=True), name="web")
