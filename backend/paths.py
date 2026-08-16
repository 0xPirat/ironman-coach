"""Cross-platform paths for development and packaged desktop builds."""
from __future__ import annotations

import os
import sys
from pathlib import Path


def resource_root() -> Path:
    """Root containing bundled ``backend/``, ``research/`` and ``web/`` files."""
    bundle_root = getattr(sys, "_MEIPASS", None)
    if bundle_root:
        return Path(bundle_root)
    return Path(__file__).resolve().parent.parent


def user_data_dir() -> Path:
    """Stable per-user data folder that survives app upgrades."""
    if sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    elif os.name == "nt":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "IronmanCoach"
