# -*- coding: utf-8 -*-
"""
Base classes for the plugin-based Rules Framework.
"""

class HardRule:
    """
    Physical law or regulatory guideline. If broken, the entire schedule becomes INVALID.
    """
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    def evaluate(self, scenario, schedule_data: dict) -> tuple:
        """
        Evaluate the schedule against this hard rule.
        Returns:
            (is_valid: bool, violation_message_or_none: str)
        """
        raise NotImplementedError


class SoftRule:
    """
    Optimization objective. If deviated from, increases the penalty/cost score.
    """
    def __init__(self, name: str, description: str, category: str):
        self.name = name
        self.description = description
        self.category = category # MUST be "individual", "operator", or "overall"

    def evaluate(self, scenario, schedule_data: dict) -> float:
        """
        Evaluate penalty or cost score based on the current schedule statistics.
        Returns:
            penalty_score: float
        """
        raise NotImplementedError
