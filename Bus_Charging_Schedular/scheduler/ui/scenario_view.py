# -*- coding: utf-8 -*-
"""
UI component rendering the active scenario description, constants stats, and buses list.
"""
import streamlit as st
import pandas as pd

def render_scenario_view(scenario):
    """
    Renders the declarative dynamic specifications of the active scenario.
    """
    st.markdown(f"### 📋 {scenario.name}")
    st.markdown(f"*{scenario.description}*")
    st.write("")

    # Display key constants in a nice grid
    c_cols = st.columns(3)
    with c_cols[0]:
        st.metric(
            label="⚡ Max Battery Range",
            value=f"{scenario.constants['batteryRangeKm']} km",
            help="Maximum distance a bus can cover of cumulative segments without stopping to charge."
        )
    with c_cols[1]:
        st.metric(
            label="⏱️ Charge Duration",
            value=f"{scenario.constants['chargeDurationMin']} mins",
            help="Standard fast charging time slot duration."
        )
    with c_cols[2]:
        st.metric(
            label="🚀 Avg Transit Speed",
            value=f"{scenario.constants['speedKmph']} km/h",
            help="Locomotive speed of all buses in the fleet."
        )

    st.write("")
    
    # Grid: Path Segments and Stations List
    cols = st.columns([12, 12])
    with cols[0]:
        st.markdown("<p style='font-size:14px; font-weight:600; color:#334155; margin-bottom:8px;'>🗺️ Route Segments & Distance Map</p>", unsafe_allow_html=True)
        route_data = []
        for idx, seg in enumerate(scenario.route.segments):
            route_data.append({
                "Seq": idx + 1,
                "Origin Station": seg.from_node,
                "Destination Station": seg.to_node,
                "Segment Distance": f"{seg.distance} km"
            })
        st.dataframe(pd.DataFrame(route_data), use_container_width=True, hide_index=True)

    with cols[1]:
        st.markdown("<p style='font-size:14px; font-weight:600; color:#334155; margin-bottom:8px;'>🔋 Station Fast Charger Capacities</p>", unsafe_allow_html=True)
        station_data = []
        for st_obj in scenario.stations:
            station_data.append({
                "Station ID": st_obj.id,
                "Station Name": st_obj.name,
                "Available Chargers count": f"{st_obj.chargers_count} lane(s)"
            })
        st.dataframe(pd.DataFrame(station_data), use_container_width=True, hide_index=True)

    st.write("")
    
    # Collapsible Buses List Table
    with st.expander(f"🚌 Registered Buses List ({len(scenario.buses)} active schedules)"):
        bus_data = []
        for bus in scenario.buses:
            bus_data.append({
                "Bus ID": bus.id,
                "Fleet Operator": bus.operator.upper(),
                "Direction Pattern": bus.direction,
                "Initial Departure (19:00 baseline)": bus.departure_time_str
            })
        st.dataframe(pd.DataFrame(bus_data), use_container_width=True, hide_index=True)
