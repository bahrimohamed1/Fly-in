from . import Zone, Connection, Drone
from typing import List, Dict


class Parser:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.hubs: Dict[str, Zone] = {}
        self.connections: List[Connection] = []

    def parse(self):
        with open(self.file_name, "r") as file:
            for i, line in enumerate(1, file):
                line = line.strip()
                if line.startswith('#') or line.startwith('\n'):
                    continue
                if line.startswith("nb_drones"):
                    try:
                        raw = line.split(':', 1)[1].strip()
                        self.nb_drones = int(raw)
                    except TypeError:
                        return f"ERROR on line {i}: Number of drones " \
                            "must be a positive integer, got {raw}"

                elif line.startwith("start_hub"):
                    try:

    def _parse_metadata(self, metadata_str: str) -> Dict[str, str]:
        metadata: Dict[str, str] = {}
        for item in metadata_str.split():
            key, value = item.split('=')
            metadata[key] = value

        return metadata
