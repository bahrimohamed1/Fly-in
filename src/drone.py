from .zone import Zone
from typing import Tuple


class Drone:
    def __init__(self, drone_id: int, current_zone: Zone) -> None:
        self.drone_id: int = drone_id
        self.current_zone: Zone = current_zone

    def move_to(self, new_zone: Zone) -> bool:
        if new_zone.add_drone():
            self.current_zone.remove_drone()
            self.current_zone = new_zone
            return True

        return False

    def get_position(self) -> Tuple[int, int]:
        return (self.current_zone.x, self.current_zone.y)
