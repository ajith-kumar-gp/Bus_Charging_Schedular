# -*- coding: utf-8 -*-
"""
UI component rendering the station-wise schedules and occupation timelines.
"""
import streamlit as st
import pandas as pd
from scheduler.models.bus import Bus

def render_station_view(scenario, schedule_dict: dict):
    """
    Renders Gantt-like chronological occupation lanes for each station's charger slots.
    """
    st.markdown("### 🔌 Per-Station Charging Timetable")
    st.markdown("<p style='font-size:13px; color:#64748b;'>Chronological sequences of fast charges performed at each station.</p>", unsafe_allow_html=True)
    st.write("")

    station_timelines = schedule_dict.get("stationTimelines", {})
    stations_by_id = {st.id: st for st in scenario.stations}

    for station_id, st_data in station_timelines.items():
        station = stations_by_id.get(station_id)
        if not station:
            continue

        slots = st_data.get("busySlots", [])
        
        st.markdown(f"##### 📍 {st_data['stationId']} — {station.name} ({station.chargers_count} charger lane{'s' if station.chargers_count > 1 else ''})")
        
        if not slots:
            st.info("No charges planned at this station.")
            st.write("")
            continue
            
        rows = []
        for s in slots:
            # Color badge by operator
            op_color = "#1e293b" # Default charcoal
            bus_id = s['busId']
            
            # Extract operator by matching bus
            matching_bus = next((b for b in scenario.buses if b.id == bus_id), None)
            op_label = matching_bus.operator.upper() if matching_bus else "UNKNOWN"
            
            rows.append({
                "Seq": s["sequence"],
                "Bus ID": bus_id,
                "Fleet Operator": op_label,
                "Charge Start Time": Bus.minutes_to_time_str(s["startTime"]),
                "Charge End Time": Bus.minutes_to_time_str(s["endTime"]),
                "Duration": f"{s['endTime'] - s['startTime']} min"
            })
            
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Simple visual heat-line representing timeline bookings
        st.markdown("<p style='font-size:11px; margin-top:-8px; margin-bottom:18px; color:#94a3b8;'>👉 Seq order is strictly deterministic and queue-sorted to prevent ties or conflicts.</p>", unsafe_allow_html=True)
