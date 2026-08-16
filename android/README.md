# Ironman Coach für Android

Die Android-App ist ein nativer Kotlin-/Jetpack-Compose-Client für das
vorhandene Ironman-Coach-Backend. Sie zeigt Garmin-Metriken, Ziele, geplante
und absolvierte Einheiten, speichert den Tages-Check-in und unterstützt den
streamenden Coach-Chat.

## Wichtig: App und Backend

Die APK enthält bewusst weder Python, die SQLite-Datenbank noch Claude- oder
Garmin-Zugangsdaten. Diese Komponenten laufen weiterhin auf dem Mac. Die App
funktioniert als Oberfläche, sobald sie die authentifizierte Mobile-API des
Macs erreicht. Ohne Backend lässt sich die App öffnen und konfigurieren, aber
Coach, Sync und Trainingsdaten sind dann nicht verfügbar.

## Fertige APK aus GitHub installieren

1. Auf GitHub rechts **Releases** öffnen.
2. Aus einem Release mit Tag `android-v…` die Datei
   `ironman-coach-android-debug.apk` herunterladen.
3. Android erlaubt die Installation nach Bestätigung von „Unbekannte Apps aus
   dieser Quelle“. Danach die APK öffnen und installieren.

Der Workflow erzeugt ein installierbares **Debug-APK** mit der üblichen
Android-Debugsignatur. Es enthält keine privaten Projekt-Schlüssel und ist für
freie Testverteilung gedacht, nicht für den Play Store. Da Debugsignaturen von
verschiedenen Build-Umgebungen abweichen können, muss eine alte Installation
vor einem Wechsel der Signatur eventuell deinstalliert werden.

Bei normalen Branch-Builds liegt dieselbe APK unter **Actions → Android APK →
Artifacts**. GitHub verlangt für den Artifact-Download üblicherweise eine
Anmeldung. Bei einem `android-v…`-Tag legt der Workflow ein öffentliches GitHub
Release an, sofern das Repository öffentlich ist.

## Mobile-Backend auf dem Mac starten

Im Projektordner:

```bash
cd /pfad/zu/ironman-coach
export IRONMAN_MOBILE_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
.venv/bin/python -m backend.mobile_server
```

Der neue, separate Mobile-Server läuft standardmäßig auf `0.0.0.0:8766`. Er
startet nur mit einem Token von mindestens 32 Zeichen. Der normale macOS-
Sidecar bleibt unabhängig davon auf `127.0.0.1:8765` und benötigt keinen Token.

Die lokale IP des Macs findet man in macOS unter **Systemeinstellungen → WLAN
→ Details**. In der App werden dann beispielsweise diese Werte eingetragen:

- Server: `http://192.168.178.20:8766`
- Zugriffstoken: der Inhalt von `IRONMAN_MOBILE_TOKEN`

Das Handy und der Mac müssen sich im selben vertrauenswürdigen Netz befinden;
die macOS-Firewall muss Python eingehende Verbindungen auf Port 8766 erlauben.
Jeder API-Request einschließlich `/health` sendet
`Authorization: Bearer <token>`. Der Token wird auf Android per AES-GCM mit
einem Schlüssel aus Android Keystore gespeichert.

### Sicherheit

HTTP im lokalen WLAN verschlüsselt den Datenverkehr nicht. Es ist nur für ein
vertrauenswürdiges Heimnetz vorgesehen. Port 8766 nicht am Router ins Internet
freigeben. Für unterwegs einen privaten VPN-Zugang (z. B. WireGuard/Tailscale)
oder einen HTTPS-Reverse-Proxy mit zusätzlichem Zugriffsschutz verwenden. Die
API enthält Gesundheits- und Trainingsdaten.

## Lokal bauen

Voraussetzungen: JDK 17 und Android SDK 35. Der SDK-Pfad wird absichtlich nicht
als maschinenspezifische `local.properties` eingecheckt. Entweder sind
`ANDROID_HOME`/`ANDROID_SDK_ROOT` bereits gesetzt, oder der Build erhält den
absoluten SDK-Pfad direkt:

```bash
cd android
ANDROID_HOME=/absoluter/pfad/zum/android-sdk \
ANDROID_SDK_ROOT=/absoluter/pfad/zum/android-sdk \
./gradlew --no-daemon testDebugUnitTest lintDebug assembleDebug
```

Bei einer Standardinstallation von Android Studio auf macOS ist der Pfad meist
`$HOME/Library/Android/sdk`. GitHub Actions setzt die beiden Variablen durch
`android-actions/setup-android` automatisch.

Das installierbare Ergebnis liegt unter:

```text
android/app/build/outputs/apk/debug/ironman-coach-android-debug.apk
```

Installation auf einem per USB-Debugging verbundenen Gerät:

```bash
adb install -r app/build/outputs/apk/debug/ironman-coach-android-debug.apk
```

Im Android-Emulator verweist `http://10.0.2.2:8766` auf den Entwicklungs-Mac.

## Architektur

- Kotlin, Jetpack Compose und Material 3; minSdk 26, targetSdk 35
- Ein `CoachViewModel` hält den UI-Zustand und koordiniert parallele REST-Aufrufe
- `CoachApi` nutzt OkHttp und kotlinx.serialization, einschließlich SSE-Chat
- Basis-URL ist frei konfigurierbar; Bearer-Token wird verschlüsselt gespeichert
- Responsive Kartenanordnung für Smartphone und Tablet
- Kein Secret und kein fest verdrahteter Server im Quellcode

Der Android-Unterordner steht unter der [MIT-Lizenz](LICENSE). Für Backend- und
Apple-Code gelten die Lizenzangaben im jeweiligen Projektbereich.
