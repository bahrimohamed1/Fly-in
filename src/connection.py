from .zone import Zone


class Connection:
    def __init__(self, zone1: Zone, zone2: Zone,
                 max_link_capacity: int = 1) -> None:
        self.zone1: Zone = zone1
        self.zone2: Zone = zone2
        self.max_link_capacity: int = max_link_capacity
        self.current_drones_using: int = 0

    def can_drone_traverse(self) -> bool:
        return self.current_drones_using < self.max_link_capacity

    def add_drone(self) -> bool:
        if self.can_drone_traverse():
            self.current_drones_using += 1
            return True

        return False

    def remove_drone(self) -> bool:
        if self.current_drones_using >= 1:
            self.current_drones_using -= 1
            return True

        return False

    def connects(self, zone_a: Zone, zone_b: Zone) -> bool:
        return (zone_a is self.zone1 and zone_b is self.zone2)
    
    def __str__(self) -> str:
        return f"{self.zone1}-{self.zone2}"
