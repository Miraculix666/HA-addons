# TariffWise ⚡ - Dynamic Energy Tariff & Device Optimization Suite

**Target Repository**: `ha_addons_ext/tariffwise/README.md`  
**Integration Scope**: Tibber API, PyScript Helper Engine, Home Assistant Blueprints, Echo TTS Announcements, Pool Pump Controller, EV & Appliance Scheduler, Lovelace Energy Dashboard.

---

## 📌 Master System Requirements & Goal Specifications

TariffWise is an all-in-one smart energy optimization suite for Home Assistant, designed for dynamic electricity tariffs (Tibber, aWATTar, etc.). It automates energy-intensive consumers (pool pump, hot tub, washing machine, heat pump, EV charging) while maintaining 100% operational fail-safety and multi-channel notifications.

### 1. 🌊 Pool Pump & Circulation Controller Rules
* **Minimum Daily Runtime Guard**:
  - Spring to Late-Summer baseline: **Minimum 1.5 hours daily runtime guaranteed**, regardless of API state.
  - **Summer Water Quality Guard**: Splits the day into 8 equal 3-hour intervals. Guarantees at least 15 minutes of water circulation per 3-hour block to prevent algae growth and chemical stagnation.
  - Temperature & Solar Dynamic Scaling: Automatically extends runtime based on pool/outside temperature and solar radiation (lux).
* **Negative Price Super-Charge**: Automatically triggers 100% max pump & hot tub filtration if prices drop below **0.00 ct/kWh**.
* **Hard Emergency Fallback**: If the Tibber API fails or internet connection drops:
  - Automatically defaults to a hardcoded emergency fallback schedule (**1.5h daily run between 12:00 - 13:30**).
  - Never leaves pool uncirculated for more than 24 hours.

### 2. 🔔 Multi-Channel Notification & Echo Voice Announcements
* **Daily Price Forecast & Schedule Digest**:
  - Automatically compiles and pushes the next day's electricity prices and scheduled device runtimes at **13:00 / 19:00**.
* **Echo / Alexa Smart Speaker Announcements**:
  - Voice announcements on Echo devices (e.g. Echo Wohnzimmer) when cheap price windows open/close or when the pool pump starts.
  - Echo Fallback: If primary Echo is offline, routes notification to mobile app push and secondary media players.
* **Flexible Device Triggers**:
  - Configurable windows (e.g. 2h in the morning, 6 cheapest hours of the day, 3h night-time window) configurable directly via UI/Lovelace.

### 3. 🚗 Smart EV Charging & Addon Synergy
* **EVCC Integration**: Co-exists with EVCC. Default dynamic charging runs via Tibber Cloud / TariffWise API; EVCC is invoked on-demand via HA switch.
* **Dashboard Control**: Full Lovelace Energy & TariffWise Control Board displaying historical price graphs, planned pool pump runtimes, manual emergency overrides, and smart charge status.

---

## 🛠️ System Components & Directory Layout

```
ha_addons_ext/tariffwise/
├── README.md                           # Master specification & Jules directive
├── config/
│   ├── dev/                            # Universal default settings
│   └── devops/                         # Machine & host deployment parameters
├── pyscript/
│   ├── tibber_pool_pump.py             # Distributed pool pump PyScript engine
│   └── tibber_smart_scheduler.py       # Universal dynamic cheap-valley scheduler
├── blueprints/
│   ├── tibber_pool_pump.yaml           # Smart pool pump automation blueprint
│   ├── tibber_pool_pump_emergency.yaml # Emergency fallback automation blueprint
│   └── universal_notification.yaml     # Push, Echo TTS & HTML notification blueprint
└── JULES_EXECUTION_DIRECTIVE.md        # Dedicated Jules execution directive
```

---

## 🤖 Automated Repair & Sync Protocol (Jules Directives)

> **JULES TARIFFWISE EXECUTION DIRECTIVE:**  
> `@jules: Read 'ha_addons_ext/tariffwise/README.md'. Inspect all PyScript engines ('pyscript/tibber_pool_pump.py', 'pyscript/tibber_smart_scheduler.py') and blueprints ('blueprints/*.yaml'). Ensure 100% compliance with master specifications: 1) Minimum 1.5h daily pool pump runtime with 12:00-13:30 fallback on API drop, 2) Summer 3h-interval 15-min water circulation guard, 3) Echo TTS announcements and daily 13:00/19:00 forecast pushes, 4) Negative price (< 0 ct) auto-trigger. Fix all syntax, entity mismatches, and PyScript execution bugs. Commit and push all repaired code directly to 'main'. Log results to '/var/log/tariffwise_jules_repair.log'.`

---

## 🔄 Automatic Live Sync & Activation Workflow

### How changes flow into Home Assistant:
1. **Jules Execution**: Jules processes the directive on `jules.google.com` or via GitHub commit and pushes the repaired TariffWise code directly into `https://github.com/Miraculix666/ha_addons_ext.git`.
2. **20-Minute Cron Auto-Sync**: The background master sync script (`/root/scripts/github_sync_cron.sh`) automatically pulls/syncs remote updates every 20 minutes.
3. **Live Container Mount**: `/GitHub/ha_addons_ext/tariffwise` is linked to Home Assistant (`/config/packages/` / `/config/pyscript/`).
4. **Automatic Service Reload**: Home Assistant automatically reloads PyScript engines and automation blueprints without requiring a full manual container restart.

