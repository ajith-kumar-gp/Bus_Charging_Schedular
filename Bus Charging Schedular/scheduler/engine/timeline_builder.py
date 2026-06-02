# -*- coding: utf-8 -*-
"""
Helper module for extracting coordinate lists, milestone calculations, and valid combinations.
"""

def generate_valid_paths(scenario, direction: str) -> list:
    """
    Generates all mathematically valid station stop combinations (paths) a bus can choose.
    Ensures that the distances between consecutive stops (and starting origin/destination endpoints)
    never exceed the bus's maximum configured battery range.
    Fully data-driven using the dynamic mileage segments without any hardcoding.
    """
    route = scenario.route
    milestones = route.get_milestones(direction)
    max_range = scenario.constants["batteryRangeKm"]

    # Filter out start and end nodes to get just intermediate charging stations
    origin_name = milestones[0]['name']
    dest_name = milestones[-1]['name']
    stations_only = [m for m in milestones if m['name'] not in (origin_name, dest_name)]
    
    total_stations = len(stations_only)
    valid_paths = []

    # DFS / recursive generation of all possible paths (subsets of station stops)
    def search(idx: int, path: list):
        if idx == total_stations:
            # Validate complete path feasibility
            if validate_path_feasibility(path, milestones, max_range):
                valid_paths.append(list(path))
            return
        
        # Choice 1: Stop at this station to charge
        path.append(stations_only[idx]['name'])
        search(idx + 1, path)
        path.pop()

        # Choice 2: Skip this station
        search(idx + 1, path)

    search(0, [])
    # Sort paths by length so shorter paths are evaluated first
    valid_paths.sort(key=len)
    return valid_paths


def validate_path_feasibility(path: list, milestones: list, max_range: float) -> bool:
    """
    Verifies if a specific station subset sequence allows a bus to transit from 0.0 to destination
    without any segment between charges exceeding max_range.
    """
    # Build complete charging coordinates sequence
    coords = [0.0]
    for station_name in path:
        # Find milestone position
        m_item = next((m for m in milestones if m['name'] == station_name), None)
        if m_item is None:
            return False
        coords.append(m_item['positionKm'])
    coords.append(milestones[-1]['positionKm'])

    # Assert consecutives are within bounds
    for i in range(len(coords) - 1):
        segment_dist = coords[i+1] - coords[i]
        if segment_dist > max_range:
            return False
    return True
