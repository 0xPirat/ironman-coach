# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_all, collect_submodules


datas = [
    ("backend/db/schema.sql", "backend/db"),
    ("research", "research"),
    ("web", "web"),
]
binaries = []
hiddenimports = (
    collect_submodules("backend")
    + collect_submodules("webview")
    + collect_submodules("keyring.backends")
)

for package in ("claude_agent_sdk", "garminconnect"):
    package_datas, package_binaries, package_hidden = collect_all(package)
    datas += package_datas
    binaries += package_binaries
    hiddenimports += package_hidden

a = Analysis(
    ["desktop_app.py"],
    pathex=["."],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="Ironman Coach",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    name="Ironman Coach",
)

if sys.platform == "darwin":
    app = BUNDLE(
        coll,
        name="Ironman Coach.app",
        bundle_identifier="com.johannesbenedict.ironmancoach",
        info_plist={
            "CFBundleDisplayName": "Ironman Coach",
            "NSHighResolutionCapable": True,
            "LSMinimumSystemVersion": "12.0",
            "NSAppTransportSecurity": {"NSAllowsLocalNetworking": True},
        },
    )
