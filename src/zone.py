from typing import Optional


class Zone:
    """Represents a static zone/hub in the Fly-in map.

    A Zone stores map data:
    - name
    - coordinates
    - type
    - color
    - maximum capacity

    """

    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str,
        max_drones: int,
        color: Optional[str],
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.color: Optional[str] = color

    def movement_cost(self) -> int:
        """Return the number of turns required to enter this zone."""
        if self.zone_type == "restricted":
            return 2
        return 1

    def is_blocked(self) -> bool:
        """Return True if drones cannot enter this zone."""
        return self.zone_type == "blocked"

    def is_priority(self) -> bool:
        """Return True if this zone should be preferred in pathfinding."""
        return self.zone_type == "priority"

    def __str__(self) -> str:
        return (
            f"name: {self.name}, x,y: ({self.x}, {self.y}), "
            f"metadata: [{self.zone_type}, {self.color}, {self.max_drones}]"
        )
