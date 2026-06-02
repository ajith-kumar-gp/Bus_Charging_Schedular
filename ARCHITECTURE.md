# Architecture

## Overview

This project implements a rule-based scheduling framework for allocating charging resources across a fleet of electric buses operating on a shared route.

The scheduler determines:

* Which charging stations each bus should use
* The charging order at each station
* Waiting times at charging stations
* Final arrival times for each bus

The system is designed to be data-driven and extensible. Routes, stations, charger counts, operators, battery constraints, and optimization weights are loaded from scenario configuration rather than being hardcoded into the scheduling engine.

The primary design goal was to support future changes without requiring modifications to the scheduler core.

---

# Why This Approach

The assignment places a strong emphasis on future extensibility rather than finding a mathematically optimal solution for today's constraints.

For this reason, I chose a simulation-driven, rule-based scheduling architecture that separates:

1. Configuration and scenario data
2. Hard operational constraints
3. Optimization objectives
4. Scheduling and simulation logic

This makes it possible to introduce new business requirements with minimal impact on the existing codebase.

Examples include:

* Additional stations
* Additional routes
* Different charger counts
* New operators
* Priority buses
* Electricity pricing rules
* Maintenance windows

---

# System Architecture

```text
Scenario Configuration
        │
        ▼
+------------------+
| Scenario Loader  |
+------------------+
        │
        ▼
+------------------+
| Scheduling Engine|
+------------------+
        │
 ┌──────┴──────┐
 ▼             ▼
Hard Rules   Soft Rules
 │             │
 └──────┬──────┘
        ▼
Schedule Generation
        │
        ▼
Simulation Results
        │
        ▼
Streamlit UI
```

---

# Core Components

## Scenario Loader

Responsible for loading all scenario-specific configuration.

Each scenario contains:

* Route definition
* Stations
* Charger counts
* Operators
* Physical constraints
* Weight configuration
* Bus schedules

The scheduler never depends on hardcoded route or station information.

---

## Scheduling Engine

The Scheduling Engine is responsible for:

* Generating valid charging plans
* Applying operational constraints
* Allocating charging resources
* Producing final schedules

The engine operates entirely on scenario data and remains independent of any specific route or operator.

---

## Hard Rules

Hard rules represent conditions that must always be satisfied.

Examples include:

* Battery range must never be exceeded
* Charger capacity limits must be respected
* Charging duration is fixed
* Route order must be maintained

If a hard rule fails, the schedule is considered invalid.

Examples:

* RangeRule
* ChargerCapacityRule
* ChargeDurationRule
* RouteOrderRule

---

## Soft Rules

Soft rules represent optimization objectives.

Unlike hard rules, they do not invalidate schedules. Instead, they influence scheduling decisions through weighted scoring.

Current objectives:

### Individual Objective

Reduce excessive waiting time for any individual bus and prevent starvation.

### Operator Objective

Promote fairness across operators and avoid disproportionate delays for a single operator.

### Overall Objective

Improve overall network efficiency and reduce total delay across the system.

These objectives are configurable through scenario weights.

---

# Data Model Design

A scenario acts as the primary input model.

Example structure:

```json
{
  "route": {},
  "stations": [],
  "operators": [],
  "weights": {},
  "buses": []
}
```

The scheduler does not assume:

* Fixed stations
* Fixed routes
* Fixed operators
* Fixed charger counts

All operational data is loaded dynamically from configuration.

---

# Future Changes Considered

| Change                         | Solution                                    | Scheduler Changes |
| ------------------------------ | ------------------------------------------- | ----------------- |
| Add Station E                  | Add station to scenario configuration       | None              |
| Increase chargers at Station B | Update charger count in configuration       | None              |
| Add new operator               | Add operator to configuration               | None              |
| Add a new route                | Define route in scenario configuration      | None              |
| Different battery capacities   | Configure battery range per bus or scenario | None              |
| Priority buses                 | Add a new scheduling rule                   | None              |
| Electricity pricing            | Add a new optimization rule                 | None              |
| Maintenance windows            | Add a new validation rule                   | None              |

The scheduler core remains unchanged in all of these cases.

---

# How to Change a Weight

Weights are stored in scenario configuration.

Example:

```json
{
  "weights": {
    "individual": 10,
    "operator": 2,
    "overall": 1
  }
}
```

Changing optimization priorities only requires updating configuration values.

No scheduler code changes are required.

---

# How to Add a New Rule

New rules are added by implementing a rule class and registering it with the scheduler.

Example:

```python
class TimeOfDayPricingRule(SoftRule):
    pass
```

After registration, the scheduler automatically evaluates the new rule as part of the optimization process.

The scheduler engine itself does not require modification.

---

# Assumptions

The following assumptions were made:

1. All buses travel at a constant speed.
2. Charging always fills the battery to full.
3. Charging duration is fixed.
4. Stations operate continuously unless restricted by future rules.
5. Buses follow the route order defined by the scenario.
6. Charger allocation decisions are determined solely by the scheduler.

These assumptions can be changed through configuration or additional rules.

---

# Conclusion

The architecture prioritizes extensibility, configurability, and separation of concerns.

The scheduling engine remains independent of route definitions, station layouts, operator counts, and future optimization objectives.

As a result, new operational requirements can be introduced primarily through configuration and rule registration rather than modifications to the scheduler core.
