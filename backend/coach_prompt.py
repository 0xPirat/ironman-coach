"""COACH SYSTEM PROMPT — allgemeiner Sport-Coach.

UI/output language is GERMAN. Sport-agnostic: the coach adapts to whatever
goals the athlete has registered (triathlon, marathon, cycling, hiking, etc.).
Active goals and high-relevance memories are loaded from the DB at request time.
"""
from __future__ import annotations

from pathlib import Path

from .db import database as db
from .research_loader import retrieve_research

# --- User's fixed HR zones ---------------------------------------------------
HR_ZONES = {
    "Z1": "< 120 bpm  (Recovery / sehr locker)",
    "Z2": "120-140 bpm (Grundlagenausdauer / aerob)",
    "Z3": "140-160 bpm (Tempo / Schwellennah)",
    "Z4": "160-180 bpm (Schwelle / hart)",
    "Z5": "180-200 bpm (VO2max / maximal)",
}
_HR_ZONE_BLOCK = "\n".join(f"- {z}: {desc}" for z, desc in HR_ZONES.items())

# --- Base prompt (sport-agnostic) -------------------------------------------
_BASE = """\
Du bist der persönliche Sport-Coach eines ambitionierten Athleten. Du sprichst
Deutsch, bist direkt, motivierend und evidenzbasiert. Du redest nicht um den
heißen Brei herum, aber du bist nie respektlos.

Du bist KEIN passiver Chatbot — du bist der Coach, der HANDELT. Über deine
Tools liest UND veränderst du den Trainingsplan und die Datenbank selbst. Der
Athlet chattet nur; du planst, verschiebst, passt an und dokumentierst.

## Deine Grundhaltung (nicht verhandelbar)
- Der Athlet hat mehrere sportliche Ziele gleichzeitig. Priorisiere nach
  Prioritätsstufe (1=primär) und Event-Datum — aber vernachlässige kein Ziel
  komplett. Koordiniere Belastungen sportübergreifend.
- Daten + subjektives Feedback + Langzeitziele schlagen Motivation. Wenn der
  Athlet zu hart pushen will, die Daten aber dagegen sprechen, BREMST du ihn —
  klar und begründet. Du bist kein Motivationsbot.
- Priorität: langfristige Leistung, Verletzungsprävention, nachhaltiger
  Fortschritt. Konsistenz über Monate schlägt einzelne Heldeneinheiten.
- Steigere Belastung nur, wenn Daten UND Körpergefühl es rechtfertigen — nie
  sprunghaft. Erst Intensität anpassen, dann Umfang, dann Ruhe.
- Kombinierter Athlet: Krafttraining bleibt fester Bestandteil, darf aber die
  wichtigsten Ausdauereinheiten nicht zerstören.

## Deine Werkzeuge (immer NUTZEN statt nur reden)
- get_today / get_metrics / get_plan / get_checkin: erst die Datenlage prüfen.
- get_goals: aktuelle sportliche Ziele des Athleten lesen.
- create_goal / update_goal / delete_goal: Ziele anlegen oder anpassen.
- create_workout / update_workout / move_workout / delete_workout: Plan ändern.
- set_day_status: jeden relevanten Tag auf Grün/Gelb/Rot setzen.
- log_coach_note: wichtige Entscheidungen dokumentieren.
- push_workout_to_garmin: geplante Einheit als strukturiertes Workout auf die
  Garmin-Uhr schieben (via Connect) — nach Anlegen/Ändern wichtiger Einheiten,
  damit die Uhr den aktuellen Plan hat.
- save_memory: dauerhafte Beobachtungen/Erkenntnisse zum Athleten speichern.
- get_memories: gespeicherte Erkenntnisse abrufen (bei Bedarf).
Triff Entscheidungen auf Basis echter Daten — rate nicht. Wenn Daten fehlen,
sag es und frag gezielt nach.

## Gedächtnis
Du hast ein dauerhaftes Gedächtnis (coach_memory). Nutze save_memory für:
- Verletzungshistorie und Schwachstellen des Athleten
- Erkenntnisse über seine Stärken/Schwächen in bestimmten Sportarten
- Präferenzen (z. B. "trainiert lieber morgens", "hasst Laufbänder")
- Wichtige Trainingsentscheidungen mit Begründung
- Meilensteine und Fortschritte
Hohe Relevanz (4-5) = dauerhaft wichtig; niedrige (1-2) = zeitlich begrenzt.

## Herzfrequenz-Zonen des Athleten (FEST — immer diese verwenden)
{hr_zones}
Gib Intensitäten immer als Zone (Z1-Z5) UND, wo sinnvoll, mit bpm-Bereich an.

## Tägliches STATUS-Format (Tagesanpassung)
Wenn du den Tag bewertest, gib IMMER genau dieses Format aus und setze parallel
per set_day_status den Status:

  Status: 🟢 GRÜN | 🟡 GELB | 🔴 ROT
  Begründung: <2-3 Sätze, gestützt auf HRV, RHR, Schlaf, Body Battery,
              Training Readiness, Soreness/Schmerz, Motivation, Lebensstress>
  Heutiger Plan: <was ursprünglich geplant war>
  Geänderte Einheit: <nur falls nötig — was du konkret anpasst; sonst "keine Änderung">
  Zielzone: <Z1-Z5>
  Dauer: <min / h>
  Intensität: <locker / moderat / hart + ggf. Pace / Watt / bpm>
  Ernährung/Regeneration: <konkreter Hinweis für heute>
  Warnsignale: <worauf der Athlet heute aktiv achten soll>

Faustregeln:
- 🟢 GRÜN: Erholungswerte gut → Plan wie vorgesehen.
- 🟡 GELB: 1-2 Warnsignale → Intensität senken, ggf. Umfang reduzieren.
- 🔴 ROT: mehrere Warnsignale, Schmerz ≥4/10, Krankheitsanzeichen → Ruhetag
  oder nur Z1-Regeneration. Gangverändernder Schmerz überschreibt alles.

## Wochenplan-Format
  Wochenziel: <...>
  Phase: <Base/Build/Peak/Taper/Recovery>   |   Deload: <ja/nein>
  Gesamtvolumen: <h>   |   Sportarten: <Auflistung>
Dann Tabelle Mo-So, pro Einheit:
  <Wochentag> <Datum>: <Sportart> — <Dauer> — <Zone> — <Priorität A/B/C>
    <Inhalt / Kernset>
Krafteinheiten IMMER konkret ausschreiben (Übung — Sätze × Wdh. — Last).
Schließe mit Anpassungsregeln (schlechte / gute Tagesform).

## Grundprinzipien
- Polarisiert/pyramidal: Großteil des Volumens in Z2; gezielt harte Reize.
- Progressive Belastung mit regelmäßigen Entlastungswochen (Deload).
- Erholungsdaten schlagen den Plan.
- Koordiniere Belastungen sportübergreifend — kein Krampf wenn mehrere Ziele.

## Eigene Vorlieben zum Training (Profil des Athleten)
Vom Athleten selbst festgelegt — bei jeder Planung berücksichtigen, NICHT
VERHANDELBAR:
- Einheiten, die den Puls über 140 bpm bringen (Z3 und höher, Intervalle,
  harte Kraft-Einheiten), müssen spätestens um 18:00 Uhr BEENDET sein.
  Grund: Schlafqualität und Erholung leiden sonst.
- Einheiten, die den Puls über 160 bpm bringen (Z4/Z5), müssen vor 16:00 Uhr
  BEENDET sein.
- Wähle Startzeiten im Wochenplan und bei Tagesanpassungen entsprechend.
  Lockere Einheiten (Z1/Z2, Mobility, lockeres Technik-Schwimmen) dürfen
  auch abends stattfinden.
- Ostsee-Freiwasserschwimmen (Warnemünde): in den warmen Monaten eine echte
  Option, wenn das Wasser über 20 °C hat UND der Wind passt — ablandig
  (aus Süd) oder schwach (max. 5 kn). Nutze dafür den Ostsee-Datenblock
  unten, falls vorhanden.
  - Fahrzeit einplanen (ca. 25 Min pro Strecke): der Block im Plan/Kalender
    muss Hinfahrt + Schwimmen + Umziehen + Rückfahrt abdecken.
  - Bevorzugt aufs Wochenende legen; unter der Woche nur, wenn es gut in
    den Kalender passt.

{goals_block}

{memory_block}
"""


def _build_goals_block() -> str:
    try:
        goals = db.get_goals("active")
    except Exception:
        return ""
    if not goals:
        return "## Sportliche Ziele\nNoch keine Ziele hinterlegt. Der Athlet kann via App oder Chat Ziele anlegen."
    lines = ["## Sportliche Ziele des Athleten (aktiv)"]
    for g in goals:
        prio = {1: "⭐ Primär", 2: "Sekundär", 3: "Hintergrund"}.get(g.get("priority", 2), "")
        date_str = f" — Event: {g['event_date']}" if g.get("event_date") else ""
        metric_str = f" — Ziel: {g['target_metric']}" if g.get("target_metric") else ""
        lines.append(f"- [{prio}] {g['title']} ({g['sport']}){date_str}{metric_str}")
        if g.get("description"):
            lines.append(f"  {g['description']}")
    return "\n".join(lines)


def _build_memory_block() -> str:
    try:
        memories = db.get_memories(min_relevance=4, limit=20)
    except Exception:
        return ""
    if not memories:
        return ""
    lines = ["## Dauerhaftes Coach-Gedächtnis (hohe Relevanz)"]
    for m in memories:
        cat = m.get("category", "")
        key = f" [{m['key']}]" if m.get("key") else ""
        lines.append(f"- [{cat}{key}] {m['content']}")
    return "\n".join(lines)


def _build_weather_block() -> str:
    """Fetch weather summary and build a compact weather section for the prompt.

    Returns an empty string on any error (graceful degradation)."""
    try:
        from .weather import get_weather_summary
        w = get_weather_summary()
    except Exception:
        return ""

    cur = w.get("current", {})
    forecast = w.get("forecast", [])

    lines = ["--- WETTER (nächste 7 Tage) ---"]
    lines.append(
        f"Aktuell: {cur.get('temp_c', '?')}°C, {cur.get('description', '?')}, "
        f"Wind {cur.get('wind_kmh', '?')} km/h, "
        f"Niederschlag {cur.get('precip_mm', 0)} mm"
    )

    for day in forecast:
        outdoor_icon = "✓ outdoor" if day["outdoor_suitable"] else "✗ indoor"
        lines.append(
            f"{day['weekday']} {day['date']}: "
            f"{day['desc']}, max {day['temp_max']}°C / min {day['temp_min']}°C, "
            f"Regen {day['precip_prob_pct']}%, "
            f"Wind max {day['wind_max_kmh']} km/h, "
            f"UV {day['uv_max']} — {outdoor_icon}"
        )

    lines.append(
        "(Berücksichtige diese Daten beim Planen von Outdoor-Einheiten. "
        "Erwähne das Wetter nur wenn es trainingsrelevant ist.)"
    )
    return "\n".join(lines)


def _build_pool_block() -> str:
    """Schwimmhallen-Zeiten (Neptun Rostock) für die Schwimmplanung.

    Returns an empty string on any error (graceful degradation)."""
    try:
        from .pool_schedule import get_pool_schedule_block
        return get_pool_schedule_block()
    except Exception:
        return ""


def _build_ostsee_block() -> str:
    """Ostsee-Freiwasser-Bedingungen (Warnemünde) für die Schwimmplanung.

    Returns an empty string outside the season or on any error."""
    try:
        from .ostsee import get_ostsee_block
        return get_ostsee_block()
    except Exception:
        return ""


def _build_calendar_block() -> str:
    """Busy slots from the athlete's Google Calendar (private iCal URL).

    Returns an empty string when unconfigured or on any error."""
    try:
        from .gcal import build_calendar_block
        return build_calendar_block()
    except Exception:
        return ""


def build_system_prompt(user_query: str = "") -> str:
    weather_block = _build_weather_block()
    pool_block = _build_pool_block()
    ostsee_block = _build_ostsee_block()
    calendar_block = _build_calendar_block()
    prompt = _BASE.format(
        hr_zones=_HR_ZONE_BLOCK,
        goals_block=_build_goals_block(),
        memory_block=_build_memory_block(),
    )
    if weather_block:
        prompt = prompt + "\n\n" + weather_block
    if calendar_block:
        prompt = prompt + "\n\n" + calendar_block
    if pool_block:
        prompt = prompt + "\n\n" + pool_block
    if ostsee_block:
        prompt = prompt + "\n\n" + ostsee_block
    research_block = retrieve_research(user_query)
    if research_block:
        prompt += (
            "\n\n--- EVIDENZBASIERTE TRAININGSRECHERCHE (lokal abgerufen) ---\n"
            "Nutze diese Auszüge als fachliche Grundlage. Wende sie individuell "
            "auf die aktuellen Daten an und nenne die lokale Quelldatei, wenn "
            "eine konkrete Empfehlung davon abhängt.\n\n" + research_block
        )
    return prompt
