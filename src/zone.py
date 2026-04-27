class Zone:
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str, max_drones: int = 1) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.current_drones_count: int = 0

    def can_drone_enter(self) -> bool:
        return self.max_drones < self.current_drones_count

    def add_drone(self) -> bool:
        if self.can_drone_enter():
            self.current_drones_count += 1
            return True

        return False

    def remove_drone(self) -> bool:
        if self.current_drones_count >= 1:
            self.current_drones_count -= 1
            return True

        return False
