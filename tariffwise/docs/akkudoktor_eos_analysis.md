# Analysis: Improving TariffWise with Akkudoktor-EOS Integration

## Overview
Currently, **TariffWise** uses a heuristic, reactive scheduling approach (e.g., finding the cheapest 4 hours via `tibber_pool_pump.py`) to manage loads based on Tibber prices. While functional, this approach lacks holistic energy optimization.

**Akkudoktor-EOS** is a mathematical optimization engine designed to build energy management plans for home automation, considering:
- Real-time electricity pricing (Tibber, aWATTar).
- Photovoltaic (PV) system yield forecasts.
- Battery storage charge/discharge cycles.
- Electric Vehicles (EV) and household load management.

## Current TariffWise Limitations vs. EOS Capabilities

### 1. Load Scheduling (Pool Pump, etc.)
**Current TariffWise:**
- Searches for the absolute cheapest blocks or distributes them across intervals (e.g., eight 3-hour windows in summer).
- It only looks at the *grid price*.
**EOS Improvement:**
- EOS uses a solver (like HiGHS/CBC) to calculate the globally optimal schedule.
- It factors in predicted local PV surplus. If electricity is slightly more expensive from the grid but PV surplus will cover the load, EOS correctly schedules the load to run on solar, reducing actual cost to zero (or the opportunity cost of feed-in tariff).

### 2. Battery Storage Integration
**Current TariffWise:**
- Has no native concept of home battery storage optimization.
**EOS Improvement:**
- EOS inherently calculates battery arbitrage. It knows when it is mathematically optimal to charge the battery from the grid (during cheap hours) and discharge it during expensive hours, preventing the pool pump from draining the home battery unnecessarily when grid prices are low.

### 3. PV Generation Forecasting
**Current TariffWise:**
- Uses a simple threshold (`solar_threshold = 500.0` W/m²) to dynamically add runtime if the sun is shining *right now*. This is purely reactive.
**EOS Improvement:**
- EOS incorporates look-ahead solar forecasting. It can plan to defer running a flexible load until the afternoon if a large PV yield is predicted, rather than running it in the morning on cheap grid power.

### 4. EVCC Synergy
**Current TariffWise:**
- Co-exists with EVCC but operates independently.
**EOS Improvement:**
- EOS can orchestrate multiple loads simultaneously, prioritizing EV charging over pool pumping or vice-versa based on global minimum cost functions over the next 24-48 hours.

## Conclusion
Integrating Akkudoktor-EOS as the underlying calculation engine (or replacing `tibber_evaluate_pool` with an EOS-generated schedule) would transform TariffWise from a **price-reactive scheduler** into a **predictive, holistic energy optimizer**. The use of Akkudoktor-EOS would significantly improve the tariff-wise integration by mathematically minimizing total energy costs across all assets (Grid, PV, Battery, EV, Loads) simultaneously.
