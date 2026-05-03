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
        self.drones: List[Drone] = []
        self.valid_zones: set[str] = {
            'normal',
            'priority',
            'restricted',
            'blocked'
        }

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
                        except ValueError:
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
                                metadata: str = ""
                            else:
                                name, x, y = info[:br].split()
                                metadata: str = info[br:].strip('[]')
                            try:
                                metadata_dict: Dict[str, Any] = \
                                    self._parse_metadata(metadata)
                            except ValueError as e:
                                print(f"ERROR on line {i}: {e}")
                                sys.exit(1)
                            if metadata_dict.get('zone') \
                                    not in self.valid_zones:
                                raise ValueError(f"{metadata_dict.get('zone')}"
                                                 "is not a valid zone type!")
                            zone: Zone = Zone(
                                name,
                                int(x),
                                int(y),
                                metadata_dict.get('zone'),
                                metadata_dict.get('max_drones'),
                                metadata_dict.get('color'),
                            )
                            self.hubs[name] = zone

                            if line.startswith("start_hub"):
                                self.start_zone = zone
                            elif line.startswith("end_hub"):
                                self.end_zone = zone

                        except Exception as e:
                            print(f"ERROR on line {i}: {e}")
                            sys.exit(1)

                    elif line.startswith("connection"):
                        try:
                            connection = line.split(':', 1)[1].strip()
                            br = connection.find('[')
                            if br == -1:
                                zone1, zone2 = connection.split('-')
                                metadata = ""
                            else:
                                connects = connection[:br]
                                zone1, zone2 = connects.split('-')
                                metadata = connection[br:-1]

                            zone1_obj: Zone = self.hubs.get(zone1)
                            zone2_obj: Zone = self.hubs.get(zone2)
                            if not zone1_obj or not zone2_obj:
                                raise ValueError(f"ERROR on line {i}: {zone1} or"
                                                 f"{zone2} is not a valid hub")

                            metadata_dict = self._parse_metadata(metadata)
                            self.connections.append(Connection(
                                zone1_obj,
                                zone2_obj,
                                metadata_dict.get('max_link_capacity')
                            ))

                        except Exception as e:
                            print(f"ERROR on line {i}: {e}")
                            sys.exit(1)

                for i in range(self.nb_drones):
                    self.drones.append(Drone(i, self.start_zone))

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

    def get_number_of_drones(self) -> int:
        return self.nb_drones

    def get_start_zone(self) -> Zone:
        return self.start_zone

    def get_end_zone(self) -> Zone:
        return self.end_zone

    def get_zones(self) -> Dict[str, Zone]:
        return self.hubs

    def get_connections(self) -> List[Connection]:
        return self.connections

    def get_drones(self) -> List[Drone]:
        return self.drones
