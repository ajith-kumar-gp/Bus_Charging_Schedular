# -*- coding: utf-8 -*-
"""
Concrete implementations of SoftRule optimization objective weights.
Genuinely competing objectives:
1. Individual Objective: Minimize worst bus wait, prevent starvation.
2. Operator Objective: Balance delays across different operators.
3. Overall Objective: Maximize network throughput, minimize total network travel & wait time.
"""
from scheduler.rules.base import SoftRule
import math

class IndividualWaitRule(SoftRule):
    """
    Minimizes single worst-case starvation duration.
    Focuses on maximum wait time of any bus.
    Uses squared/exponential penalty on single large delays to enforce uniformity.
    """
    def __init__(self):
        super().__init__(
            name="IndividualWaitRule",
            description="Applies quadratic penalty on individual bus queue starvation to ensure no single bus waits too long.",
            category="individual"
        )

    def evaluate(self, scenario, schedule_data: dict) -> float:
        # Penalize maximum delay heavily, plus some exponential scaling of wait times
        wait_times = [tl.get("totalWaitTime", 0) for tl in schedule_data["busTimelines"].values()]
        if not wait_times:
            return 0.0
        
        max_wait = max(wait_times)
        # Sum of squares of wait times penalizes any single outliers heavily
        squared_sum = sum((w ** 2) for w in wait_times)
        
        # Combining maximum wait penalty and non-linear starvation curve
        return float(max_wait * 15.0 + squared_sum * 0.5)


class OperatorFairnessRule(SoftRule):
    """
    Balances delays across operators.
    Calculates the variance/disparity between average operator delays.
    If KPN is delayed much more than Freshbus, penalize heavily.
    """
    def __init__(self):
        super().__init__(
            name="OperatorFairnessRule",
            description="Penalizes disparity in delays across different fleet operators to prevent systemic bias.",
            category="operator"
        )

    def evaluate(self, scenario, schedule_data: dict) -> float:
        operator_delays = {}
        for op in scenario.operators:
            operator_delays[op.lower()] = []

        for tl in schedule_data["busTimelines"].values():
            op = tl.get("operator", "").lower()
            if op in operator_delays:
                operator_delays[op].append(tl.get("totalWaitTime", 0))

        # Calculate average wait per operator
        averages = []
        for op, delays in operator_delays.items():
            if delays:
                averages.append(sum(delays) / len(delays))
            else:
                averages.append(0.0)

        if len(averages) <= 1:
            return 0.0

        # Calculate standard deviation or absolute max difference of operator averages
        mean_avg = sum(averages) / len(averages)
        variance = sum((a - mean_avg) ** 2 for a in averages) / len(averages)
        max_diff = max(averages) - min(averages)

        # Multiplier to make it highly sensible during optimization
        return float(max_diff * 40.0 + variance * 4.0)


class OverallThroughputRule(SoftRule):
    """
    Maximizes network-wide throughput/efficiency.
    Simple linear penalization of cumulative system wait-times and travel times to favor raw dispatch count.
    """
    def __init__(self):
        super().__init__(
            name="OverallThroughputRule",
            description="Linear penalty on absolute cumulative travel and wait times to optimize overall system throughput.",
            category="overall"
        )

    def evaluate(self, scenario, schedule_data: dict) -> float:
        total_wait = sum(tl.get("totalWaitTime", 0) for tl in schedule_data["busTimelines"].values())
        total_duration = sum(tl.get("totalTravelTime", 0) for tl in schedule_data["busTimelines"].values() if not tl.get("isFailed", False))
        
        # Emphasizes linear total delay reduction across the complete network
        return float(total_wait * 5.0 + total_duration * 0.1)
