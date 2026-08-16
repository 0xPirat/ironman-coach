#!/usr/bin/env bash
# Builds IronmanCoach.app (Release, unsigniert) und installiert sie in ~/Applications.
# Voraussetzung: Xcode, xcodegen (brew install xcodegen), Python-venv in ~/ironman-coach/.venv
#
# Ausführen:  cd ~/ironman-coach && bash install.sh

set -euo pipefail

REPO="$HOME/ironman-coach"
FRONTEND="$REPO/frontend"
BUILD_DIR="$REPO/build"
SCHEME="IronmanCoach"   # Xcode scheme/target name
APP_NAME="Coach"        # PRODUCT_NAME → Coach.app
INSTALL_DIR="$HOME/Applications"

# --- Checks ------------------------------------------------------------------
if ! command -v xcodegen &>/dev/null; then
  echo "✗ xcodegen nicht gefunden.  →  brew install xcodegen"
  exit 1
fi
if ! command -v xcodebuild &>/dev/null; then
  echo "✗ xcodebuild nicht gefunden. Xcode über den App Store installieren."
  exit 1
fi

# --- Xcode-Projekt generieren ------------------------------------------------
echo "→ XcodeGen…"
cd "$FRONTEND"
xcodegen generate --quiet 2>/dev/null || xcodegen generate

# --- Build -------------------------------------------------------------------
echo "→ Baue Release-App (ohne Signierung)…"
mkdir -p "$BUILD_DIR"
if xcodebuild \
    -project "$SCHEME.xcodeproj" \
    -scheme  "$SCHEME" \
    -configuration Release \
    -derivedDataPath "$BUILD_DIR" \
    CODE_SIGN_IDENTITY="" \
    CODE_SIGNING_REQUIRED=NO \
    CODE_SIGNING_ALLOWED=NO \
    build > "$BUILD_DIR/build.log" 2>&1; then
  echo "  Build erfolgreich."
else
  echo "✗ Build fehlgeschlagen. Letzte Zeilen aus dem Log:"
  tail -30 "$BUILD_DIR/build.log"
  exit 1
fi

# --- Installieren ------------------------------------------------------------
APP=$(find "$BUILD_DIR" -name "$APP_NAME.app" -maxdepth 7 -type d | head -1)
if [ -z "$APP" ]; then
  echo "✗ .app nicht gefunden — Build-Log prüfen: $BUILD_DIR/build.log"
  exit 1
fi

echo "→ Installiere nach ${INSTALL_DIR}…"
mkdir -p "$INSTALL_DIR"
rm -rf "$INSTALL_DIR/$APP_NAME.app"
cp -r "$APP" "$INSTALL_DIR/"

# Gatekeeper-Quarantäne entfernen (lokal gebaute, unsignierte App)
xattr -cr "$INSTALL_DIR/$APP_NAME.app"

echo ""
echo "✓ Fertig!"
echo "  Starten:    open ~/Applications/$APP_NAME.app"
echo "  Spotlight:  Cmd+Space → Coach"
echo ""
echo "  Tipp: Hintergrunddienst (Sidecar + Daily-Agent) einrichten mit:"
echo "        bash ~/ironman-coach/setup-service.sh"
