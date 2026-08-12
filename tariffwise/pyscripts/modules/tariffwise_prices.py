def get_all_blocks():
    """
    Modular price determination with multiple fallbacks.
    Returns a list of dicts: [{"start_time": "2026-08-08T10:00:00+02:00", "price": 0.12}, ...]
    """
    import datetime
    
    all_blocks = []
    
    # Fallback 1: Direct Tibber Service Call (Best Accuracy)
    try:
        tibber_res = service.call("tibber", "get_prices", return_response=True)
        if isinstance(tibber_res, dict) and "prices" in tibber_res:
            prices_dict = tibber_res.get("prices", {})
            if prices_dict:
                home_name = list(prices_dict.keys())[0]
                all_blocks = prices_dict[home_name]
                if all_blocks:
                    return all_blocks
    except Exception:
        pass
        
    # Fallback 2: Tibber Sensor Attributes (If service fails or not available)
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
                return all_blocks
                
    # Fallback 3: Nordpool Sensor (If Tibber is down but Nordpool HACS is installed)
    nordpool_sensors = [s for s in state.names("sensor") if s.startswith("sensor.nordpool_")]
    for s in nordpool_sensors:
        attrs = state.getattr(s)
        if attrs and "raw_today" in attrs:
            for day in ["raw_today", "raw_tomorrow"]:
                if day in attrs and attrs[day]:
                    for block in attrs[day]:
                        st = block.get("start")
                        pr = block.get("value")
                        if st and pr is not None:
                            # Format start to match Tibber format string if needed
                            st_str = st.strftime("%Y-%m-%dT%H:%M:%S%z") if hasattr(st, "strftime") else str(st)
                            all_blocks.append({"start_time": st_str, "price": float(pr)})
            if all_blocks:
                return all_blocks

    # Fallback 4: aWATTar / ENTSO-e (Generic fallback)
    awattar_sensors = [s for s in state.names("sensor") if s.startswith("sensor.awattar_")]
    for s in awattar_sensors:
        attrs = state.getattr(s)
        if attrs and "data" in attrs: # generic check, awattar structure varies
            for block in attrs["data"]:
                st = block.get("start_timestamp") or block.get("start_time")
                pr = block.get("marketprice") or block.get("price")
                if st and pr is not None:
                    # simplistic conversion
                    if isinstance(st, int):
                        # Convert ms to string if needed
                        st_dt = datetime.datetime.fromtimestamp(st / 1000.0)
                        st_str = st_dt.strftime("%Y-%m-%dT%H:%M:%S%z")
                    else:
                        st_str = str(st)
                    all_blocks.append({"start_time": st_str, "price": float(pr)})
            if all_blocks:
                return all_blocks

    return all_blocks
