from . import Zone, Connection, Graph
from typing import Dict


class ReservationTable:
    def __init__(self, graph: Graph) -> None:
        self.zone_reservations: Dict[str, Dict[int, int]] = {}
        self.connection_reservations: Dict[str, Dict[int, int]] = {}
        self.graph: Graph = graph

    def get_zone_count(self, zone_name: str, turn: int) -> int:
        if zone_name not in self.zone_reservations:
            return 0

        if turn not in self.zone_reservations[zone_name]:
            return 0

        return self.zone_reservations[zone_name][turn]

    def can_reserve_zone(self, zone_name: str, turn: int) -> bool:
        current: int = self.get_zone_count(zone_name, turn)

        zone: Zone | None = self.graph.get_zone(zone_name)
        if not zone:
            raise ValueError("Unknown zone")

        return current < zone.max_drones

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        if not self.can_reserve_zone(zone_name, turn):
            raise ValueError(f"Cannot reserve {zone_name} at turn {turn}")

        if zone_name not in self.zone_reservations:
            self.zone_reservations[zone_name] = {}

        if turn not in self.zone_reservations[zone_name]:
            self.zone_reservations[zone_name][turn] = 0

        self.zone_reservations[zone_name][turn] += 1

    @staticmethod
    def _normalize_key(connection_key: str) -> str:
        zone_a, zone_b = connection_key.split('-', 1)
        zone_a, zone_b = sorted([zone_a, zone_b])
        return f"{zone_a}-{zone_b}"

    def get_connection_count(self, connection_key: str, turn: int) -> int:
        normalized_key: str = self._normalize_key(connection_key)

        if normalized_key not in self.connection_reservations:
            return 0

        if turn not in self.connection_reservations[normalized_key]:
            return 0

        return self.connection_reservations[normalized_key][turn]

    def can_reserve_connection(
            self,
            connection_key: str, turn: int
    ) -> bool:
        normalized_key: str = self._normalize_key(connection_key)

        current_count: int = self.get_connection_count(connection_key, turn)

        zone_a, zone_b = normalized_key.split('-', 1)

        zone_a_obj: Zone | None = self.graph.get_zone(zone_a)
        zone_b_obj: Zone | None = self.graph.get_zone(zone_b)
        if not zone_a_obj or not zone_b_obj:
            raise ValueError("Unknown zone")

        connection: Connection | None = self.graph.get_connection(
            zone_a_obj, zone_b_obj)
        if not connection:
            raise ValueError("Unknown connection")

        return current_count < connection.max_link_capacity

    def reserve_connection(self, connection_key: str, turn: int) -> None:
        normalized_key: str = self._normalize_key(connection_key)

        if not self.can_reserve_connection(normalized_key, turn):
            raise ValueError(f"Cannot reserve {normalized_key} at turn {turn}")

        if normalized_key not in self.connection_reservations:
            self.connection_reservations[normalized_key] = {}

        if turn not in self.connection_reservations[normalized_key]:
            self.connection_reservations[normalized_key][turn] = 0

        self.connection_reservations[normalized_key][turn] += 1

    def is_wait_valid(self, zone: Zone, turn: int) -> bool:
        next_turn: int = turn + 1

        if zone.zone_type == 'blocked':
            return False

        if not self.can_reserve_zone(zone.name, next_turn):
            return False

        return True

    def is_normal_move_valid(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> bool:
        next_turn: int = turn + 1

        if neighbor_zone.zone_type == 'blocked':
            return False

        if neighbor_zone.zone_type == 'restricted':
            return False

        if not self.can_reserve_zone(neighbor_zone.name, next_turn):
            return False

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            raise ValueError("Unknown connection")

        connection_key: str = connection.key()
        if not self.can_reserve_connection(connection_key, next_turn):
            return False

        return True

    def is_restricted_move_valid(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> bool:
        next_turn: int = turn + 1
        arrival_turn: int = next_turn + 1

        if neighbor_zone.zone_type == 'blocked':
            return False

        if neighbor_zone.zone_type != 'restricted':
            return False

        if not self.can_reserve_zone(neighbor_zone.name, arrival_turn):
            return False

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            return False

        connection_key: str = connection.key()
        if not self.can_reserve_connection(connection_key, next_turn):
            return False

        if not self.can_reserve_connection(connection_key, arrival_turn):
            return False

        return True

    def reserve_wait(self, zone: Zone, turn: int) -> None:
        next_turn: int = turn + 1
        zone_name: str = zone.name

        if not self.is_wait_valid(zone, turn):
            raise ValueError(f"Cannot reserve wait: Zone {zone_name} "
                             f"is not available at turn {next_turn}")

        self.reserve_zone(zone_name, next_turn)

    def reserve_normal_move(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> None:
        next_turn: int = turn + 1
        current_zone_name: str = current_zone.name
        neighbor_zone_name: str = neighbor_zone.name

        if not self.is_normal_move_valid(current_zone, neighbor_zone, turn):
            raise ValueError("Cannot reserve normal move: "
                             f"drone cannot move from {current_zone_name} to "
                             f"{neighbor_zone_name} at turn {next_turn}")

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            raise ValueError("Unknown connection")
        connection_key: str = connection.key()

        self.reserve_connection(connection_key, next_turn)
        self.reserve_zone(neighbor_zone_name, next_turn)

    def reserve_restricted_move(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> None:
        next_turn: int = turn + 1
        arrival_turn: int = turn + 2
        current_zone_name: str = current_zone.name
        neighbor_zone_name: str = neighbor_zone.name

        if not self.is_restricted_move_valid(
                current_zone, neighbor_zone, turn):
            raise ValueError("Cannot reserve restricted move: "
                             f"drone cannot move from {current_zone_name} to "
                             f"{neighbor_zone_name} at turn {arrival_turn}")

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            raise ValueError("Unknown connection")
        connection_key: str = connection.key()

        self.reserve_connection(connection_key, next_turn)
        self.reserve_connection(connection_key, arrival_turn)
        self.reserve_zone(neighbor_zone_name, arrival_turn)
