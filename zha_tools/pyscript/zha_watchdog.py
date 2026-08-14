import time

@event_trigger("call_service")
def zha_global_watchdog(domain=None, service=None, service_data=None):
    """
    Globally intercepts service calls to unzuverlÃÂ¤ssige (unreliable) devices.
    Executes a verification loop 5 seconds after the command is sent.
    """
    if domain not in ["switch", "light", "cover", "homeassistant"]: 
        return
        
    if service not in ["turn_on", "turn_off", "toggle", "open_cover", "close_cover", "set_cover_position"]: 
        return
        
    entity_id = service_data.get("entity_id")
    if not entity_id: 
        return
        
    # Lese die Liste der unzuverlÃ¤ssigen GerÃ¤te aus der HA-Gruppe
    attrs = state.getattr("group.unreliable_devices")
    unreliable_entities = attrs.get("entity_id") if attrs else []
    
    # entity_id kann ein String oder eine Liste sein
    if isinstance(entity_id, str):
        entities = [entity_id]
    else:
        entities = entity_id
        
    # Bestimme, ob das Ziel ein unzuverlÃÂ¤ssiges GerÃÂ¤t beinhaltet
    targets = [eid for eid in entities if eid in unreliable_entities]
    
    if not targets:
        return
        
    # Da Pyscript Trigger asynchron in eigenen Tasks laufen, blockieren wir nicht den Main Loop!
    for target in targets:
        # Determine expected state based on the service
        expected_state = None
        if service in ["turn_on", "open_cover"]:
            expected_state = "on" if domain != "cover" else "open"
        elif service in ["turn_off", "close_cover"]:
            expected_state = "off" if domain != "cover" else "closed"
        elif service == "toggle":
            # For toggle, we check what it was before and expect the opposite
            current = state.get(target)
            if current in ["on", "open"]:
                expected_state = "off" if domain != "cover" else "closed"
            else:
                expected_state = "on" if domain != "cover" else "open"
        else:
            # FÃ¼r set_cover_position etc. ist die Logik komplexer, wir loggen nur
            pass
            
        log.warning(f"ZHA Watchdog: Intercepted command '{service}' for unreliable device {target}. Waiting 5s for verification...")
        
        retries = 3
        for attempt in range(retries):
            time.sleep(5)
            
            try:
                # Force Hardware Quittung
                homeassistant.update_entity(entity_id=target)
                time.sleep(2)
                
                # Verify state
                current_state = state.get(target)
                if expected_state and current_state == expected_state:
                    log.warning(f"ZHA Watchdog: SUCCESS! {target} confirmed {current_state} on attempt {attempt+1}.")
                    return
                elif expected_state:
                    log.warning(f"ZHA Watchdog: FAILED. {target} is {current_state} but should be {expected_state}. Retrying...")
                    # Resend original service call
                    globals()['service'].call(domain, service, **service_data)
                else:
                    # If we don't have a clear expected_state (e.g. set_position), just update entity and exit
                    log.warning(f"ZHA Watchdog: Quittung fetched for {target}. No explicit state verification done.")
                    return
                    
            except Exception as e:
                log.warning(f"ZHA Watchdog: Exception while verifying {target}: {e}")
                
        log.error(f"ZHA Watchdog: FATAL ERROR. {target} failed {retries} retry attempts!")
        persistent_notification.create(title="ZHA Hardware Fehler", message=f"W\u00e4chter: Ger\u00e4t {target} hat 3x nicht auf '{service}' reagiert (Keine Quittung)!")
