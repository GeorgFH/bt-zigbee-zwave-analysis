# Zigbee versus Z-Wave – Technische Artefakte zur empirischen Untersuchung im Rahmen einer Bachelorarbeit

Dieses Repository enthält die technischen Artefakte zur Bachelorarbeit **„Zigbee versus Z-Wave: Latenz, Interoperabilität und Integrationsfähigkeit in Smart Home Systemen mit openHAB“**.

Ziel des Repositories ist es, den im Rahmen der Bachelorarbeit durchgeführten empirischen Versuchsaufbau sowie die Datenerhebung nachvollziehbar zu dokumentieren. Die hier bereitgestellten Inhalte dienen der Reproduzierbarkeit und Transparenz des durchgeführten Feldexperiments und der Fallstudie.

## Ziel und Fragestellung

Ziel der Bachelorarbeit ist es, die Kommunikationsprotokolle Zigbee und Z-Wave hinsichtlich ihrer Eignung für den Einsatz in Smart Home Systemen empirisch zu untersuchen. Der Fokus liegt dabei insbesondere auf den Aspekten: 

- **Latenz**,
- **Interoperabilität**,
- und **Integrationsfähigkeit**

innerhalb einer offenen Smart Home Plattform auf Basis von openHAB.

Die zentrale Forschungsfrage lautet:

*Wie unterscheiden sich Zigbee und Z-Wave hinsichtlich ihrer Eignung für Smart Home Systeme,
insbesondere im Hinblick auf Latenz, Interoperabilität und Integrationsfähigkeit in offene
Plattformen wie openHAB?*

Die methodische Umsetzung erfolgt anhand eines Mixed-Methods-Ansatzes (Feldexperiment und deskriptive Fallstudie) und wird mithilfe des Goal-Question-Metric-Ansatzes (GQM) strukturiert.

## Zweck des Repositories

Dieses Repository ergänzt die Bachelorarbeit um folgende technische Artefakte:

- Dokumentation des **technischen Versuchsaufbaus**
- verwendetes **Python-Skript** zur Datenerfassung und Klassifikation
- **Rohdaten** und **technisch aufbereitete CSV-Messdaten** der Latenzmessungen
- relevante **Konfigurationsdateien** der eingesetzten Systeme

Die statistische Auswertung, Interpretation und Diskussion der Messergebnisse erfolgen ausschließlich in der Bachelorarbeit und sind daher **nicht Bestandteil** dieses Repositories.

Das Repository stellt alle wesentlichen technischen Informationen bereit, um den Versuchsaufbau und die Datenerhebung nachvollziehen zu können. Abweichungen in konkreten Hardware-, Funk- oder Umgebungsbedingungen können zu unterschiedlichen Messergebnissen führen.

## Repository-Struktur

- `docs/`  
  Technische Dokumentation der empirischen Umsetzung sowie ergänzende Diagramme.

- `scripts/`  
  Python-Skript zur automatisierten Latenzberechnung, zeitlichen Zuordnung und Klassifikation der Schaltvorgänge.

- `data/`  
  Rohdaten sowie technisch aufbereitete CSV-Dateien der durchgeführten Messdurchgänge.

- `config/openhab/rules/`  
   openHAB Rules zur technischen Umsetzung der Intra-Binding- und Cross-Binding-Szenarien.

## Python-Skript

Das Python-Skript wurde im Rahmen des Versuchsaufbaus direkt auf dem Raspberry Pi ausgeführt, auf dem auch openHAB, die InfluxDB sowie die weiteren notwendigen Systemkomponenten betrieben wurden. Es basiert auf einer Standard-Python-3-Installation und verwendet die Bibliothek `pandas` zur Verarbeitung der aus der InfluxDB ausgelesenen Zeitreihendaten. Das Skript übernimmt die zeitliche Zuordnung von Button- und Aktorereignissen, berechnet die Latenzen, klassifiziert die Schaltvorgänge und exportiert die Ergebnisse in strukturierter Form als CSV-Dateien. Eine lauffähige Entwicklungsumgebung ist für das Verständnis des Skripts nicht erforderlich.

## Lizenz

Dieses Repository steht unter der MIT-Lizenz.
