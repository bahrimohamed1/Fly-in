from typing import Any, Dict, List, Tuple
from . import Connection, Zone, Drone

class Graph:
    def __init__(self, zones: Dict[str, Any],
                 connections: List[Connection]) -> None:
        self.zones: Dict[str, Zone] = zones
        self.connections: List[Connection] = connections
        self.adjacency_list: Dict[str, List[Tuple[Zone, Connection]]] = {}
        self._build_adjacency_list()
        
    def get_neighbors(self, zone_name: str) -> List[Tuple[Zone, Connection]]:
        pass
    
    def get_zone(self, zone_name: str) -> Zone:
        return self.zones.get(zone_name)
    
    def get_distance(self, from_zone: Zone, to_zone: Zone) -> int:
        pass
    
    def has_path(self, start: Zone, end: Zone) -> bool:
        pass 