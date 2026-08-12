import datetime

@service
def tibber_evaluate_pool(target_entity=None, hours=4.0, season_sensor=None, solar_radiation=None, temperature_sensor=None, negative_prices_always_on=True):
    if not target_entity:
        log.error("Tibber Pool: No target_entity provided!")
        return

    try:
        hours = float(hours)
    except Exception:
        hours = 4.0

    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_hour_prefix = now.strftime("%Y-%m-%dT%H:00:")

    # 1. Track runtime (pyscript runs every 15 minutes)
    # Reset at midnight (00:00 - 00:15 window)
    if now.hour == 0 and now.minute < 15:
        state.set("sensor.pool_pump_runtime_today", value=0.0, new_attributes={"unit_of_measurement": "min", "icon": "mdi:clock"})
    else:
        # If pump is currently running, increment today's runtime by 15 minutes
        current_state = state.get(target_entity)
        if current_state == "on":
            current_runtime = float(state.get("sensor.pool_pump_runtime_today") or 0.0)
            state.set("sensor.pool_pump_runtime_today", value=current_runtime + 15.0, new_attributes={"unit_of_measurement": "min", "icon": "mdi:clock"})

    # 2. Fetch Prices (Modular via TariffWise)
    from tariffwise_prices import get_all_blocks
    all_blocks = get_all_blocks()

    if not all_blocks:
        log.error("Tibber Pool: No electricity prices found!")
        return

    today_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(today_str)]
    if not today_blocks:
        log.error("Tibber Pool: No price blocks found for today!")
        return

    # Sort today's blocks by start time to keep them ordered
    today_blocks = sorted(today_blocks, key=lambda x: x["start_time"])

    # 3. Adjust target run hours based on temperature / solar / season
    temp = 20.0
    if temperature_sensor:
        try:
            temp = float(state.get(temperature_sensor))
        except Exception:
            pass

    solar = 0.0
    if solar_radiation:
        try:
            solar = float(state.get(solar_radiation))
        except Exception:
            pass

    season = "summer"
    if season_sensor:
        try:
            season = state.get(season_sensor).lower()
        except Exception:
            pass

    # Dynamic hour adjustment:
    adjusted_hours = hours
    if season == "summer" or temp >= 25.0:
        if temp >= 30.0:
            adjusted_hours += 2.0
        elif temp >= 25.0:
            adjusted_hours += 1.0
        
        if solar > 500:
            adjusted_hours += 0.5
    elif season == "winter" or temp <= 10.0:
        adjusted_hours = max(1.0, adjusted_hours - 2.0)
    elif temp <= 15.0:
        adjusted_hours = max(1.5, adjusted_hours - 1.0)

    required_hours = max(1, round(adjusted_hours))

    # 4. Divide day into 8 intervals of 3 hours:
    scheduled_times = set()

    # Always enforce Water Quality Guard: Ensure at least one run in each of the 8 intervals of 3 hours
    for i in range(8):
        start_h = i * 3
        end_h = start_h + 3
        interval_blocks = [
            b for b in today_blocks 
            if start_h <= int(b["start_time"][11:13]) < end_h
        ]
        if interval_blocks:
            cheapest_in_interval = min(interval_blocks, key=lambda x: x["price"])
            scheduled_times.add(cheapest_in_interval["start_time"])

    # If we need more hours to meet the required_hours, fill with the cheapest overall remaining hours
    remaining_needed = required_hours - len(scheduled_times)
    if remaining_needed > 0:
        remaining_blocks = [b for b in today_blocks if b["start_time"] not in scheduled_times]
        sorted_remaining = sorted(remaining_blocks, key=lambda x: x["price"])
        for b in sorted_remaining[:remaining_needed]:
            scheduled_times.add(b["start_time"])

    # 5. Negative and 0 ct prices override (always run at 0 ct or negative)
    if negative_prices_always_on:
        for b in today_blocks:
            if b["price"] <= 0.0:
                scheduled_times.add(b["start_time"])

    # 6. Format schedule for UI sensors
    today_times_list = sorted(list(set(b["start_time"][11:16] for b in today_blocks if b["start_time"] in scheduled_times)))
    today_schedule_str = ", ".join(today_times_list)
    state.set("sensor.pool_pump_schedule_today", value=today_schedule_str, new_attributes={"icon": "mdi:pool"})

    # 7. Apply switching action
    should_run = any(st.startswith(current_hour_prefix) for st in scheduled_times)
    current_state = state.get(target_entity)

    if should_run:
        if current_state != "on":
            log.info(f"Tibber Pool: Turning ON {target_entity} (Price scheduled)")
            service.call("switch", "turn_on", entity_id=target_entity)
    else:
        if current_state != "off":
            log.info(f"Tibber Pool: Turning OFF {target_entity}")
            service.call("switch", "turn_off", entity_id=target_entity)

    # 8. Evening notification for tomorrow at 19:00 (includes real runtime summary)
    if now.hour == 19 and now.minute < 15:
        # Get tomorrow's schedule
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        tomorrow_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(tomorrow_str)]
        if tomorrow_blocks:
            tom_scheduled = set()
            if is_high_summer:
                for i in range(8):
                    start_h = i * 3
                    end_h = start_h + 3
                    interval_blocks = [b for b in tomorrow_blocks if start_h <= int(b["start_time"][11:13]) < end_h]
                    if interval_blocks:
                        tom_scheduled.add(min(interval_blocks, key=lambda x: x["price"])["start_time"])
                remaining_needed = required_hours - len(tom_scheduled)
                if remaining_needed > 0:
                    remaining_blocks = [b for b in tomorrow_blocks if b["start_time"] not in tom_scheduled]
                    sorted_remaining = sorted(remaining_blocks, key=lambda x: x["price"])
                    for b in sorted_remaining[:remaining_needed]:
                        tom_scheduled.add(b["start_time"])
            else:
                sorted_blocks_tom = sorted(tomorrow_blocks, key=lambda x: x["price"])
                for b in sorted_blocks_tom[:required_hours]:
                    tom_scheduled.add(b["start_time"])

            if negative_prices_always_on:
                for b in tomorrow_blocks:
                    if b["price"] <= 0.0:
                        tom_scheduled.add(b["start_time"])

            tom_times_list = sorted(list(set(b["start_time"][11:16] for b in tomorrow_blocks if b["start_time"] in tom_scheduled)))
            tom_schedule_str = ", ".join(tom_times_list)
            state.set("sensor.pool_pump_schedule_tomorrow", value=tom_schedule_str, new_attributes={"icon": "mdi:pool"})

            # Send push notification with real runtime summary
            last_sent = state.get("sensor.pool_notification_last_sent")
            if last_sent != today_str:
                real_runtime = float(state.get("sensor.pool_pump_runtime_today") or 0.0)
                real_hours = round(real_runtime / 60.0, 1)
                
                prices = [b["price"] for b in tomorrow_blocks]
                avg_price = sum(prices) / len(prices)
                min_block = min(tomorrow_blocks, key=lambda x: x["price"])
                min_time = min_block["start_time"][11:16]
                
                msg = f"Poolpumpe lief heute real {real_hours} Stunden. Tibber Info für morgen: Durchschnitt {round(avg_price * 100, 2)} Cent. Die günstigste Zeit ist um {min_time}. Geplant: {tom_schedule_str}."
                try:
                    service.call("notify", "mobile_app_marius_13tpro", title="Tibber Poolplan & Laufzeit", message=msg)
                    state.set("sensor.pool_notification_last_sent", value=today_str)
                    log.info("Pool notification sent successfully.")
                except Exception as e:
                    log.error(f"Error sending pool notification: {e}")
