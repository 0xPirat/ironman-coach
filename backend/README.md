# Ironman Coach — Backend (Python sidecar)

Local FastAPI server (127.0.0.1 only) that runs the coaching agent
(claude-agent-sdk, subscription auth), syncs Garmin data, and stores everything
in SQLite.

## Run standalone (for testing, without the macOS app)

From the **project root** (`/Users/johannesbenedict/ironman-coach`):

```bash
# 1) One-time: create venv + install deps
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt

# 2) Make sure you are logged into Claude Code (subscription auth)
claude /login          # once; writes OAuth creds to the macOS Keychain

# 3) Run the sidecar (PYTHONPATH must point at the project root)
PYTHONPATH=$PWD .venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8765 --reload
```

> Do **not** export `ANTHROPIC_API_KEY` — the coach must use your subscription,
> not paid API tokens. The agent strips it from the child env anyway.

## Smoke-test the endpoints

```bash
curl -s http://127.0.0.1:8765/health
# streaming coach reply (SSE):
curl -N -X POST http://127.0.0.1:8765/chat \
  -H 'Content-Type: application/json' \
  -d '{"message":"Wie sieht meine Woche aus?"}'
```

Or run the spikes:
```bash
PYTHONPATH=$PWD .venv/bin/python spikes/auth_spike.py   # proves subscription auth
PYTHONPATH=$PWD .venv/bin/python spikes/coach_e2e.py     # coach reads data + writes DB
```

## Garmin credentials (stored in the macOS Keychain, never plaintext)

```bash
PYTHONPATH=$PWD .venv/bin/python -m backend.credentials   # prompts for email/password
# then:
curl -X POST "http://127.0.0.1:8765/sync/garmin?days=14"
```

## REST + streaming API

| Method | Path                 | Purpose                                   |
| ------ | -------------------- | ----------------------------------------- |
| GET    | `/health`            | liveness                                  |
| GET    | `/today?date=`       | plan + metrics + activities + checkin     |
| GET    | `/metrics`           | daily metrics (HRV/RHR/sleep/CTL/ATL/TSB) |
| GET    | `/plan`              | planned workouts in range                 |
| GET    | `/activities`        | completed activities in range             |
| GET/POST | `/checkin`         | subjective daily check-in                 |
| POST   | `/workouts`          | create planned workout                    |
| PATCH  | `/workouts/{id}`     | update workout                            |
| DELETE | `/workouts/{id}`     | delete workout                            |
| POST   | `/sync/garmin?days=` | pull Garmin data into SQLite              |
| POST   | `/chat`              | **streaming** coach reply (SSE)           |
| GET    | `/chat/history`      | persisted transcript                      |

## Layout

```
backend/
  main.py            FastAPI app (REST + /chat SSE)
  coach_prompt.py    COACH SYSTEM PROMPT (German) + HR zones + status/plan formats
                     -> // TODO: methodology from research/ironman-training-methodology.md
  credentials.py     macOS Keychain helpers (keyring)
  garmin_sync.py     python-garminconnect -> SQLite + CTL/ATL/TSB (PMC) compute
  agent/
    coach_agent.py   claude-agent-sdk wiring; subscription auth; streaming
    coach_tools.py   custom tools: get_today/get_metrics/get_plan/get_checkin,
                     create/update/move/delete_workout, set_day_status, log_coach_note
  db/
    schema.sql       SQLite schema (idempotent)
    database.py      thin DB access layer
```
