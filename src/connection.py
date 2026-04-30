"""Connection data structure for the Fly-in drone routing simulation."""

from dataclasses import dataclass, field


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones.

    Attributes:
        zone_a:           Name of the first zone endpoint.
        zone_b:           Name of the second zone endpoint.
        max_link_capacity: Maximum number of drones that may use this
                           connection in a single turn.
    """

    zone_a: str
    zone_b: str
    max_link_capacity: int = field(default=1)
