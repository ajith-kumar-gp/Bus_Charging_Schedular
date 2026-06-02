# -*- coding: utf-8 -*-
"""
Scenario Model containing all dynamic data variables parsed from JSON files.
"""
from scheduler.models.route import Route
from scheduler.models.station import Station
from scheduler.models.bus import Bus

class Scenario:
    def __init__(self, id_str: str, name: str, description: str, route: Route,
                 stations: list, operators: list, constants: dict, weights: dict, buses: list):
        self.id = id_str
        self.name = name
        self.description = description
        self.route = route
        self.stations = [
            Station.from_dict(st) if isinstance(st, dict) else st
            for st in stations
        ]
        self.operators = operators
        self.constants = {
            "batteryRangeKm": float(constants.get("batteryRangeKm", 240)),
            "chargeDurationMin": int(constants.get("chargeDurationMin", 25)),
            "speedKmph": float(constants.get("speedKmph", 60))
        }
        self.weights = {
            "individual": float(weights.get("individual", 1.0)),
            "operator": float(weights.get("operator", 1.0)),
            "overall": float(weights.get("overall", 1.0))
        }
        self.buses = [
            Bus.from_dict(b) if isinstance(b, dict) else b
            for b in buses
        ]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "route": self.route.to_dict(),
            "stations": [st.to_dict() for st in self.stations],
            "operators": self.operators,
            "constants": self.constants,
            "weights": self.weights,
            "buses": [b.to_dict() for b in self.buses]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Scenario':
        return cls(
            id_str=data["id"],
            name=data["name"],
            description=data["description"],
            route=Route.from_dict(data["route"]),
            stations=data["stations"],
            operators=data.get("operators", ["kpn", "freshbus", "flixbus"]),
            constants=data.get("constants", {"batteryRangeKm": 240, "chargeDurationMin": 25, "speedKmph": 60}),
            weights=data.get("weights", {"individual": 1.0, "operator": 1.0, "overall": 1.0}),
            buses=data["buses"]
        )
