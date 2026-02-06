# Technische Dokumentation der empirischen Umsetzung

Diese technische Dokumentation ergänzt die Bachelorarbeit **„Zigbee versus Z-Wave: Latenz, Interoperabilität und Integrationsfähigkeit in Smart Home Systemen mit openHAB“**.

Ziel dieses Dokuments ist es, den im Rahmen der Arbeit umgesetzten Versuchsaufbau sowie die technische Integration der eingesetzten Systemkomponenten nachvollziehbar zu dokumentieren. Die dargestellten
Konfigurations- und Implementierungsschritte dienen der Reproduzierbarkeit des Feldexperiments und der Fallstudie.

Die statistische Auswertung, Interpretation und Diskussion der Messergebnisse  erfolgen ausschließlich in der Bachelorarbeit und sind nicht Bestandteil dieser technischen Dokumentation.

---

## 1. Systemübersicht

Der Versuchsaufbau basiert auf einer lokal betriebenen Smart Home Umgebung, in der openHAB als zentrale Steuer-, Integrations- und Automatisierungsplattform eingesetzt wurde. Die Funkprotokolle Zigbee und Z-Wave wurden nicht direkt über native openHAB-Bindings integriert, sondern über externe Protokolladapter an die Plattform angebunden.

Die Kommunikation zwischen den Protokolladaptern und openHAB erfolgte ausschließlich über MQTT, wodurch eine klare Trennung zwischen protokollspezifischer Verarbeitung und plattforminterner Automatisierungslogik realisiert wurde.

---

## 2. Hardwarebasis

Der im Rahmen der Arbeit eingesetzte Versuchsaufbau basiert auf folgender
Hardwarekonfiguration:

- **Raspberry Pi 4 (Model B, 8 GB RAM)**
- Betriebssystem: Debian GNU/Linux 12 (bookworm, 64-bit)
- Netzwerk: drahtlose WLAN-Anbindung (privates Netzwerk)
- USB-Geräte:
  - Aeotec Z-Stick 7 (Z-Wave)
  - Sonoff Zigbee 3.0 USB-Dongle  
    (angeschlossen über USB-Hub: D-Link DUB-H4)

Als Endgeräte wurden jeweils ein Taster (Button) und ein Aktor (Plug) für die Funkprotokolle Zigbee und Z-Wave eingesetzt. Die Taster dienten als Eingabegeräte zur Auslösung von Schaltvorgängen, während die Aktoren als schaltbare Aktoren für die Messungen und Integrationsszenarien verwendet wurden.

Der Raspberry Pi diente als zentrale Laufzeitumgebung für openHAB, Zigbee2MQTT, Z-Wave JS UI, den MQTT-Broker sowie das Python-Skript zur Datenerfassung und Klassifikation.

---

## 3. Betriebssystem und Basisinstallation

Als Grundlage des Versuchsaufbaus wurde auf dem Raspberry Pi ein Linux-Betriebssystem installiert, das als Laufzeitumgebung für alle weiteren Systemkomponenten diente. Das Betriebssystem bildet die Basis für den Betrieb von openHAB, der eingesetzten Protokolladapter, des MQTT-Brokers, der Influx Datenbank sowie des Python-Skripts zur Datenerfassung.

### 3.1 Betriebssystem

Im vorliegenden Versuchsaufbau kam **Debian GNU/Linux 12 (bookworm)** in der  64-Bit-Variante zum Einsatz. Nach der Installation des Betriebssystems wurden die grundlegenden Systemfunktionen konfiguriert, insbesondere:

- Einrichtung eines regulären Benutzerkontos
- Aktivierung der Netzwerkverbindung im lokalen WLAN
- Aktualisierung der Paketquellen und installierten Systempakete

Das Betriebssystem wurde anschließend unverändert als stabile Laufzeitumgebung verwendet. Weitere systemnahe Anpassungen erfolgten ausschließlich im Zusammenhang mit der Installation der im Folgenden beschriebenen Dienste und Anwendungen.

### 3.2 Installation der Java-Laufzeitumgebung

openHAB basiert auf Java und benötigt daher eine installierte Java-Laufzeitumgebung. Aus diesem Grund wurde vor der Installation von openHAB eine geeignete Java-Version auf dem System eingerichtet. Im Versuchsaufbau wurde OpenJDK in der vom Betriebssystem bereitgestellten Version 17 verwendet. Die Installation erfolgte über die Paketverwaltung von Debian:

```bash
sudo apt install openjdk-17-jdk
```

### 3.3 Installation und Grundkonfiguration von openHAB

openHAB wurde als zentrale IoT-Plattform für die Steuerung, Integration und Automatisierung der eingesetzten Systemkomponenten verwendet. Die Installation erfolgte über das offizielle openHAB-Paketrepository.

Zunächst wurde das Repository eingebunden und der zugehörige Signaturschlüssel importiert:

```bash
wget -qO - 'https://openhab.jfrog.io/artifactory/api/gpg/key/public' | sudo apt-key add -
echo 'deb https://openhab.jfrog.io/artifactory/openhab-linuxpkg stable main' | sudo tee /etc/apt/sources.list.d/openhab.list
```

Anschließend wurde openHAB über die Paketverwaltung installiert:

```bash
sudo apt update
sudo apt install openhab
```

Nach der Installation wurde der openHAB-Dienst aktiviert und gestartet:

```bash
sudo systemctl enable openhab
sudo systemctl start openhab
```

openHAB wurde im Versuchsaufbau als systemd-Dienst betrieben und startete automatisch beim Systemstart. Die Web-Oberfläche von openHAB war nach Abschluss der Installation über den Standardport erreichbar:

```text
http://10.0.0.42:8080
```

### 3.4 Installation und Grundkonfiguration der InfluxDB

Zur persistente Speicherung von Zustands- und Ereignisdaten innerhalb von openHAB wurde im Versuchsaufbau eine lokale Instanz der InfluxDB eingesetzt. Die Datenbank diente als Zeitreihenspeicher für ausgewählte Item- und Statusänderungen, die im Rahmen der Integrations- und Schaltszenarien erzeugt wurden.

Die InfluxDB wurde auf dem Raspberry Pi installiert und direkt mit openHAB gekoppelt. openHAB übernahm dabei die Aufgabe, relevante Zustandsänderungen – insbesondere die Item-Updates der Buttons sowie die State-Updates der Aktoren – in der InfluxDB zu persistieren.

Die Installation der InfluxDB erfolgte über das offizielle Paketrepository. Zunächst wurde das Repository eingebunden:

```bash
wget -qO- https://repos.influxdata.com/influxdata-archive.key | sudo gpg --dearmor -o /usr/share/keyrings/influxdata-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/influxdata-archive-keyring.gpg] https://repos.influxdata.com/debian bookworm stable" | sudo tee /etc/apt/sources.list.d/influxdb.list
```

Anschließend wurde die InfluxDB installiert:

```bash
sudo apt update
sudo apt install influxdb
```

Nach der Installation wurde der Datenbankdienst aktiviert und gestartet:

```bash
sudo systemctl enable influxdb
sudo systemctl start influxdb
```

Die InfluxDB lief im Versuchsaufbau als lokaler Dienst und war ausschließlich für interne Zugriffe vorgesehen. Die konkrete Konfiguration der Anbindung an openHAB sowie die Auswahl der zu speichernden Items werden in den nachfolgenden Kapiteln im Kontext der openHAB-Integration beschrieben.

Ein separates Python-Skript wurde zur Auswertung der gespeicherten Zeitreihendaten eingesetzt. Dieses Skript las die relevanten Messdaten aus der InfluxDB aus, führte eine zeitliche Zuordnung und Klassifikation der Ereignisse durch und exportierte die aufbereiteten Daten als CSV-Dateien in ein gemeinsames Verzeichnis zur weiteren Analyse. Das Python-Skript schrieb dabei keine Daten in die InfluxDB zurück.

---

## 4. Kommunikationsstruktur (MQTT)

Zur Kopplung der eingesetzten Systemkomponenten wurde ein MQTT-Broker auf Basis von **Eclipse Mosquitto** eingerichtet. Der Broker fungierte als zentrale Kommunikationsschnittstelle zwischen den Protokolladaptern (Zigbee2MQTT, Z-Wave JS UI) und der offenen IoT-Plattform openHAB.

Sämtliche Statusmeldungen, Ereignisse und Steuerbefehle wurden über den MQTT-Broker transportiert, wodurch eine klare Trennung zwischen protokollspezifischer Verarbeitung und der ereignis- bzw. regelbasierten Logik innerhalb von openHAB erreicht wurde.

Die Installation des MQTT-Brokers erfolgte über die Paketverwaltung des Betriebssystems. Als Broker kam **Eclipse Mosquitto** zum Einsatz, der als Systemdienst eingerichtet wurde. Der Dienst wurde so konfiguriert, dass er automatisch beim Systemstart gestartet wird und dauerhaft im Hintergrund läuft.

```bash
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

---

## 5. Integration der Zigbee-Komponenten

Zur Integration der Zigbee-Komponenten wurde **Zigbee2MQTT** als externer Protokolladapter eingesetzt. Die Anwendung fungierte als Protokolladapter zwischen dem Zigbee-Funkkoordinator und dem MQTT-Broker und stellte die von den Zigbee-Geräten erzeugten Zustands- und Ereignisdaten zur Weiterverarbeitung in openHAB bereit.

Zigbee2MQTT wurde auf dem Raspberry Pi installiert und nutzte den angeschlossenen **Sonoff Zigbee 3.0 USB-Dongle** als Zigbee-Koordinator.

### 5.1 Installation der Laufzeitumgebung (Node.js)

Zigbee2MQTT basiert auf Node.js und benötigt eine aktuelle LTS-Version. Da die Standardpakete des Betriebssystems häufig veraltete Versionen enthalten, wurde Node.js über das offizielle NodeSource-Repository installiert.

Zunächst wurde das Setup-Skript eingebunden, das das zusätzliche Paketrepository konfiguriert:

```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
```

Anschließend wurde Node.js über die Paketverwaltung installiert:

```bash
sudo apt install -y nodejs
```

### 5.2 Installation von Zigbee2MQTT
Zigbee2MQTT wurde in einem dedizierten Verzeichnis unter /opt installiert und unter dem Systembenutzer openhab betrieben, um eine konsistente Ausführungsumgebung mit openHAB sicherzustellen.

```bash
sudo mkdir /opt/zigbee2mqtt
sudo chown openhab:openhab /opt/zigbee2mqtt
```

Das Projekt wurde anschließend aus dem offiziellen GitHub-Repository geklont und die Abhängigkeiten installiert:

```bash
cd /opt
sudo -u openhab git clone https://github.com/Koenkk/zigbee2mqtt.git
cd /opt/zigbee2mqtt
sudo -u openhab npm ci
```

### 5.3 Konfiguration von Zigbee2MQTT

Die zentrale Konfiguration von Zigbee2MQTT erfolgte über die Datei:

```text
/opt/zigbee2mqtt/data/configuration.yaml
```

In dieser Datei wurden die für den stabilen Betrieb erforderlichen Parameter festgelegt, insbesondere die Anbindung an den MQTT-Broker, die Definition des Zigbee-Koordinators sowie grundlegende Laufzeitoptionen.

Die Anbindung an den MQTT-Broker erfolgte über folgenden Konfigurationsblock:

```yaml
mqtt:
  base_topic: zigbee2mqtt
  server: mqtt://10.0.0.42
```

Alle von Zigbee2MQTT erzeugten Status- und Ereignismeldungen wurden damit unter einem einheitlichen Topic-Präfix (zigbee2mqtt) veröffentlicht und über den lokal betriebenen MQTT-Broker an openHAB weitergeleitet.

Die explizite Festlegung des seriellen Ports des Zigbee-Koordinators stellte eine eindeutige und stabile Zuordnung des USB-Dongles sicher:

```yaml
serial:
  port: /dev/serial/by-id/usb-ITead_Sonoff_Zigbee_3.0_USB_Dongle_Plus_b47b2580286bef119f66a4adc169b110-if00-port0
  adapter: zstack
```

Die Verwendung des persistenten Gerätepfads (/dev/serial/by-id/...) verhindert Probleme durch wechselnde Gerätezuordnungen beim Systemstart.

Für Verwaltungs- und Diagnosezwecke wurde die integrierte Web-Oberfläche
aktiviert:

```yaml
frontend:
  enabled: true
  port: 8081
```

### 5.4 Pairing der Zigbee-Endgeräte

Das Pairing der Zigbee-Endgeräte erfolgte über die Web-Oberfläche von Zigbee2MQTT. Hierzu wurde der Pairing-Modus aktiviert und die jeweiligen Endgeräte gemäß den Herstellerangaben in den Kopplungsmodus versetzt. Nach erfolgreichem Pairing standen die Geräte als eigenständige MQTT-Topics zur Verfügung und konnten für die weitere Integration in openHAB verwendet werden.

Nach dem erfolgreichen Abschluss des Pairing-Prozesses erfolgten zusätzliche Konfigurationsschritte zur Stabilisierung und eindeutigen Identifikation der Geräte.

Die Geräte wurden explizit benannt, um eine konsistente Weiterverarbeitung in openHAB sicherzustellen. Zusätzlich wurde für jedes Gerät die Verfügbarkeitsübermittlung aktiviert:

```yaml
availability:
  active: true
  timeout: 300
```

Durch diese Konfiguration publizierte Zigbee2MQTT den Online- und Offline-Status der Geräte regelmäßig über MQTT. Diese Information war Voraussetzung für eine korrekte Geräteerkennung sowie eine konsistente Statusverarbeitung innerhalb von openHAB.

### 5.5 Betrieb als Systemdienst

Um einen stabilen und dauerhaften Betrieb sicherzustellen, wurde Zigbee2MQTT als systemd-Dienst eingerichtet. Hierzu wurde eine eigene Service-Unit definiert, die die Anwendung unter dem Systembenutzer `openhab` aus dem Installationsverzeichnis `/opt/zigbee2mqtt` startet. Die Service-Datei wurde im systemd-Verzeichnis angelegt:

```bash
sudo nano /etc/systemd/system/zigbee2mqtt.service
```

Nach dem Anlegen der Service-Unit wurde systemd neu geladen und der Dienst aktiviert:

```bash
sudo systemctl daemon-reload
sudo systemctl enable zigbee2mqtt
sudo systemctl start zigbee2mqtt
```

Durch die Aktivierung mittels enable wird Zigbee2MQTT automatisch beim Systemstart gestartet.

Die Web-Oberfläche von Zigbee2MQTT war im Versuchsaufbau unter folgendem
Endpunkt erreichbar:

```text
http://10.0.0.42:8081
```

Diese Oberfläche wurde zur Überwachung des Zigbee-Netzwerks, zum Pairing der Endgeräte sowie zur Kontrolle der erzeugten MQTT-Nachrichten verwendet. Zigbee2MQTT bildete damit die Grundlage für die nachgelagerte Integration der Zigbee-Geräte in openHAB.

---

## 6. Integration der Z-Wave-Komponenten

Zur Integration der Z-Wave-Komponenten wurde **Z-Wave JS UI** als externer Protokolladapter eingesetzt. Die Anwendung fungierte als Vermittlungsschicht zwischen dem Z-Wave-Funkcontroller und der MQTT-Kommunikationsebene und stellte die von den Z-Wave-Geräten erzeugten Zustands- und Ereignisdaten über einen MQTT-Broker für die Weiterverarbeitung in openHAB bereit.

Z-Wave JS UI wurde auf dem Raspberry Pi installiert und nutzte den angeschlossenen **Aeotec Z-Stick 7** als Z-Wave-Funkcontroller.

### 6.1 Installation von Z-Wave JS UI

Z-Wave JS UI wurde als eigenständiger Dienst auf dem Raspberry Pi betrieben. Die Anwendung kapselt die vollständige Kommunikation mit dem Z-Wave-Netzwerk und stellt eine browserbasierte Verwaltungsoberfläche zur Konfiguration und Überwachung bereit.

Die Installation erfolgte in einem dedizierten Verzeichnis unter `/opt`:

```bash
sudo mkdir /opt/zwavejsui
sudo chown openhab:openhab /opt/zwavejsui
```

Anschließend wurde das Projekt aus dem offiziellen GitHub-Repository geklont:

```bash
cd /opt
sudo -u openhab git clone https://github.com/zwave-js/zwave-js-ui.git
```

### 6.2 Konfiguration der MQTT-Anbindung

Die Konfiguration von Z-Wave JS UI erfolgte nicht über eine manuell gepflegte zentrale Konfigurationsdatei, sondern vollständig über die browserbasierte Web-Oberfläche der Anwendung. Sämtliche Einstellungen wurden automatisch persistiert.

Über die Web-Oberfläche wurde Z-Wave JS UI so konfiguriert, dass alle Zustands- und Ereignisdaten der Z-Wave-Geräte über den lokal betriebenen MQTT-Broker publiziert werden. Steuerbefehle wurden entsprechend über MQTT entgegengenommen.

Alle von Z-Wave JS UI erzeugten MQTT-Nachrichten wurden unter einem einheitlichen Topic-Präfix (`zwave2mqtt`) veröffentlicht. Dieses Basis-Topic wurde in der MQTT-Konfiguration der Web-Oberfläche überprüft und stellte sicher, dass sämtliche Z-Wave-spezifischen Nachrichten eindeutig identifizierbar und konsistent über den MQTT-Broker bereitgestellt wurden. Dadurch war eine protokollunabhängige Weiterverarbeitung der Z-Wave-Geräte in openHAB über das MQTT-Binding möglich.

Die vorgenommenen Einstellungen, einschließlich der Auswahl des Z-Wave-Controllers, der MQTT-Anbindung sowie der Netzwerkkonfiguration, wurden automatisch im Installationsverzeichnis unter `/opt/zwavejsui` gespeichert.

### 6.3 Pairing der Z-Wave-Endgeräte

Das Pairing der Z-Wave-Endgeräte erfolgte ausschließlich über die Web-Oberfläche von Z-Wave JS UI. Hierzu wurde der Inklusionsmodus aktiviert und die jeweiligen Endgeräte gemäß den Herstellerangaben in den Kopplungsmodus versetzt.

Nach erfolgreichem Pairing wurden die Geräte in das bestehende Z-Wave-Netzwerk aufgenommen und standen unmittelbar für die weitere Verarbeitung zur Verfügung. Die von den Geräten erzeugten Zustandsänderungen und Ereignisse wurden in Echtzeit über MQTT publiziert.

Z-Wave-Geräte werden innerhalb des Netzwerks eindeutig über sogenannte Node-IDs identifiziert. Diese Struktur spiegelte sich direkt in den von Z-Wave JS UI erzeugten MQTT-Topics wider und bildete die Grundlage für die nachgelagerte Integration der Geräte in openHAB.

### 6.4 Betrieb als Systemdienst

Z-Wave JS UI wurde als dauerhaft laufender Dienst betrieben und gemeinsam mit openHAB sowie dem MQTT-Broker beim Systemstart automatisch gestartet. Dadurch war sichergestellt, dass das Z-Wave-Netzwerk unmittelbar nach dem Systemstart vollständig verfügbar war.

Die Anwendung wurde manuell als systemd-Dienst eingerichtet, sodass sie unabhängig von interaktiven Benutzeranmeldungen im Hintergrund ausgeführt wird. Hierzu wurde eine eigene Service-Unit definiert, die Z-Wave JS UI aus dem Installationsverzeichnis `/opt/zwavejsui` unter dem Systembenutzer `openhab` startet.

Die Service-Datei wurde im systemd-Verzeichnis angelegt:

```bash
sudo nano /etc/systemd/system/zwavejsui.service
```

Nach dem Anlegen der Service-Unit wurde systemd neu geladen und der Dienst aktiviert:

```bash
sudo systemctl daemon-reload
sudo systemctl enable zwavejsui
sudo systemctl start zwavejsui
```
Durch die Aktivierung mittels enable wird Z-Wave JS UI automatisch beim Systemstart gestartet und dauerhaft im Hintergrund betrieben.

Die Web-Oberfläche von Z-Wave JS UI war im Versuchsaufbau unter folgendem Endpunkt erreichbar:

```text
http://10.0.0.42:8091
```

Diese Oberfläche wurde zur Verwaltung des Z-Wave-Netzwerks, zum Pairing der Endgeräte sowie zur Überwachung der erzeugten MQTT-Nachrichten verwendet. Z-Wave JS UI bildete damit die Grundlage für die nachgelagerte Integration der Z-Wave-Geräte in openHAB.


## 7. Integration in openHAB

Nach der Einrichtung der Protokolladapter für Zigbee und Z-Wave sowie der Konfiguration der MQTT-Kommunikationsstruktur erfolgte die Integration der Systemkomponenten in die offene IoT-Plattform openHAB.

Die Integration der Zigbee- und Z-Wave-Geräte erfolgte ausschließlich über MQTT. Zigbee2MQTT und Z-Wave JS UI stellten die von den Funkgeräten erzeugten Zustands- und Ereignisdaten über den MQTT-Broker bereit. openHAB abonnierte diese Daten und stellte im Gegenzug Steuerbefehle über MQTT zur Verfügung.

Durch diese Architektur wurde eine klare Trennung zwischen der protokollspezifischen Verarbeitung und der regel- und ereignisbasierten Logik innerhalb von openHAB realisiert.

### 7.1 MQTT-Bindings

Die Installation des MQTT-Bindings erfolgte über die Web-Oberfläche von openHAB. Hierzu wurde in der openHAB-Main-UI der Add-on-Bereich aufgerufen und das MQTT-Binding installiert. Nach der Installation stand die MQTT-Funktionalität systemweit zur Verfügung.

Für die Kommunikation zwischen openHAB und den externen Protokolladaptern wurde der bereits eingerichtete MQTT-Broker auf Basis von Eclipse Mosquitto verwendet. In openHAB wurde dieser Broker als MQTT-Broker-Thing angelegt.

Die Konfiguration des Broker-Things erfolgte über die openHAB-UI und umfasste insbesondere:

- die Adresse des MQTT-Brokers im lokalen Netzwerk
- den Standardport 1883
- eine eindeutige Client-ID für openHAB

Eine Authentifizierung wurde im Versuchsaufbau nicht verwendet, da der MQTT-Broker ausschließlich im lokalen Netzwerk betrieben wurde. Nach Abschluss der Konfiguration wurde die Verbindung zum MQTT-Broker hergestellt und dauerhaft aufrechterhalten.

Das MQTT-Binding stellt die technische Grundlage für die weitere Integration der Zigbee- und Z-Wave-Geräte in openHAB dar. Sämtliche Zustandsmeldungen, Ereignisse und Steuerbefehle werden über MQTT transportiert.

Die Kommunikationskette im Versuchsaufbau lässt sich wie folgt zusammenfassen:

```markdown
Zigbee / Z-Wave
        ↓
Zigbee2MQTT / Z-Wave JS UI
        ↓
        MQTT
        ↓
      openHAB
```

Auf Basis dieser Broker-Verbindung werden in den folgenden Abschnitten separate MQTT-Things für die Zigbee- und Z-Wave-Geräte definiert und weiterverarbeitet.

### 7.2 MQTT Things

Nach der Einrichtung der MQTT-Broker-Verbindung wurden in openHAB MQTT-Things zur Abbildung der über MQTT bereitgestellten Geräteinformationen definiert. MQTT-Things stellen die Verbindung zwischen dem MQTT-Broker und den nachgelagerten Channels dar und dienen der strukturierten Verarbeitung von MQTT-Nachrichten.

Im Versuchsaufbau wurden die MQTT-Things manuell angelegt und jeweils mit dem zuvor konfigurierten MQTT-Broker verbunden.

Für die Integration der Zigbee-Komponenten wurden die folgenden zwei separaten MQTT-Things definiert:

- Zigbee Smart Button 01 (Repräsentation des eingesetzten Zigbee-Buttons zur Erzeugung von Ereignissen)
- ZigbeePlugE2 (Repräsentation des eingesetzten Zigbee-Aktors zur Ausführung von Schaltbefehlen)

Analog dazu wurden für die Z-Wave-Komponenten die folgenden MQTT-Things definiert:

- Z_Wave_Button (Repräsentation des eingesetzten Z-Wave-Buttons zur Erzeugung von Schaltimpulsen)
- ZWave_Plug (Repräsentation des eingesetzten Z-Wave-Aktors zur Umsetzung von Schaltbefehlen)

Die Verarbeitung der bereitgestellten Zustands- und Ereignisdaten erfolgte nicht auf Thing-Ebene, sondern ausschließlich über die zugehörigen Channels.

Durch die getrennte Definition der MQTT-Things für Zigbee- und Z-Wave-Geräte wurde eine klare und nachvollziehbare Struktur innerhalb von openHAB geschaffen. Diese Struktur bildete die Grundlage für die nachfolgende Definition der Channels sowie der darauf aufbauenden Items und Rules.

### 7.3 Channels

Nach der Definition der MQTT-Things wurden in openHAB die zugehörigen Channels angelegt. Die Channels stellen die konkrete Verbindung zwischen einem MQTT-Thing und MQTT-Nachrichten dar und definieren, wie eingehende Werte innerhalb von openHAB verarbeitet werden bzw. wie Steuerbefehle über MQTT gesendet werden. Im Versuchsaufbau wurden die Channels manuell konfiguriert, wobei je nach Gerätetyp unterschiedliche Channel-Typen verwendet wurden.

Für die Taster wurden die Channels als reine State-Verarbeitung konfiguriert, da die Geräte ausschließlich eingehende Ereignisse liefern und keine Steuerbefehle über MQTT entgegennehmen. Der Zigbee-Taster wurde über einen Channel vom Typ String abgebildet, da die von Zigbee2MQTT bereitgestellten Aktionswerte als Textwerte geliefert wurden. Der Z-Wave-Taster wurde über einen Channel vom Typ Number/Point abgebildet, da die von Z-Wave JS UI bereitgestellten Ereignisse als numerische Werte vorlagen.

Für die Aktoren wurden Channels vom Typ On/Off Switch definiert. Dadurch konnten die Aktoren innerhalb von openHAB als schaltbare Geräte abgebildet und über Steuerbefehle angesteuert werden. Für die Aktoren wurden jeweils sowohl ein State Topic zur Verarbeitung des aktuellen Schaltzustands als auch ein Command Topic zur Übermittlung von Schaltbefehlen konfiguriert.

Die für die Channel-Konfiguration erforderlichen Topics wurden den MQTT-Nachrichten der jeweiligen Protokolladapter entnommen. Die Zigbee-Topics wurden aus der von Zigbee2MQTT bereitgestellten MQTT-Struktur abgeleitet, während die Z-Wave-Topics aus der von Z-Wave JS UI publizierten Topic-Struktur übernommen wurden.

Da die MQTT-Payloads der Buttons als strukturierte JSON-Nachrichten vorlagen, wurde auf Channel-Ebene eine Incoming Value Transformation konfiguriert (JSONPATH:$.action). Zusätzlich wurden bei den Channels der Aktoren benutzerdefinierte Werte für ON und OFF gesetzt, um eine konsistente Zuordnung zwischen MQTT-Payload und openHAB-Schaltzuständen sicherzustellen.

Zur Verifikation der von den Tastern und Aktoren publizierten MQTT-Nachrichten wurden die entsprechenden Topics direkt am MQTT-Broker mitgelesen. Hierzu wurden die mit Eclipse Mosquitto mitgelieferten Kommandozeilenwerkzeuge verwendet.

```bash
mosquitto_sub -h localhost -t zigbee2mqtt/# -v
mosquitto_sub -h localhost -t zwave2mqtt/# -v
```

Über diese Befehle konnten die von Zigbee2MQTT bzw. Z-Wave JS UI veröffentlichten Topics und Payloads eingesehen und für die Konfiguration der Channels in openHAB herangezogen werden.

Durch diese Channel-Konfiguration standen die Ereignisse der Taster sowie die Zustände und Steuerungsmöglichkeiten der Aktoren in openHAB in einer einheitlichen Form zur Verfügung und konnten im nächsten Schritt über Items weiter abstrahiert werden.

### 7.4 Items

Nach der Definition der Channels wurden in openHAB die zugehörigen Items angelegt. Die Items wurden manuell definiert, jeweils eindeutig einem Channel zugeordnet und entsprechend der Art der über den Channel bereitgestellten Werte typisiert.

Für den Z-Wave-Taster wurde ein Item mit dem Label Z_Wave_Button vom Typ Number angelegt, das die vom Taster gelieferten numerischen Ereigniswerte abbildete. Der Z-Wave-Aktor wurde über ein Item mit dem Label Z-Wave_Plug_On-Off vom Typ Switch abgebildet, über das der Schaltzustand des Aktors verarbeitet und gesteuert wurde.

Für den Zigbee-Taster wurde ein Item mit dem Label Zigbee_Button_Action vom Typ String definiert, das die von Zigbee2MQTT gelieferten Aktionswerte repräsentierte. Der Zigbee-Aktor wurde über ein Item mit dem Label ZigbeePlug_Switch vom Typ Switch abgebildet.

Durch diese einheitliche Typisierung und semantische Zuordnung standen die Ereignisse der Taster sowie die Schaltzustände der Aktoren in strukturierter Form innerhalb von openHAB zur Verfügung und bildeten die Grundlage für die nachfolgende Persistierung und Automatisierungslogik.

### 7.5 Speicherung der Item-Zustände

Zur Speicherung ausgewählter Zustands- und Ereignisdaten wurde openHAB im Versuchsaufbau mit der InfluxDB gekoppelt. Die Speicherung diente dazu, Änderungen der definierten Items für eine nachgelagerte Auswertung bereitzustellen. Hierzu wurde in openHAB das InfluxDB Persistence Binding über die Web-Oberfläche installiert und grundlegend konfiguriert. Die Anbindung erfolgte an die lokal betriebene InfluxDB-Instanz.

Die eigentliche Aktivierung der Speicherung erfolgte nicht über die Web-Oberfläche, sondern über eine dateibasierte Persistenzdefinition. Hierzu wurde im openHAB-Konfigurationsverzeichnis die Persistenzdatei influxdb.persist unter /etc/openhab/persistence angelegt.

In dieser Datei wurden sowohl Persistenzstrategien als auch die zu speichernden Items definiert. Für den Versuchsaufbau wurde eine ereignisbasierte Speicherung konfiguriert, bei der Item-Updates bei jeder Zustandsänderung in der InfluxDB gespeichert werden. Zusätzlich wurde für die relevanten Items eine Wiederherstellung des letzten bekannten Zustands beim Systemstart aktiviert.

```text
Strategies {
    everyMinute : "0 * * * * ?"
    everyHour   : "0 0 * * * ?"
    default     = everyChange
}

Items {
    Zigbee_Smart_Button_01_Button_Action : strategy = everyChange, restoreOnStartup
    ZigbeePlugE2_Switch                  : strategy = everyChange, restoreOnStartup
    Z_Wave_Button                        : strategy = everyChange, restoreOnStartup
    ZWave_Plug_OnOff                     : strategy = everyChange, restoreOnStartup
}
```

Durch diese Konfiguration wurden die Ereignisse der Buttons sowie die Zustandsänderungen der Aktoren kontinuierlich als Zeitreihendaten gespeichert. Die InfluxDB diente dabei ausschließlich als Datenspeicher. Eine direkte Auswertung oder Weiterverarbeitung der Daten erfolgte nicht innerhalb von openHAB.

### 7.6 Rules

Nach der Definition der Items wurden in openHAB vier Rules umgesetzt, um die Schaltlogik für die Intra-Binding- und Cross-Binding-Szenarien technisch abzubilden. Zwei Rules realisierten Intra-Binding-Szenarien innerhalb desselben Funkprotokolls, zwei weitere Rules dienten der protokollübergreifenden Kopplung (Cross-Binding).

Alle Rules folgten demselben Grundschema. Als Auslöser diente jeweils ein Item-Update eines Button-Items. Bei Eintreten des Triggers wurde ein Inline-Skript ausgeführt, das den aktuellen Button-Wert auswertete und abhängig davon einen Schaltbefehl an den zugehörigen Aktor sendete. Die Umsetzung erfolgte vollständig auf Item-Ebene innerhalb von openHAB.

Für die Intra-Binding-Szenarien wurden je eine Rule für Zigbee und Z-Wave definiert. Ereignisse des Zigbee-Buttons führten dabei zu Schaltbefehlen am Zigbee-Aktor, während Ereignisse des Z-Wave-Buttons den Z-Wave-Aktor steuerten. Die Interpretation der Button-Ereignisse erfolgte abhängig vom jeweiligen Datenformat: Beim Zigbee-Button wurden textuelle Aktionswerte ausgewertet, beim Z-Wave-Button numerische Werte.

Für die Cross-Binding-Szenarien wurden zwei weitere Rules definiert, die nach demselben Schema arbeiteten. In diesen Rules lösten Ereignisse des Zigbee-Buttons Schaltbefehle am Z-Wave-Aktor aus, während Ereignisse des Z-Wave-Buttons den Zigbee-Aktor steuerten. Die Zuordnung der Schaltbefehle erfolgte identisch zu den Intra-Binding-Rules, lediglich das jeweils angesprochene Aktor-Item unterschied sich.

Innerhalb der Rules wurde zusätzlich eine einfache Protokollierung umgesetzt, um ausgelöste Ereignisse und resultierende Schaltbefehle nachvollziehbar zu machen. Nicht relevante oder unbekannte Button-Werte wurden explizit ignoriert und führten zu keiner Aktion.

Die Rules enthielten ausschließlich die technische Logik zur Weiterleitung von Button-Ereignissen an die entsprechenden Aktoren und realisierten damit die Intra- und Cross-Binding-Szenarien im Versuchsaufbau.

## 8. Datenerfassung und -aufbereitung

Die Datenerfassung und -aufbereitung der Messdaten erfolgte über ein externes Python-Skript. Das Skript ist nicht Teil der openHAB-Laufzeitumgebung und übernimmt keine Steuerungs- oder Persistenzaufgaben innerhalb des Smart Home Systems. Es greift ausschließlich lesend auf die in der InfluxDB gespeicherten Zeitreihendaten zu und dient der strukturierten technischen Aufbereitung der Messdaten für die nachgelagerte Auswertung.

Im Rahmen der Datenerfassung werden die von openHAB persistierten Rohdaten ausgelesen und in eine auswertungsfähige Form überführt. Die Datenaufbereitung umfasst dabei insbesondere die zeitliche Zuordnung von Button-Ereignissen und Aktor-Zustandsänderungen, die Berechnung der resultierenden Latenzen sowie die technische Klassifikation der beobachteten Schaltvorgänge. Eine statistische Auswertung oder Interpretation der Ergebnisse erfolgt nicht innerhalb des Python-Skripts, sondern ausschließlich in den entsprechenden Ergebniskapiteln der Bachelorarbeit.

### 8.1 Datenbasis und Datenquelle

Als Datenbasis dienten die in der InfluxDB gespeicherten Zeitreihendaten, die zuvor in openHAB durch die relevanten Items erzeugt wurden. Die InfluxDB fungierte dabei als zentraler Datenspeicher für sämtliche Zustands- und Ereignisdaten der eingesetzten Buttons und Aktoren.

Die vom Python-Skript ausgelesenen Daten basierten auf den Item-Updates der definierten Button- und Aktor-Items. Die Button-Items lieferten die auslösenden Ereignisse, während die Aktor-Items die resultierenden Zustandsänderungen repräsentierten. Beide Datentypen wurden als Zeitreihen mit präzisen Zeitstempeln gespeichert und konnten eindeutig über ihre jeweiligen Measurements identifiziert werden.

Der Zugriff auf die InfluxDB erfolgte ausschließlich lesend über die InfluxDB-API. Das Python-Skript führte keine Schreiboperationen auf der Datenbank aus und veränderte die gespeicherten Messdaten nicht. Durch diese klare Trennung blieb die Verantwortlichkeit zwischen Datenerzeugung (openHAB), Datenspeicherung (InfluxDB) und technischer Datenaufbereitung (Python-Skript) eindeutig abgegrenzt.

### 8.2 Parametrisierung der Messdurchgänge

Die Messdurchgänge wurden im Python-Skript über eine zentrale Parametrisierung gesteuert. Dadurch konnten unterschiedliche Versuchsbedingungen reproduzierbar ausgeführt werden, ohne die Verarbeitungslogik des Skripts zu verändern.

Zu den definierten Parametern zählten der Messmodus (Intra-Binding oder Cross-Binding), die jeweilige Distanzstufe sowie zeitliche Schwellenwerte für die Zuordnung und Klassifikation der Schaltvorgänge. Zusätzlich wurden die für den jeweiligen Messdurchgang relevanten Button- und Aktor-Measurements sowie die erwarteten Trigger-Werte der Taster festgelegt.

Die Variation der Messdurchgänge erfolgte ausschließlich über diese Parameter. Die Verarbeitung der aus der InfluxDB ausgelesenen Daten blieb dabei unverändert, wodurch eine konsistente und vergleichbare Durchführung über alle Versuchsbedingungen hinweg sichergestellt wurde.

### 8.3 Zeitliche Zuordnung von Button- und Aktorereignissen

Die im Python-Skript aus der InfluxDB ausgelesenen Zeitreihendaten wurden technisch weiterverarbeitet, indem auslösende Button-Ereignisse zeitlich den jeweils zugehörigen Zustandsänderungen der Aktoren zugeordnet wurden. Grundlage dieser Zuordnung bildeten die in der Datenbank gespeicherten Zeitstempel der jeweiligen Ereignisse.

Für jedes Button-Ereignis wurde innerhalb eines vordefinierten Beobachtungsfensters nach der ersten passenden Zustandsänderung des zugehörigen Aktors gesucht. Die zeitliche Differenz zwischen dem Button-Ereignis und der korrespondierenden Aktor-Zustandsänderung wurde als Latenz erfasst. Um Mehrfachzuordnungen zu vermeiden, wurden Aktor-Ereignisse nach erfolgter Zuordnung nicht erneut berücksichtigt.

Die konkrete Umsetzung dieser Zuordnungslogik kann dem im Verzeichnis `scripts/` abgelegten Python-Skript entnommen werden.

### 8.4 Klassifikation der Schaltvorgänge

Auf Basis der zeitlichen Zuordnung von Button- und Aktorereignissen wurden die einzelnen Schaltvorgänge im Python-Skript technisch klassifiziert. Ziel der Klassifikation war es, die beobachteten Reaktionen der Aktoren in klar definierte Kategorien einzuordnen und dadurch eine strukturierte Grundlage für die nachgelagerte Auswertung zu schaffen.

Die Klassifikation erfolgte ausschließlich regelbasiert anhand der berechneten Latenzwerte und vordefinierter zeitlicher Schwellen. Für jeden zugeordneten Schaltvorgang wurde geprüft, ob und innerhalb welchen Zeitraums eine Reaktion des Aktors auf das auslösende Button-Ereignis erfolgte. Abhängig vom Ergebnis dieser Prüfung wurde der Schaltvorgang einer der folgenden Klassen zugeordnet:

- SUCCESS: Der Aktor reagierte innerhalb eines definierten Zeitfensters mit einer gültigen Zustandsänderung auf das Button-Ereignis.
- DELAYED: Eine Zustandsänderung des Aktors trat auf, jedoch erst nach Überschreiten des für eine erfolgreiche Reaktion vorgesehenen Zeitfensters.
- TIMEOUT: Innerhalb des maximalen Beobachtungsfensters konnte keine passende Zustandsänderung des Aktors festgestellt werden.
- NO_REACTION: Für das Button-Ereignis konnte keine Reaktion des zugehörigen Aktors ermittelt werden.

Die verwendeten Zeitfenster und Schwellenwerte wurden im Rahmen der Parametrisierung der Messdurchgänge festgelegt und für alle Versuchsbedingungen konsistent angewendet. 

Durch diese technische Klassifikation konnten die Schaltvorgänge eindeutig und reproduzierbar beschrieben werden. Die resultierenden Klassenzuordnungen bildeten insbesondere für die spätere Auswertung der Cross-Binding-Szenarien eine wesentliche Grundlage.

### 8.5 Export der Messergebnisse

Die im Python-Skript technisch aufbereiteten und klassifizierten Messdaten wurden nach Abschluss der Verarbeitung in strukturierter Form exportiert. Der Export erfolgte in Form von CSV-Dateien, um eine einfache und einheitliche Weiterverarbeitung der Daten mit Microsoft Excel zu ermöglichen.

Die CSV-Dateien enthielten pro Schaltvorgang unter anderem die Zeitstempel der auslösenden Button-Ereignisse und der zugeordneten Aktor-Zustandsänderungen, die berechnete Latenz sowie die zugewiesene Klassifikation. Die Dateien wurden in einem gemeinsamen Verzeichnis abgelegt und bildeten die Grundlage für die nachgelagerte statistische Auswertung.

Für jeden Messdurchgang wurde eine eigene CSV-Datei erzeugt. Die Dateibenennung folgte einem konsistenten Schema und enthielt Informationen zum Messmodus (Intra-Binding oder Cross-Binding), zur Distanzstufe sowie einen Zeitstempel zur eindeutigen Identifikation des jeweiligen Messdurchgangs.
