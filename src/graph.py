"""Graph data structure for the Fly-in drone routing simulation."""

from typing import Optional

from src.connection import Connection
from src.zone import Zone, ZoneType


class Graph:
    """Flight network graph with adjacency list representation.

    Stores zones (nodes) and connections (edges) and provides methods for
    navigating and querying the network.

    Attributes:
        zones:       Mapping of zone name → Zone object.
        connections: Mapping of (zone_a, zone_b) → Connection object.
        adjacency:   Mapping of zone name → list of neighbour names.
        start_zone:  Name of the designated start hub.
        end_zone:    Name of the designated end hub.
    """

    def __init__(self) -> None:
        """Initialise an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: dict[tuple[str, str], Connection] = {}
        self.adjacency: dict[str, list[str]] = {}
        self.start_zone: str = ""
        self.end_zone: str = ""

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph.

        Args:
            zone: The Zone to add.  The zone's name must be unique.
        """
        self.zones[zone.name] = zone
        if zone.name not in self.adjacency:
            self.adjacency[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """Add a bidirectional connection between two zones.

        Args:
            conn: The Connection to add.  Both zone endpoints must already
                  exist in the graph.
        """
        key: tuple[str, str] = (conn.zone_a, conn.zone_b)
        self.connections[key] = conn
        self.adjacency[conn.zone_a].append(conn.zone_b)
        self.adjacency[conn.zone_b].append(conn.zone_a)

    def get_neighbors(self, name: str) -> list[str]:
        """Return list of neighbour zone names for the given zone.

        Args:
            name: Name of the zone to query.

        Returns:
            List of zone names directly connected to *name*.
        """
        return self.adjacency.get(name, [])

    def get_connection(self, a: str, b: str) -> Optional[Connection]:
        """Return the connection between zones *a* and *b* (bidirectional).

        Args:
            a: First zone name.
            b: Second zone name.

        Returns:
            The Connection object if one exists, otherwise None.
        """
        if (a, b) in self.connections:
            return self.connections[(a, b)]
        if (b, a) in self.connections:
            return self.connections[(b, a)]
        return None

    def get_connection_key(
        self, a: str, b: str
    ) -> Optional[tuple[str, str]]:
        """Return the canonical connection key for an a–b or b–a edge.

        Args:
            a: First zone name.
            b: Second zone name.

        Returns:
            The stored tuple key if the connection exists, otherwise None.
        """
        if (a, b) in self.connections:
            return (a, b)
        if (b, a) in self.connections:
            return (b, a)
        return None

    def is_reachable(self, name: str) -> bool:
        """Check if a zone exists and is not blocked.

        Args:
            name: Name of the zone to check.

        Returns:
            True if the zone exists and its type is not BLOCKED.
        """
        zone = self.zones.get(name)
        if zone is None:
            return False
        return zone.zone_type != ZoneType.BLOCKED

    def reset_occupancy(self) -> None:
        """Placeholder for occupancy reset (managed by Simulator)."""
        pass
