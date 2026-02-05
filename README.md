# Zigbee versus Z-Wave – Technische Artefakte zur empirischen Untersuchung im Rahmen einer Bachelorarbeit

Dieses Repository enthält die technischen Artefakte zur Bachelorarbeit  
**„Zigbee versus Z-Wave: Latenz, Interoperabilität und Integrationsfähigkeit in Smart Home Systemen mit openHAB“**.

Ziel des Repositories ist es, den im Rahmen der Bachelorarbeit durchgeführten empirischen
Versuchsaufbau sowie die Datenerhebung nachvollziehbar zu dokumentieren.
Die hier bereitgestellten Inhalte dienen der Reproduzierbarkeit und Transparenz
des durchgeführten Feldexperiments und der Fallstudie.

## Wissenschaftliche Einordnung

Ziel der Bachelorarbeit ist es, die Kommunikationsprotokolle Zigbee und Z-Wave
hinsichtlich ihrer Eignung für den Einsatz in Smart Home Systemen empirisch zu
untersuchen. Der Fokus liegt dabei insbesondere auf den Aspekten

- **Latenz** (Feldexperiment im Intra-Binding),
- **Interoperabilität** (Cross-Binding-Szenarien),
- **Integrationsfähigkeit** (Konfigurations- und Einrichtungsaufwand)

innerhalb einer offenen Smart-Home-Plattform auf Basis von openHAB.

Die zentrale Forschungsfrage lautet:

*Wie unterscheiden sich Zigbee und Z-Wave hinsichtlich ihrer Eignung für Smart Home Systeme,
insbesondere im Hinblick auf Latenz, Interoperabilität und Integrationsfähigkeit in offene
Plattformen wie openHAB?*

Die methodische Umsetzung erfolgt anhand eines Mixed-Methods-Ansatzes
(Feldexperiment und deskriptive Fallstudie) und wird mithilfe des
Goal-Question-Metric-Ansatzes (GQM) strukturiert.

## Zweck des Repositories

Dieses Repository ergänzt die Bachelorarbeit um folgende technische Artefakte:

- Dokumentation des **technischen Versuchsaufbaus**
- verwendetes **Python-Skript** zur Datenerfassung und Klassifikation
- **unveränderte Rohdaten** der Latenzmessungen
- relevante **Konfigurationsdateien** der eingesetzten Systeme

Die statistische Auswertung, Interpretation und Diskussion der Messergebnisse
erfolgen ausschließlich in der Bachelorarbeit und sind daher **nicht Bestandteil**
dieses Repositories.

## Repository-Struktur

- `docs/`  
  Technische Dokumentation zur Systemintegration (Hardware, Software,
  Kommunikationsstruktur, openHAB-Konfiguration).

- `scripts/`  
  Python-Skript zur automatisierten Auswertung der in InfluxDB erfassten
  Zeitstempel und zur Klassifikation der Schaltvorgänge.

- `data/`  
  CSV-Dateien mit den unveränderten Rohdaten der im Feldexperiment erhobenen
  Latenzmessungen (Intra-Binding).

- `config/`  
  Ausgewählte Konfigurationsdateien (z. B. openHAB, Zigbee2MQTT), die für das
  Verständnis des Versuchsaufbaus relevant sind.

## Python-Skript

Das Python-Skript wurde mit einer Standard-Python-3-Installation ausgeführt und
verwendet die Bibliothek `pandas` zur Verarbeitung der Zeitreihendaten.
Eine lauffähige Entwicklungsumgebung ist für das Verständnis des Skripts nicht
erforderlich.

## Reproduzierbarkeit und Einschränkungen

Das Repository stellt alle wesentlichen technischen Informationen bereit, um den
Versuchsaufbau und die Datenerhebung nachvollziehen zu können.
Abweichungen in konkreten Hardware-, Funk- oder Umgebungsbedingungen können
zu unterschiedlichen Messergebnissen führen.

## Zielgruppe

Das Repository richtet sich primär an Fachleute und Expert:innen aus den Bereichen
IoT und Smart Home Systeme sowie an Studierende der Informations- und
Kommunikationstechnologien, die sich mit der Performance und Integration
heterogener Smart-Home-Protokolle befassen.

## Lizenz

Dieses Repository steht unter der MIT License.
