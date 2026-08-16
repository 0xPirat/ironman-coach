# Coach auf iPhone, iPad und Mac

Die SwiftUI-App besitzt zwei Apple-Targets aus demselben Quellcode:

- `Coach-iOS`: iOS/iPadOS 17 oder neuer, als Client für den selbst gehosteten Coach-Server
- `Coach-macOS`: macOS 14 oder neuer, mit lokalem Python-Sidecar oder einem konfigurierten Server

Das Projekt wird reproduzierbar aus `frontend/project.yml` mit XcodeGen erzeugt. Es werden keine Zertifikate, Provisioning Profiles, Tokens oder sonstige Geheimnisse eingecheckt.

## Was GitHub ohne Apple-Zertifikat bereitstellen kann

Der Workflow `.github/workflows/apple.yml` prüft beide Targets. Bei einem Tag wie `apple-v0.2.0` erstellt er eine GitHub-Release mit:

- `Coach-macOS-adhoc-not-notarized.zip`: eine ad-hoc-signierte, nicht notarierte macOS-App. Sie ist technisch startfähig, macOS kann beim ersten Download aber eine Gatekeeper-Warnung anzeigen. Der Python-Backend-Teil ist nicht in diesem kleinen Client-Artefakt enthalten.
- `Coach-iOS-Simulator-only.zip`: eine App ausschließlich für Apples iPhone-/iPad-Simulator. Sie lässt sich nicht auf echter iPhone-/iPad-Hardware installieren.
- `SHA256SUMS.txt`: Prüfsummen der beiden ZIP-Dateien.

Eine allgemein installierbare iPhone-/iPad-IPA kann GitHub nicht seriös ohne ein Apple-Developer-Zertifikat und Provisioning Profile erzeugen. TestFlight und App Store benötigen zusätzlich einen kostenpflichtigen Apple-Developer-Account. Diese Grenze ist eine Vorgabe von Apple, kein Fehler des Projekts.

## Auf einem echten iPhone oder iPad installieren

Benötigt werden ein Mac mit Xcode, eine Apple-ID und das per USB oder WLAN verbundene Gerät. Ein kostenloses „Personal Team“ reicht zum persönlichen Test; eine damit installierte App muss typischerweise nach einigen Tagen erneut aus Xcode signiert werden.

1. Das GitHub-Repository als Source Code herunterladen oder klonen.
2. XcodeGen einmalig installieren: `brew install xcodegen`.
3. Im Terminal aus dem Repository ausführen:

   ```bash
   cd frontend
   xcodegen generate --spec project.yml
   open IronmanCoach.xcodeproj
   ```

4. In Xcode das Scheme `Coach-iOS` und das eigene iPhone/iPad wählen.
5. Im Target `IronmanCoachMobile` unter **Signing & Capabilities** das eigene Team wählen. Falls die Bundle-ID bereits vergeben ist, `com.johannesbenedict.ironmancoach.mobile` durch eine eigene eindeutige ID ersetzen.
6. Auf **Run** drücken. Falls iOS danach fragt, den Entwicklermodus beziehungsweise das Entwicklerzertifikat auf dem Gerät bestätigen.

Damit signiert Xcode die lokal aus dem offenen Quellcode gebaute App für genau dieses Gerät. Es werden keine geheimen Projektzertifikate benötigt.

## Coach-Server für iPhone/iPad starten

iOS darf keinen Python-Prozess aus einem App-Bundle starten. Die mobile App verbindet sich daher mit dem separaten, token-geschützten Server auf einem Mac oder einem eigenen HTTPS-Host.

Auf dem Mac im Repository:

```bash
python3 -m venv .venv
.venv/bin/pip install -r backend/requirements.txt
export IRONMAN_MOBILE_TOKEN="$(openssl rand -hex 32)"
.venv/bin/python -m backend.mobile_server
```

Der mobile Server hört standardmäßig auf Port `8766` und verweigert den Start ohne einen ausreichend starken `IRONMAN_MOBILE_TOKEN`. Die bisherige lokale macOS-Verbindung `127.0.0.1:8765` bleibt davon getrennt.

Die lokale IP-Adresse des Macs findet man zum Beispiel unter **Systemeinstellungen → WLAN → Details → TCP/IP**. Danach in der iPhone-/iPad-App über das Zahnrad eintragen:

- Server: `http://IP-DES-MACS:8766`, zum Beispiel `http://192.168.1.20:8766`
- Token: exakt der Wert aus `IRONMAN_MOBILE_TOKEN`

Mac und Mobilgerät müssen sich im selben vertrauenswürdigen privaten Netz befinden, und die macOS-Firewall muss die Verbindung erlauben. Niemals Port 8766 ohne HTTPS über das öffentliche Internet freigeben. Für Nutzung außerhalb des eigenen WLANs gehört ein TLS-terminierender Reverse Proxy oder ein vertrauenswürdiges privates VPN vor den Server.

Der Token wird in Apples Schlüsselbund gespeichert. Der Client sendet ihn bei jedem Request als `Authorization: Bearer …`, auch bei `/health`.

## Lokal ohne Signierung prüfen

```bash
cd frontend
xcodegen generate --spec project.yml

# macOS
xcodebuild \
  -project IronmanCoach.xcodeproj \
  -scheme Coach-macOS \
  -configuration Debug \
  -destination 'platform=macOS' \
  -derivedDataPath /tmp/coach-macos \
  CODE_SIGNING_ALLOWED=NO build

# iPhone/iPad-Simulator
xcodebuild \
  -project IronmanCoach.xcodeproj \
  -scheme Coach-iOS \
  -configuration Debug \
  -sdk iphonesimulator \
  -destination 'generic/platform=iOS Simulator' \
  -derivedDataPath /tmp/coach-ios \
  CODE_SIGNING_ALLOWED=NO build
```

Das Simulator-Artefakt kann anschließend so installiert werden:

```bash
xcrun simctl install booted /tmp/coach-ios/Build/Products/Debug-iphonesimulator/Coach.app
xcrun simctl launch booted com.johannesbenedict.ironmancoach.mobile
```

## Spätere offizielle Verteilung

Für eine Installation ohne Xcode muss der Projektinhaber einen Apple-Developer-Account bereitstellen und sich für TestFlight/App Store oder eine andere von Apple erlaubte Distributionsart entscheiden. Erst dann sollten Zertifikate und Provisioning Profiles als verschlüsselte GitHub-Secrets hinterlegt und ein signierter Archive-/Export-Schritt ergänzt werden. Private Keys dürfen niemals in das Repository gelangen.

## Noch offene Open-Source-Lizenz

Im Repository-Root liegt derzeit noch keine `LICENSE`. Öffentlich sichtbarer Quellcode ist deshalb rechtlich noch nicht automatisch Open Source. Vor einer öffentlichen Freigabe muss der Rechteinhaber bewusst eine Projektlizenz auswählen (zum Beispiel MIT, Apache-2.0 oder GPL); diese Entscheidung wurde nicht automatisiert vorweggenommen.
