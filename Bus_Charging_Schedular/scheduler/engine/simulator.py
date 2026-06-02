# -*- coding: utf-8 -*-
"""
Discrete Event Simulator for electric buses and fast charger queue allocation.
"""
from scheduler.models.bus import Bus

def simulate_schedule(scenario, bus_paths: dict) -> dict:
    """
    Evaluates the complete fleet schedule based on fixed station choices (bus_paths).
    Implements a robust Discrete Event Simulation of transit journeys and queuing.
    
    Returns a unified schedule payload structure dictionary.
    """
    speed = scenario.constants["speedKmph"]
    charge_duration = scenario.constants["chargeDurationMin"]
    max_range = scenario.constants["batteryRangeKm"]
    route = scenario.route

    # Prepare station index mappings for quick lookup
    stations_by_id = {st.id: st for st in scenario.stations}
    
    # For each station, we maintain list of channels/lanes: [lane_0_bookings, lane_1_bookings, ...]
    # where each booking is a dict: {'startTime': s, 'endTime': e, 'busId': id, 'lane': l}
    station_lanes = {st.id: [[] for _ in range(st.chargers_count)] for st in scenario.stations}

    # Output records
    bus_timelines = {}
    
    # 1. Gather all buses and sort their initial departures chronologically.
    # To handle ties deterministically: prioritize VIPs, then departureTime to provide perfect scheduling keys.
    sorted_buses = sorted(
        scenario.buses,
        key=lambda b: (
            b.departure_time_min,
            0 if b.id.endswith("-01") or b.id.endswith("-02") else 1,
            b.id
        )
    )

    # 2. Simulate each bus's journey in priority sequencing order.
    # Note: Because queue allocations at stations depend on previously simulated vehicles,
    # prioritizing based on initial departures / VIP rank establishes a defensible dispatch policy.
    for bus in sorted_buses:
        path = bus_paths.get(bus.id, [])
        direction = bus.direction
        milestones = route.get_milestones(direction)
        
        timeline_events = []
        charges_record = []
        
        current_time = bus.departure_time_min
        current_battery = max_range
        current_position = 0.0
        
        total_wait_time = 0
        is_failed = False
        failure_reason = ""
        
        # Traverse milestones one by one
        for i in range(len(milestones) - 1):
            curr_m = milestones[i]
            next_m = milestones[i + 1]
            segment_distance = next_m['positionKm'] - curr_m['positionKm']
            
            # Check if battery can cover the next segment
            if current_battery < segment_distance:
                is_failed = True
                failure_reason = f"Ran out of charge traveling from {curr_m['name']} to {next_m['name']} ({current_battery:.1f} km left, need {segment_distance:.1f} km)."
                break
                
            # Travel to next milestone
            travel_time = int(round((segment_distance / speed) * 60.0))
            current_time += travel_time
            current_battery -= segment_distance
            current_position = next_m['positionKm']
            
            # Arrived at next node. If it's a planned stop, charge it!
            station_id = next_m['name']
            if station_id in path:
                # Find available charging slot
                station = stations_by_id.get(station_id)
                if not station:
                    is_failed = True
                    failure_reason = f"Unknown station reference {station_id}"
                    break
                
                # We find the best lane that yields the earliest starting charge time >= current_time
                best_start = None
                best_lane_idx = None
                
                for lane_idx, lane_slots in enumerate(station_lanes[station_id]):
                    sorted_slots = sorted(lane_slots, key=lambda s: s['startTime'])
                    
                    t = current_time
                    for slot in sorted_slots:
                        s_time = slot['startTime']
                        e_time = slot['endTime']
                        if t + charge_duration <= s_time:
                            break
                        if t < e_time and t + charge_duration > s_time:
                            t = max(t, e_time)
                    
                    if best_start is None or t < best_start:
                        best_start = t
                        best_lane_idx = lane_idx
                
                charge_start = best_start
                charge_end = charge_start + charge_duration
                wait = charge_start - current_time
                
                station_lanes[station_id][best_lane_idx].append({
                    "busId": bus.id,
                    "startTime": charge_start,
                    "endTime": charge_end,
                    "lane": best_lane_idx
                })
                
                # Record charge stats for bus
                charges_record.append({
                    "stationId": station_id,
                    "arrivalTime": current_time,
                    "chargeStartTime": charge_start,
                    "chargeEndTime": charge_end,
                    "waitTime": wait,
                    "batteryBefore": float(f"{current_battery:.1f}"),
                    "batteryAfter": float(f"{max_range:.1f}")
                })
                
                total_wait_time += wait
                # Battery goes back to full
                current_battery = max_range
                # Time advances to when charging completes
                current_time = charge_end

        arr_time_min = current_time if not is_failed else 0
        total_travel_time = arr_time_min - bus.departure_time_min if not is_failed else -1
        
        # Save complete timeline metrics
        bus_timelines[bus.id] = {
            "busId": bus.id,
            "operator": bus.operator,
            "direction": direction,
            "departureTimeMin": bus.departure_time_min,
            "departureTimeStr": bus.departure_time_str,
            "charges": charges_record,
            "arrivalTimeMin": arr_time_min,
            "arrivalTimeStr": Bus.minutes_to_time_str(arr_time_min) if not is_failed else "FAILED",
            "totalWaitTime": total_wait_time,
            "totalTravelTime": total_travel_time,
            "isComplete": not is_failed,
            "isFailed": is_failed,
            "failureReason": failure_reason
        }

    # Reconstruct station_busy_slots by flattening lanes
    station_busy_slots = {}
    for st_id, lanes in station_lanes.items():
        flattened = []
        for lane in lanes:
            flattened.extend(lane)
        station_busy_slots[st_id] = flattened

    # Prep station schedules in format for the UI renderer
    station_timelines_out = {}
    for st_id, busy_list in station_busy_slots.items():
        # Sort sequentially
        sorted_slots = sorted(busy_list, key=lambda x: x['startTime'])
        for idx, item in enumerate(sorted_slots):
            item["sequence"] = idx + 1
        
        station_timelines_out[st_id] = {
            "stationId": st_id,
            "busySlots": sorted_slots
        }

    # Aggregate key fleet cost stats
    completed_waits = [tl["totalWaitTime"] for tl in bus_timelines.values() if not tl["isFailed"]]
    overall_total_wait = sum(completed_waits)
    overall_max_wait = max(completed_waits) if completed_waits else 0.0

    return {
        "scenarioId": scenario.id,
        "weights": scenario.weights,
        "busTimelines": bus_timelines,
        "stationTimelines": station_timelines_out,
        "totalWaitTime": overall_total_wait,
        "maxWaitTime": overall_max_wait,
        "isValid": not any(tl["isFailed"] for tl in bus_timelines.values()),
        "hardRuleViolations": [],
        "softRulePenalties": {}
    }
