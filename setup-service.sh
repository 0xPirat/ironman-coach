#!/usr/bin/env bash
# Richtet zwei macOS-Hintergrunddienste (LaunchAgents) ein:
#
#   com.ironmancoach.sidecar  — Python-API läuft immer, auch wenn die App zu ist
#   com.ironmancoach.daily    — täglicher Coach-Check um 07:30 + macOS-Notification
#
# Ausführen:
#   bash setup-service.sh          # einrichten / aktualisieren
#   bash setup-service.sh stop     # stoppen
#   bash setup-service.sh status   # Status prüfen
#   bash setup-service.sh run-now  # Daily-Agent jetzt manuell ausführen

set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
VENV="$REPO/.venv/bin/python"
LAUNCHD_DIR="$HOME/Library/LaunchAgents"
DATA_DIR="$HOME/Library/Application Support/IronmanCoach"
DB_PATH="$DATA_DIR/ironman.db"
LOG_DIR="$DATA_DIR/logs"
UID_PATH="gui/$(id -u)"

SIDECAR_LABEL="com.ironmancoach.sidecar"
DAILY_LABEL="com.ironmancoach.daily"
SIDECAR_PLIST="$LAUNCHD_DIR/$SIDECAR_LABEL.plist"
DAILY_PLIST="$LAUNCHD_DIR/$DAILY_LABEL.plist"

_unload() {
  local label="$1" plist="$2"
  launchctl bootout "$UID_PATH/$label" 2>/dev/null \
    || launchctl unload "$plist" 2>/dev/null \
    || true
}

_load() {
  local plist="$1" label="$2"
  launchctl bootstrap "$UID_PATH" "$plist" 2>/dev/null \
    || launchctl load -w "$plist"
  echo "  ✓ $label geladen"
}

# --- Kommandos ---------------------------------------------------------------
case "${1:-install}" in
  stop)
    _unload "$SIDECAR_LABEL" "$SIDECAR_PLIST"
    echo "Sidecar gestoppt."
    _unload "$DAILY_LABEL" "$DAILY_PLIST"
    echo "Daily-Agent gestoppt."
    exit 0
    ;;
  status)
    echo "=== Sidecar ==="
    launchctl print "$UID_PATH/$SIDECAR_LABEL" 2>/dev/null \
      || launchctl list "$SIDECAR_LABEL" 2>/dev/null \
      || echo "  nicht geladen"
    echo ""
    echo "=== Daily-Agent ==="
    launchctl print "$UID_PATH/$DAILY_LABEL" 2>/dev/null \
      || launchctl list "$DAILY_LABEL" 2>/dev/null \
      || echo "  nicht geladen"
    exit 0
    ;;
  run-now)
    echo "→ Führe Daily-Agent jetzt aus…"
    PYTHONPATH="$REPO" COACH_DB="$DB_PATH" "$VENV" -m backend.daily_agent
    exit 0
    ;;
esac

# --- Checks ------------------------------------------------------------------
if [ ! -f "$VENV" ]; then
  echo "✗ Python-venv nicht gefunden: $VENV"
  echo "  Bitte zuerst:"
  echo "    cd ~/ironman-coach"
  echo "    python3 -m venv .venv"
  echo "    .venv/bin/pip install -r backend/requirements.txt"
  exit 1
fi

mkdir -p "$LAUNCHD_DIR" "$LOG_DIR" "$DATA_DIR"

# --- Sidecar-LaunchAgent schreiben ------------------------------------------
echo "→ Schreibe Sidecar-LaunchAgent (KeepAlive)…"
cat > "$SIDECAR_PLIST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>              <string>${SIDECAR_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${VENV}</string>
        <string>-m</string>       <string>uvicorn</string>
        <string>backend.main:app</string>
        <string>--host</string>   <string>127.0.0.1</string>
        <string>--port</string>   <string>8765</string>
    </array>
    <key>WorkingDirectory</key>   <string>${REPO}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>     <string>${REPO}</string>
        <key>COACH_DB</key>       <string>${DB_PATH}</string>
        <key>HOME</key>           <string>${HOME}</string>
    </dict>
    <key>RunAtLoad</key>          <true/>
    <key>KeepAlive</key>          <true/>
    <key>ThrottleInterval</key>   <integer>10</integer>
    <key>StandardOutPath</key>    <string>${LOG_DIR}/sidecar.log</string>
    <key>StandardErrorPath</key>  <string>${LOG_DIR}/sidecar.error.log</string>
</dict>
</plist>
PLIST

# --- Daily-Agent-LaunchAgent schreiben ---------------------------------------
echo "→ Schreibe Daily-Agent-LaunchAgent (täglich 07:30)…"
cat > "$DAILY_PLIST" << PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>              <string>${DAILY_LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${VENV}</string>
        <string>-m</string>       <string>backend.daily_agent</string>
    </array>
    <key>WorkingDirectory</key>   <string>${REPO}</string>
    <key>EnvironmentVariables</key>
    <dict>
        <key>PYTHONPATH</key>     <string>${REPO}</string>
        <key>COACH_DB</key>       <string>${DB_PATH}</string>
        <key>HOME</key>           <string>${HOME}</string>
    </dict>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>           <integer>7</integer>
        <key>Minute</key>         <integer>30</integer>
    </dict>
    <key>StandardOutPath</key>    <string>${LOG_DIR}/daily_agent.log</string>
    <key>StandardErrorPath</key>  <string>${LOG_DIR}/daily_agent.error.log</string>
</dict>
</plist>
PLIST

# --- Laden -------------------------------------------------------------------
echo "→ Lade Services…"
_unload "$SIDECAR_LABEL" "$SIDECAR_PLIST"
_load "$SIDECAR_PLIST" "$SIDECAR_LABEL"

_unload "$DAILY_LABEL" "$DAILY_PLIST"
_load "$DAILY_PLIST" "$DAILY_LABEL"

echo ""
echo "✓ Services aktiv!"
echo "  Sidecar:      läuft auf 127.0.0.1:8765 (immer — auch ohne App)"
echo "  Daily-Agent:  startet täglich automatisch um 07:30"
echo ""
echo "  Logs live:    tail -f $LOG_DIR/sidecar.log"
echo "                tail -f $LOG_DIR/daily_agent.log"
echo "  Datenspeicher: $DB_PATH"
echo "  Jetzt testen: bash \"$REPO/setup-service.sh\" run-now"
echo "  Stoppen:      bash \"$REPO/setup-service.sh\" stop"
