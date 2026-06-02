# -*- coding: utf-8 -*-
"""
Concrete implementations of HardRule physical constraints.
"""
from scheduler.rules.base import HardRule

class RangeRule(HardRule):
    """
    Ensures that no bus ever runs out of battery range in transit.
    """
    def __init__(self):
        super().__init__(
            name="RangeRule",
            description="Verify that no bus drops to 0 km remaining battery range between charging stops."
        )

    def evaluate(self, scenario, schedule_data: dict) -> tuple:
        for bus_id, timeline in schedule_data["busTimelines"].items():
            if timeline.get("isFailed", False):
                reason = timeline.get("failureReason", "Unspecified battery failure.")
                return False, f"Bus {bus_id} violated RangeRule: {reason}"
        return True, ""


class ChargerCapacityRule(HardRule):
    """
    Ensures that the number of concurrent charging buses does not exceed charger capacities.
    """
    def __init__(self):
        super().__init__(
            name="ChargerCapacityRule",
            description="Checks that no station hosts more charging buses than its physically available chargers count."
        )

    def evaluate(self, scenario, schedule_data: dict) -> tuple:
        stations = scenario.stations
        station_timelines = schedule_data["stationTimelines"]

        for station in stations:
            timeline = station_timelines.get(station.id)
            if not timeline:
                continue
            
            usage_map = {}
            for slot in timeline.get("busySlots", []):
                for minute in range(slot['startTime'], slot['endTime']):
                    usage_map[minute] = usage_map.get(minute, 0) + 1
            
            for minute, count in usage_map.items():
                if count > station.chargers_count:
                    return False, (
                        f"Station {station.name} exceeded physical charger capacity at minute {minute}: "
                        f"{count} buses charging with only {station.chargers_count} chargers."
                    )
        return True, ""


class RouteOrderRule(HardRule):
    """
    Ensures that a bus visits stations strictly in sequence without backtracking or skipping order.
    """
    def __init__(self):
        super().__init__(
            name="RouteOrderRule",
            description="Asserts that travel paths align with physical coordinates and do not contain backtracks."
        )

    def evaluate(self, scenario, schedule_data: dict) -> tuple:
        stations_order = [s.id for s in scenario.stations]
        origin = scenario.route.origin
        destination = scenario.route.destination
        forward_dir = f"{origin}→{destination}"

        for bus_id, timeline in schedule_data["busTimelines"].items():
            # Extract path from charges
            path = [ch["stationId"] for ch in timeline.get("charges", [])]
            direction = timeline["direction"]

            if direction == forward_dir:
                last_idx = -1
                for station_id in path:
                    idx = stations_order.index(station_id) if station_id in stations_order else -1
                    if idx <= last_idx:
                        return False, (
                            f"Bus {bus_id} violated RouteOrderRule: "
                            f"backtracked or skipped sequentially (stopped at {station_id} after station index {last_idx})"
                        )
                    last_idx = idx
            else:
                # Reverse route
                last_idx = len(stations_order)
                for station_id in path:
                    idx = stations_order.index(station_id) if station_id in stations_order else -1
                    if idx >= last_idx:
                        return False, (
                            f"Bus {bus_id} violated RouteOrderRule: "
                            f"backtracked or skipped sequentially in reverse direction (stopped at {station_id} after reversed index {last_idx})"
                        )
                    last_idx = idx

        return True, ""


class ChargeDurationRule(HardRule):
    """
    Ensures that every charge event lasts exactly the scenario's standard charging duration.
    """
    def __init__(self):
        super().__init__(
            name="ChargeDurationRule",
            description="Confirms that all charge sessions complete to full and take exactly the scheduled baseline duration count."
        )

    def evaluate(self, scenario, schedule_data: dict) -> tuple:
        req_duration = scenario.constants["chargeDurationMin"]
        for bus_id, timeline in schedule_data["busTimelines"].items():
            for charge in timeline.get("charges", []):
                duration = charge["chargeEndTime"] - charge["chargeStartTime"]
                if duration != req_duration:
                    return False, (
                        f"Bus {bus_id} violated ChargeDurationRule: "
                        f"charged for {duration} mins instead of required {req_duration} mins at {charge['stationId']}."
                    )
        return True, ""
