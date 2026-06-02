# -*- coding: utf-8 -*-
"""
Decoupled rules registry enabling easy runtime class loading and plugin additions.
"""
from scheduler.rules.hard_rules import RangeRule, ChargerCapacityRule, RouteOrderRule, ChargeDurationRule
from scheduler.rules.soft_rules import IndividualWaitRule, OperatorFairnessRule, OverallThroughputRule

class RuleRegistry:
    def __init__(self):
        self.hard_rules = []
        self.soft_rules = []
        self.reset_to_defaults()

    def reset_to_defaults(self):
        """
        Initializes the default suite of physical hard laws and tunable business soft policies.
        """
        self.hard_rules = [
            RangeRule(),
            ChargerCapacityRule(),
            RouteOrderRule(),
            ChargeDurationRule()
        ]
        self.soft_rules = [
            IndividualWaitRule(),
            OperatorFairnessRule(),
            OverallThroughputRule()
        ]

    def register_hard_rule(self, rule_instance):
        """
        Dynamically registers a custom physical law.
        """
        self.hard_rules.append(rule_instance)

    def register_soft_rule(self, rule_instance):
        """
        Dynamically registers a custom soft business objective.
        """
        self.soft_rules.append(rule_instance)

    def evaluate_hard_rules(self, scenario, schedule_dict: dict) -> tuple:
        """
        Validates a completed timeline dictionary configuration against all laws.
        Returns (is_valid: bool, violations: list[str])
        """
        is_valid = True
        violations = []
        for rule in self.hard_rules:
            ok, msg = rule.evaluate(scenario, schedule_dict)
            if not ok:
                is_valid = False
                violations.append(f"[{rule.name}] {msg}")
        return is_valid, violations

    def evaluate_soft_rules(self, scenario, schedule_dict: dict, weights: dict) -> tuple:
        """
        Calculates penalty costs weighted by specific objective modifiers.
        Returns (total_weighted_cost: float, breakdown_dict: dict)
        """
        w_ind = float(weights.get("individual", 1.0))
        w_op = float(weights.get("operator", 1.0))
        w_all = float(weights.get("overall", 1.0))

        scores = {
            "individual": 0.0,
            "operator": 0.0,
            "overall": 0.0
        }

        for rule in self.soft_rules:
            score = rule.evaluate(scenario, schedule_dict)
            if rule.category in scores:
                scores[rule.category] += score

        weighted_cost = (
            w_ind * scores["individual"] +
            w_op * scores["operator"] +
            w_all * scores["overall"]
        )

        breakdown = {
            "individual": scores["individual"],
            "operator": scores["operator"],
            "overall": scores["overall"],
            "individualWeighted": w_ind * scores["individual"],
            "operatorWeighted": w_op * scores["operator"],
            "overallWeighted": w_all * scores["overall"],
        }

        return weighted_cost, breakdown
