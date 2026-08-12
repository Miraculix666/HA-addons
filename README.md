# Home Assistant Addons & Custom HACS Extensions Repository

This repository contains custom Home Assistant integrations, HACS extensions, and custom Addon blueprints.

---

## Included Integrations & Extensions

### 1. `custom_components/tibber_prices` (TariffWise HACS Extension)
- **Description**: Advanced dynamic electricity tariff calculator, cost-optimal charge scheduler, and Tibber price analyzer.
- **Features**:
  - Automated cheapest price block calculation (`find_cheapest_block`, `plan_charging`).
  - EV and heat pump smart boost scheduling.
  - Native ApexCharts data provider for Lovelace dashboards.

### 2. `tibber-smart-energy`
- Smart energy orchestration module and automation templates.

### 3. `Obico-HA-addon`
- Custom Obico 3D printing monitoring integration.

---

## Installation via HACS

To add any custom component from this repository to Home Assistant:
1. Open **HACS** > **Integrations** > **Custom Repositories**.
2. Add `https://github.com/Miraculix666/HA-addons.git` as an Integration.
3. Search for **TariffWise (Tibber Prices)** and click **Install**.


## Configuration Schema
This repository follows the standardized configuration schema:
- **`config/dev/`**: General universal configurations (environment-agnostic).
- **`config/devops/`**: Machine-specific parameters and host deployment configs.
