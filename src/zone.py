"""Zone data structures for the Fly-in drone routing simulation."""

from dataclasses import dataclass, field
from enum import Enum


class ZoneType(Enum):
    """Types of zones in the flight network."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


@dataclass
class Zone:
    """Represents a hub/zone in the flight network.

    Attributes:
        name:       Unique identifier for the zone (no dashes allowed).
        x:          X coordinate on the map grid.
        y:          Y coordinate on the map grid.
        zone_type:  The traversal behaviour of this zone.
        color:      Display colour name (used by the renderer).
        max_drones: Maximum number of drones that may occupy this zone
                    simultaneously.
    """

    name: str
    x: int
    y: int
    zone_type: ZoneType = field(default=ZoneType.NORMAL)
    color: str = field(default="none")
    max_drones: int = field(default=1)
