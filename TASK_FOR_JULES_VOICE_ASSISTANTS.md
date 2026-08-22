# Task for Jules: Custom Voice Assistant & DiyHue Hub

## Background
Der User benötigt eine spezifische Seite (vergleichbar mit der Home Assistant Cloud / Nabu Casa Übersichtsseite), auf der alle lokalen/alternativen Sprachassistenten zentral verwaltet werden können.

## Requirements
1. **Zentrale Admin-Seite / Panel:** Erstelle ein Custom Panel oder eine Lovelace-Ansicht, die als "Voice Assistant Hub" fungiert.
2. **Alternative Addons:** Die Seite muss Module/Kacheln für die Konfiguration und den Status von:
   - **Google Assistant** (Manuelle/Lokale Integration)
   - **Amazon Alexa** (Manuelle/Lokale Integration)
   - **diyHue** (Emulator für Philips Hue, essentiell für lokale Alexa/Google Anbindung)
3. **Funktionalitäten:** 
   - Anzeige des Verbindungsstatus (z.B. diyHue Container läuft, Ports 80/443 offen).
   - Filter-Management für Entitäten (welche Lampen/Schalter an diyHue gesendet werden).
   - Schnelle Links zu den jeweiligen Addon-Logs oder Konfigurationsdateien.

## Expected Deliverables
- Ein HACS-kompatibles Package oder AppDaemon Dashboard, das dieses UI bereitstellt.
- YAML-Konfigurationen für die Einbindung als Custom Panel (`panel_custom:` oder `panel_iframe:` falls es eine externe Web-App wird).
- Anleitung zur automatischen Verlinkung der `alexa:` und `google_assistant:` Intents mit diesem Hub.

Bitte dieses Feature als eigenständige Erweiterung im `ha_addons_ext` Repository umsetzen.
