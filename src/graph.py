from typing import Dict, List, Tuple, Optional
from . import Connection, Zone
from collections import deque
import heapq


class Graph:
    def __init__(
        self,
        zones: Dict[str, Zone],
        connections: List[Connection],
        start_zone: Zone,
        end_zone: Zone
    ) -> None:
        self.zones: Dict[str, Zone] = zones
        self.connections: List[Connection] = connections
        self.adjacency_list: Dict[str, List[Tuple[Zone, Connection]]] = {}
        self.start_zone: Zone = start_zone
        self.end_zone: Zone = end_zone

        if start_zone.name not in zones or start_zone.zone_type == 'blocked':
            raise ValueError(f"ERROR: {start_zone.name} is invalid")

        if end_zone.name not in zones or end_zone.zone_type == 'blocked':
            raise ValueError(f"ERROR: {end_zone.name} is invalid")

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

    def get_zone(self, zone_name: str) -> Optional[Zone]:
        return self.zones.get(zone_name)

    def get_connection(self,
                       zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        for connection in self.connections:
            if connection.zone1.name == zone_a.name and \
                    connection.zone2.name == zone_b.name or \
                    connection.zone2.name == zone_a.name and \
                    connection.zone1.name == zone_b.name:
                return connection

        return None

    def has_path(self, start: Zone, end: Zone) -> bool:
        """BFS"""
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

    def get_distance(self, from_name: str, to_name: str) -> int | float:
        """
        Calculate the shortest path distance between two zones using Dijkstra.
        Returns the minimum number of turns to travel,
        from from_zone to to_zone.
        Returns float('inf') if no path exists.
        """
        if from_name == to_name:
            return 0

        from_zone = self.get_zone(from_name)
        to_zone = self.get_zone(to_name)

        if from_zone is None or to_zone is None:
            return float('inf')

        # Dijkstra's algorithm
        distances: Dict[str, int] = {from_name: 0}
        heap: List[Tuple[int, str]] = [(0, from_name)]
        visited: set[str] = set()

        while heap:
            current_dist, current_name = heapq.heappop(heap)

            if current_name in visited:
                continue

            visited.add(current_name)

            if current_name == to_name:
                return current_dist

            for neighbor_zone, _ in self.get_neighbors(current_name):
                if neighbor_zone.zone_type == 'blocked':
                    continue

                # Movement cost depends on destination zone type
                if neighbor_zone.zone_type == 'restricted':
                    move_cost = 2
                else:
                    move_cost = 1

                new_dist = current_dist + move_cost

                if new_dist < distances.get(neighbor_zone.name, float('inf')):
                    distances[neighbor_zone.name] = new_dist
                    heapq.heappush(heap, (new_dist, neighbor_zone.name))

        return float('inf')
