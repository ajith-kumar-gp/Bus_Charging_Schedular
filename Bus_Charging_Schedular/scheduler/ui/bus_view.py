# -*- coding: utf-8 -*-
"""
UI component rendering detailed per-bus timetables, arrival timelines, and battery health milestones.
"""
import streamlit as st
import pandas as pd
from scheduler.models.bus import Bus

def render_bus_view(scenario, schedule_dict: dict):
    """
    Renders per-bus travel diaries, charging events, and delays.
    """
    st.markdown("### 🚌 Bus Timeline Explorer")
    
    # 1. Broad metric summary of performance
    m_cols = st.columns(3)
    with m_cols[0]:
        st.metric(
            label="⏱️ Worst Bus Wait Time",
            value=f"{schedule_dict.get('maxWaitTime', 0.0)} mins",
            help="The absolute longest queue waiting delay endured by any individual bus in the fleet."
        )
    with m_cols[1]:
        st.metric(
            label="⚖️ Operator Delay Variance",
            value=f"{schedule_dict.get('totalWaitTime', 0.0) / len(scenario.buses):.1f} mins",
            help="System-wide average waiting delay per vehicle."
        )
    with m_cols[2]:
        validity_status = "✅ Feasible" if schedule_dict.get("isValid", True) else "❌ VIOLATION"
        st.metric(
            label="⚡ Safe Charging Margins",
            value=validity_status,
            help="Status check verifying whether any battery hit below zero."
        )

    st.write("")

    # 2. Filter / selector for looking up a specific bus's route diary
    buses_list = [b.id for b in scenario.buses]
    selected_bus_id = st.selectbox("🔍 Pick a Bus to view its complete journey path & charge logs:", buses_list)
    
    bus_timelines = schedule_dict.get("busTimelines", {})
    if selected_bus_id in bus_timelines:
        timeline = bus_timelines[selected_bus_id]
        
        st.markdown(f"#### 🛰️ Travel Record for **{selected_bus_id}** ({timeline['operator'].upper()})")
        st.markdown(f"**Direction:** {timeline['direction']} | **Departure Time:** {timeline['departureTimeStr']} | **Final Arrival:** `{timeline['arrivalTimeStr']}`")
        
        # Display key metrics
        stats_cols = st.columns(3)
        stats_cols[0].metric("Queue Wait Time", f"{timeline['totalWaitTime']} mins")
        stats_cols[1].metric("Total Travel Time", f"{timeline['totalTravelTime']} mins")
        
        # Render historical diary of stopped stations
        charges = timeline.get("charges", [])
        if not charges:
            st.info("⚡ This bus completed a non-stop transit! No charging stations were required.")
        else:
            st.markdown("##### 📝 Sequence of Stops & Queue Durations:")
            charge_data = []
            for idx, ch in enumerate(charges):
                charge_data.append({
                    "Stop #": idx + 1,
                    "Station Node": ch["stationId"],
                    "Segment Arrival": Bus.minutes_to_time_str(ch["arrivalTime"]),
                    "Charge Starred": Bus.minutes_to_time_str(ch["chargeStartTime"]),
                    "Charge Terminated": Bus.minutes_to_time_str(ch["chargeEndTime"]),
                    "Queue Wait Duration": f"{ch['waitTime']} min",
                    "Est. Battery Before": f"{ch['batteryBefore']} km",
                    "Est. Battery After": f"{ch['batteryAfter']} km"
                })
            st.dataframe(pd.DataFrame(charge_data), use_container_width=True, hide_index=True)

    st.write("")
    st.markdown("#### 📊 System-Wide Master Fleet Dispatch Schedule")
    
    # 3. Complete system-wide overview dataframe
    rows = []
    for b_id, tl in bus_timelines.items():
        rows.append({
            "Bus ID": b_id,
            "Operator": tl["operator"].upper(),
            "Departure": tl["departureTimeStr"],
            "Stops count": len(tl.get("charges", [])),
            "Stops list": " → ".join([c["stationId"] for c in tl.get("charges", [])]) if tl.get("charges") else "Direct",
            "Queue Delay": f"{tl['totalWaitTime']} mins",
            "Final Arrival": tl["arrivalTimeStr"],
            "Total Trip": f"{tl['totalTravelTime']} mins"
        })
        
    df_all = pd.DataFrame(rows).sort_values(by="Departure")
    st.dataframe(df_all, use_container_width=True, hide_index=True)
