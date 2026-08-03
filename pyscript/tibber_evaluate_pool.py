import datetime

@service
def tibber_evaluate_pool(target_entity=None, hours=4, season_sensor=None, solar_radiation=None, temperature_sensor=None, negative_prices_always_on=True):
    if not target_entity:
        return

    try:
        hours = float(hours)
    except:
        hours = 4.0

    # Dynamic adjustments
    try:
        if temperature_sensor:
            temp = float(state.get(temperature_sensor))
            if temp > 25.0: hours += 1.5
            elif temp > 20.0: hours += 0.5
            elif temp < 15.0: hours -= 1.0
        if season_sensor:
            season = state.get(season_sensor)
            if season == "summer": hours += 1.0
            elif season == "winter": hours -= 1.0
        if solar_radiation:
            solar = float(state.get(solar_radiation))
            if solar > 500: hours += 1.0
    except Exception as e:
        log.warning(f"Failed to adjust pool hours: {e}")

    hours = max(1.0, hours) # Prevent it from going <= 0 unexpectedly

    log.info(f"Evaluating Tibber pool schedule for {target_entity} (Duration: {hours}h)")

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

    today_str = now.strftime("%Y-%m-%d")
    valid_blocks = [b for b in all_blocks if b.get("start_time", "").startswith(today_str)]

    if not valid_blocks:
        return

    expanded_blocks = []
    for b in valid_blocks:
        st = b["start_time"]
        try:
            year, month, day = int(st[0:4]), int(st[5:7]), int(st[8:10])
            hour, minute = int(st[11:13]), int(st[14:16])
            dt = datetime.datetime(year, month, day, hour, minute)
            for i in range(4):
                bucket_dt = dt + datetime.timedelta(minutes=15 * i)
                expanded_blocks.append({
                    "start_time": bucket_dt.strftime("%Y-%m-%dT%H:%M:"),
                    "price": b["price"]
                })
        except:
            pass

    sorted_blocks = sorted(expanded_blocks, key=lambda x: x["price"])
    blocks_needed = int(hours * 4)
    cheapest_blocks = sorted_blocks[:blocks_needed]

    should_run = any([b["start_time"].startswith(current_bucket_prefix) for b in cheapest_blocks])

    if not should_run and negative_prices_always_on:
        current_block = [b for b in expanded_blocks if b["start_time"].startswith(current_bucket_prefix)]
        if current_block and current_block[0]["price"] <= 0.0:
            should_run = True
            log.info(f"Tibber Pool Scheduler: Overriding schedule because price is <= 0 ({current_block[0]['price']} EUR)")

    try:
        current_state = state.get(target_entity)

        if should_run:
            if current_state != "on":
                log.info(f"Tibber Pool Scheduler: Turning ON {target_entity}")
                homeassistant.turn_on(entity_id=target_entity)
        else:
            if current_state != "off":
                log.info(f"Tibber Pool Scheduler: Turning OFF {target_entity}")
                homeassistant.turn_off(entity_id=target_entity)
    except Exception as e:
        log.error(f"Failed to switch {target_entity}: {e}")
