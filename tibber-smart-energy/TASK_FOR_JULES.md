# TASK FOR JULES (jules.google.com)
**Topic:** Architektur und Entwicklung einer universellen Home Assistant Integration für dynamische Strompreise (Fokus auf Tibber, Awattar, etc.)

## 🎯 Übergeordnete Vision
Die bisherige "Tibber Pool-Steuerung" war nur ein MVP und eine erste Beispielanwendung. Deine neue Aufgabe ist weitaus größer:
Baue eine **universell nutzbare, dynamisch preisbasierte, zeit- und preisoptimierte Integration / Erweiterung**! 

Die Poolpumpe dient ab sofort nur noch als erste Test-Anwendung. Das Addon/die Integration soll fähig sein, beliebige Geräte im Haushalt (Waschmaschine, E-Auto, Boiler etc.) effizient nach dynamischen Tarifen zu steuern.

## 📋 Kern-Requirements

1. **Universelle Zeiträume (Frei definierbar):**
   - Der Nutzer muss in der Lage sein, beliebig viele, völlig freie Zeiträume (z.B. "Jeden Tag zwischen 10:00 und 14:00 Uhr" oder "Nachts") zu definieren.
   - Innerhalb dieser Zeiträume soll die Engine die X günstigsten Stunden/Minuten für die Aktivierung berechnen.

2. **Umfassendes Notification-System:**
   - Jede denkbare Benachrichtigungsvariante muss frei auswählbar sein: Gruppen-Benachrichtigungen, Popups auf Dashboards, Sprachausgabe über Mediengeräte (Smart Speaker, TVs), "All"-Broadcasts usw.

3. **Wunderschöne & intuitive GUI:**
   - Dies ist von höchster Priorität: Baue ein modernes, selbsterklärendes UI (Config Flow / Frontend), in dem der Nutzer seine Entitäten, Preis-Grenzen, Zeitfenster und Notifications per Mausklick zusammenklicken kann. Kein reines YAML mehr!

4. **Codebase & Referenzen (Integrationen):**
   - Bediene dich an der Codebase existierender, erfolgreicher HA-Integrationen für dynamische Preise, um Best Practices zu übernehmen (z.B. offizielle Tibber Integration, EVCC, ev_smart_charging, ha-battery-optimizer). Nutze diese Repositories als Grundlage für die Preisberechnungslogik und Architektur.

## 🛠️ Nächste Schritte für dich (Jules)
- Erstelle ein technisches Konzept für eine vollwertige Custom Component (`custom_components/dynamic_energy_optimizer`).
- Implementiere den Config Flow (GUI) und die Preis-Berechnungs-Engine.
- Committe deine Ergebnisse zurück in dieses Repository.
