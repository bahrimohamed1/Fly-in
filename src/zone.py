from enum import Enum
from dataclasses import dataclass, field


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
