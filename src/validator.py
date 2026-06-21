from . import Graph, PathStep
from typing import Dict, List


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