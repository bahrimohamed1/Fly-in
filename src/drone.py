from typing import List, Tuple
from .zone import Zone


class Drone:
    """Represents one drone in the simulation.

    The drone stores its identity and current zone.

    """

    def __init__(self, drone_id: int, current_zone: Zone) -> None:
        self.drone_id: int = drone_id
        self.current_zone: Zone = current_zone
        self.path: List[str] = []
        self.delivered: bool = False

    def move_to(self, new_zone: Zone) -> None:
        """Update the drone current zone without checking capacity."""
        self.current_zone = new_zone

    def mark_delivered(self) -> None:
        """Mark the drone as delivered to the end zone."""
        self.delivered = True

    def get_position(self) -> Tuple[int, int]:
        """Return the current coordinates of the drone."""
        return (self.current_zone.x, self.current_zone.y)

    def __str__(self) -> str:
        return f"id: {self.drone_id}, current_hub: {self.current_zone.name}"
