# -*- coding: utf-8 -*-
"""
Station Model representing physical transit nodes on the path containing variable charger lanes.
"""

class Station:
    def __init__(self, id_str: str, name: str, chargers_count: int):
        self.id = id_str
        self.name = name
        self.chargers_count = chargers_count

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "chargersCount": self.chargers_count
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Station':
        return cls(
            id_str=data["id"],
            name=data["name"],
            chargers_count=int(data["chargersCount"])
        )
