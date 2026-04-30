"""Graph data structures for the Fly-in drone routing simulation."""

from enum import Enum
from dataclasses import dataclass, field
from typing import Optional


class ZoneType(Enum):
    """Types of zones in the flight network."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    """Represents a hub/zone in the flight network."""

    name: str
    x: int
    y: int
    zone_type: ZoneType = field(default=ZoneType.NORMAL)
    color: str = field(default="none")
    max_drones: int = field(default=1)


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones."""

    zone_a: str
    zone_b: str
    max_link_capacity: int = field(default=1)


class Graph:
    """Flight network graph with adjacency list representation."""

    def __init__(self) -> None:
        """Initialise an empty graph."""
        self.zones: dict[str, Zone] = {}
        self.connections: dict[tuple[str, str], Connection] = {}
        self.adjacency: dict[str, list[str]] = {}
        self.start_zone: str = ""
        self.end_zone: str = ""

    def add_zone(self, zone: Zone) -> None:
        """Add a zone to the graph."""
        self.zones[zone.name] = zone
        if zone.name not in self.adjacency:
            self.adjacency[zone.name] = []

    def add_connection(self, conn: Connection) -> None:
        """Add a bidirectional connection between two zones."""
        key: tuple[str, str] = (conn.zone_a, conn.zone_b)
        self.connections[key] = conn
        self.adjacency[conn.zone_a].append(conn.zone_b)
        self.adjacency[conn.zone_b].append(conn.zone_a)

    def get_neighbors(self, name: str) -> list[str]:
        """Return list of neighbour zone names."""
        return self.adjacency.get(name, [])

    def get_connection(self, a: str, b: str) -> Optional[Connection]:
        """Return connection between zones a and b (bidirectional)."""
        if (a, b) in self.connections:
            return self.connections[(a, b)]
        if (b, a) in self.connections:
            return self.connections[(b, a)]
        return None

    def get_connection_key(
        self, a: str, b: str
    ) -> Optional[tuple[str, str]]:
        """Return canonical connection key for a-b or b-a."""
        if (a, b) in self.connections:
            return (a, b)
        if (b, a) in self.connections:
            return (b, a)
        return None

    def is_reachable(self, name: str) -> bool:
        """Check if zone exists and is not blocked."""
        zone = self.zones.get(name)
        if zone is None:
            return False
        return zone.zone_type != ZoneType.BLOCKED

    def reset_occupancy(self) -> None:
        """Placeholder for occupancy reset (managed by Simulator)."""
        pass
