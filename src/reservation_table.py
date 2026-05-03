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
        zone: Zone = self.graph.get_zone(zone_name)

        return current < zone.max_drones

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        if not self._can_reserve_zone(zone_name, turn):
            raise ValueError(f"Cannot reserve {zone_name} at turn {turn}")

        if zone_name not in self.zone_reservations:
            self.zone_reservations[zone_name] = {}

        if turn not in self.zone_reservations[zone_name]:
            self.zone_reservations[zone_name][turn] = 0

        self.zone_reservations[zone_name][turn] += 1

    def get_connection_count(self, connection_key: str, turn: int) -> int:
        if connection_key not in self.connection_reservations:
            return 0

        if turn not in self.connection_reservations[connection_key]:
            return 0

        return self.connection_reservations[connection_key][turn]

    def can_reserve_connection(
            self,
            connection_key: str, turn: int
    ) -> bool:
        current_count: int = self.get_connection_count(connection_key, turn)

        zone_a, zone_b = connection_key.split('-', 1)
        zone_a_obj: Zone = self.graph.get_zone(zone_a)
        zone_b_obj: Zone = self.graph.get_zone(zone_b)
        connection: Connection = self.graph.get_connection(
            zone_a_obj, zone_b_obj)

        return current_count < connection.max_link_capacity

    def reserve_connection(self, connection_key: str, turn: int) -> None:
        if not self._can_reserve_connection(connection_key, turn):
            raise ValueError(f"Cannot reserve {connection_key} at turn {turn}")

        if connection_key not in self.connection_reservations:
            self.connection_reservations[connection_key] = {}

        if turn not in self.connection_reservations[connection_key]:
            self.connection_reservations[connection_key][turn] = 0

        self.connection_reservations[connection_key][turn] += 1


    def is_wait_valid(self, zone: Zone, turn: int) -> None:
        pass