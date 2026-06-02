# -*- coding: utf-8 -*-
"""
UI component rendering detailed architectural justifications and dynamic weights trade-off explanations.
"""
import streamlit as st
import pandas as pd

def render_explanation_view(scenario, schedule_dict: dict, rule_registry):
    """
    Renders Staff-level analytical comments explaining scheduler trade-offs, weight differences,
    and active database rule configurations.
    """
    st.markdown("### 🎓 Systems Design, Weights, & Trade-Offs Analyst")
    
    # 1. Weights Analysis Metrics
    w = scenario.weights
    w_ind = float(w.get("individual", 1.0))
    w_op = float(w.get("operator", 1.0))
    w_all = float(w.get("overall", 1.0))

    st.markdown("#### ⚖️ Dynamic Tuning Objectives Evaluation")
    
    # Render weights sliders information
    st.write(
        f"The current optimization run uses a custom weighted policy ratio: **Individual: {w_ind}** | **Operator: {w_op}** | **Overall: {w_all}**. "
        "Changing these weights guides the meta-heuristic search space to favor different trade-offs."
    )

    penalty_breakdown = schedule_dict.get("softRulePenalties", {})
    
    p_cols = st.columns(3)
    with p_cols[0]:
        st.metric(
            label="🤠 Individual Starvation",
            value=f"{penalty_breakdown.get('individual', 0.0):.1f} pts",
            delta="Worst-Case Minimized" if w_ind > w_all else "High Risk",
            help="Starvation penalty (sum of squares of waits). High weight enforces uniform individual bus wait times."
        )
    with p_cols[1]:
        st.metric(
            label="⚖️ Operator Variance",
            value=f"{penalty_breakdown.get('operator', 0.0):.1f} pts",
            delta="Fair Distribution" if w_op > w_ind else "Uneven Delays",
            help="Disparity between operators (KPN vs FlixBus vs Freshbus). High weight forces equal average delay."
        )
    with p_cols[2]:
        st.metric(
            label="📈 Total Network Penalty",
            value=f"{penalty_breakdown.get('overall', 0.0):.1f} pts",
            delta="Max Throughput" if w_all > w_ind else "Slower System",
            help="Linear aggregate of all travel and queue wait times. High weight minimizes overall transit times."
        )

    st.write("")
    
    # Detailed design analysis feedback
    st.markdown("#### 📡 Staff engineer's trade-Off assessment")
    
    # Read the active dominant weight and generate an engineered narrative
    longest_wait_id = ""
    longest_wait_val = -1
    for bus_id, tl in schedule_dict.get("busTimelines", {}).items():
        if tl.get("totalWaitTime", 0) > longest_wait_val:
            longest_wait_val = tl.get("totalWaitTime", 0)
            longest_wait_id = bus_id
            
    if w_ind >= max(w_op, w_all) * 2:
        analysis_text = (
            f"**Current Domination: Individual Starvation Prevention**\n"
            f"- **How it works:** The optimizer is penalizing individual bottlenecks using a quadratic starvation cost curve ($Wait^2$).\n"
            f"- **Result:** It spreads charging action sequences uniformly across multiple stations (e.g., electing Station A or Station D over congested points). "
            f"Worst case individual wait is kept highly controlled at **{longest_wait_val} mins** (encountered by *{longest_wait_id}*).\n"
            f"- **Trade-off:** Overall linear throughput might be slightly lower due to longer routes chosen."
        )
    elif w_op >= max(w_ind, w_all) * 2:
        analysis_text = (
            f"**Current Domination: Operator Fairness balancing**\n"
            f"- **How it works:** The scheduler actively analyzes disparity variances between KPN, Freshbus, and Flixbus averages.\n"
            f"- **Result:** If KPN gets heavily bunched at Station B, the scheduler pushes KPN to skip charging or shifts competing Flixbus schedules, "
            f"even if it increases individual bus delay, to maintain operator-level equality.\n"
            f"- **Trade-off:** Single buses might bear higher wait times to protect competitive parity shares."
        )
    elif w_all >= max(w_ind, w_op) * 2:
        analysis_text = (
            f"**Current Domination: Overall System Throughput Maximization**\n"
            f"- **How it works:** The optimizer aims to minimize the pure linear sum of absolute cumulative wait & travel times.\n"
            f"- **Result:** It packs the chargers compactly sequentially to ensure the fleet runs green and arrives fast.\n"
            f"- **Trade-off:** Extreme starvation check is muted. Single buses (like *{longest_wait_id}* with **{longest_wait_val} mins** wait) may get 'starved' "
            f"in deep queues to keep the other 19 buses traveling non-stop."
        )
    else:
        analysis_text = (
            f"**Current Domination: Balanced Compromise**\n"
            f"- **How it works:** Multi-objective evaluation checks all categories evenly.\n"
            f"- **Result:** Compromises between absolute system packing and starvation capping. "
            f"The worst wait is capped at **{longest_wait_val} mins**, operator disparity is minimized smoothly, and network speed remains robust."
        )

    st.info(analysis_text)

    # 3. Rules Engine Directory View
    st.write("")
    st.markdown("#### 🔌 Registered Plugin-Based Rules")
    st.markdown(
        "Our backend uses an extensible plugin-based rules registry. Adding a new rule "
        "requires simply inheriting from `HardRule` or `SoftRule` and registering it—zero scheduler/optimizer rewrites required."
    )

    h_rows = []
    for r in rule_registry.hard_rules:
        h_rows.append({"Rule Type": "⛔ PHYSICAL HARD LAW", "Name": r.name, "Scope / Constraint Checking Mode": r.description})
    for r in rule_registry.soft_rules:
        h_rows.append({"Rule Type": "🎯 SOFT OPTIMIZATION OBJECTIVE", "Name": r.name, "Scope / Constraint Checking Mode": r.description})
        
    st.dataframe(pd.DataFrame(h_rows), use_container_width=True, hide_index=True)
