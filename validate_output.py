#!/usr/bin/env python3
"""
Output Validator for Fly-in Drones Project

This script validates drone paths from the scheduler against all constraints:
- Movement rules (normal, restricted, wait)
- Zone capacities (max_drones)
- Connection capacities (max_link_capacity)
- Timing constraints (strictly increasing turns)
- Start/end zone rules
"""

import sys
from typing import Dict, List
from src import Parser, Graph, PathStep


class OutputValidator:
    """Validates drone paths against all constraints."""

    def __init__(self, graph: Graph):
        self.graph = graph
        self.errors: List[str] = []

    def validate_all(self, all_paths: Dict[int, List[PathStep]]) -> bool:
        """Run all validation checks."""
        self.errors = []
        self._validate_structure(all_paths)
        self._validate_transitions(all_paths)
        self._validate_capacities(all_paths)
        return len(self.errors) == 0

    def _add_error(self, msg: str) -> None:
        """Add an error message."""
        self.errors.append(f"❌ {msg}")
        print(f"  ❌ {msg}")

    def _validate_structure(self, all_paths: Dict[int, List[PathStep]]) -> None:
        """Validate path structure: start, end, turns, etc."""
        if not all_paths:
            self._add_error("No paths to validate")
            return

        for drone_id, path in all_paths.items():
            # Check path not empty
            if not path:
                self._add_error(f"Drone {drone_id} has empty path")
                continue

            # Check first step
            first = path[0]
            if first.turn != 0:
                self._add_error(f"Drone {drone_id} first turn is {first.turn}, expected 0")
            if first.kind != 'zone':
                self._add_error(f"Drone {drone_id} first step is not a zone (got {first.kind})")
            if first.name != self.graph.start_zone.name:
                self._add_error(f"Drone {drone_id} first zone is '{first.name}', expected '{self.graph.start_zone.name}'")

            # Check last step
            last = path[-1]
            if last.kind != 'zone':
                self._add_error(f"Drone {drone_id} last step is not a zone (got {last.kind})")
            if last.name != self.graph.end_zone.name:
                self._add_error(f"Drone {drone_id} last zone is '{last.name}', expected '{self.graph.end_zone.name}'")

            # Check strictly increasing turns
            prev_turn = -1
            for step in path:
                if step.turn <= prev_turn:
                    self._add_error(f"Drone {drone_id} has non-increasing turns: {prev_turn} -> {step.turn}")
                if step.kind not in ('zone', 'connection'):
                    self._add_error(f"Drone {drone_id} has invalid step kind: '{step.kind}'")
                prev_turn = step.turn

    def _validate_transitions(self, all_paths: Dict[int, List[PathStep]]) -> None:
        """Validate each transition (wait, normal move, restricted move)."""
        for drone_id, path in all_paths.items():
            i = 0
            while i < len(path) - 1:
                prev = path[i]
                curr = path[i + 1]

                # Previous step must be a zone
                if prev.kind != 'zone':
                    self._add_error(f"Drone {drone_id} transition starts from '{prev.kind}', expected 'zone'")
                    i += 1
                    continue

                prev_zone = self.graph.get_zone(prev.name)
                if prev_zone is None:
                    self._add_error(f"Drone {drone_id}: zone '{prev.name}' not found")
                    i += 1
                    continue

                # Case 1: Zone -> Zone (wait or normal move)
                if curr.kind == 'zone':
                    curr_zone = self.graph.get_zone(curr.name)
                    if curr_zone is None:
                        self._add_error(f"Drone {drone_id}: zone '{curr.name}' not found")
                        i += 1
                        continue

                    # Check timing
                    if curr.turn != prev.turn + 1:
                        self._add_error(f"Drone {drone_id}: zone->zone move should take 1 turn (got {curr.turn - prev.turn})")

                    # Wait (same zone)
                    if curr.name == prev.name:
                        if curr_zone.zone_type == 'blocked':
                            self._add_error(f"Drone {drone_id}: waiting on blocked zone '{curr.name}'")
                        i += 1
                        continue

                    # Normal move (different zone)
                    if curr_zone.zone_type == 'blocked':
                        self._add_error(f"Drone {drone_id}: move to blocked zone '{curr.name}'")
                    if curr_zone.zone_type == 'restricted':
                        self._add_error(f"Drone {drone_id}: restricted zone '{curr.name}' requires connection step")

                    # Check connection exists
                    conn = self.graph.get_connection(prev_zone, curr_zone)
                    if conn is None:
                        self._add_error(f"Drone {drone_id}: no connection between '{prev.name}' and '{curr.name}'")

                    i += 1
                    continue

                # Case 2: Zone -> Connection (restricted move)
                elif curr.kind == 'connection':
                    if i + 2 >= len(path):
                        self._add_error(f"Drone {drone_id}: connection step missing arrival zone")
                        i += 1
                        continue

                    arrival = path[i + 2]
                    if arrival.kind != 'zone':
                        self._add_error(f"Drone {drone_id}: restricted move must end in zone (got {arrival.kind})")
                        i += 1
                        continue

                    arrival_zone = self.graph.get_zone(arrival.name)
                    if arrival_zone is None:
                        self._add_error(f"Drone {drone_id}: arrival zone '{arrival.name}' not found")
                        i += 1
                        continue

                    # Check timing
                    if curr.turn != prev.turn + 1:
                        self._add_error(f"Drone {drone_id}: connection step turn should be {prev.turn+1}, got {curr.turn}")
                    if arrival.turn != prev.turn + 2:
                        self._add_error(f"Drone {drone_id}: arrival turn should be {prev.turn+2}, got {arrival.turn}")

                    # Check arrival zone is restricted
                    if arrival_zone.zone_type != 'restricted':
                        self._add_error(f"Drone {drone_id}: arrival zone '{arrival.name}' is not restricted")

                    # Check connection exists
                    conn = self.graph.get_connection(prev_zone, arrival_zone)
                    if conn is None:
                        self._add_error(f"Drone {drone_id}: no connection between '{prev.name}' and '{arrival.name}'")
                    else:
                        if curr.name != conn.key():
                            self._add_error(f"Drone {drone_id}: connection step '{curr.name}' does not match actual connection '{conn.key()}'")

                    i += 2
                    continue

                else:
                    self._add_error(f"Drone {drone_id}: invalid step kind '{curr.kind}'")
                    i += 1

    def _validate_capacities(self, all_paths: Dict[int, List[PathStep]]) -> None:
        """Validate zone and connection capacities."""
        # Build occupancy maps
        zone_occupancy: Dict[int, Dict[str, int]] = {}
        conn_occupancy: Dict[int, Dict[str, int]] = {}

        # Count zone occupancy
        for drone_id, path in all_paths.items():
            for step in path:
                if step.kind == 'zone':
                    zone_name = step.name
                    turn = step.turn
                    if turn not in zone_occupancy:
                        zone_occupancy[turn] = {}
                    zone_occupancy[turn][zone_name] = zone_occupancy[turn].get(zone_name, 0) + 1

        # Count connection occupancy
        for drone_id, path in all_paths.items():
            i = 0
            while i < len(path) - 1:
                prev = path[i]
                curr = path[i + 1]

                if prev.kind != 'zone':
                    i += 1
                    continue

                prev_zone = self.graph.get_zone(prev.name)
                if prev_zone is None:
                    i += 1
                    continue

                # Normal move: connection used at curr.turn
                if curr.kind == 'zone':
                    curr_zone = self.graph.get_zone(curr.name)
                    if curr_zone is not None and curr.name != prev.name:
                        conn = self.graph.get_connection(prev_zone, curr_zone)
                        if conn is not None:
                            turn = curr.turn
                            key = conn.key()
                            if turn not in conn_occupancy:
                                conn_occupancy[turn] = {}
                            conn_occupancy[turn][key] = conn_occupancy[turn].get(key, 0) + 1
                    i += 1

                # Restricted move: connection used at turn+1 and turn+2
                elif curr.kind == 'connection':
                    if i + 2 < len(path):
                        arrival = path[i + 2]
                        arrival_zone = self.graph.get_zone(arrival.name)
                        if arrival_zone is not None and prev_zone is not None:
                            conn = self.graph.get_connection(prev_zone, arrival_zone)
                            if conn is not None:
                                key = conn.key()
                                for t in (prev.turn + 1, prev.turn + 2):
                                    if t not in conn_occupancy:
                                        conn_occupancy[t] = {}
                                    conn_occupancy[t][key] = conn_occupancy[t].get(key, 0) + 1
                    i += 2

        # Check zone capacities
        for turn, zones in zone_occupancy.items():
            for zone_name, count in zones.items():
                # Skip start and end zones (special rules)
                if zone_name == self.graph.start_zone.name:
                    continue
                if zone_name == self.graph.end_zone.name:
                    continue

                zone = self.graph.get_zone(zone_name)
                if zone is None:
                    self._add_error(f"Zone '{zone_name}' not found at turn {turn}")
                    continue
                if count > zone.max_drones:
                    self._add_error(
                        f"Zone '{zone_name}' capacity exceeded at turn {turn}: "
                        f"{count} > {zone.max_drones}"
                    )

        # Check connection capacities
        for turn, conns in conn_occupancy.items():
            for key, count in conns.items():
                # Get connection from key
                parts = key.split('-')
                if len(parts) != 2:
                    self._add_error(f"Invalid connection key: {key}")
                    continue
                zone_a = self.graph.get_zone(parts[0])
                zone_b = self.graph.get_zone(parts[1])
                if zone_a is None or zone_b is None:
                    self._add_error(f"Zone missing for connection key: {key}")
                    continue
                conn = self.graph.get_connection(zone_a, zone_b)
                if conn is None:
                    self._add_error(f"Connection '{key}' not found")
                    continue
                if count > conn.max_link_capacity:
                    self._add_error(
                        f"Connection '{key}' capacity exceeded at turn {turn}: "
                        f"{count} > {conn.max_link_capacity}"
                    )

    def print_report(self) -> None:
        """Print validation report."""
        if self.errors:
            print(f"\n❌ Validation FAILED: {len(self.errors)} errors found")
            for error in self.errors:
                print(f"  {error}")
        else:
            print("\n✅ VALIDATION PASSED! All constraints respected.")

    def get_errors(self) -> List[str]:
        """Return list of error messages."""
        return self.errors


def main():
    """Main entry point for validation script."""
    if len(sys.argv) < 2:
        print("Usage: python validate_output.py <map_file>")
        sys.exit(1)

    map_file = sys.argv[1]

    print("=" * 60)
    print(f"VALIDATING MAP: {map_file}")
    print("=" * 60)

    # Parse map
    print("\n[1] Parsing map...")
    try:
        parser = Parser(map_file)
        graph = parser.parse()
        print(f"  ✅ Parsed: {len(graph.zones)} zones, {len(graph.connections)} connections")
    except Exception as e:
        print(f"  ❌ Parse error: {e}")
        sys.exit(1)

    # Run scheduler
    print("\n[2] Running scheduler...")
    from src import Scheduler
    scheduler = Scheduler(graph)
    try:
        all_paths = scheduler.schedule_drones(
            start_zone=graph.start_zone,
            end_zone=graph.end_zone,
            nb_drones=parser.nb_drones,
            max_turns=500
        )
        print(f"  ✅ Scheduled {len(all_paths)} drones")
    except Exception as e:
        print(f"  ❌ Scheduling error: {e}")
        sys.exit(1)

    # Validate
    print("\n[3] Validating paths...")
    validator = OutputValidator(graph)
    valid = validator.validate_all(all_paths)
    validator.print_report()

    # Summary
    if valid:
        max_turn = 0
        for path in all_paths.values():
            for step in path:
                if step.turn > max_turn:
                    max_turn = step.turn
        print(f"\n📊 Makespan: {max_turn} turns")
        print("✅ All constraints respected!")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()