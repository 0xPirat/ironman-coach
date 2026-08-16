"""Native macOS/Windows launcher for the local Ironman Coach web UI."""
from __future__ import annotations

import json
import os
import socket
import sys
import threading
import time
from pathlib import Path
from urllib.request import urlopen

from backend.paths import user_data_dir


HOST = "127.0.0.1"


def _free_port(preferred: int = 8765) -> int:
    with socket.socket() as probe:
        try:
            probe.bind((HOST, preferred))
            return preferred
        except OSError:
            probe.bind((HOST, 0))
            return int(probe.getsockname()[1])


def _wait_for_server(url: str, timeout: float = 20.0) -> None:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with urlopen(f"{url}/health", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.15)
    raise RuntimeError("Der lokale Coach-Dienst konnte nicht gestartet werden.")


def _existing_server_url(port: int = 8765) -> str | None:
    url = f"http://{HOST}:{port}"
    try:
        with urlopen(f"{url}/health", timeout=1) as response:
            body = response.read().decode("utf-8")
        return url if response.status == 200 and "sport-coach" in body else None
    except OSError:
        return None


def main() -> None:
    data_dir = user_data_dir()
    data_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("COACH_DB", str(data_dir / "ironman.db"))
    os.environ.setdefault("COACH_LOG_DIR", str(data_dir / "logs"))
    os.environ.pop("ANTHROPIC_API_KEY", None)

    smoke_test = "--smoke-test" in sys.argv
    if smoke_test:
        # CI-safe package verification: importing the full API also imports the
        # coach SDK, and init_db proves that bundled schema/resources resolve.
        # Avoid opening a native window or depending on a runner's network loop.
        from backend.db import database as db
        from backend.main import app_info
        db.init_db()
        payload = app_info()
        if not payload["research_ready"]:
            raise RuntimeError("Gebündelte Trainingsrecherche fehlt.")
        print(json.dumps(payload, ensure_ascii=False))
        return

    url = _existing_server_url()
    server = worker = None
    if url is None:
        port = _free_port()
        url = f"http://{HOST}:{port}"
        import uvicorn
        config = uvicorn.Config(
            "backend.main:app", host=HOST, port=port, log_level="warning", access_log=False
        )
        server = uvicorn.Server(config)
        worker = threading.Thread(target=server.run, name="coach-sidecar", daemon=True)
        worker.start()
        _wait_for_server(url)

    import webview

    window = webview.create_window(
        "Ironman Coach",
        url,
        width=1440,
        height=900,
        min_size=(980, 680),
        background_color="#071018",
    )
    webview.start(debug=os.environ.get("COACH_DEBUG") == "1")
    if server and worker:
        server.should_exit = True
        worker.join(timeout=3)


if __name__ == "__main__":
    main()
