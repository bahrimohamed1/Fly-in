from . import Zone, Connection, Drone
from typing import List, Dict, Any
import sys


class Parser:
    def __init__(self, file_name: str) -> None:
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.start_zone: Zone = None
        self.end_zone: Zone = None
        self.hubs: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.valid_zones: List[str] = [
            'normal',
            'priority',
            'restricted',
            'blocked'
        ]

    def parse(self) -> Any:
        try:
            with open(self.file_name, "r") as file:
                for i, line in enumerate(file, 1):
                    line: str = line.strip()
                    if line.startswith('#') or line.startswith('\n'):
                        continue
                    if line.startswith("nb_drones"):
                        try:
                            raw: str = line.split(':', 1)[1].strip()
                            self.nb_drones = int(raw)
                        except TypeError:
                            print(f"ERROR on line {i}: Number of drones "
                                  f"must be a positive integer, got {raw}")
                            sys.exit(1)

                    elif line.startswith("start_hub") or \
                            line.startswith("hub") or \
                            line.startswith("end_hub"):
                        try:
                            info: str = line.split(':', 1)[1].strip()
                            br = info.find('[')
                            if br == -1:
                                name, x, y = info.split()
                                metadata = ""
                            else:
                                name, x, y = info[:br].split()
                                metadata: str = info[br:].strip('[]')
                            metadata_dict: Dict[str, Any] = \
                                self._parse_metadata(metadata)
                            if metadata_dict.get('zone') \
                                    not in self.valid_zones:
                                raise ValueError(f"{metadata_dict.get('zone')}"
                                                 "is not a valid zone type!")
                            if line.startswith("start_hub"):
                                self.start_zone = Zone(
                                    name,
                                    int(x),
                                    int(y),
                                    metadata_dict.get('zone'),
                                    metadata_dict.get('max_drones'),
                                    metadata_dict.get('color'),
                                )
                            elif line.startswith("end_hub"):
                                self.end_zone = Zone(
                                    name,
                                    int(x),
                                    int(y),
                                    metadata_dict.get('zone'),
                                    metadata_dict.get('max_drones'),
                                    metadata_dict.get('color'),
                                )
                            else:
                                self.hubs[name] = Zone(
                                    name,
                                    int(x),
                                    int(y),
                                    metadata_dict.get('zone'),
                                    metadata_dict.get('max_drones'),
                                    metadata_dict.get('color'),
                                )
                        except Exception as e:
                            print(f"ERROR on line {i}: {e}")
                            sys.exit(1)

                    elif line.startswith("connection"):
                        try:
                            connection = line.split(':', 1)[1].strip()

                        except Exception as e:
                            print(f"ERROR on line {i}: {e}")
                            sys.exit(1)
        except FileNotFoundError:
            print(f"ERROR: File '{self.file_name}' not found")
            sys.exit(1)

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            "zone": "normal",
            "color": None,
            "max_drones": 1,
            "max_link_capacity": 1
        }
        if metadata_str:
            for item in metadata_str.split():
                key, value = item.split('=')
                if key == "max_drones" or key == "max_link_capacity":
                    metadata[key] = int(value)
                else:
                    metadata[key] = value

        return metadata
