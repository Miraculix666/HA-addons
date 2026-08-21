import datetime
import re

def _is_valid_entity_id(entity_id):
    return isinstance(entity_id, str) and re.match(r'^[a-z0-9_]+\.[a-z0-9_]+$', entity_id) is not None

@service
def tibber_evaluate_pool(
    target_entity=None,
    hours=4.0,
    season_sensor=None,
    solar_radiation=None,
    temperature_sensor=None,
    negative_prices_always_on=True,
    temp_high=25.0,
    temp_very_high=30.0,
    temp_low=15.0,
    temp_very_low=10.0,
    solar_threshold=500.0,
    notification_service="",
    optimization_engine="heuristic",
    eos_schedule_sensor=""
):
    if not target_entity or not _is_valid_entity_id(target_entity):
        log.warning(f"Invalid target_entity: {target_entity}")
        return

    if season_sensor and not _is_valid_entity_id(season_sensor):
        season_sensor = None
    if solar_radiation and not _is_valid_entity_id(solar_radiation):
        solar_radiation = None
    if temperature_sensor and not _is_valid_entity_id(temperature_sensor):
        temperature_sensor = None

    if eos_schedule_sensor and not _is_valid_entity_id(eos_schedule_sensor):
        eos_schedule_sensor = None


    try: hours = float(hours)
    except Exception: hours = 4.0
    try: temp_high = float(temp_high)
    except Exception: temp_high = 25.0
    try: temp_very_high = float(temp_very_high)
    except Exception: temp_very_high = 30.0
    try: temp_low = float(temp_low)
    except Exception: temp_low = 15.0
    try: temp_very_low = float(temp_very_low)
    except Exception: temp_very_low = 10.0
    try: solar_threshold = float(solar_threshold)
    except Exception: solar_threshold = 500.0

    now = datetime.datetime.now()
    today_str = now.strftime("%Y-%m-%d")
    current_hour_prefix = now.strftime("%Y-%m-%dT%H:00:")

    # 1. Track runtime (pyscript runs every 15 minutes)
    if now.hour == 0 and now.minute < 15:
        state.set("sensor.pool_pump_runtime_today", value=0.0, new_attributes={"unit_of_measurement": "min", "icon": "mdi:clock"})
    else:
        current_state = state.get(target_entity)
        if current_state == "on":
            current_runtime = float(state.get("sensor.pool_pump_runtime_today") or 0.0)
            state.set("sensor.pool_pump_runtime_today", value=current_runtime + 15.0, new_attributes={"unit_of_measurement": "min", "icon": "mdi:clock"})

    # 2. Fetch Prices
    all_blocks = []
    try:
        from tariffwise_prices import get_all_blocks
        all_blocks = get_all_blocks()
    except ImportError:
        try:
            tibber_res = tibber.get_prices()
            prices_dict = tibber_res.get("prices", {})
            if prices_dict:
                home_name = list(prices_dict.keys())[0]
                all_blocks = prices_dict[home_name]
        except Exception as e:
            log.error(f"Tibber evaluate fallback failed: {e}")

    if not all_blocks:
        log.warning("Tibber Pool: No electricity prices found!")
        return

    today_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(today_str)]
    if not today_blocks:
        log.warning("Tibber Pool: No price blocks found for today!")
        return

    today_blocks = sorted(today_blocks, key=lambda x: x["start_time"])

    # 3. Adjust target run hours
    temp = 20.0
    if temperature_sensor:
        try: temp = float(state.get(temperature_sensor))
        except Exception: pass

    solar = 0.0
    if solar_radiation:
        try: solar = float(state.get(solar_radiation))
        except Exception: pass

    season = "summer"
    if season_sensor:
        try: season = state.get(season_sensor).lower()
        except Exception: pass

    # Adjusted seasons based on prompt: "spring and autumn use 24/4 in winter 24/2 parts of the day"
    is_high_summer = (season == "summer" or temp >= temp_high)
    is_transition = (season in ["spring", "autumn"] or (temp_low < temp < temp_high))
    is_winter = (season == "winter" or temp <= temp_very_low)

    adjusted_hours = hours
    if is_high_summer:
        if temp >= temp_very_high:
            adjusted_hours += 2.0
        elif temp >= temp_high:
            adjusted_hours += 1.0
        if solar > solar_threshold:
            adjusted_hours += 0.5
    elif is_winter:
        adjusted_hours = max(1.0, adjusted_hours - 2.0)
    elif is_transition:
        adjusted_hours = max(1.5, adjusted_hours - 1.0)

    required_hours = max(1, round(adjusted_hours))

    # 4. Schedule based on season/temperature
    scheduled_times = set()
    if is_high_summer:
        # High Summer: 8 intervals of 3 hours (24/8 = 3)
        intervals = 8
        interval_hours = 3
    elif is_transition:
        # Spring/Autumn: 4 intervals of 6 hours (24/4 = 6)
        intervals = 4
        interval_hours = 6
    else:
        # Winter: 2 intervals of 12 hours (24/2 = 12)
        intervals = 2
        interval_hours = 12

    for i in range(intervals):
        start_h = i * interval_hours
        end_h = start_h + interval_hours
        interval_blocks = [
            b for b in today_blocks 
            if start_h <= int(b["start_time"][11:13]) < end_h
        ]
        if interval_blocks:
            cheapest_in_interval = min(interval_blocks, key=lambda x: x["price"])
            scheduled_times.add(cheapest_in_interval["start_time"])

    remaining_needed = required_hours - len(scheduled_times)
    if remaining_needed > 0:
        remaining_blocks = [b for b in today_blocks if b["start_time"] not in scheduled_times]
        sorted_remaining = sorted(remaining_blocks, key=lambda x: x["price"])
        for b in sorted_remaining[:remaining_needed]:
            scheduled_times.add(b["start_time"])

    # 5. Negative and 0 ct prices override
    if negative_prices_always_on:
        for b in today_blocks:
            if b["price"] <= 0.0:
                scheduled_times.add(b["start_time"])


    # 5.5 Check EOS Optimization
    if optimization_engine == "akkudoktor_eos" and eos_schedule_sensor:
        try:
            eos_state = state.get(eos_schedule_sensor)
            if eos_state and eos_state.lower() not in ["unknown", "unavailable"]:
                # Assume EOS sensor returns "on" or "off" for current time block
                # Or contains a schedule array. For simplicity in this adaptation, if it's "on", we run.
                # If we want to fully override the schedule based on an EOS schedule array, we would parse it here.
                # Here we check if the EOS schedule explicitly wants it on.
                if eos_state == "on":
                    should_run = True
                    scheduled_times.add(now.strftime("%Y-%m-%dT%H:%M:00")) # Dummy add to trigger should_run later
                else:
                    should_run = False
                    scheduled_times = set() # Clear heuristic schedule
                log.info(f"Tibber Pool: Using Akkudoktor-EOS schedule for {target_entity} (State: {eos_state})")
        except Exception as e:
            log.warning(f"Tibber Pool: Failed to read EOS schedule, falling back to heuristic: {e}")

    # 6. Format schedule
    today_times_list = sorted(list(set(b["start_time"][11:16] for b in today_blocks if b["start_time"] in scheduled_times)))
    today_schedule_str = ", ".join(today_times_list) if today_times_list else "Keine"
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

    # 8. Evening notification
    if now.hour == 19 and now.minute < 15 and notification_service:
        tomorrow = now + datetime.timedelta(days=1)
        tomorrow_str = tomorrow.strftime("%Y-%m-%d")
        tomorrow_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(tomorrow_str)]
        if tomorrow_blocks:
            tom_scheduled = set()
            for i in range(intervals):
                start_h = i * interval_hours
                end_h = start_h + interval_hours
                interval_blocks = [b for b in tomorrow_blocks if start_h <= int(b["start_time"][11:13]) < end_h]
                if interval_blocks:
                    tom_scheduled.add(min(interval_blocks, key=lambda x: x["price"])["start_time"])
            remaining_needed = required_hours - len(tom_scheduled)
            if remaining_needed > 0:
                remaining_blocks = [b for b in tomorrow_blocks if b["start_time"] not in tom_scheduled]
                sorted_remaining = sorted(remaining_blocks, key=lambda x: x["price"])
                for b in sorted_remaining[:remaining_needed]:
                    tom_scheduled.add(b["start_time"])

            if negative_prices_always_on:
                for b in tomorrow_blocks:
                    if b["price"] <= 0.0:
                        tom_scheduled.add(b["start_time"])

            tom_times_list = sorted(list(set(b["start_time"][11:16] for b in tomorrow_blocks if b["start_time"] in tom_scheduled)))
            tom_schedule_str = ", ".join(tom_times_list) if tom_times_list else "Keine"
            state.set("sensor.pool_pump_schedule_tomorrow", value=tom_schedule_str, new_attributes={"icon": "mdi:pool"})

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
                    if notification_service.startswith("script.universal_notification") or notification_service.startswith("script."):
                        service_domain, service_name = notification_service.split(".", 1)
                        service.call(service_domain, service_name, title="Tibber Poolplan", message=msg)
                    elif "." in notification_service:
                        service_domain, service_name = notification_service.split(".", 1)
                        service.call(service_domain, service_name, title="Tibber Poolplan", message=msg)
                    else:
                        service.call("notify", notification_service, title="Tibber Poolplan", message=msg)
                    state.set("sensor.pool_notification_last_sent", value=today_str)
                    log.info("Pool notification sent successfully.")
                except Exception as e:
                    log.error(f"Error sending pool notification: {e}")
