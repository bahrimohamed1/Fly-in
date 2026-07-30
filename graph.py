"""Graph module for the Fly-in Drones project.

This module defines the Graph class representing the drone network topology,
including zones, connections, and pathfinding utilities.
"""

from connection import Connection
from zone import Zone

from typing import Dict, List, Tuple, Optional
from collections import deque
import heapq


class Graph:
    """Represents the static topology of the drone network.

    The Graph manages zones and connections, providing methods for
    neighborhood queries, path existence checks, and shortest path
    distance calculations.

    Attributes:
        zones: Dictionary mapping zone name to Zone object.
        connections: List of all connections in the graph.
        adjacency_list: Dictionary mapping zone name to list of
        (neighbor, connection) tuples.
        start_zone: The starting zone for all drones.
        end_zone: The target zone for all drones.
    """

    def __init__(
        self,
        zones: Dict[str, Zone],
        connections: List[Connection],
        start_zone: Zone,
        end_zone: Zone
    ) -> None:
        """Initialize the graph with zones, connections, and start/end zones.

        Args:
            zones: Dictionary mapping zone name to Zone object.
            connections: List of all connections in the graph.
            start_zone: The starting zone for all drones.
            end_zone: The target zone for all drones.

        Raises:
            ValueError: If start_zone or end_zone
            is not in zones or is blocked.
        """
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
        """Build the adjacency list from zones and connections.

        Creates a bidirectional mapping where each zone maps to a list of
        (neighbor_zone, connection) tuples. This provides O(1) access to
        all neighbors of any zone.

        Raises:
            KeyError: If a connection references a zone not in the graph.
        """
        for zone_name in self.zones:
            self.adjacency_list[zone_name] = []

        for connection in self.connections:
            zone1: Zone = connection.zone1
            zone2: Zone = connection.zone2

            self.adjacency_list[zone1.name].append((zone2, connection))
            self.adjacency_list[zone2.name].append((zone1, connection))

    def get_neighbors(self, zone_name: str) -> List[Tuple[Zone, Connection]]:
        """Get all neighboring zones and their connections.

        Args:
            zone_name: The name of the zone to query.

        Returns:
            A list of (neighbor_zone, connection) tuples.

        Raises:
            KeyError: If the zone_name is not in the adjacency list.
        """
        if zone_name not in self.adjacency_list:
            raise KeyError(
                f"{zone_name} is not accessible in the adjacency list")

        return self.adjacency_list[zone_name]

    def get_zone(self, zone_name: str) -> Optional[Zone]:
        """Retrieve a zone by its name.

        Args:
            zone_name: The name of the zone to retrieve.

        Returns:
            The Zone object if found, None otherwise.
        """
        return self.zones.get(zone_name)

    def get_connection(self,
                       zone_a: Zone, zone_b: Zone) -> Optional[Connection]:
        """Find the connection between two zones.

        Args:
            zone_a: First zone.
            zone_b: Second zone.

        Returns:
            The Connection object if one exists, None otherwise.
        """
        for connection in self.connections:
            if connection.zone1.name == zone_a.name and \
                    connection.zone2.name == zone_b.name or \
                    connection.zone2.name == zone_a.name and \
                    connection.zone1.name == zone_b.name:
                return connection

        return None

    def has_path(self, start: Zone, end: Zone) -> bool:
        """Check if a path exists between two zones using BFS.

        This method ignores movement costs and capacities, only checking
        topological connectivity through non-blocked zones.

        Args:
            start: The starting zone.
            end: The target zone.

        Returns:
            True if there is a valid path through non-blocked zones,
            False otherwise.
        """
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
        """Calculate the shortest path distance between two zones.

        Uses Dijkstra's algorithm with movement costs (1 for normal/priority
        zones, 2 for restricted zones). This ignores capacities and other
        drones, returning the theoretical minimum turn cost.

        Args:
            from_name: The name of the starting zone.
            to_name: The name of the target zone.

        Returns:
            The minimum number of turns required to travel from from_name to
            to_name, or float('inf') if no path exists.

        Examples:
            >>> graph.get_distance("start", "goal")
            23
            >>> graph.get_distance("start", "nonexistent")
            inf
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
