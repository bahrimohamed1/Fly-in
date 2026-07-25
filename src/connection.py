"""Connection module for the Fly-in Drones project.

This module defines the Connection class representing a bidirectional
edge between two zones in the drone network graph.
"""

from .zone import Zone
from typing import List, Any


class Connection:
    """Represents a static bidirectional connection between two zones.

    A Connection stores map data linking two zones with a capacity limit
    on how many drones can traverse it simultaneously.

    Attributes:
        zone1: The first zone connected by this edge.
        zone2: The second zone connected by this edge.
        max_link_capacity: Maximum number of drones that can traverse
            this connection simultaneously (default: 1).
    """

    def __init__(
        self,
        zone1: Zone,
        zone2: Zone,
        max_link_capacity: Any = 1,
    ) -> None:
        """Initialize a new bidirectional connection between two zones.

        Args:
            zone1: The first zone connected by this edge.
            zone2: The second zone connected by this edge.
            max_link_capacity: Maximum number of drones that can traverse
                this connection simultaneously. Defaults to 1.

        Raises:
            TypeError: If zone1 or zone2 is not a Zone instance.
        """
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_link_capacity

    def key(self) -> str:
        """Return a canonical unique identifier for this connection.

        The key is a sorted string of the two zone names separated by a hyphen.
        This ensures consistency regardless of which zone is zone1 or zone2.

        Returns:
            A string in the format "zoneA-zoneB"
            with names sorted alphabetically.
        """
        key: List[str] = sorted([self.zone1.name, self.zone2.name])
        return f"{key[0]}-{key[1]}"

    def connects(self, zone_a: Zone, zone_b: Zone) -> bool:
        """Check if this connection links the two given zones.

        Connections are bidirectional, so order of zones does not matter.

        Args:
            zone_a: First zone to check.
            zone_b: Second zone to check.

        Returns:
            True if this connection directly connects zone_a and zone_b,
            False otherwise.
        """
        return (
            (zone_a is self.zone1 and zone_b is self.zone2)
            or (zone_a is self.zone2 and zone_b is self.zone1)
        )

    def other_zone(self, zone: Zone) -> Zone:
        """Return the zone at the opposite end of this connection.

        Args:
            zone: One of the zones connected by this edge.

        Returns:
            The other zone connected by this edge.

        Raises:
            ValueError: If the given zone is not part of this connection.
        """
        if zone is self.zone1:
            return self.zone2
        if zone is self.zone2:
            return self.zone1
        raise ValueError(f"Zone '{zone.name}' is not part of this connection")

    def display_name(self) -> str:
        """Return a human-readable name for this connection.

        Returns:
            A string in the format "zone1-zone2" using the stored order.
        """
        return f"{self.zone1.name}-{self.zone2.name}"

    def __str__(self) -> str:
        """Return a string representation of the connection."""
        return (
            f"{self.zone1.name}-{self.zone2.name} "
            f"[max_link_capacity={self.max_link_capacity}]"
        )
