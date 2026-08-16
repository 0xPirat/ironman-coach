"""SQLite access layer for the Sport Coach.

Single local DB file. Thin helpers used by both the FastAPI routes and the
Agent SDK coach tools. Intentionally simple (no ORM) — this is a single-user
local app.
"""
from __future__ import annotations

import json
import os
import sqlite3
from contextlib import contextmanager
from datetime import date as _date
from pathlib import Path
from typing import Any, Iterable, Iterator

# DB lives next to the backend package by default; overridable for tests.
# COACH_DB overrides IRONMAN_DB (legacy) for new installs.
DB_PATH = Path(
    os.environ.get("COACH_DB")
    or os.environ.get("IRONMAN_DB")
    or (Path(__file__).resolve().parent.parent / "ironman.db")
)
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.sql"

SCHEMA_VERSION = 1


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db() -> None:
    """Create the schema if missing. Idempotent — safe on every startup."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    with get_conn() as conn:
        conn.executescript(schema)
        row = conn.execute("SELECT MAX(version) AS v FROM schema_version").fetchone()
        if row is None or row["v"] is None:
            conn.execute("INSERT INTO schema_version (version) VALUES (?)", (SCHEMA_VERSION,))
        # Future migrations: compare row["v"] to SCHEMA_VERSION and ALTER as needed.


def rows_to_dicts(rows: Iterable[sqlite3.Row]) -> list[dict[str, Any]]:
    return [dict(r) for r in rows]


# ---------------------------------------------------------------------------
# Generic upsert helpers
# ---------------------------------------------------------------------------

def upsert(table: str, key_cols: list[str], data: dict[str, Any]) -> None:
    """Insert-or-update on a unique key. `data` includes the key columns."""
    cols = list(data.keys())
    placeholders = ", ".join("?" for _ in cols)
    col_list = ", ".join(cols)
    update_cols = [c for c in cols if c not in key_cols]
    set_clause = ", ".join(f"{c}=excluded.{c}" for c in update_cols)
    conflict = ", ".join(key_cols)
    sql = (
        f"INSERT INTO {table} ({col_list}) VALUES ({placeholders}) "
        f"ON CONFLICT({conflict}) DO UPDATE SET {set_clause}"
    )
    if update_cols:
        sql += ", updated_at=datetime('now')" if _has_updated_at(table) else ""
    with get_conn() as conn:
        conn.execute(sql, [_coerce(v) for v in data.values()])


def _has_updated_at(table: str) -> bool:
    return table in {
        "planned_workouts", "daily_metrics", "daily_checkin",
        "day_status", "plan_weeks", "athlete_goals", "coach_memory",
    }


def _coerce(v: Any) -> Any:
    if isinstance(v, (dict, list)):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, bool):
        return int(v)
    return v


# ---------------------------------------------------------------------------
# Query helpers used by routes + coach tools
# ---------------------------------------------------------------------------

def today_str() -> str:
    return _date.today().isoformat()


def get_metrics(start: str, end: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM daily_metrics WHERE date BETWEEN ? AND ? ORDER BY date",
            (start, end),
        ).fetchall()
    return rows_to_dicts(rows)


def get_plan(start: str, end: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM planned_workouts WHERE date BETWEEN ? AND ? "
            "ORDER BY date, sport",
            (start, end),
        ).fetchall()
    return rows_to_dicts(rows)


def get_activities(start: str, end: str) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM activities WHERE date BETWEEN ? AND ? ORDER BY date",
            (start, end),
        ).fetchall()
    return rows_to_dicts(rows)


def get_checkin(date: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM daily_checkin WHERE date = ?", (date,)).fetchone()
    return dict(row) if row else None


def get_day_status(date: str) -> dict[str, Any] | None:
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM day_status WHERE date = ?", (date,)).fetchone()
    return dict(row) if row else None


def create_workout(data: dict[str, Any]) -> int:
    cols = list(data.keys())
    sql = (
        f"INSERT INTO planned_workouts ({', '.join(cols)}) "
        f"VALUES ({', '.join('?' for _ in cols)})"
    )
    with get_conn() as conn:
        cur = conn.execute(sql, [_coerce(v) for v in data.values()])
        return int(cur.lastrowid)


def update_workout(workout_id: int, data: dict[str, Any]) -> bool:
    if not data:
        return False
    set_clause = ", ".join(f"{c}=?" for c in data) + ", updated_at=datetime('now')"
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE planned_workouts SET {set_clause} WHERE id=?",
            [*[_coerce(v) for v in data.values()], workout_id],
        )
        return cur.rowcount > 0


def move_workout(workout_id: int, new_date: str) -> bool:
    return update_workout(workout_id, {"date": new_date})


def delete_workout(workout_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM planned_workouts WHERE id=?", (workout_id,))
        return cur.rowcount > 0


def set_day_status(date: str, status: str, reason: str | None, set_by: str = "coach") -> None:
    upsert(
        "day_status", ["date"],
        {"date": date, "status": status, "reason": reason, "set_by": set_by},
    )


def log_coach_note(date: str, note: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO coach_notes (date, note) VALUES (?, ?)", (date, note)
        )
        return int(cur.lastrowid)


def save_chat_message(role: str, content: str) -> int:
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO chat_messages (role, content) VALUES (?, ?)", (role, content)
        )
        return int(cur.lastrowid)


def get_chat_history(limit: int = 50) -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM (SELECT * FROM chat_messages ORDER BY id DESC LIMIT ?) "
            "ORDER BY id ASC",
            (limit,),
        ).fetchall()
    return rows_to_dicts(rows)


# ---------------------------------------------------------------------------
# Athlete Goals
# ---------------------------------------------------------------------------

def get_goals(status: str = "active") -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM athlete_goals WHERE status=? ORDER BY priority, event_date",
            (status,),
        ).fetchall()
    return rows_to_dicts(rows)


def get_all_goals() -> list[dict[str, Any]]:
    with get_conn() as conn:
        rows = conn.execute(
            "SELECT * FROM athlete_goals ORDER BY priority, event_date"
        ).fetchall()
    return rows_to_dicts(rows)


def create_goal(data: dict[str, Any]) -> int:
    cols = list(data.keys())
    sql = (
        f"INSERT INTO athlete_goals ({', '.join(cols)}) "
        f"VALUES ({', '.join('?' for _ in cols)})"
    )
    with get_conn() as conn:
        cur = conn.execute(sql, [_coerce(v) for v in data.values()])
        return int(cur.lastrowid)


def update_goal(goal_id: int, data: dict[str, Any]) -> bool:
    if not data:
        return False
    set_clause = ", ".join(f"{c}=?" for c in data) + ", updated_at=datetime('now')"
    with get_conn() as conn:
        cur = conn.execute(
            f"UPDATE athlete_goals SET {set_clause} WHERE id=?",
            [*[_coerce(v) for v in data.values()], goal_id],
        )
        return cur.rowcount > 0


def delete_goal(goal_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM athlete_goals WHERE id=?", (goal_id,))
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Coach Memory
# ---------------------------------------------------------------------------

def save_memory(category: str, content: str, key: str | None = None,
                relevance: int = 3, expires_at: str | None = None) -> int:
    """Insert a new memory or update existing one if key matches."""
    if key:
        with get_conn() as conn:
            existing = conn.execute(
                "SELECT id FROM coach_memory WHERE key=?", (key,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE coach_memory SET content=?, relevance=?, "
                    "expires_at=?, updated_at=datetime('now') WHERE key=?",
                    (content, relevance, expires_at, key),
                )
                return int(existing["id"])
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO coach_memory (category, key, content, relevance, expires_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (category, key, content, relevance, expires_at),
        )
        return int(cur.lastrowid)


def get_memories(min_relevance: int = 1, category: str | None = None,
                 limit: int = 50) -> list[dict[str, Any]]:
    today = today_str()
    where = ["(expires_at IS NULL OR expires_at > ?)"]
    params: list[Any] = [today]
    if min_relevance > 1:
        where.append("relevance >= ?")
        params.append(min_relevance)
    if category:
        where.append("category = ?")
        params.append(category)
    params.append(limit)
    sql = (
        f"SELECT * FROM coach_memory WHERE {' AND '.join(where)} "
        f"ORDER BY relevance DESC, updated_at DESC LIMIT ?"
    )
    with get_conn() as conn:
        rows = conn.execute(sql, params).fetchall()
    return rows_to_dicts(rows)


def delete_memory(memory_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute("DELETE FROM coach_memory WHERE id=?", (memory_id,))
        return cur.rowcount > 0


# ---------------------------------------------------------------------------
# Weather cache
# ---------------------------------------------------------------------------

def get_weather_cache(max_age_seconds: int = 1800,
                      allow_stale: bool = False) -> "dict | None":
    """Return cached weather data if younger than max_age_seconds.

    allow_stale=True skips the age check — fallback when the weather API
    is unreachable (old forecast beats no forecast).
    """
    import datetime as _dt
    with get_conn() as conn:
        row = conn.execute(
            "SELECT fetched_at, data_json FROM weather_cache ORDER BY id DESC LIMIT 1"
        ).fetchone()
    if row is None:
        return None
    fetched_at = _dt.datetime.fromisoformat(row["fetched_at"])
    age = _dt.datetime.utcnow() - fetched_at
    if not allow_stale and age.total_seconds() > max_age_seconds:
        return None
    return json.loads(row["data_json"])


def save_weather_cache(data: dict) -> None:
    """Replace weather cache with fresh data."""
    import datetime as _dt
    now = _dt.datetime.utcnow().isoformat()
    data_json = json.dumps(data, ensure_ascii=False)
    with get_conn() as conn:
        conn.execute("DELETE FROM weather_cache")
        conn.execute(
            "INSERT INTO weather_cache (fetched_at, data_json) VALUES (?, ?)",
            (now, data_json),
        )


# ---------------------------------------------------------------------------
# Athlete config
# ---------------------------------------------------------------------------

def get_athlete_config(key: str, default=None) -> "str | None":
    with get_conn() as conn:
        row = conn.execute(
            "SELECT value FROM athlete_config WHERE key = ?", (key,)
        ).fetchone()
    return row["value"] if row else default


def set_athlete_config(key: str, value: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO athlete_config (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value),
        )
