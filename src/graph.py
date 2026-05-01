from typing import Any, Dict, List, Tuple
from . import Connection, Zone


class Graph:
    def __init__(self, zones: Dict[str, Any],
                 connections: List[Connection]) -> None:
        self.zones: Dict[str, Any] = zones
        self.connections: List[Connection] = connections
        self.adjacency_list: Dict[str, List[Tuple[Zone, Connection]]] = {}
        self._build_adjacency_list()

    def _build_adjacency_list(self) -> None:
        for zone_name in self.zones:
            self.adjacency_list[zone_name] = []

        for connection in self.connections:
            zone1: Zone = connection.zone1
            zone2: Zone = connection.zone2

            self.adjacency_list[zone1.name].append((zone2, connection))
            self.adjacency_list[zone2.name].append((zone1, connection))

    def get_neighbors(self, zone_name: str) -> List[Tuple[Zone, Connection]]:
        if zone_name not in self.adjacency_list:
            raise KeyError(
                f"{zone_name} is not accessible in the adjacency list")

        return self.adjacency_list.get(zone_name)

    def get_zone(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Connection | None:
        for connection in self.connections:
            if connection.zone1 is zone_a and connection.zone2 is zone_b or \
                    connection.zone2 is zone_a and connection.zone1 is zone_b:
                return connection

        return None

    def get_distance(self, from_zone: Zone, to_zone: Zone) -> int:
        pass

    def has_path(self, start: Zone, end: Zone) -> bool:
        if start.zone_type == 'blocked' or end.zone_type == 'blocked':
            return False

        visited: List[Zone] = []

        queue: List[Zone] = []
        queue.append(start)

        while queue:
            current: Zone = queue.pop()

            if current is end:
                return True

            if current in visited:
                continue

            for neighbor, _ in self.get_neighbors(current.name):
                if neighbor.zone_type != 'blocked' and neighbor not in visited:
                    queue.append(current)

        return False
