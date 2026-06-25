from . import Graph, PathStep, Zone, Connection
from typing import Dict, List, Optional


class Validator:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph

    def validate_paths_structure(self,
                                 all_paths: Dict[int, List[PathStep]]
                                 ) -> bool:
        if not all_paths:
            raise ValueError("No drone path to validate")

        for drone_id, path_steps in all_paths.items():
            if not path_steps:
                raise ValueError(f"Drone{drone_id} has empty path")

            first_step: PathStep = path_steps[0]
            if first_step.turn != 0:
                raise ValueError(f"Drone {drone_id} does not start at turn 0")

            if first_step.kind != 'zone':
                raise ValueError(f"Drone {drone_id} does not start in a zone")

            if first_step.name != self.graph.start_zone.name:
                raise ValueError(
                    f"Drone {drone_id} does not start at start zone")

            last_step: PathStep = path_steps[-1]
            if last_step.kind != 'zone':
                raise ValueError(f"Drone {drone_id} does not end in a zone")

            if last_step.name != self.graph.end_zone.name:
                raise ValueError(f"Drone {drone_id} does not end at end zone")

            previous_turn = -1
            for step in path_steps:
                if step.kind != 'zone' and step.kind != 'connection':
                    raise ValueError(f"Drone {drone_id} has invalid step kind")

                if step.turn <= previous_turn:
                    raise ValueError(
                        f"Drone {drone_id} turns are not strictly increasing")

                previous_turn = step.turn

        return True

    def validate_transitions(self,
                             all_paths: Dict[int, List[PathStep]]) -> bool:
        for drone_id, path_steps in all_paths.items():
            i = 0
            while i < len(path_steps) - 1:
                previous: PathStep = path_steps[i]
                current: PathStep = path_steps[i+1]

                if previous.kind != 'zone':
                    raise ValueError(f"Drone {drone_id} has invalid "
                                     "transition starting from non-zone")

                previous_zone: Optional[Zone] = self.graph.get_zone(
                    previous.name)
                if not previous_zone:
                    raise ValueError(f"{previous.name} does not exist")

                # WAIT & NORMAL
                if current.kind == 'zone':
                    current_zone: Optional[Zone] = self.graph.get_zone(
                        current.name)
                    if not current_zone:
                        raise ValueError(f"{current.name} does not exist")

                    # WAIT
                    if current_zone.name == previous_zone.name:
                        if current_zone.zone_type == 'blocked':
                            raise ValueError(f"{current_zone.name} is blocked")

                        i = i + 1
                        continue

                    if current_zone.zone_type == 'blocked':
                        raise ValueError(f"{current_zone.name} is blocked")

                    if current_zone.zone_type == 'restricted':
                        raise ValueError(
                            "Restricted zone entered without connection step")

                    connection: Connection | None = self.graph.get_connection(
                        previous_zone, current_zone)
                    if not connection:
                        raise ValueError(
                            "Illegal move: zones are not connected")

                    i = i + 1
                    continue

                # RESTRICTED
                if current.kind == 'connection':
                    if i + 2 >= len(path_steps):
                        raise ValueError(
                            "Connection step missing arrival zone")

                    arrival: PathStep = path_steps[i+2]
                    if arrival.kind != 'zone':
                        raise ValueError("Restricted zone must end in a zone")

                    arrival_zone: Optional[Zone] = self.graph.get_zone(
                        arrival.name)
                    if not arrival_zone:
                        raise ValueError(f"{arrival.name} does not exist")

                    if arrival_zone.zone_type != 'restricted':
                        raise ValueError(f"{arrival_zone.zone_type} must be"
                                         "a restricted zone")

                    connection = self.graph.get_connection(
                        previous_zone, arrival_zone)
                    if not connection:
                        raise ValueError(
                            "No connection for restricted movement")

                    if current.name != connection.key():
                        raise ValueError("Wrong connection step")

                    if current.turn != previous.turn + 1:
                        raise ValueError("Wrong connection turn")

                    if arrival.turn != previous.turn + 2:
                        raise ValueError("Wrong arrival turn")

                    i = i + 2
                    continue

                raise ValueError("Invalid step kind")

        return True

    def validate_capacities(self, all_paths: Dict[int, List[PathStep]]) -> bool:
        """
        Validates that all zone and connection capacities are respected
        at every turn according to the handover rule.
        """
        # Dictionaries: turn -> resource_name -> count
        zone_usage: Dict[int, Dict[str, int]] = {}
        conn_usage: Dict[int, Dict[str, int]] = {}

        # 1. Collect zone occupancy from zone steps
        #    (post‑move occupancy, i.e., after all moves of that turn)
        for drone_id, path_steps in all_paths.items():
            for step in path_steps:
                if step.kind == 'zone':
                    zone_name = step.name
                    turn = step.turn
                    if turn not in zone_usage:
                        zone_usage[turn] = {}
                    zone_usage[turn][zone_name] = zone_usage[turn].get(
                        zone_name, 0) + 1

        # 2. Collect connection usage from transitions
        for drone_id, path_steps in all_paths.items():
            i = 0
            while i < len(path_steps) - 1:
                current_step = path_steps[i]
                next_step = path_steps[i + 1]

                # Ensure current is a zone (should already be validated)
                if current_step.kind != 'zone':
                    raise ValueError(
                        f"Drone {drone_id} transition starts from non-zone")

                current_zone = self.graph.get_zone(current_step.name)
                if current_zone is None:
                    raise ValueError(f"Zone {current_step.name} not found")

                if next_step.kind == 'zone':
                    # Wait or normal move
                    next_zone = self.graph.get_zone(next_step.name)
                    if next_zone is None:
                        raise ValueError(f"Zone {next_step.name} not found")

                    if next_zone.name != current_zone.name:
                        # Normal move: connection used at arrival turn
                        conn = self.graph.get_connection(
                            current_zone, next_zone)
                        if conn is None:
                            raise ValueError(
                                f"No connection between {current_zone.name} and {next_zone.name}")
                        conn_key = conn.key()
                        usage_turn = next_step.turn
                        if usage_turn not in conn_usage:
                            conn_usage[usage_turn] = {}
                        conn_usage[usage_turn][conn_key] = conn_usage[usage_turn].get(
                            conn_key, 0) + 1
                    # Wait: no connection usage
                    i += 1

                elif next_step.kind == 'connection':
                    # Restricted move: connection used for two turns
                    if i + 2 >= len(path_steps):
                        raise ValueError(
                            f"Drone {drone_id} restricted move missing arrival zone")
                    arrival_step = path_steps[i + 2]
                    if arrival_step.kind != 'zone':
                        raise ValueError(
                            f"Drone {drone_id} restricted move must end with zone")

                    arrival_zone = self.graph.get_zone(arrival_step.name)
                    if arrival_zone is None:
                        raise ValueError(f"Zone {arrival_step.name} not found")
                    if arrival_zone.zone_type != 'restricted':
                        raise ValueError(
                            f"Arrival zone {arrival_zone.name} is not restricted")

                    conn = self.graph.get_connection(
                        current_zone, arrival_zone)
                    if conn is None:
                        raise ValueError(
                            f"No connection between {current_zone.name} and {arrival_zone.name}")
                    conn_key = conn.key()

                    # Connection used in the two turns following the start
                    conn_turn1 = current_step.turn + 1
                    conn_turn2 = current_step.turn + 2
                    for t in (conn_turn1, conn_turn2):
                        if t not in conn_usage:
                            conn_usage[t] = {}
                        conn_usage[t][conn_key] = conn_usage[t].get(
                            conn_key, 0) + 1

                    i += 2   # skip connection and arrival steps
                else:
                    raise ValueError(
                        f"Drone {drone_id} invalid step kind: {next_step.kind}")

        # 3. Validate zone capacities
        for turn, zones in zone_usage.items():
            for zone_name, count in zones.items():
                zone = self.graph.get_zone(zone_name)
                if zone is None:
                    raise ValueError(f"Zone {zone_name} not found")
                # Skip start and end zones (they have special capacity rules)
                if zone_name == self.graph.start_zone.name:
                    continue
                if zone_name == self.graph.end_zone.name:
                    continue
                if count > zone.max_drones:
                    raise ValueError(
                        f"Zone {zone_name} capacity exceeded at turn {turn}: "
                        f"{count} > {zone.max_drones}"
                    )

        # 4. Validate connection capacities
        for turn, conns in conn_usage.items():
            for conn_key, count in conns.items():
                # Reconstruct connection from key
                parts = conn_key.split('-')
                if len(parts) != 2:
                    raise ValueError(f"Invalid connection key: {conn_key}")
                zone_a = self.graph.get_zone(parts[0])
                zone_b = self.graph.get_zone(parts[1])
                if zone_a is None or zone_b is None:
                    raise ValueError(
                        f"Zone missing for connection key: {conn_key}")
                conn = self.graph.get_connection(zone_a, zone_b)
                if conn is None:
                    raise ValueError(f"Connection {conn_key} not found")
                if count > conn.max_link_capacity:
                    raise ValueError(
                        f"Connection {conn_key} capacity exceeded at turn {turn}: "
                        f"{count} > {conn.max_link_capacity}"
                    )

        return True

    def validate_all(self, all_paths: Dict[int, List[PathStep]]) -> bool:
        self.validate_paths_structure(all_paths)
        self.validate_transitions(all_paths)
        self.validate_capacities(all_paths)
        
        return True