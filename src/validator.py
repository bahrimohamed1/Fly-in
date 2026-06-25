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
