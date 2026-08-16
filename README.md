# Ironman Coach

Lokale, KI-gestützte Ausdauer-Coaching-App für **Windows, macOS, Android, iPhone und iPad**. Sie verbindet
Trainingsplanung, Garmin-Daten, tägliche Check-ins, Coach-Gedächtnis und eine
umfangreiche evidenzbasierte Wissenssammlung in Desktop- und Mobil-Clients.

> Unabhängiges privates Projekt; keine offizielle App der IRONMAN Group.

## Download

Unter **Releases** die passende ZIP-Datei laden:

- `Ironman-Coach-Windows-x64.zip` für Windows 10/11
- `Ironman-Coach-macOS-Apple-Silicon.zip` für Macs mit M‑Chip
- `Ironman-Coach-macOS-Intel.zip` für ältere Intel-Macs

Für iPhone und iPad gibt es einen nativen SwiftUI-Client. Wegen Apples vorgeschriebener
Gerätesignierung wird er aus Xcode mit der eigenen Apple-ID installiert; der GitHub-Build
ohne Zertifikat ist nur im Simulator lauffähig. Die vollständige, ehrliche Anleitung steht
in [APPLE_DISTRIBUTION.md](APPLE_DISTRIBUTION.md).

Für Android erzeugt GitHub ein direkt installierbares Debug-APK. Es ist bei Tags wie
`android-v0.1.0` unter **Releases** als `ironman-coach-android-debug.apk` verfügbar;
bei normalen Builds liegt es als Actions-Artefakt bereit. Installation, lokaler Build und
Sicherheitsgrenzen sind in [android/README.md](android/README.md) dokumentiert.

ZIP entpacken und `Ironman Coach.exe` beziehungsweise `Ironman Coach.app` starten.
Die Builds sind noch nicht mit einem kostenpflichtigen Entwicklerzertifikat signiert;
Windows SmartScreen oder macOS Gatekeeper können beim ersten Start deshalb nach einer
Bestätigung fragen.

## Mobile Clients und Server

Android, iPhone und iPad sind native Clients. Python, Claude-/Garmin-Anbindung und die
persönliche SQLite-Datenbank laufen weiterhin auf dem eigenen Mac oder Server; es wird
keine vollständige Offline-KI in die Mobil-App eingebettet.

Für Mobilgeräte wird die API bewusst separat und token-geschützt gestartet:

```bash
export IRONMAN_MOBILE_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
.venv/bin/python -m backend.mobile_server
```

Dieser opt-in Server bindet an `0.0.0.0:8766` und verlangt bei jedem Request
`Authorization: Bearer <token>`. Der normale Desktop-Sidecar bleibt getrennt auf
`127.0.0.1:8765` und verhält sich unverändert. Port 8766 nur in einem vertrauenswürdigen
privaten Netz nutzen und niemals unverschlüsselt ins Internet weiterleiten; für externen
Zugriff sind ein privates VPN oder HTTPS mit zusätzlichem Zugriffsschutz erforderlich.

## Einmalige Einrichtung

1. [Claude Code](https://docs.anthropic.com/en/docs/claude-code/setup) installieren.
2. Im Terminal beziehungsweise in PowerShell einmal `claude /login` ausführen und
   mit einem Claude-Pro-/Max-Konto anmelden.
3. In der App unter **Einstellungen** die eigenen Garmin-Zugangsdaten hinterlegen.
   Sie landen im macOS-Schlüsselbund beziehungsweise in der Windows-
   Anmeldeinformationsverwaltung, niemals im Repository.
4. Optional unter **Einstellungen** eine private iCal-URL eintragen. Auf dem Mac ist
   zusätzlich der lokale Apple-Kalender verfügbar.

Die App entfernt `ANTHROPIC_API_KEY` bewusst aus ihrer Umgebung. Der Coach nutzt das
Claude-Abo und soll keine Pay-per-use-API-Kosten verursachen.

## Was lokal erhalten bleibt

Jede Desktop-Installation besitzt eine eigene SQLite-Datenbank; die Mobil-Clients
greifen nach ausdrücklicher Verbindung auf die Datenbank ihres Backends zu:

- macOS: `~/Library/Application Support/IronmanCoach/ironman.db`
- Windows: `%APPDATA%\IronmanCoach\ironman.db`

Darin bleiben Chatverlauf, Coach-Gedächtnis, Ziele, Check-ins, Trainingsplan und
Garmin-Werte über App-Neustarts und Updates hinweg erhalten. Die persönliche Datenbank
ist absichtlich **nicht** in Git enthalten. Eine neue Installation beginnt daher mit
einem leeren persönlichen Profil.

Die allgemeine Trainingsrecherche liegt unter `research/` und wird in jede Desktop-
App eingebaut. Der Coach sucht bei jeder Frage automatisch die relevantesten Abschnitte
aus den kuratierten Methodik-, Trainings-, Ernährungs-, Erholungs-, Verletzungs- und
Race-Day-Dokumenten. Lokal verwendete automatisch erzeugte Transkripte fremder Inhalte
werden aus Lizenzgründen nicht im öffentlichen Repository weitergegeben.

## Funktionen

- Dashboard mit HRV, Ruhepuls, Body Battery, Readiness und CTL/ATL/TSB
- Ziele und Trainingsplan mit Workout-Verwaltung
- Wochenkalender für geplante und absolvierte Einheiten
- täglicher subjektiver Check-in
- persistenter deutschsprachiger Coach-Chat
- Garmin-Sync und Push strukturierter Workouts
- Wetter-, Kalender-, Schwimmhallen- und Ostsee-Kontext
- lokaler Datenspeicher; Desktop-Backend auf `127.0.0.1`, opt-in Mobile-API auf Port 8766

## Entwicklung

Voraussetzungen: Python 3.11+.

```bash
python -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
COACH_DB=/tmp/ironman-coach-dev.db .venv/bin/uvicorn backend.main:app --host 127.0.0.1 --port 8765
```

Unter Windows lautet der Aktivierungspfad `.venv\Scripts\python.exe`.
Danach im Browser `http://127.0.0.1:8765` öffnen.

Desktop-Build lokal:

```bash
python -m pip install pyinstaller
pyinstaller --noconfirm --clean IronmanCoach.spec
```

GitHub Actions baut bei Tags wie `v0.1.0` automatisch Windows x64, macOS Apple
Silicon und macOS Intel. Separate `apple-v…`- und `android-v…`-Tags prüfen die
nativen Clients und veröffentlichen die jeweils ohne private Signierschlüssel
sinnvoll erzeugbaren Artefakte.

## Projektstruktur

```text
backend/       FastAPI, Coach-Agent, Garmin, SQLite und lokale Recherche-Suche
web/           gemeinsame responsive Desktop-Oberfläche
research/      evidenzbasierte Methodik, Deep Dives und Quelltranskripte
frontend/      aktive native SwiftUI-Oberfläche für macOS, iPhone und iPad
android/       native Kotlin-/Jetpack-Compose-App für Android
desktop_app.py plattformübergreifender nativer Launcher
```

## Datenschutz

Persönliche Trainingsdaten und Zugangsdaten werden nicht mit einem Release geteilt.
Netzwerkzugriffe gehen nur zu den vom Nutzer aktiv verwendeten Diensten (Claude,
Garmin, Open-Meteo und optional Kalenderquellen). Das Projekt ersetzt keine
medizinische Diagnose; Schmerzen, Krankheitssymptome oder medizinische Risiken gehören
in professionelle Hände.
