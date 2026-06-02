# -*- coding: utf-8 -*-
"""
Bus Model representing electric buses and general domain time-conversions.
"""

class Bus:
    def __init__(self, id_str: str, operator: str, direction: str, departure_time_str: str):
        self.id = id_str
        self.operator = operator.lower()
        self.direction = direction
        self.departure_time_str = departure_time_str
        self.departure_time_min = self.time_str_to_minutes(departure_time_str)

    @staticmethod
    def time_str_to_minutes(time_str: str) -> int:
        """
        Converts time string HH:MM (relative to a 19:00 departure baseline) into minutes.
        Supports wrap-around within 24-hr boundaries.
        """
        hours, minutes = map(int, time_str.split(':'))
        total_min = hours * 60 + minutes
        start_min = 19 * 60 # Default 19:00 origin
        diff = total_min - start_min
        if diff < -12 * 60:
            diff += 24 * 60
        elif diff > 12 * 60:
            diff -= 24 * 60
        return diff

    @staticmethod
    def minutes_to_time_str(minutes: int) -> str:
        """
        Converts minutes from baseline 19:00 departure offset back into a clean HH:MM string.
        """
        total_min = 19 * 60 + minutes
        if total_min < 0:
            total_min += 24 * 60
        total_min = total_min % (24 * 60)
        hours = total_min // 60
        mins = total_min % 60
        return f"{hours:02d}:{mins:02d}"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "operator": self.operator,
            "direction": self.direction,
            "departureTimeStr": self.departure_time_str
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Bus':
        return cls(
            id_str=data["id"],
            operator=data["operator"],
            direction=data["direction"],
            departure_time_str=data["departureTimeStr"]
        )
