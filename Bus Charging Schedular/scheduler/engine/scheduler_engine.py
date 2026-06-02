# -*- coding: utf-8 -*-
"""
Main unified API gateway for parsing scenarios, registering rules, and executing optimizations.
"""
from scheduler.rules.registry import RuleRegistry
from scheduler.engine.optimizer import optimize_schedule

class SchedulerEngine:
    def __init__(self):
        self.rule_registry = RuleRegistry()

    def run(self, scenario, max_iterations: int = 400) -> dict:
        """
        Runs the optimizer engine against a given Scenario instance using the live environment weights.
        Returns a rich analytics result dictionary.
        """
        schedule_dict, best_paths = optimize_schedule(
            scenario=scenario,
            rule_registry=self.rule_registry,
            max_iterations=max_iterations
        )
        
        # Attach the best chosen paths per bus for visual reference
        schedule_dict["busSelectedPaths"] = best_paths
        return schedule_dict

    def register_custom_hard_rule(self, rule_instance):
        self.rule_registry.register_hard_rule(rule_instance)

    def register_custom_soft_rule(self, rule_instance):
        self.rule_registry.register_soft_rule(rule_instance)
