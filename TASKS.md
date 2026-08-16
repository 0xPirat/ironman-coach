# Offene Aufgaben

## Priorität 1: Technik für Schwimmen, Laufen und Radfahren lehren

**Status:** Geplant – Konzept und Umsetzung noch offen

Die App soll den Nutzern die richtige Technik in allen drei Triathlon-Disziplinen vermitteln. Sie soll nicht nur Trainings vorgeben, sondern verständlich erklären, wie Bewegungen korrekt, effizient und möglichst verletzungsarm ausgeführt werden.

### Disziplinen

- [ ] **Schwimmen:** Wasserlage, Atmung, Armzug, Beinschlag, Körperrotation und Koordination vermitteln.
- [ ] **Laufen:** Körperhaltung, Fußaufsatz, Schrittfrequenz, Armführung und einen effizienten Laufstil vermitteln.
- [ ] **Radfahren:** Sitzposition, Tritttechnik, Schalten, Bremsen, Kurvenfahren und sicheres Fahren vermitteln.

### Noch zu klärende Unteraufgaben

- [ ] Festlegen, wie die Technik in der App gelehrt werden soll, zum Beispiel mit Texten, Bildern, Videos, Animationen oder interaktiven Übungen.
- [ ] Techniklektionen nach Erfahrungsniveau strukturieren.
- [ ] Passende Technikübungen und Drills in Trainingspläne integrieren.
- [ ] Häufige Technikfehler erklären und konkrete Korrekturhinweise geben.
- [ ] Prüfen, welche Rückmeldungen sich aus Garmin- und anderen Sensordaten ableiten lassen.
- [ ] Prüfen, ob später Videoaufnahmen oder Bewegungsanalysen für individuelles Feedback genutzt werden können.
- [ ] Inhalte fachlich prüfen lassen und klare Sicherheitshinweise vorsehen.

### Ziel

Nutzer sollen die richtige Technik verstehen, gezielt üben und schrittweise verbessern können. Die genaue Gestaltung dieses Bereichs wird später ausgearbeitet.

## Karten- und Routenfeature

**Status:** Geplant – noch nicht begonnen

Die App soll Routen für Trainings übersichtlich auf einer Karte darstellen und – sofern Garmin und das jeweilige Gerät dies unterstützen – an die Garmin-Uhr beziehungsweise über Garmin Connect übertragen können.

### Unteraufgaben

- [ ] Prüfen, welche Garmin-Geräte und Garmin-Schnittstellen das Übertragen von Routen unterstützen.
- [ ] Prüfen, welche Routenformate benötigt werden, zum Beispiel GPX, FIT oder TCX.
- [ ] Eine eigene Routen- beziehungsweise Kartenansicht in der App entwerfen.
- [ ] Fahrrad- und Laufrouten auf der Karte anzeigen.
- [ ] Prüfen, ob sich sinnvolle Schwimmrouten für Seen beziehungsweise Open-Water-Training abbilden lassen.
- [ ] Routendetails darstellen, zum Beispiel Verlauf, Distanz, Höhenprofil und Start-/Zielpunkt.
- [ ] Eine Route aus der App an Garmin beziehungsweise Garmin Connect übertragen.
- [ ] Verständlich anzeigen, wenn ein Garmin-Gerät oder eine Aktivitätsart die Funktion nicht unterstützt.
- [ ] Optional einen Link zum Öffnen der Route in Google Maps oder einem anderen Kartendienst anbieten.
- [ ] Datenschutz, Kartenanbieter, Nutzungskosten und notwendige API-Schlüssel prüfen.

### Ziel

Nutzer sollen eine geplante Trainingsroute zuerst direkt in der App ansehen und sie anschließend mit möglichst wenigen Schritten auf ein kompatibles Garmin-Gerät übertragen können.

## Verbindung zu Fahrradcomputern

**Status:** Geplant – noch nicht begonnen

Die App soll Trainings und Routen auch mit gängigen Fahrradcomputern austauschen können. Im Mittelpunkt stehen zunächst Garmin und Wahoo.

### Unteraufgaben

- [ ] Den aktuellen Umfang der bereits eingebauten Garmin-Anbindung dokumentieren.
- [ ] Prüfen, ob die bestehende Garmin-Anbindung auch Fahrradcomputer, Routen und strukturierte Radtrainings vollständig abdeckt.
- [ ] Verfügbare Wahoo-APIs, Partnerprogramme, Authentifizierung und technische Einschränkungen recherchieren.
- [ ] Prüfen, ob Routen und strukturierte Trainings direkt oder über einen Zwischendienst an Wahoo-Geräte übertragen werden können.
- [ ] Ein gemeinsames Schnittstellenkonzept für Garmin und Wahoo entwerfen, damit weitere Hersteller später ergänzt werden können.
- [ ] Verbindungsstatus, Synchronisationsfehler und nicht unterstützte Geräte verständlich in der App anzeigen.
- [ ] Automatisierte Tests für die Wahoo-Anbindung ohne physisches Gerät vorsehen, zum Beispiel mit Testdaten oder simulierten API-Antworten.
- [ ] Einen späteren Praxistest mit einem echten Wahoo-Fahrradcomputer einplanen.

### Hinweis zur Prüfung

Für Garmin besteht bereits eine grundsätzliche Anbindung. Ob sie alle benötigten Funktionen für Fahrradcomputer abdeckt, muss noch geprüft werden. Ein Wahoo-Gerät steht derzeit nicht zur Verfügung; deshalb kann die Entwicklung zunächst nur gegen Dokumentation, Testdaten und gegebenenfalls eine Sandbox erfolgen. Vor einer Freigabe ist ein Test mit echter Hardware erforderlich.
