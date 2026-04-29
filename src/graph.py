from typing import Any, Dict, Any, List
from . import Connection, Zone, Drone

class Graph:
    def __init__(self, zones: Dict[str, Any],
                 connections: List[Connection]) -> None:
        self.zones: Dict[str, Any] = zones
        self.connections: List[Connection] = connections
        
    def get_neighbors(self, zone_name: str) -> List[Zone, Connection]:
        pass
    
    def get_zone(self, zone_name: str) -> Zone:
        return self.zones.get(zone_name)
    
    def get_distance(self, from_zone: Zone, to_zone: Zone) -> int:
        pass
    
    def has_path(self, start: Zone, end: Zone) -> bool:
        pass 