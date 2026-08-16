# iPhone-/iPad-Test mit Freunden

Stand: 16. August 2026. Apple kann Programmregeln, Preise und Upload-Anforderungen ändern; vor der tatsächlichen Einrichtung sollten die unten verlinkten Apple-Seiten noch einmal geprüft werden.

## Empfehlung

Für einen kleinen privaten Freundeskreis ist **TestFlight mit externen Testern** die beste legale und praktische Lösung.

- Freunde brauchen nur ein unterstütztes iPhone oder iPad, einen normalen Apple Account und die kostenlose TestFlight-App.
- Sie brauchen weder einen Mac noch Xcode, keine Geräte-UDID und keinen aktivierten Entwicklermodus.
- Neue Builds und Updates kommen über TestFlight.
- Die App muss dafür nicht öffentlich im App Store erscheinen.
- Erforderlich ist eine Mitgliedschaft im Apple Developer Program für 99 USD pro Mitgliedschaftsjahr beziehungsweise den von Apple angezeigten lokalen Preis.
- Ein TestFlight-Build kann höchstens 90 Tage getestet werden. Danach muss ein neuer Build bereitgestellt werden.
- Bis zu 10.000 externe Tester sind möglich. Für diesen privaten Test sollten Einladungen per E-Mail statt eines öffentlichen Links verwendet werden.
- Der erste Build für eine externe Testgruppe wird von Apple geprüft; spätere Builds erfordern möglicherweise keine vollständige erneute Prüfung.

Offizielle Grundlagen: [Apple Developer Program und Preis](https://developer.apple.com/programs/whats-included/), [TestFlight-Überblick und Grenzen](https://developer.apple.com/help/app-store-connect/test-a-beta-version/testflight-overview/), [externe Tester einladen](https://developer.apple.com/help/app-store-connect/test-a-beta-version/invite-external-testers/).

## Vergleich der realistischen und angefragten Wege

| Weg | Voraussetzungen und Grenzen | Erfahrung für Freunde | Bewertung |
| --- | --- | --- | --- |
| **TestFlight extern** | Bezahltes Apple Developer Program; erster externer Build durch TestFlight App Review; maximal 10.000 externe Tester; Build 90 Tage gültig | TestFlight installieren, Einladung annehmen, App installieren; Updates ebenfalls über TestFlight | **Empfohlen** |
| **Ad-hoc-Verteilung** | Bezahltes Programm; Apple-Distribution-Zertifikat; UDID jedes Geräts; Ad-hoc-Profil; maximal 100 registrierte iPhones und 100 registrierte iPads pro Mitgliedschaftsjahr. Deaktivierte Geräte geben innerhalb des Jahres keinen Platz zurück | IPA muss zum Beispiel per Apple Configurator oder über eine korrekt eingerichtete HTTPS-OTA-Verteilung installiert werden; bei lokaler IPA-Installation ist Entwicklermodus erforderlich | Ausweichweg für sehr wenige, bekannte Geräte oder wenn TestFlight Review vorübergehend blockiert |
| **Kostenlose Apple-ID / Personal Team** | Jeder Signierende braucht einen Mac und Xcode; höchstens 10 App-IDs, 3 registrierte Geräte und 3 Apps pro Gerät; App-IDs, Geräte und Provisioning Profiles laufen nach 7 Tagen ab | Jeder Freund muss den Quellcode selbst in Xcode bauen, mit dem eigenen Apple Account signieren und wöchentlich neu installieren | Kostenloser Kurztest, aber keine brauchbare Freundes-Beta |
| **EU-Webverteilung** | Nur für eine im EU-Raum registrierte Organisation; mindestens zwei durchgehende Jahre im Developer Program und eine App mit mehr als einer Million Erstinstallationen in der EU im Vorjahr; EU-Zusatzbedingungen, Notarisierung und eigene registrierte Website; mindestens iOS 17.5 beziehungsweise iPadOS 18 | Installation von der Entwickler-Website nach ausdrücklicher Freigabe in den Geräteeinstellungen | Für dieses junge Projekt derzeit nicht realistisch |
| **Alternative EU-Marketplaces** | Bezahltes Programm, EU-Zusatzbedingungen, Notarisierung und eine Geschäftsbeziehung zu einem zugelassenen Marketplace. Ein eigener Marketplace verlangt zusätzlich eine EU-Organisation und unter anderem entweder eine Kreditgarantie über 1 Mio. EUR oder zwei Jahre Mitgliedschaft plus eine App mit mehr als einer Million EU-Erstinstallationen im Vorjahr | EU-gebundener Marketplace-Installationsablauf statt TestFlight | Für einen privaten Freundeskreis unnötig komplex und nicht empfohlen |

Apple dokumentiert die Ad-hoc-Grenzen unter [Devices overview](https://developer.apple.com/help/account/devices/devices-overview/), die kostenlose Personal-Team-Grenzen unter [Developer account overview](https://developer.apple.com/help/account/basics/about-your-developer-account), Web Distribution unter [Getting started with Web Distribution in the EU](https://developer.apple.com/support/web-distribution-eu/) und alternative Marketplaces unter [Getting started as an alternative app marketplace](https://developer.apple.com/support/alternative-app-marketplace-in-the-eu/).

Das Apple Developer Enterprise Program ist keine Abkürzung: Es ist für interne Apps an Beschäftigte einer berechtigten Organisation gedacht, nicht für Freunde oder allgemeine Betatester.

## Bereits vorhandene technische Grundlage

Das Repository ist für den ersten manuellen TestFlight-Upload grundsätzlich passend vorbereitet:

- Scheme: `Coach-iOS`
- Target: `IronmanCoachMobile`
- Bundle-ID: `com.johannesbenedict.ironmancoach.mobile`
- iPhone und iPad: `TARGETED_DEVICE_FAMILY = "1,2"`
- Mindestversion: iOS/iPadOS 17
- Signierung: automatisch, aber noch ohne fest eingetragenes Development Team
- 1024-Pixel-App-Icon ist vorhanden

Der bestehende Workflow `.github/workflows/apple.yml` ist bewusst **kein** TestFlight-Workflow. Er baut einen iPhone-/iPad-Simulator-Client ohne Signierung. Dieses Artefakt ist nicht auf echter Hardware installierbar. Derzeit gibt es außerdem weder eine App-Store-Exportkonfiguration noch im Repository hinterlegte Signierungsdaten. Das ist vor der Kontoeinrichtung der richtige Zustand.

Vor dem ersten Upload müssen Versions- und Buildnummern sauber verwaltet werden. `frontend/IronmanCoach/Info-iOS.plist` enthält derzeit feste Werte für `CFBundleShortVersionString` und `CFBundleVersion`. Jede neue Übertragung an App Store Connect braucht eine noch nicht verwendete Buildnummer. Sinnvoll ist, die Plist-Werte später an `MARKETING_VERSION` und `CURRENT_PROJECT_VERSION` aus `frontend/project.yml` zu binden und vor jedem Upload `CURRENT_PROJECT_VERSION` zu erhöhen.

## Konkreter TestFlight-Ablauf

### 1. Bezahlte Mitgliedschaft einrichten

Mit dem eigenen Apple Account als Einzelperson oder Organisation in das Apple Developer Program eintreten. Für einen Einzelentwickler ist die Einzelmitgliedschaft der einfachste Einstieg. Bei einer Einzelmitgliedschaft erscheint der verifizierte persönliche Name als Entwicklername; eine Organisation benötigt unter anderem eine rechtliche Organisation und eine D-U-N-S-Nummer.

Noch keine Zertifikate oder privaten Schlüssel ins Repository hochladen. Account-Passwort und Zwei-Faktor-Codes niemals weitergeben.

### 2. App-ID und App-Store-Connect-Datensatz anlegen

1. In „Certificates, Identifiers & Profiles“ eine explizite App-ID für `com.johannesbenedict.ironmancoach.mobile` registrieren, sofern Xcode sie nicht automatisch anlegt.
2. In App Store Connect unter „Apps“ einen neuen iOS-App-Datensatz anlegen. Ein App-Datensatz muss existieren, bevor der erste Build hochgeladen werden kann.
3. Als Bundle-ID genau `com.johannesbenedict.ironmancoach.mobile` wählen.
4. Einen internen SKU-Wert festlegen, zum Beispiel `ironman-coach-ios`.
5. Eine öffentlich erreichbare Datenschutzerklärung vorbereiten. Sie muss die tatsächliche Verarbeitung von Trainings-, Fitness-, Gesundheits-, Chat- und Garmin-Daten sowie den selbst betriebenen Server korrekt beschreiben. Keine pauschale Aussage „keine Datenerhebung“ wählen, solange der Backend-Datenfluss das nicht zweifelsfrei erfüllt.

Offizielle Hilfe: [App Store Connect workflow](https://developer.apple.com/help/app-store-connect/get-started/app-store-connect-workflow), [App-Datenschutz verwalten](https://developer.apple.com/help/app-store-connect/manage-app-information/manage-app-privacy/).

### 3. Ersten Build manuell aus Xcode hochladen

Der erste Upload sollte bewusst manuell erfolgen. Das vermeidet CI- und Secret-Probleme, bis Bundle-ID, Vertrag und App-Store-Connect-Datensatz einmal nachweislich funktionieren.

1. `frontend/IronmanCoach.xcodeproj` in Xcode öffnen.
2. Im Target `IronmanCoachMobile` unter „Signing & Capabilities“ das bezahlte Team auswählen und automatische Signierung beibehalten.
3. Eindeutige Marketing- und Buildnummer setzen. Die Buildnummer muss bei jedem Upload steigen.
4. Als Ziel „Any iOS Device (arm64)“ beziehungsweise ein generisches iOS-Gerät wählen.
5. „Product → Archive“ ausführen.
6. Im Organizer „Distribute App → App Store Connect → Upload“ wählen.

Xcode 13 und neuer kann im Organizer cloudverwaltete Distribution-Zertifikate verwenden. Für diesen manuellen Weg ist deshalb normalerweise kein Export einer `.p12`-Datei nötig. Aktuell ist lokal eine Apple-Development-Identität vorhanden; ein Apple-Distribution-Zertifikat ist erst nach der bezahlten Mitgliedschaft beziehungsweise beim Distributionsvorgang erforderlich.

Offizielle Hilfe: [Builds hochladen](https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/), [cloudverwaltete Zertifikate](https://developer.apple.com/help/account/certificates/cloud-managed-certificates/).

### 4. Eine echte Review- und Testumgebung bereitstellen

Dieser Schritt ist für Coach genauso wichtig wie die Apple-Signierung. Die iPhone-/iPad-App enthält absichtlich keinen Python-Server. Beim ersten Start verlangt sie eine Server-URL und einen Bearer-Token.

Für Apple TestFlight App Review und Freunde außerhalb des eigenen WLANs sollte daher ein zeitlich begrenzter **HTTPS-Staging-Server** existieren:

- von außen über eine stabile HTTPS-URL erreichbar;
- getrennte Testdatenbank ohne persönliche Trainings- oder Garmin-Daten;
- eigener Beta-Token, der nach dem Test widerrufen oder rotiert wird;
- keine privaten Garmin-Zugangsdaten;
- während der Review und des vereinbarten Testzeitraums verfügbar;
- Serverprotokolle und Datenspeicherung in der Datenschutzerklärung korrekt beschrieben.

Der aktuelle Backend-Zugang verwendet einen gemeinsamen `IRONMAN_MOBILE_TOKEN`. Dieser Token darf nicht in Quellcode, IPA, GitHub Actions oder öffentliche TestFlight-Notizen geschrieben werden. Für den kleinen privaten Kreis kann er getrennt über einen sicheren Kanal übermittelt werden. Weil alle Tester mit diesem gemeinsamen Token auf dieselben Backend-Daten zugreifen können, dürfen in der Beta-Umgebung keine persönlichen Produktionsdaten liegen.

Eine öffentliche Portweiterleitung auf `http://...:8766` ist keine sichere Lösung. Für externe Tests ausschließlich HTTPS oder ein vertrauenswürdiges privates VPN verwenden. Freunde im selben privaten WLAN können alternativ ihren eigenen lokalen Server wie in `APPLE_DISTRIBUTION.md` beschrieben nutzen.

### 5. TestFlight-Information und Review ausfüllen

In App Store Connect unter „TestFlight → Test Information“ mindestens ausfüllen:

- Beta-App-Beschreibung;
- Feedback-E-Mail-Adresse;
- zu testende Funktionen;
- Review-Kontakt;
- die HTTPS-Testserver-URL und einen funktionierenden Review-Token im dafür vorgesehenen nichtöffentlichen Review-Feld;
- genaue Schritte: App starten, Zahnrad öffnen, URL und Token eingeben, „Speichern und testen“ wählen;
- Hinweis, dass nur synthetische Testdaten verwendet werden.

Wenn App Review notwendige Einstellungen, Zugänge oder Anweisungen fehlen, kann sich die Prüfung verzögern. Der Review-Server muss deshalb funktionieren, bevor der Build der externen Gruppe zugewiesen wird. Siehe [Testinformationen bereitstellen](https://developer.apple.com/help/app-store-connect/test-a-beta-version/provide-test-information/) und [App Review Information](https://developer.apple.com/distribute/app-review/).

### 6. Freunde einladen

1. In TestFlight zuerst eine interne und anschließend eine externe Gruppe wie `Freunde Beta` anlegen.
2. Den verarbeiteten Build der externen Gruppe zuweisen und zur TestFlight App Review senden.
3. Nach Freigabe die Freunde gezielt per E-Mail einladen. Für einen privaten Kreis keinen öffentlichen Einladungslink posten.
4. URL und Beta-Token getrennt und sicher schicken.
5. Vor Ablauf der 90 Tage einen neuen Build hochladen oder den Test bewusst beenden.

## Ad-hoc als Ausweichweg

Ad-hoc ist sinnvoll, wenn nur ein bis fünf konkrete Geräte kurzfristig testen sollen und die erste TestFlight-Prüfung nicht abgewartet werden kann. Es umgeht nicht die bezahlte Mitgliedschaft.

Benötigt werden:

- UDID jedes iPhones und iPads;
- Registrierung dieser Geräte im Developer Account;
- explizite App-ID;
- Apple-Distribution-Zertifikat samt privatem Schlüssel;
- Ad-hoc-Provisioning-Profile mit genau diesen Geräten;
- eine damit exportierte und signierte IPA.

Apple erlaubt bis zu 100 Geräte **je Produktfamilie und Mitgliedschaftsjahr**. iPhone und iPad sind getrennte Produktfamilien. Das Deaktivieren eines Geräts gibt den Platz während des laufenden Jahres nicht zurück. Siehe [Ad-hoc-Profil erstellen](https://developer.apple.com/help/account/provisioning-profiles/create-an-ad-hoc-provisioning-profile/) und [App an registrierte Geräte verteilen](https://developer.apple.com/documentation/xcode/distributing-your-app-to-registered-devices).

Eine IPA in einem GitHub Release ist nicht automatisch per Antippen installierbar. Für wenige Freunde ist Apple Configurator auf einem Mac der geradlinigste Installationsweg; das Gerät verlangt für eine lokal installierte IPA den Entwicklermodus. Eine drahtlose OTA-Verteilung verlangt zusätzliche HTTPS-Infrastruktur und ein Installationsmanifest und lohnt sich hier gegenüber TestFlight nicht.

## Kostenlose Personal-Team-Notlösung

Ohne bezahltes Programm kann jeder Freund mit eigenem Mac Folgendes tun:

1. Repository klonen und XcodeGen ausführen.
2. Das Projekt in Xcode öffnen.
3. Den eigenen kostenlosen Apple Account als Personal Team auswählen.
4. Falls nötig eine eigene, eindeutige Bundle-ID setzen.
5. Das eigene iPhone oder iPad anschließen, Entwicklermodus aktivieren und „Run“ ausführen.

Apple begrenzt ein Personal Team auf 10 App-IDs, 3 Geräte und 3 Apps pro Gerät. Provisioning Profiles, App-IDs und Geräte laufen nach 7 Tagen ab; danach muss neu gebaut und installiert werden. Diese Variante eignet sich für einen einzelnen Technik-affinen Freund, aber nicht für eine bequem nutzbare Beta.

## Spätere GitHub-Automatisierung

Erst nachdem ein manueller TestFlight-Upload erfolgreich war, sollte ein eigener signierter CI-Workflow ergänzt werden. Der bestehende signierungsfreie Apple-Workflow sollte als normaler Buildcheck erhalten bleiben.

Für die automatisierte App-Store-Connect-Anmeldung eignen sich eine App-Store-Connect-API-Key-ID, Issuer-ID und der private `.p8`-Schlüssel. Abhängig vom gewählten Signing-Verfahren braucht der Runner zusätzlich entweder Zugriff auf cloudverwaltetes Signing oder:

- ein Apple-Distribution-Zertifikat mit privatem Schlüssel als passwortgeschützte `.p12`-Datei;
- das `.p12`-Passwort;
- ein App-Store-Connect-Provisioning-Profile;
- die Apple Team ID.

Diese Werte gehören ausschließlich in geschützte GitHub-Secrets beziehungsweise geschützte Environment-Secrets. Niemals ein Apple-Account-Passwort, einen Zwei-Faktor-Code, `.p8`, `.p12`, Provisioning Profile oder Backend-Token committen. Der API-Schlüssel sollte nur die erforderlichen Rollen besitzen und bei Verlust sofort widerrufen werden.

## Entscheidung

1. **Jetzt kostenlos:** Eigenes iPhone/iPad einmal über Xcode und Personal Team prüfen.
2. **Danach für Freunde:** Apple Developer Program buchen, den ersten Build manuell hochladen und per TestFlight-E-Mail an eine kleine externe Gruppe verteilen.
3. **Parallel vor der Einladung:** Einen abgesicherten HTTPS-Staging-Server mit synthetischen Daten bereitstellen.
4. **Nur als Fallback:** Ad-hoc für wenige bekannte UDIDs.
5. **Nicht verfolgen:** EU-Webverteilung, eigener Marketplace oder Enterprise-Verteilung.
