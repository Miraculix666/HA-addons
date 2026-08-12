import datetime

@service
def tibber_evaluate_device(target_entity=None, hours=2, start_time="00:00", end_time="23:59", continuous=False):
    if not target_entity:
        return
        
    try:
        hours = float(hours)
    except:
        hours = 2.0
        
    log.info(f"Evaluating Tibber schedule for {target_entity} (Duration: {hours}h, Window: {start_time}-{end_time}, Continuous: {continuous})")
    
    now = datetime.datetime.now()
    current_minute = now.minute
    bucket_minute = (current_minute // 15) * 15
    current_bucket_prefix = now.strftime(f"%Y-%m-%dT%H:{bucket_minute:02d}:")
    
    from tariffwise_prices import get_all_blocks
    all_blocks = get_all_blocks()
                             
    if not all_blocks:
        log.error(f"Tibber evaluate failed for {target_entity}: No prices found")
        return

    # Filter blocks
    valid_blocks = []
    today_str = now.strftime("%Y-%m-%d")
    tomorrow = now + datetime.timedelta(days=1)
    tomorrow_str = tomorrow.strftime("%Y-%m-%d")
    
    for b in all_blocks:
        st = b.get("start_time", "")
        if not st: continue
        time_part = st[11:16]
        date_part = st[0:10]
        
        if date_part not in [today_str, tomorrow_str]:
            continue
            
        if start_time <= end_time:
            if start_time <= time_part <= end_time:
                valid_blocks.append(b)
        else:
            if time_part >= start_time or time_part <= end_time:
                valid_blocks.append(b)

    if not valid_blocks:
        return

    blocks_needed = int(hours * 4)
    valid_blocks = sorted(valid_blocks, key=lambda x: x["start_time"])
    
    if str(continuous).lower() in ["true", "1", "yes"] and len(valid_blocks) >= blocks_needed:
        # Find cheapest contiguous block
        min_price = float('inf')
        best_sequence = []
        for i in range(len(valid_blocks) - blocks_needed + 1):
            sequence = valid_blocks[i:i+blocks_needed]
            # Verify they are actually contiguous in time (approximate check by looking at length, assuming 15min intervals)
            seq_price = sum(b["price"] for b in sequence)
            if seq_price < min_price:
                min_price = seq_price
                best_sequence = sequence
        cheapest_blocks = best_sequence
    else:
        # Non-continuous (Absolute cheapest hours)
        sorted_blocks = sorted(valid_blocks, key=lambda x: x["price"])
        cheapest_blocks = sorted_blocks[:blocks_needed]
    
    should_run = any([b["start_time"].startswith(current_bucket_prefix) for b in cheapest_blocks])
    
    try:
        current_state = state.get(target_entity)
        
        # Determine human readable name
        attrs = state.getattr(target_entity)
        friendly_name = attrs.get("friendly_name") if attrs and "friendly_name" in attrs else target_entity
        
        if should_run:
            if current_state != "on":
                log.info(f"Tibber Scheduler: Turning ON {target_entity}")
                service.call("homeassistant", "turn_on", entity_id=target_entity)
                # Fire notification event
                event.fire("tibber_device_switched", device=friendly_name, state="eingeschaltet", hours=hours)
        else:
            if current_state != "off":
                log.info(f"Tibber Scheduler: Turning OFF {target_entity}")
                service.call("homeassistant", "turn_off", entity_id=target_entity)
                # Fire notification event
                event.fire("tibber_device_switched", device=friendly_name, state="ausgeschaltet", hours=hours)
    except Exception as e:
        log.error(f"Failed to switch {target_entity}: {e}")


@service
@time_trigger("startup", "cron(0 19 * * *)")
def tibber_daily_notification():
    log.warning("tibber_daily_notification START")
    try:
        now = datetime.datetime.now()
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        
        from tariffwise_prices import get_all_blocks
        all_blocks = get_all_blocks()
            
        if not all_blocks:
            sensor_names = [s for s in state.names("sensor") if s.startswith("sensor.electricity_price_")]
            for s in sensor_names:
                attrs = state.getattr(s)
                if attrs and "today" in attrs:
                    for day in ["today", "tomorrow"]:
                        if day in attrs and attrs[day]:
                            for block in attrs[day]:
                                st = block.get("startsAt") or block.get("start_time")
                                pr = block.get("total") if "total" in block else block.get("price")
                                if st and pr is not None:
                                    all_blocks.append({"start_time": st, "price": float(pr)})
                    if all_blocks:
                        break
                                
        if not all_blocks: 
            log.warning("ERROR: No prices found")
            event.fire("tibber_prices_calculated", title="Tibber Fehler", message="Es konnten keine Preise (weder fÃ¼r heute noch morgen) gefunden werden. Bitte Integration prÃ¼fen!")
            return
        
        tom_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(tomorrow_str)]
        if not tom_blocks: 
            log.warning("ERROR: No blocks for tomorrow found! Sending fallback notification.")
            today_str = now.strftime("%Y-%m-%d")
            today_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(today_str)]
            if today_blocks:
                prices = [b["price"] for b in today_blocks]
                avg_price = sum(prices) / len(prices)
                current_blocks = [b for b in today_blocks if b["start_time"].startswith(now.strftime("%Y-%m-%dT%H:00:"))]
                current_block = current_blocks[0] if current_blocks else None
                curr_price_str = f"Aktuell: {round(current_block['price'] * 100, 2)} ct." if current_block else ""
                msg = f"Hinweis: Noch keine Preise fÃ¼r morgen verfÃ¼gbar. Heute: Ã {round(avg_price * 100, 2)} ct. {curr_price_str}"
            else:
                msg = "Hinweis: Keine aktuellen Tibber-Daten verfÃ¼gbar (Weder fÃ¼r heute noch morgen)."
            
            event.fire("tibber_prices_calculated", title="Tibber Strompreise (Info)", message=msg)
            return
        
        prices = [b["price"] for b in tom_blocks]
        avg_price = sum(prices) / len(prices)
        min_block = min(tom_blocks, key=lambda x: x["price"])
        min_time = min_block["start_time"][11:16]
        max_block = max(tom_blocks, key=lambda x: x["price"])
        max_time = max_block["start_time"][11:16]
        
        msg = f"Tibber Info fÃ¼r morgen: Durchschnitt {round(avg_price * 100, 2)} ct. GÃ¼nstigst um {min_time} ({round(min_block['price'] * 100, 2)} ct). Teuerst um {max_time}."
        
        import urllib.parse
        import json
        
        labels = [b["start_time"][11:13] for b in tom_blocks]
        data = [round(b["price"] * 100, 1) for b in tom_blocks]
        
        chart_config = {
            "type": "bar",
            "data": {
                "labels": labels,
                "datasets": [{
                    "label": "Strompreis (ct/kWh)",
                    "data": data,
                    "backgroundColor": "rgba(54, 162, 235, 0.5)",
                    "borderColor": "rgb(54, 162, 235)",
                    "borderWidth": 1
                }]
            },
            "options": {
                "title": {
                    "display": True,
                    "text": "Tibber Preise Morgen"
                }
            }
        }
        
        chart_url = "https://quickchart.io/chart?c=" + urllib.parse.quote(json.dumps(chart_config))
        
        # Fire event
        event.fire("tibber_prices_calculated", title="Tibber Strompreise", message=msg, image=chart_url)
        
        # Direct notification for debug
        service.call("persistent_notification", "create", title="Tibber DEBUG", message=f"Pyscript lief erfolgreich! {msg}")
        
        log.warning("Event fired successfully!")
    except Exception as e:
        log.warning(f"Exception in tibber: {e}")
        service.call("persistent_notification", "create", title="Tibber DEBUG ERROR", message=str(e))
        event.fire("tibber_prices_calculated", title="Tibber Skript-Fehler", message=f"Kritischer Fehler im Tibber Skript: {e}")
