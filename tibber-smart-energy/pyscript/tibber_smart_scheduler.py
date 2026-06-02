import datetime

@service
def tibber_evaluate_device(target_entity=None, hours=2, start_time="00:00", end_time="23:59"):
    if not target_entity:
        return
        
    try:
        hours = float(hours)
    except:
        hours = 2.0
        
    log.info(f"Evaluating Tibber schedule for {target_entity} (Duration: {hours}h, Window: {start_time}-{end_time})")
    
    now = datetime.datetime.now()
    current_minute = now.minute
    bucket_minute = (current_minute // 15) * 15
    current_bucket_prefix = now.strftime(f"%Y-%m-%dT%H:{bucket_minute:02d}:")
    
    try:
        tibber_res = tibber.get_prices()
        prices_dict = tibber_res.get("prices", {})
        if not prices_dict: return
        home_name = list(prices_dict.keys())[0]
        all_blocks = prices_dict[home_name]
    except Exception as e:
        log.error(f"Tibber evaluate failed for {target_entity}: {e}")
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

    sorted_blocks = sorted(valid_blocks, key=lambda x: x["price"])
    blocks_needed = int(hours * 4)
    cheapest_blocks = sorted_blocks[:blocks_needed]
    
    should_run = any([b["start_time"].startswith(current_bucket_prefix) for b in cheapest_blocks])
    
    try:
        current_state = state.get(target_entity)
        
        # Determine human readable name
        attrs = state.get(target_entity + ".attributes")
        friendly_name = attrs.get("friendly_name") if attrs and "friendly_name" in attrs else target_entity
        
        if should_run:
            if current_state != "on":
                log.info(f"Tibber Scheduler: Turning ON {target_entity}")
                homeassistant.turn_on(entity_id=target_entity)
                # Fire notification event
                event.fire("tibber_device_switched", device=friendly_name, state="eingeschaltet", hours=hours)
        else:
            if current_state != "off":
                log.info(f"Tibber Scheduler: Turning OFF {target_entity}")
                homeassistant.turn_off(entity_id=target_entity)
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
        
        tibber_res = tibber.get_prices()
        
        prices_dict = tibber_res.get("prices", {})
        if not prices_dict: 
            log.warning("ERROR: No prices in dict")
            return
            
        home_name = list(prices_dict.keys())[0]
        all_blocks = prices_dict[home_name]
        
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
        
        # Fire event
        event.fire("tibber_prices_calculated", title="Tibber Strompreise", message=msg)
        
        # Direct notification for debug
        persistent_notification.create(title="Tibber DEBUG", message=f"Pyscript lief erfolgreich! {msg}")
        
        log.warning("Event fired successfully!")
    except Exception as e:
        log.warning(f"Exception in tibber: {e}")
        persistent_notification.create(title="Tibber DEBUG ERROR", message=str(e))
