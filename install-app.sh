#!/usr/bin/env bash
# Builds Coach.app and installs it to ~/Applications.
#
# Why not a plain `xcodebuild build`: macOS puts a protected `com.apple.macl`
# xattr on the icon assets, and codesign refuses to sign a bundle carrying it
# ("resource fork, Finder information, or similar detritus not allowed").
# `xattr -c` cannot strip macl. So we build unsigned, copy the bundle through
# `ditto --noextattr` (which drops every xattr), and ad-hoc sign the clean copy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
STAGE="$(mktemp -d)/Coach.app"
DEST="$HOME/Applications/Coach.app"
trap 'rm -rf "$(dirname "$STAGE")"' EXIT

echo "→ Baue (Release, unsigniert)…"
xcodebuild -project "$ROOT/frontend/IronmanCoach.xcodeproj" \
           -scheme IronmanCoach -configuration Release \
           -derivedDataPath "$ROOT/build" \
           CODE_SIGNING_ALLOWED=NO build >/dev/null

echo "→ Kopiere attributfrei und signiere…"
ditto --noextattr --norsrc "$ROOT/build/Build/Products/Release/Coach.app" "$STAGE"
codesign --force --deep --sign - "$STAGE"
codesign --verify --verbose "$STAGE"

echo "→ Beende laufende App…"
osascript -e 'quit app "Coach"' 2>/dev/null || true
sleep 2
pkill -f "Coach.app/Contents/MacOS/Coach" 2>/dev/null || true
sleep 1

# Keep exactly one rollback copy rather than a growing pile of backups.
if [ -d "$DEST" ]; then
    echo "→ Sichere bisherige Version nach Coach-vorher.app…"
    rm -rf "$HOME/Applications/Coach-vorher.app"
    mv "$DEST" "$HOME/Applications/Coach-vorher.app"
fi

echo "→ Installiere…"
ditto --noextattr --norsrc "$STAGE" "$DEST"

echo "✓ Fertig. Starte mit: open \"$DEST\""
