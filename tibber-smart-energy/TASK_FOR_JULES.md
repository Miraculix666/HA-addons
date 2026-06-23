# TASK FOR JULES (jules.google.com)
**Topic:** Komplett-Überarbeitung: Tibber Pool-Steuerung & Benachrichtigungen (HA-Addon)
**Target File:** `pyscript/tibber_pool_pump_new.py`

Der aktuelle Code für die Tibber-Pool-Steuerung und die entsprechenden Benachrichtigungen funktioniert nicht mehr zuverlässig. Bitte überprüfe und überarbeite das Skript grundlegend anhand der folgenden Dev-Goals:

## 🎯 Dev-Goals

1. **Tibber API & Preis-Logik fixen:** 
   Prüfe, ob die Tibber-Strompreise (Intervalle) korrekt abgerufen und ausgewertet werden. Die JSON-Pfade oder die Berechnungslogik für die "billigsten Stunden" könnten veraltet sein.

2. **Entity-State Handling (PyScript):** 
   Die Ansteuerung der Poolpumpe schlägt fehl. Stelle sicher, dass das Skript saubere Service-Calls an Home Assistant sendet (Vermeidung von veralteten `extra keys` Fehlern) und die korrekten Rechte im PyScript-Sandboxing besitzt.

3. **Notification Routing reparieren:** 
   Die Benachrichtigungs-Payloads laufen ins Leere. Die Logik muss auf den neuesten Home Assistant Notification-Standard (mit sauberen Fallbacks) gehoben werden, um sicherzustellen, dass die Nachrichten auch ankommen.

4. **Fehlertoleranz & Logging (History-Bezug):** 
   In der Vergangenheit sind solche Automatisierungen oft unbemerkt fehlgeschlagen. Implementiere ein robustes `try/except`-Logging. Wenn Tibber z.B. keine Preise liefert, muss sofort ein klarer Fehler im HA-Log (und idealerweise als Fallback-Notification) erscheinen.

Bitte teste die Anpassungen und committe die funktionsfähige Version zurück in dieses Repository.
