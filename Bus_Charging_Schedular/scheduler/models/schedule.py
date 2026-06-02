# -*- coding: utf-8 -*-
"""
Schedule Model representing the final simulated results, queue timings, and validation rules telemetry.
"""

class Schedule:
    def __init__(self, scenario_id: str, weights: dict, bus_timelines: dict, station_timelines: dict,
                 total_wait_time: float = 0.0, max_wait_time: float = 0.0, is_valid: bool = True,
                 hard_rule_violations: list = None, soft_rule_penalties: dict = None):
        self.scenario_id = scenario_id
        self.weights = weights
        self.bus_timelines = bus_timelines
        self.station_timelines = station_timelines
        self.total_wait_time = total_wait_time
        self.max_wait_time = max_wait_time
        self.is_valid = is_valid
        self.hard_rule_violations = hard_rule_violations or []
        self.soft_rule_penalties = soft_rule_penalties or {"individual": 0.0, "operator": 0.0, "overall": 0.0}

    def to_dict(self) -> dict:
        return {
            "scenarioId": self.scenario_id,
            "weights": self.weights,
            "busTimelines": self.bus_timelines,
            "stationTimelines": self.station_timelines,
            "totalWaitTime": self.total_wait_time,
            "maxWaitTime": self.max_wait_time,
            "isValid": self.is_valid,
            "hardRuleViolations": self.hard_rule_violations,
            "softRulePenalties": self.soft_rule_penalties
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Schedule':
        return cls(
            scenario_id=data["scenarioId"],
            weights=data["weights"],
            bus_timelines=data["busTimelines"],
            station_timelines=data["stationTimelines"],
            total_wait_time=data.get("totalWaitTime", 0.0),
            max_wait_time=data.get("maxWaitTime", 0.0),
            is_valid=data.get("isValid", True),
            hard_rule_violations=data.get("hardRuleViolations", []),
            soft_rule_penalties=data.get("softRulePenalties", {"individual": 0.0, "operator": 0.0, "overall": 0.0})
        )
