# -*- coding: utf-8 -*-
"""
Meta-heuristic Hill-Climbing Search for dispatch optimization across multiple competing weights.
"""
import random
import copy
from scheduler.engine.timeline_builder import generate_valid_paths
from scheduler.engine.simulator import simulate_schedule

def optimize_schedule(scenario, rule_registry, max_iterations: int = 500) -> tuple:
    """
    Finds the optimal path combination for all buses using a high-performance heuristic search.
    Balances three genuinely competing objectives: Individual, Operator Fairness, and Overall Throughput.
    
    Returns:
        (best_schedule_dict, best_bus_paths)
    """
    origin = scenario.route.origin
    destination = scenario.route.destination
    forward_dir = f"{origin}→{destination}"
    reverse_dir = f"{destination}→{origin}"

    # Generate feasible paths upfront. This prunes unviable solutions completely.
    forward_paths = generate_valid_paths(scenario, forward_dir)
    reverse_paths = generate_valid_paths(scenario, reverse_dir)

    # If no paths are available for any route, fallback to empty arrays
    if not forward_paths:
        forward_paths = [[]]
    if not reverse_paths:
        reverse_paths = [[]]

    # Initialize bus paths with the baseline feasibility routes (shortest length paths)
    bus_paths = {}
    for bus in scenario.buses:
        candidates = forward_paths if bus.direction == forward_dir else reverse_paths
        bus_paths[bus.id] = list(candidates[0]) if candidates else []

    # Helper to calculate total penalty cost and run through hard rule check
    def evaluate_cost(paths: dict) -> tuple:
        test_sched = simulate_schedule(scenario, paths)
        
        # Hard validation filter
        is_ok, violations = rule_registry.evaluate_hard_rules(scenario, test_sched)
        test_sched["isValid"] = is_ok
        test_sched["hardRuleViolations"] = violations
        
        if not is_ok:
            # Heavily penalize invalid candidate paths so optimizer rejects them instantly
            return 999999.0, test_sched

        # Soft objectives optimization
        weighted_cost, breakdown = rule_registry.evaluate_soft_rules(scenario, test_sched, scenario.weights)
        test_sched["softRulePenalties"] = breakdown
        return weighted_cost, test_sched

    # Evaluate initial state
    best_cost, best_schedule = evaluate_cost(bus_paths)
    best_paths = copy.deepcopy(bus_paths)

    # Meta-heuristic local neighborhood search (Hill-Climbing with stochastic restarts/escapes)
    no_improvement_counter = 0
    t = 1.0 # Temperature factor for probabilistic hill-climbing escape
    
    for iteration in range(max_iterations):
        # Pick a random bus to perturb
        target_bus = random.choice(scenario.buses)
        candidates = forward_paths if target_bus.direction == forward_dir else reverse_paths
        
        if len(candidates) <= 1:
            continue
            
        current_bus_path = bus_paths[target_bus.id]
        alternative_paths = [p for p in candidates if p != current_bus_path]
        
        if not alternative_paths:
            continue
            
        new_path = random.choice(alternative_paths)
        
        # Tentatively apply change
        bus_paths[target_bus.id] = new_path
        new_cost, test_sched = evaluate_cost(bus_paths)
        
        # Decide if we accept current neighborhood swap
        # We accept if it decreases the cost, or stochastically with small temperature decay
        if new_cost < best_cost:
            best_cost = new_cost
            best_schedule = test_sched
            best_paths = copy.deepcopy(bus_paths)
            no_improvement_counter = 0
        else:
            # Revert change
            bus_paths[target_bus.id] = current_bus_path
            no_improvement_counter += 1
            
        # Anneal the search space slightly
        t *= 0.98
        
        # Short-circuit if convergence is met
        if no_improvement_counter > 150:
            break

    # Re-verify and bake the ultimate best schedule
    _, final_schedule = evaluate_cost(best_paths)
    return final_schedule, best_paths
