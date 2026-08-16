#!/usr/bin/env python3
"""End-to-end smoke test: init DB, seed a metric, ask the coach to act.

Verifies the coach can (a) authenticate via subscription, (b) call a custom
tool, (c) modify the local DB. Run:
    .venv/bin/python spikes/coach_e2e.py
"""
import asyncio
import os
import sys

os.environ.pop("ANTHROPIC_API_KEY", None)

from backend.db import database as db
from backend.agent.coach_agent import coach_reply_once


async def main() -> int:
    db.init_db()
    # Seed today's metrics so the coach has data to reason about.
    today = db.today_str()
    db.upsert("daily_metrics", ["date"], {
        "date": today, "hrv": 45, "rhr": 52, "sleep_hours": 5.2,
        "body_battery": 35, "training_readiness": 28,
    })

    prompt = (
        f"Heute ist {today}. Schau dir meine Werte für heute an "
        "(nutze deine Tools), bewerte den Tag mit Status Grün/Gelb/Rot und "
        "setze den Status per Tool. Halte dich kurz."
    )
    print("Asking coach...\n")
    reply = await coach_reply_once(prompt)
    print("COACH REPLY:\n", reply, "\n")

    status = db.get_day_status(today)
    print("DB day_status after:", status)
    if status:
        print("\nE2E OK: coach authenticated, called a tool, and wrote to the DB.")
        return 0
    print("\nE2E WARN: coach replied but did not write day_status (check reply).")
    return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
