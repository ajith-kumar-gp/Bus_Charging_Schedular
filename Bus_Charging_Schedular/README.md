# Electric Bus Charging Scheduler

A Python and Streamlit application that schedules charging for electric buses operating on a shared route with limited charging infrastructure.

The scheduler determines:

* Which charging stations each bus should use
* The charging order at each station
* Bus waiting times
* Final arrival times

The solution uses a configurable rule-based scheduling framework with weighted objectives for:

* Individual bus delay
* Operator fairness
* Overall network efficiency

The system is designed to be data-driven and extensible. Routes, stations, charger counts, operators, and scenario configurations are loaded from configuration data rather than being hardcoded into the scheduling engine.

## Tech Stack

* Python 3
* Streamlit
* Pandas

## Running Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deployment

This application can be deployed directly on Streamlit Community Cloud by connecting the GitHub repository and selecting `app.py` as the entry point.

## Repository Structure

```text
app.py

scheduler/
├── engine/
├── models/
├── rules/
├── data/
├── ui/

README.md
ARCHITECTURE.md
requirements.txt
```

## Extensibility

The scheduler is designed so that:

* New stations can be added through configuration
* Charger counts can be changed through configuration
* New operators can be added through configuration
* Scenario weights can be changed through configuration
* New scheduling rules can be added without modifying the scheduler core

See `ARCHITECTURE.md` for implementation details and extension examples.
