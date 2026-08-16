-- Sport Coach — SQLite schema (local-only DB)
-- All dates are ISO-8601 'YYYY-MM-DD' text. Times in minutes unless noted.
-- This file is idempotent: safe to run on every startup.

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

-- ---------------------------------------------------------------------------
-- schema_version: trivial migration bookkeeping.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS schema_version (
    version     INTEGER NOT NULL,
    applied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- plan_weeks: weekly plan container (phase/goal/deload).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS plan_weeks (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    week_start      TEXT    NOT NULL UNIQUE,   -- Monday of the week (YYYY-MM-DD)
    phase           TEXT,                      -- e.g. Base / Build / Peak / Taper / Recovery
    goal            TEXT,                      -- free text weekly goal
    deload          INTEGER NOT NULL DEFAULT 0,-- 0/1
    planned_hours   REAL,                      -- optional target volume
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- planned_workouts: the prescribed plan the coach reads & modifies.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS planned_workouts (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT    NOT NULL,          -- YYYY-MM-DD
    sport           TEXT    NOT NULL,          -- swim | bike | run | strength | brick | rest | other
    title           TEXT,
    duration_min    INTEGER,                   -- planned duration in minutes
    distance_km     REAL,                      -- optional
    target_zone     TEXT,                      -- e.g. 'Z2' or 'Z2-Z3'
    content         TEXT,                      -- human-readable description / instructions
    structured_steps TEXT,                     -- JSON: list of {duration_min, zone, note, repeats}
    priority        TEXT    NOT NULL DEFAULT 'B', -- A (key) | B | C (optional)
    status          TEXT    NOT NULL DEFAULT 'planned', -- planned | completed | skipped | partial
    completed_activity_id INTEGER,             -- FK -> activities.id once done
    garmin_workout_id TEXT,                    -- Garmin workout-service id after push
    garmin_schedule_id TEXT,                   -- Garmin calendar schedule id after push
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (completed_activity_id) REFERENCES activities(id) ON DELETE SET NULL
);
CREATE INDEX IF NOT EXISTS idx_planned_date ON planned_workouts(date);

-- ---------------------------------------------------------------------------
-- activities: completed sessions, mostly synced from Garmin.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS activities (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    garmin_id       TEXT    UNIQUE,            -- Garmin activityId, null for manual entries
    date            TEXT    NOT NULL,          -- YYYY-MM-DD (local start date)
    start_time      TEXT,                      -- ISO datetime
    sport           TEXT    NOT NULL,          -- swim | bike | run | strength | other
    title           TEXT,
    duration_min    REAL,
    distance_km     REAL,
    avg_hr          INTEGER,
    max_hr          INTEGER,
    avg_power       INTEGER,                   -- bike/run power if available
    elevation_gain_m REAL,
    calories        INTEGER,
    training_load   REAL,                      -- Garmin per-activity training load (EPOC-based)
    tss             REAL,                      -- training stress score (computed or provided)
    avg_pace_min_km REAL,
    raw_json        TEXT,                      -- full Garmin payload for later mining
    created_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_activities_date ON activities(date);

-- ---------------------------------------------------------------------------
-- daily_metrics: one row per day, synced from Garmin wellness endpoints.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_metrics (
    date                TEXT PRIMARY KEY,      -- YYYY-MM-DD
    hrv                 REAL,                  -- overnight HRV (ms)
    hrv_status          TEXT,                  -- BALANCED | UNBALANCED | LOW | POOR ...
    rhr                 INTEGER,               -- resting HR
    sleep_hours         REAL,
    sleep_quality       TEXT,                  -- Garmin sleep score / quality label
    sleep_score         INTEGER,
    body_battery        INTEGER,               -- highest/most-relevant BB value
    body_battery_low    INTEGER,
    training_readiness  INTEGER,               -- 0-100
    training_load       REAL,                  -- acute load / 7-day load
    training_status     TEXT,                  -- PRODUCTIVE | MAINTAINING | OVERREACHING ...
    vo2max              REAL,
    stress              INTEGER,               -- avg daily stress
    weight_kg           REAL,
    -- Performance Management Chart values (computed from activities/TSS):
    ctl                 REAL,                  -- Chronic Training Load (fitness)
    atl                 REAL,                  -- Acute Training Load (fatigue)
    tsb                 REAL,                  -- Training Stress Balance (form) = ctl - atl
    raw_json            TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- daily_checkin: subjective data the user enters in the app.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_checkin (
    date            TEXT PRIMARY KEY,          -- YYYY-MM-DD
    soreness        INTEGER,                   -- 1-5 muscle soreness
    pain_location   TEXT,                      -- free text (e.g. 'left knee')
    pain_level      INTEGER,                   -- 0-10
    motivation      INTEGER,                   -- 1-5
    mental_energy   INTEGER,                   -- 1-5
    available_time  INTEGER,                   -- minutes available to train today
    life_stress     INTEGER,                   -- 1-5
    notes           TEXT,
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- day_status: coach's Grün/Gelb/Rot verdict + reasoning per day.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS day_status (
    date            TEXT PRIMARY KEY,          -- YYYY-MM-DD
    status          TEXT NOT NULL,             -- green | yellow | red
    reason          TEXT,                      -- coach explanation (German)
    set_by          TEXT NOT NULL DEFAULT 'coach', -- coach | user
    created_at      TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- ---------------------------------------------------------------------------
-- coach_notes: free-form notes the coach logs (decisions, observations).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coach_notes (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    date            TEXT NOT NULL,
    note            TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_coach_notes_date ON coach_notes(date);

-- ---------------------------------------------------------------------------
-- chat_messages: persisted chat transcript with the coach.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS chat_messages (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    role            TEXT NOT NULL,             -- user | assistant | system
    content         TEXT NOT NULL,
    created_at      TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_chat_created ON chat_messages(created_at);

-- ---------------------------------------------------------------------------
-- athlete_goals: the user's sport ambitions (multiple, different sports).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS athlete_goals (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT    NOT NULL,          -- e.g. "Ironman Frankfurt 2026"
    sport           TEXT    NOT NULL,          -- swim | bike | run | triathlon | cycling | hiking | strength | other
    category        TEXT    NOT NULL DEFAULT 'endurance', -- endurance | strength | team | skill | other
    event_date      TEXT,                      -- YYYY-MM-DD target date (optional)
    description     TEXT,                      -- free-text goal description
    target_metric   TEXT,                      -- e.g. "sub-10h", "sub-4h Marathon"
    priority        INTEGER NOT NULL DEFAULT 2, -- 1=primary, 2=secondary, 3=background
    status          TEXT    NOT NULL DEFAULT 'active', -- active | achieved | abandoned | paused
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_goals_status ON athlete_goals(status);

-- ---------------------------------------------------------------------------
-- coach_memory: persistent coach observations, insights, athlete preferences.
-- The coach saves key facts here so they survive across conversations.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS coach_memory (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    category        TEXT    NOT NULL,          -- observation | insight | milestone | decision | preference | injury
    key             TEXT,                      -- optional short tag/label for dedup
    content         TEXT    NOT NULL,          -- the memory text
    relevance       INTEGER NOT NULL DEFAULT 3, -- 1-5; entries with relevance>=4 auto-load into system prompt
    expires_at      TEXT,                      -- YYYY-MM-DD, null = permanent
    created_at      TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at      TEXT    NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_memory_cat ON coach_memory(category);
CREATE INDEX IF NOT EXISTS idx_memory_rel ON coach_memory(relevance);

-- ---------------------------------------------------------------------------
-- weather_cache: cached Open-Meteo API response (refreshed every 3h max).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weather_cache (
    id          INTEGER PRIMARY KEY,
    fetched_at  TEXT    NOT NULL,   -- ISO datetime (UTC)
    data_json   TEXT    NOT NULL    -- full weather summary JSON
);

-- ---------------------------------------------------------------------------
-- athlete_config: simple key/value store for athlete preferences / settings.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS athlete_config (
    key     TEXT PRIMARY KEY,
    value   TEXT NOT NULL
);
