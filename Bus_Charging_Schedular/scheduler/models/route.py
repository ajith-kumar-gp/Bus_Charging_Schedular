# -*- coding: utf-8 -*-
"""
Route Segment and Main Route Models. Handles calculating cumulative miles/kilometers dynamically.
"""

class RouteSegment:
    def __init__(self, from_node: str, to_node: str, distance: float):
        self.from_node = from_node
        self.to_node = to_node
        self.distance = distance

    def to_dict(self) -> dict:
        return {
            "from": self.from_node,
            "to": self.to_node,
            "distance": self.distance
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'RouteSegment':
        return cls(
            from_node=data["from"],
            to_node=data["to"],
            distance=float(data["distance"])
        )


class Route:
    def __init__(self, name: str, origin: str, destination: str, segments: list):
        self.name = name
        self.origin = origin
        self.destination = destination
        self.segments = [
            RouteSegment.from_dict(seg) if isinstance(seg, dict) else seg
            for seg in segments
        ]

    def get_milestones(self, direction: str) -> list:
        """
        Calculates cumulative milestone positions (in km) from start origin depending on travel direction,
        fully data-driven without hardcoding 'Bengaluru' or 'Kochi' in segment routing logic.
        """
        is_forward = direction.startswith(self.origin)
        
        milestones = []
        if is_forward:
            milestones.append({'name': self.origin, 'positionKm': 0.0})
            cumulative = 0.0
            for segment in self.segments:
                cumulative += segment.distance
                milestones.append({'name': segment.to_node, 'positionKm': cumulative})
        else:
            milestones.append({'name': self.destination, 'positionKm': 0.0})
            cumulative = 0.0
            reversed_segments = list(reversed(self.segments))
            for segment in reversed_segments:
                cumulative += segment.distance
                milestones.append({'name': segment.from_node, 'positionKm': cumulative})
                
        return milestones

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "origin": self.origin,
            "destination": self.destination,
            "segments": [seg.to_dict() for seg in self.segments]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Route':
        return cls(
            name=data["name"],
            origin=data["origin"],
            destination=data["destination"],
            segments=data["segments"]
        )
