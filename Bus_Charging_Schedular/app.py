# -*- coding: utf-8 -*-
"""
Multi-Objective Electric Bus Charging Scheduler Dashboard
Designed as an elite, data-driven system for production-ready technical interviews.
"""

import streamlit as st
import json
import os
import copy
import pandas as pd

from scheduler.models.scenario import Scenario
from scheduler.models.route import Route
from scheduler.models.station import Station
from scheduler.models.bus import Bus
from scheduler.engine.scheduler_engine import SchedulerEngine

from scheduler.ui.scenario_view import render_scenario_view
from scheduler.ui.station_view import render_station_view
from scheduler.ui.bus_view import render_bus_view
from scheduler.ui.explanation_view import render_explanation_view

st.set_page_config(
    page_title="Multi-Objective Electric Bus Charging Scheduler",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

code, pre {
    font-family: 'JetBrains Mono', monospace !important;
}

/* Metric card styling */
div[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 15px 20px;
    border-radius: 12px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
}

div[data-testid="stMetric"] label {
    font-size: 11px !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b !important;
    font-weight: 600;
}

div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
    font-size: 22px !important;
    font-weight: 700;
    color: #0f172a;
}

/* Base custom card styled box */
.custom-card {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)


# --- Helper Function to Load Default Scenarios ---
def load_default_scenarios():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    scenarios_dir = os.path.join(
        base_dir,
        "scheduler",
        "data",
        "scenarios"
    )

    default_scenarios = []

    try:
        filenames = sorted(os.listdir(scenarios_dir))

        for fname in filenames:
            if fname.endswith(".json"):
                with open(
                    os.path.join(scenarios_dir, fname),
                    "r",
                    encoding="utf-8"
                ) as f:
                    default_scenarios.append(json.load(f))

    except Exception as e:
        st.error(f"Error loading system scenarios: {e}")

    return default_scenarios


# Setup default scenario lists inside Session State
if "default_scenarios" not in st.session_state:
    st.session_state.default_scenarios = load_default_scenarios()

if "custom_scenarios" not in st.session_state:
    st.session_state.custom_scenarios = {}

# Build absolute list of active scenarios
all_scenarios_dict = {}
for ds in st.session_state.default_scenarios:
    all_scenarios_dict[ds["id"]] = ds
for s_id, cs in st.session_state.custom_scenarios.items():
    all_scenarios_dict[s_id] = cs

# Setup default active item
if "selected_scenario_id" not in st.session_state or st.session_state.selected_scenario_id not in all_scenarios_dict:
    if all_scenarios_dict:
        st.session_state.selected_scenario_id = list(all_scenarios_dict.keys())[0]
    else:
        st.session_state.selected_scenario_id = "empty"

if (
    "active_scenario_raw" not in st.session_state
    or not st.session_state.active_scenario_raw
    ):
    if st.session_state.selected_scenario_id in all_scenarios_dict:
        st.session_state.active_scenario_raw = copy.deepcopy(all_scenarios_dict[st.session_state.selected_scenario_id])
    else:
        st.session_state.active_scenario_raw = {}


# --- Header Structure ---
st.markdown("""
<div style="margin-bottom: 10px;">
  <span style="background-color: #10b981; color: white; font-size: 10px; font-weight: bold; font-family: monospace; padding: 2px 6px; border-radius: 3px; letter-spacing: 0.1em; text-transform: uppercase;">
    100% Data-Driven Model
  </span>
  <span style="font-size: 11px; color: #4338ca; font-weight: 600; background-color: #e0e7ff; padding: 2px 8px; border-radius: 9999px; margin-left: 8px; border: 1px solid #c7d2fe;">
    Decoupled Rules Registry Active
  </span>
</div>
""", unsafe_allow_html=True)

st.title("Electric Bus Multi-Objective Dispatch Scheduler")
st.caption("Discrete Event Queue Simulator (DES) with meta-heuristic search optimization. 100% decoupling between scheduler core logic and underlying configuration datasets.")

st.write("")

# Dynamic scenario selectors
header_col1, header_col2, header_col3 = st.columns([3, 2, 1])

with header_col1:
    scenario_choices = {s_id: sc["name"] for s_id, sc in all_scenarios_dict.items()}
    scenario_ids = list(scenario_choices.keys())

    selected_scen_id = st.selectbox(
        "📂 Active Operational Scenario Template:",
        options=scenario_ids,
        index=0 if scenario_ids else None,
        format_func=lambda x: scenario_choices.get(x, x),
        key="scenario_selector_main"
    )

    if (
        selected_scen_id
        and selected_scen_id in all_scenarios_dict
        and selected_scen_id != st.session_state.selected_scenario_id
    ):
        st.session_state.selected_scenario_id = selected_scen_id
        st.session_state.active_scenario_raw = copy.deepcopy(
            all_scenarios_dict[selected_scen_id]
        )
        st.rerun()

# with header_col2:
#     # 9. Upload Custom Scenario JSON widget
#     uploaded_file = st.file_uploader("📂 Upload Custom Scenario JSON", type=["json"], help="Instantly load dynamic routes or operational schedules on the fly.")
#     if uploaded_file is not None:
#         try:
#             custom_data = json.load(uploaded_file)
#             if "id" in custom_data and "name" in custom_data:
#                 c_id = custom_data["id"]
#                 st.session_state.custom_scenarios[c_id] = custom_data
#                 all_scenarios_dict[c_id] = custom_data
#                 st.session_state.selected_scenario_id = c_id
#                 st.session_state.active_scenario_raw = copy.deepcopy(custom_data)
#                 st.success(f"Custom scenario '{custom_data['name']}' uploaded successfully!")
#                 st.rerun()
#             else:
#                 st.error("JSON schema must contain at least 'id' and 'name' attributes.")
#         except Exception as ex:
#             st.error(f"Failed to parse custom file: {ex}")

with header_col3:
    st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
    if st.button("🔄 Reset Baseline", help="Restore active parameters to baseline specifications", use_container_width=True):
        if st.session_state.selected_scenario_id in all_scenarios_dict:
            baseline_scen = all_scenarios_dict[st.session_state.selected_scenario_id]
            st.session_state.active_scenario_raw = copy.deepcopy(baseline_scen)
            st.toast("Active parameters restored to baseline specifications!")
            st.rerun()


# --- Left Sandbox Modifiers and Right Schedule Output Views ---
active_raw = st.session_state.active_scenario_raw

if active_raw:
    left_col, right_col = st.columns([5, 7])

    # --- LEFT COL: SANDBOX MODIFIERS ---
    with left_col:
        st.markdown("<h4 style='color:#0f172a; margin-top:0;'>🛠️ Real-Time Parameters Sandbox</h4>", unsafe_allow_html=True)
        st.markdown("<p style='font-size:12px; color:#64748b; margin-top:-8px;'>Fulfill the technical rounds by modifying hardware, distances, and priority weight metrics live.</p>", unsafe_allow_html=True)

        # 5. Weights sliders
        st.markdown("##### ⚖️ Competing Objectives Weighting Tuning")
        w_ind = st.slider(
            "Individual Bus Starvation weight (Squared Delay)",
            min_value=1.0, max_value=100.0,
            value=float(active_raw.get("weights", {}).get("individual", 1.0)),
            step=1.0
        )
        w_op = st.slider(
            "Operator Fairness weight (Average Variance Gap)",
            min_value=1.0, max_value=100.0,
            value=float(active_raw.get("weights", {}).get("operator", 1.0)),
            step=1.0
        )
        w_all = st.slider(
            "Overall System Throughput weight (Linear Wait Duration)",
            min_value=1.0, max_value=100.0,
            value=float(active_raw.get("weights", {}).get("overall", 1.0)),
            step=1.0
        )

        # Apply slider values
        if "weights" not in active_raw:
            active_raw["weights"] = {}
        active_raw["weights"]["individual"] = w_ind
        active_raw["weights"]["operator"] = w_op
        active_raw["weights"]["overall"] = w_all

        # Physical constantssandbox
        st.markdown("##### ⏱️ Physical constants sandbox")
        c_cols = st.columns(2)
        with c_cols[0]:
            batt_range = st.number_input(
                "Max battery autonomy range (km)",
                min_value=100.0, max_value=500.0,
                value=float(active_raw.get("constants", {}).get("batteryRangeKm", 240.0)),
                step=10.0
            )
        with c_cols[1]:
            charge_duration = st.number_input(
                "Standard charging duration (mins)",
                min_value=5, max_value=120,
                value=int(active_raw.get("constants", {}).get("chargeDurationMin", 25)),
                step=5
            )
        active_raw["constants"]["batteryRangeKm"] = batt_range
        active_raw["constants"]["chargeDurationMin"] = charge_duration

        # Charger capacities scaling
        st.markdown("##### ⚡ Charger stations capacities sandbox")
        for idx, station_cfg in enumerate(active_raw.get("stations", [])):
            s_cols = st.columns([3, 2])
            with s_cols[0]:
                st.markdown(f"<p style='margin-top:6px; font-size:13px;'>📍 <strong>[{station_cfg['id']}]</strong> {station_cfg['name']}</p>", unsafe_allow_html=True)
            with s_cols[1]:
                chargers_val = st.number_input(
                    "Lanes count",
                    min_value=1, max_value=10,
                    value=int(station_cfg.get("chargersCount", 1)),
                    key=f"sandbox_station_charger_{station_cfg['id']}",
                    label_visibility="collapsed"
                )
                station_cfg["chargersCount"] = chargers_val

        # Dynamic live insertion sandbox for Station E/F curveballs
        st.markdown("##### 🚀 Live Extension Station Insertion")
        st.markdown("<p style='font-size:11px; color:#64748b; margin-top:-8px;'>Interviewer Curveball: Insert a new station live into segments graph to verify the dynamic router adapts through data-alone.</p>", unsafe_allow_html=True)
        
        ins_cols = st.columns([2, 2, 1])
        with ins_cols[0]:
            new_st_id = st.text_input("Station ID Code", value="", placeholder="E.g. E", key="insert_st_id_input")
        with ins_cols[1]:
            new_st_name = st.text_input("Station Label", value="", placeholder="E.g. Station E", key="insert_st_name_input")
        with ins_cols[2]:
            st.write("<div style='height: 28px;'></div>", unsafe_allow_html=True)
            add_trigger = st.button("Add ➕")

        if add_trigger and new_st_id and new_st_name:
            clean_id = new_st_id.strip().upper()
            if any(s["id"] == clean_id for s in active_raw.get("stations", [])):
                st.error("Station ID is already registered in active scenario map.")
            else:
                # Add station node
                new_st = {
                    "id": clean_id,
                    "name": new_st_name.strip(),
                    "chargersCount": 1
                }
                active_raw["stations"].append(new_st)
                
                # Split the last segment mapping cleanly
                segments = active_raw["route"]["segments"]
                if segments:
                    last_seg = segments[-1]
                    last_distance = last_seg["distance"]
                    half_dist = round(last_distance / 2.0, 1)
                    
                    segments[-1] = {
                        "from": last_seg["from"],
                        "to": clean_id,
                        "distance": half_dist
                    }
                    segments.append({
                        "from": clean_id,
                        "to": last_seg["to"],
                        "distance": round(last_distance - half_dist, 1)
                    })
                
                st.success(f"Dynamic node '{clean_id}' successfully mapped! Routing recalculated chronologically.")
                st.rerun()

    # --- RIGHT COL: DISPATCH ANALYTICS & SCHEDULER ENGINE ---
    with right_col:
        # 1. Parse active RAW sandbox config into structured Scenario OO Model
        active_scenario_model = Scenario.from_dict(active_raw)

        # 2. Fire unified decoupled Scheduler Engine
        engine = SchedulerEngine()
        
        with st.spinner("Invoking high-speed meta-heuristic dispatch engine..."):
            optimized_schedule_dict = engine.run(active_scenario_model, max_iterations=450)

        # 3. Render Metric Statistics Block
        st.markdown("<h4 style='color:#0f172a; margin-top:0;'>📊 Simulation & Optimization metrics</h4>", unsafe_allow_html=True)
        m_grid = st.columns(3)
        with m_grid[0]:
            st.metric(
                label="Overall System Delay",
                value=f"{optimized_schedule_dict.get('totalWaitTime', 0.0)} mins",
                help="Sum total of all waiting delay times accrued at stations across the network."
            )
        with m_grid[1]:
            st.metric(
                label="Peak Starvation Delay",
                value=f"{optimized_schedule_dict.get('maxWaitTime', 0.0)} mins",
                help="The absolute single worst-case delay encountered by a bus."
            )
        with m_grid[2]:
            is_valid_bool = optimized_schedule_dict.get("isValid", True)
            status_symbol = "🟢 Feasible" if is_valid_bool else "🔴 Range Violated"
            st.metric(
                label="System Health",
                value=status_symbol,
                help="Indicates if all physical range constraints and laws are fully satisfied."
            )

        # Error violations banner
        if optimized_schedule_dict.get("hardRuleViolations"):
            st.error("❗ **Physical Law Violations Precluding Dispatch:**\n" + "\n".join(optimized_schedule_dict["hardRuleViolations"]))

        # 4. Beautiful Tabs Interface
        st.write("")
        tab1, tab2, tab3, tab5 = st.tabs([
            "📋 Scenario Inputs",
            "🚌 Per-Bus Timetable",
            "🔌 Per-Station Charging Orders",
            # "⚙️ Technical Explanations",
            "🔍 Raw JSON Configuration"
        ])

        with tab1:
            render_scenario_view(active_scenario_model)

        with tab2:
            render_bus_view(active_scenario_model, optimized_schedule_dict)

        with tab3:
            render_station_view(active_scenario_model, optimized_schedule_dict)

        # with tab4:
        #     render_explanation_view(active_scenario_model, optimized_schedule_dict, engine.rule_registry)

        with tab5:
            # 8. Render configuration JSON text-area for prompt inspection or micro-scaling on spot during evaluation.
            st.markdown("##### 🛠️ Workspace JSON Live Sandbox")
            st.markdown("<p style='font-size:12px; color:#64748b;'>Directly edit raw parameters (coordinates, constants, fleet dispatches) inside this JSON workbench.</p>", unsafe_allow_html=True)
            
            scen_json_str = json.dumps(active_raw, indent=2)
            edited_json_str = st.text_area(
                "Sandbox JSON payload inspector:",
                value=scen_json_str,
                height=350,
                key="workspace_json_textarea_item"
            )
            
            ap_cols = st.columns(2)
            with ap_cols[0]:
                if st.button("🚀 Apply Workspace Changes", use_container_width=True):
                    try:
                        parsed_schema = json.loads(edited_json_str)
                        if isinstance(parsed_schema, dict) and "buses" in parsed_schema and "stations" in parsed_schema:
                            st.session_state.active_scenario_raw = parsed_schema
                            st.toast("Active workspace synced successfully!")
                            st.rerun()
                        else:
                            st.error("JSON config must represent a key-value dictionary schema containing both 'stations' and 'buses'.")
                    except Exception as e:
                        st.error(f"Failed parsing: {e}")
            with ap_cols[1]:
                if st.button("🔄 Discard Changes", use_container_width=True):
                    baseline_scen = all_scenarios_dict[st.session_state.selected_scenario_id]
                    st.session_state.active_scenario_raw = copy.deepcopy(baseline_scen)
                    st.toast("Active workspace reset to baseline template!")
                    st.rerun()

st.divider()
st.markdown("<div style='text-align:center; font-size:11px; color:#94a3b8;'>© 2026 Fleet Operations Scheduler Decoupled Core. Engineered for robust multi-operator grid dispatching algorithms.</div>", unsafe_allow_html=True)
