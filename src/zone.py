from typing import Optional

class Zone:
    def __init__(self, name: str, x: int, y: int,
                 zone_type: str, max_drones: int, color: Optional[int]) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.max_drones: int = max_drones
        self.color: Optional[int] = color
        self.current_drones_count: int = 0

    def can_drone_enter(self) -> bool:
        return self.current_drones_count < self.max_drones

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
    
    def __str__(self):
        return f"name: {self.name}, x,y: ({self.x}, {self.y}), metadata: " +\
            f"[{self.zone_type}, {self.color}, {self.max_drones}]"
