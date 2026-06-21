from . import PathFinder, ReservationTable, Graph, Zone, PathStep
from typing import Dict, List, Optional


class Scheduler:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph
        self.reservation_table: ReservationTable = ReservationTable(self.graph)
        self.pathfinder: PathFinder = PathFinder(
            self.graph, self.reservation_table)

    def schedule_drones(self,
                        nb_drones: int,
                        max_turns: int) -> Dict[int, List[PathStep]]:
        all_paths: Dict[int, List[PathStep]] = {}
        start_zone: Zone = self.graph.start_zone
        end_zone: Zone = self.graph.end_zone

        for drone_id in range(1, nb_drones+1):
            path: Optional[List[PathStep]] = self.pathfinder.find_path(
                start_zone, end_zone, max_turns)

            if not path:
                raise ValueError(f"ERROR: No path found for drone {drone_id}")

            self.reservation_table.reserve_path(path)

            all_paths[drone_id] = path

        return all_paths
