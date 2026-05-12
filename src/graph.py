from typing import Dict, List, Tuple
from . import Connection, Zone
from collections import deque


class Graph:
    def __init__(
        self,
        zones: Dict[str, Zone],
        connections: List[Connection]
    ) -> None:
        self.zones: Dict[str, Zone] = zones
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

        return self.adjacency_list[zone_name]

    def get_zone(self, zone_name: str) -> Zone | None:
        return self.zones.get(zone_name)

    def get_connection(self, zone_a: Zone, zone_b: Zone) -> Connection | None:
        for connection in self.connections:
            if connection.zone1.name == zone_a.name and \
                    connection.zone2.name == zone_b.name or \
                    connection.zone2.name == zone_a.name and \
                    connection.zone1.name == zone_b.name:
                return connection

        return None

    def has_path(self, start: Zone, end: Zone) -> bool:
        if start.zone_type == 'blocked' or end.zone_type == 'blocked':
            return False

        visited: set[str] = set()

        queue: deque[str] = deque()
        queue.appendleft(start.name)

        while queue:
            current: str = queue.popleft()

            if current == end.name:
                return True

            if current in visited:
                continue

            visited.add(current)

            for neighbor, _ in self.get_neighbors(current):
                if neighbor.zone_type != 'blocked' and \
                        neighbor.name not in visited:
                    queue.append(neighbor.name)

        return False
