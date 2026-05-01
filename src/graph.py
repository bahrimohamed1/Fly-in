from typing import Any, Dict, List, Tuple
from . import Connection, Zone, Drone
import math

class Graph:
    def __init__(self, zones: Dict[str, Any],
                 connections: List[Connection]) -> None:
        self.zones: Dict[str, Zone] = zones
        self.connections: List[Connection] = connections
        self.adjacency_list: Dict[str, List[Tuple[Zone, Connection]]] = {}
        self._build_adjacency_list()

    def _build_adjacency_list(self):
        for zone_name in self.zones:
            self.adjacency_list[zone_name] = []

        for connection in self.connections:
            zone1: Zone = connection.zone1
            zone2: Zone = connection.zone2

            self.adjacency_list[zone1.name].append((zone2, connection))
            self.adjacency_list[zone2.name].append((zone1, connection))

    def get_neighbors(self, zone_name: str) -> List[Tuple[Zone, Connection]]:
        if zone_name not in self.adjacency_list:
            raise KeyError(f"Zone '{zone_name}' not found in graph")

        return self.adjacency_list[zone_name]

    def get_zone(self, zone_name: str) -> Zone | None:
        if zone_name not in self.adjacency_list[zone_name]:
            return None

        return self.zones.get(zone_name)

    def get_distance(self, from_zone: Zone, to_zone: Zone) -> int:
        if from_zone.name == to_zone.name:
            return 0
        
        start_zone: Zone = self.get_zone(from_zone.name)
        end_zone: Zone = self.get_zone(to_zone.name)
        if not start_zone or not end_zone:
            return math.inf

    def has_path(self, start: Zone, end: Zone) -> bool:
        pass
