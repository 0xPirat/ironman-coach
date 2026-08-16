"""Agent SDK custom tools — the coach's hands on the plan, goals & memory.

Each tool returns the MCP content shape:
  {"content": [{"type": "text", "text": ...}], "is_error"?: bool}

Naming: tools are addressable as mcp__coach__<tool_name> in allowed_tools.
"""
from __future__ import annotations

import datetime as dt
import json
from typing import Any

from claude_agent_sdk import tool

from ..db import database as db


def _ok(payload: Any) -> dict[str, Any]:
    text = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False, indent=2)
    return {"content": [{"type": "text", "text": text}]}


def _err(msg: str) -> dict[str, Any]:
    return {"content": [{"type": "text", "text": msg}], "is_error": True}


def _week_range(anchor: str | None = None) -> tuple[str, str]:
    d = dt.date.fromisoformat(anchor) if anchor else dt.date.today()
    monday = d - dt.timedelta(days=d.weekday())
    return monday.isoformat(), (monday + dt.timedelta(days=6)).isoformat()


# --- READ tools --------------------------------------------------------------

@tool("get_today", "Hole Datum, geplantes Training, Metriken, Check-in und Status für heute (oder ein Datum).",
      {"date": str})
async def get_today(args: dict[str, Any]) -> dict[str, Any]:
    date = args.get("date") or db.today_str()
    return _ok({
        "date": date,
        "plan": db.get_plan(date, date),
        "metrics": db.get_metrics(date, date),
        "activities": db.get_activities(date, date),
        "checkin": db.get_checkin(date),
        "day_status": db.get_day_status(date),
    })


@tool("get_metrics", "Hole Garmin-Tagesmetriken (HRV, RHR, Schlaf, Body Battery, Readiness, CTL/ATL/TSB) für einen Zeitraum.",
      {"start": str, "end": str})
async def get_metrics(args: dict[str, Any]) -> dict[str, Any]:
    return _ok(db.get_metrics(args["start"], args["end"]))


@tool("get_plan", "Hole geplante Einheiten in einem Datumsbereich. Ohne Argumente: aktuelle Woche.",
      {"start": str, "end": str})
async def get_plan(args: dict[str, Any]) -> dict[str, Any]:
    if args.get("start") and args.get("end"):
        start, end = args["start"], args["end"]
    else:
        start, end = _week_range(args.get("start"))
    return _ok({"range": [start, end], "workouts": db.get_plan(start, end)})


@tool("get_checkin", "Hole den subjektiven Daily Check-in (Soreness, Schmerz, Motivation, Energie, Zeit, Stress) für ein Datum.",
      {"date": str})
async def get_checkin(args: dict[str, Any]) -> dict[str, Any]:
    date = args.get("date") or db.today_str()
    c = db.get_checkin(date)
    return _ok(c if c else f"Kein Check-in für {date} vorhanden.")


# --- GOAL tools --------------------------------------------------------------

@tool("get_goals", "Hole alle sportlichen Ziele des Athleten. Optional: status (active|achieved|paused|abandoned).",
      {"status": str})
async def get_goals(args: dict[str, Any]) -> dict[str, Any]:
    status = args.get("status", "active")
    if status == "all":
        goals = db.get_all_goals()
    else:
        goals = db.get_goals(status)
    return _ok({"goals": goals, "count": len(goals)})


@tool(
    "create_goal",
    "Lege ein neues sportliches Ziel an. Pflicht: title, sport. Optional: category, "
    "event_date (YYYY-MM-DD), description, target_metric, priority (1=primär/2=sekundär/3=hintergrund).",
    {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "sport": {"type": "string"},
            "category": {"type": "string", "enum": ["endurance", "strength", "team", "skill", "other"]},
            "event_date": {"type": "string"},
            "description": {"type": "string"},
            "target_metric": {"type": "string"},
            "priority": {"type": "integer", "enum": [1, 2, 3]},
        },
        "required": ["title", "sport"],
    },
)
async def create_goal(args: dict[str, Any]) -> dict[str, Any]:
    data = {k: v for k, v in args.items() if v is not None}
    gid = db.create_goal(data)
    return _ok({"created_goal_id": gid, **data})


@tool(
    "update_goal",
    "Ändere ein Ziel. Pflicht: id. Optional: title, sport, category, event_date, "
    "description, target_metric, priority, status (active|achieved|abandoned|paused).",
    {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "title": {"type": "string"},
            "sport": {"type": "string"},
            "category": {"type": "string"},
            "event_date": {"type": "string"},
            "description": {"type": "string"},
            "target_metric": {"type": "string"},
            "priority": {"type": "integer"},
            "status": {"type": "string", "enum": ["active", "achieved", "abandoned", "paused"]},
        },
        "required": ["id"],
    },
)
async def update_goal(args: dict[str, Any]) -> dict[str, Any]:
    gid = args.pop("id")
    data = {k: v for k, v in args.items() if v is not None}
    if not data:
        return _err("Keine Felder zum Aktualisieren angegeben.")
    ok = db.update_goal(gid, data)
    return _ok({"updated": ok, "id": gid}) if ok else _err(f"Ziel {gid} nicht gefunden.")


@tool("delete_goal", "Lösche ein Ziel. Pflicht: id.", {"id": int})
async def delete_goal(args: dict[str, Any]) -> dict[str, Any]:
    ok = db.delete_goal(args["id"])
    return _ok({"deleted": ok, "id": args["id"]}) if ok else _err("Ziel nicht gefunden.")


# --- MEMORY tools ------------------------------------------------------------

@tool(
    "save_memory",
    "Speichere eine dauerhafte Beobachtung/Erkenntnis zum Athleten. "
    "Pflicht: category (observation|insight|milestone|decision|preference|injury), content. "
    "Optional: key (eindeutiger Tag für Dedup-Update), relevance (1-5, default 3), "
    "expires_at (YYYY-MM-DD, null=permanent).",
    {
        "type": "object",
        "properties": {
            "category": {"type": "string",
                         "enum": ["observation", "insight", "milestone", "decision", "preference", "injury"]},
            "content": {"type": "string"},
            "key": {"type": "string"},
            "relevance": {"type": "integer", "minimum": 1, "maximum": 5},
            "expires_at": {"type": "string"},
        },
        "required": ["category", "content"],
    },
)
async def save_memory(args: dict[str, Any]) -> dict[str, Any]:
    mid = db.save_memory(
        category=args["category"],
        content=args["content"],
        key=args.get("key"),
        relevance=args.get("relevance", 3),
        expires_at=args.get("expires_at"),
    )
    return _ok({"memory_id": mid, "saved": True})


@tool(
    "get_memories",
    "Hole gespeicherte Coach-Erinnerungen. Optional: min_relevance (1-5), "
    "category (observation|insight|milestone|decision|preference|injury), limit.",
    {
        "type": "object",
        "properties": {
            "min_relevance": {"type": "integer", "minimum": 1, "maximum": 5},
            "category": {"type": "string"},
            "limit": {"type": "integer"},
        },
    },
)
async def get_memories(args: dict[str, Any]) -> dict[str, Any]:
    memories = db.get_memories(
        min_relevance=args.get("min_relevance", 1),
        category=args.get("category"),
        limit=args.get("limit", 30),
    )
    return _ok({"memories": memories, "count": len(memories)})


# --- WRITE tools -------------------------------------------------------------

@tool(
    "create_workout",
    "Lege eine geplante Einheit an. Pflicht: date (YYYY-MM-DD), sport "
    "(swim|bike|run|strength|brick|triathlon|cycling|hiking|yoga|rowing|rest|other). "
    "Optional: title, duration_min, distance_km, target_zone (z.B. 'Z2'), content, "
    "priority (A|B|C), structured_steps (JSON-String).",
    {
        "type": "object",
        "properties": {
            "date": {"type": "string"},
            "sport": {"type": "string"},
            "title": {"type": "string"},
            "duration_min": {"type": "integer"},
            "distance_km": {"type": "number"},
            "target_zone": {"type": "string"},
            "content": {"type": "string"},
            "priority": {"type": "string", "enum": ["A", "B", "C"]},
            "structured_steps": {"type": "string"},
        },
        "required": ["date", "sport"],
    },
)
async def create_workout(args: dict[str, Any]) -> dict[str, Any]:
    data = {k: v for k, v in args.items() if v is not None}
    wid = db.create_workout(data)
    return _ok({"created_workout_id": wid, **data})


@tool(
    "update_workout",
    "Ändere Felder einer geplanten Einheit. Pflicht: id. Setze nur die zu "
    "ändernden Felder (z.B. duration_min, target_zone, content, status "
    "[planned|completed|skipped|partial], priority).",
    {
        "type": "object",
        "properties": {
            "id": {"type": "integer"},
            "sport": {"type": "string"},
            "title": {"type": "string"},
            "duration_min": {"type": "integer"},
            "distance_km": {"type": "number"},
            "target_zone": {"type": "string"},
            "content": {"type": "string"},
            "priority": {"type": "string"},
            "status": {"type": "string"},
            "structured_steps": {"type": "string"},
        },
        "required": ["id"],
    },
)
async def update_workout(args: dict[str, Any]) -> dict[str, Any]:
    wid = args.pop("id")
    data = {k: v for k, v in args.items() if v is not None}
    if not data:
        return _err("Keine Felder zum Aktualisieren angegeben.")
    ok = db.update_workout(wid, data)
    return _ok({"updated": ok, "id": wid, "fields": list(data)}) if ok else _err(f"Einheit {wid} nicht gefunden.")


@tool("move_workout", "Verschiebe eine geplante Einheit auf ein anderes Datum. Pflicht: id, new_date (YYYY-MM-DD).",
      {"id": int, "new_date": str})
async def move_workout(args: dict[str, Any]) -> dict[str, Any]:
    ok = db.move_workout(args["id"], args["new_date"])
    return _ok({"moved": ok, "id": args["id"], "new_date": args["new_date"]}) if ok else _err("Einheit nicht gefunden.")


@tool("delete_workout", "Lösche eine geplante Einheit. Pflicht: id.", {"id": int})
async def delete_workout(args: dict[str, Any]) -> dict[str, Any]:
    ok = db.delete_workout(args["id"])
    return _ok({"deleted": ok, "id": args["id"]}) if ok else _err("Einheit nicht gefunden.")


@tool(
    "set_day_status",
    "Setze den Tages-Status Grün/Gelb/Rot mit Begründung. Pflicht: date, "
    "status (green|yellow|red). Optional: reason.",
    {
        "type": "object",
        "properties": {
            "date": {"type": "string"},
            "status": {"type": "string", "enum": ["green", "yellow", "red"]},
            "reason": {"type": "string"},
        },
        "required": ["date", "status"],
    },
)
async def set_day_status(args: dict[str, Any]) -> dict[str, Any]:
    db.set_day_status(args["date"], args["status"], args.get("reason"))
    return _ok({"date": args["date"], "status": args["status"]})


@tool("log_coach_note", "Dokumentiere eine Coaching-Entscheidung/Beobachtung. Pflicht: note. Optional: date.",
      {"note": str, "date": str})
async def log_coach_note(args: dict[str, Any]) -> dict[str, Any]:
    date = args.get("date") or db.today_str()
    nid = db.log_coach_note(date, args["note"])
    return _ok({"note_id": nid, "date": date})


# --- WEATHER tool ------------------------------------------------------------

@tool(
    "get_weather",
    "Get current weather and 7-day forecast for the athlete's location. "
    "Use this when planning outdoor workouts, evaluating whether to move a "
    "session outside/inside, or advising on training conditions. "
    "outdoor_suitable=True means conditions are OK for outdoor training.",
    {},
)
async def get_weather(args: dict[str, Any]) -> dict[str, Any]:
    try:
        from ..weather import get_weather_summary
        return _ok(get_weather_summary())
    except Exception as exc:  # noqa: BLE001
        return _err(f"Wetterdaten nicht verfügbar: {exc}")


# --- CALENDAR tool -----------------------------------------------------------

@tool(
    "get_calendar",
    "Hole die Kalender-Termine (Busy-Slots) des Athleten für die nächsten Tage "
    "aus seinem Google Kalender. Nutze das beim Planen/Verschieben von "
    "Einheiten: Trainings gehören NUR in freie Zeitfenster. "
    "Optional: days (1-14, default 7), refresh (true erzwingt frischen Abruf).",
    {
        "type": "object",
        "properties": {
            "days": {"type": "integer", "minimum": 1, "maximum": 14},
            "refresh": {"type": "boolean"},
        },
    },
)
async def get_calendar(args: dict[str, Any]) -> dict[str, Any]:
    try:
        from ..gcal import get_calendar_summary
        return _ok(get_calendar_summary(
            days=args.get("days", 7),
            force_refresh=bool(args.get("refresh", False)),
        ))
    except Exception as exc:  # noqa: BLE001
        return _err(f"Kalenderdaten nicht verfügbar: {exc}")


# --- GARMIN push tool ----------------------------------------------------------

@tool(
    "push_workout_to_garmin",
    "Pushe eine geplante Einheit als strukturiertes Workout nach Garmin Connect "
    "(erscheint in der Connect-App und nach dem Uhr-Sync auf der Uhr, am geplanten "
    "Tag im Kalender). Pflicht: id (der geplanten Einheit). Nutzt structured_steps "
    "wenn vorhanden, sonst duration_min + target_zone. Ein erneuter Push ersetzt "
    "die alte Garmin-Version. Rufe das nach relevanten Planänderungen auf.",
    {"id": int},
)
async def push_workout_to_garmin(args: dict[str, Any]) -> dict[str, Any]:
    try:
        from ..garmin_push import push_planned_workout
        result = push_planned_workout(args["id"])
    except Exception as exc:  # noqa: BLE001
        return _err(f"Garmin-Push fehlgeschlagen: {exc}")
    return _ok({"workout_id": args["id"], **result})


ALL_TOOLS = [
    get_today, get_metrics, get_plan, get_checkin,
    get_goals, create_goal, update_goal, delete_goal,
    save_memory, get_memories,
    create_workout, update_workout, move_workout, delete_workout,
    set_day_status, log_coach_note,
    get_weather, get_calendar,
    push_workout_to_garmin,
]

ALLOWED_TOOL_NAMES = [
    "mcp__coach__get_today",
    "mcp__coach__get_metrics",
    "mcp__coach__get_plan",
    "mcp__coach__get_checkin",
    "mcp__coach__get_goals",
    "mcp__coach__create_goal",
    "mcp__coach__update_goal",
    "mcp__coach__delete_goal",
    "mcp__coach__save_memory",
    "mcp__coach__get_memories",
    "mcp__coach__create_workout",
    "mcp__coach__update_workout",
    "mcp__coach__move_workout",
    "mcp__coach__delete_workout",
    "mcp__coach__set_day_status",
    "mcp__coach__log_coach_note",
    "mcp__coach__get_weather",
    "mcp__coach__get_calendar",
    "mcp__coach__push_workout_to_garmin",
]
