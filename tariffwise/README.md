# TariffWise ⚡

TariffWise is a premium Home Assistant integration and automation suite for dynamic electricity tariffs (Tibber, Awattar, etc.). It helps you schedule energy-intensive household appliances (pool pumps, washing machines, EV chargers, boilers) to run during the cheapest hours, saving electricity costs automatically.

## 🎯 Key Features

1. **Flexible Time Windows (Arbitrary Timeframes):**
   - Define custom start and end times (e.g., "Between 10:00 and 14:00" or "Night time").
   - The engine automatically calculates and schedules the cheapest $X$ hours/minutes within your custom timeframe.

2. **Smart Distributed Pool Pump Controller:**
   - **Summer Water Quality Guard:** During summer/high temperature, the day is split into 8 intervals of 3 hours. The pump is guaranteed to run at least 15 minutes per interval to keep the water circulated, preventing algae growth.
   - **Dynamic Adjustments:** Automatically adjusts daily run hours based on water/outside temperature, season, and solar radiation (lux/solar sensors).
   - **Negative Price Override:** Automatically turns on the pump if electricity prices fall below 0 ct/kWh.

3. **Advanced Notification System:**
   - Sends daily price summaries (including interactive HTML price charts) at 19:00 for the next day.
   - Triggers customizable notifications (mobile app pushes, smart speakers, media players) whenever a scheduled device switches on or off.

4. **Premium GUI Flow (No Raw YAML):**
   - Add and configure all settings, price thresholds, target entities, and notification preferences through an intuitive, modern HACS configuration flow.

---

## 🛠️ Installation & Setup

### 1. PyScript Helpers
TariffWise relies on lightweight PyScript engines to perform advanced evaluations (such as finding multiple cheap valleys, parsing weather forecasts, and distributed scheduling).
Copy the following files to your `/config/pyscript/` folder:
- `tibber_pool_pump.py` (Pool pump interval controller)
- `tibber_smart_scheduler.py` (Universal device scheduler)

### 3. Blueprints
Install the automation blueprints located in the `blueprints/` folder:
- `tibber_pool_pump.yaml` (Smart pool pump controller)
- `tibber_pool_pump_emergency.yaml` (Emergency fail-safe pool control)
- `universal_notification.yaml` (Push and announcement notification handler)


## Configuration Schema
This repository follows the standardized configuration schema:
- **`config/dev/`**: General universal configurations (environment-agnostic).
- **`config/devops/`**: Machine-specific parameters and host deployment configs.
