from .zone import Zone


class Connection:
    """Represents a static bidirectional connection between two zones.

    A Connection stores map data:
    - zone1
    - zone2
    - max_link_capacity

    """

    def __init__(
        self,
        zone1: Zone,
        zone2: Zone,
        max_link_capacity: int = 1,
    ) -> None:
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_link_capacity

    def key(self) -> tuple[str, str]:
        """Return a normalized key for duplicate detection."""
        return tuple(sorted((self.zone1.name, self.zone2.name)))

    def connects(self, zone_a: Zone, zone_b: Zone) -> bool:
        """Return True if this connection links zone_a and zone_b.

        Connections are bidirectional.
        """
        return (
            (zone_a is self.zone1 and zone_b is self.zone2)
            or (zone_a is self.zone2 and zone_b is self.zone1)
        )

    def other_zone(self, zone: Zone) -> Zone:
        """Return the opposite zone connected to the given zone."""
        if zone is self.zone1:
            return self.zone2
        if zone is self.zone2:
            return self.zone1
        raise ValueError(f"Zone '{zone.name}' is not part of this connection")

    def display_name(self) -> str:
        """Return the display name of the connection."""
        return f"{self.zone1.name}-{self.zone2.name}"

    def __str__(self) -> str:
        return (
            f"{self.zone1.name}-{self.zone2.name} "
            f"[max_link_capacity={self.max_link_capacity}]"
        )
