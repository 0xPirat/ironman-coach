"""Background daily agent.

Runs once per day via launchd (see setup-service.sh). Does:
  1. Garmin sync (last 2 days to catch overnight uploads)
  2. Asks the coach to evaluate the day, update status and memory
  3. Sends a macOS notification with the short summary

Manual run:  cd ~/ironman-coach && .venv/bin/python -m backend.daily_agent
"""
from __future__ import annotations

import asyncio
import subprocess
from datetime import date


DAILY_PROMPT = """\
Führe den täglichen Morgen-Check durch. Heute ist {today}.

1. Prüfe mit get_today, get_metrics und get_checkin die aktuellen Daten.
2. Hole mit get_weather die aktuellen Wetterdaten und den 7-Tages-Forecast.
3. Bewerte den Tag: setze den Status via set_day_status (GRÜN/GELB/ROT) mit kurzer Begründung.
   Berücksichtige dabei das Wetter — z. B. ob die geplante Outdoor-Einheit bei den heutigen
   und morgigen Bedingungen sinnvoll ist oder ob eine Anpassung (Indoor/Verschieben) besser wäre.
4. Falls Outdoor-Einheiten in den nächsten 3 Tagen bei ungünstigen Bedingungen (outdoor_suitable=False)
   geplant sind, schlage proaktiv eine Anpassung vor (Indoor-Alternative oder Tausch mit einem
   besseren Wettertag).
5. Speichere neue, dauerhaft relevante Erkenntnisse zum Athleten via save_memory (nur wenn wirklich neu).
6. Gib am Ende eine kurze Zusammenfassung aus (3-5 Sätze, kein Markdown) — diese erscheint
   als macOS-Benachrichtigung auf dem Sperrbildschirm. Erwähne das Wetter nur wenn es
   trainingsrelevant ist (z. B. "Morgen Regen — Ride auf übermorgen verschoben.").
"""


def _notify(title: str, body: str) -> None:
    safe_body = body.replace('"', "'").replace("\n", " ")
    safe_title = title.replace('"', "'")
    subprocess.run(
        ["osascript", "-e", f'display notification "{safe_body}" with title "{safe_title}"'],
        check=False,
    )


def _extract_summary(text: str, max_chars: int = 220) -> str:
    structured_prefixes = (
        "Status:", "Begründung:", "Heutiger Plan:", "Geänderte Einheit:",
        "Zielzone:", "Dauer:", "Intensität:", "Ernährung", "Warnsignal",
        "🟢", "🟡", "🔴",
    )
    prose = [
        line.strip()
        for line in text.splitlines()
        if line.strip() and not any(line.strip().startswith(p) for p in structured_prefixes)
    ]
    summary = " ".join(prose)
    if len(summary) > max_chars:
        summary = summary[:max_chars].rsplit(" ", 1)[0] + "…"
    return summary or text[:max_chars]


async def _run() -> None:
    from .db import database as db
    from .garmin_sync import sync_last_n_days

    db.init_db()

    print("→ Garmin-Sync (2 Tage)…", flush=True)
    try:
        result = sync_last_n_days(2)
        print(f"  Sync: {result}", flush=True)
    except Exception as exc:  # noqa: BLE001
        print(f"  Sync-Fehler (fortfahren): {exc}", flush=True)

    print("→ Coach-Analyse…", flush=True)
    from .agent.coach_agent import coach_reply_once

    today = date.today().isoformat()
    reply = await coach_reply_once(DAILY_PROMPT.format(today=today))
    print(reply, flush=True)

    summary = _extract_summary(reply)
    _notify("Ironman Coach", summary)
    print("→ Benachrichtigung gesendet.", flush=True)


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
