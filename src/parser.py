from . import Zone, Connection, Graph
from typing import List, Dict, Optional, Any


class Parser:
    def __init__(self, map_file: str) -> None:
        self.map: str = map_file
        self.nb_drones: int = 0
        self.zones: Dict[str, Zone] = {}
        self.connections: List[Connection] = []
        self.start_zone: Optional[Zone] = None
        self.end_zone: Optional[Zone] = None
        self.valid_zone_types: set[str] = {
            'normal', 'priority', 'restricted', 'blocked'}
        self.seen_connections: set[str] = set()

    def parse(self) -> Graph:
        with open(self.map, 'r') as file:
            for n, raw_line in enumerate(file, 1):
                line = raw_line.strip()

                if not line or line.startswith('#'):
                    continue

                if line.startswith('nb_drones'):
                    self._parse_nb_drones(line, n)

                elif line.startswith('start_hub') or\
                    line.startswith('end_hub') or\
                        line.startswith('hub'):
                    self._parse_zone_line(line, n)

                elif line.startswith('connection'):
                    self._parse_connection_line(line, n)

                else:
                    raise ValueError("ERROR: UNKNOWN LINE TYPE")

            self._validate_final_result()
            if not self.start_zone or not self.end_zone:
                raise ValueError("ERROR: INVALID START ZONE OR END ZONE")

            return Graph(
                self.zones,
                self.connections,
                self.start_zone,
                self.end_zone,
            )

    def _parse_nb_drones(self, line: str, n: int) -> None:
        if self.nb_drones:
            raise ValueError(
                f"ERROR on line {n}: NB_DRONES DEFINED MULTIPLE TIMES")

        if ':' not in line:
            raise ValueError(f"ERROR on line {n}: INVALID NB_DRONES FORMAT")

        raw_value: str = line.split(':', 1)[-1].strip()
        if not raw_value:
            raise ValueError(f"ERROR on line {n}: MISSING NB_DRONES VALUE")

        try:
            value: int = int(raw_value)
        except ValueError:
            raise ValueError(
                f"ERROR on line {n}: NB_DRONES MUST BE AN INTEGER")

        if value <= 0:
            raise ValueError(f"ERROR on line {n}: NB_DRONES MUST BE POSITIVE")

        self.nb_drones = value

    def _parse_metadata(self, metadata_txt: str, n: int) -> Dict[str, Any]:
        metadata: Dict[str, Any] = {
            'zone': 'normal',
            'color': None,
            'max_drones': 1,
            'max_link_capacity': 1
        }

        clean_metadata_txt: str = metadata_txt.removeprefix(
            '[').removesuffix(']').strip()
        if not clean_metadata_txt:
            return metadata

        for item in clean_metadata_txt.split():
            if '=' not in item:
                raise ValueError(f"ERROR on line {n}: INVALID METADATA ITEM")

            key, value = item.split('=', 1)
            if not key or not value:
                raise ValueError(f"ERROR on line {n}: INVALID METADATA ITEM")

            if key not in metadata.keys():
                raise ValueError(f"ERROR on line {n}: UNKNOWN METADATA KEY")

            if key == 'max_drones' or key == 'max_link_capacity':
                try:
                    value: int = int(value)
                except ValueError:
                    raise ValueError(
                        f"ERROR on line {n}: Metadata value must be integer")

                if value <= 0:
                    raise ValueError(
                        f"ERROR on line {n}: Metadata value must be positive")

                metadata[key] = value

            elif key == 'zone':
                if value not in self.valid_zone_types:
                    raise ValueError(f"ERROR on line {n}: Invalid zone type")

                metadata[key] = value

            elif key == 'color':
                metadata[key] = value

        return metadata

    def _parse_zone_line(self, line: str, n: int) -> None:
        if ':' not in line:
            raise ValueError(f"ERROR on line {n}: Invalid zone format")

        prefix, content = line.split(':', 1)
        prefix: str = prefix.strip()
        content: str = content.strip()

        if prefix not in ['start_hub', 'end_hub', 'hub']:
            raise ValueError(f"ERROR on line {n}: Invalid zone prefix")
        if not content:
            raise ValueError(f"ERROR on line {n}: Missing zone data")

        metadata_txt = ''
        if '[' in content:
            if not content.endswith(']'):
                raise ValueError(f"ERROR on line {n}: Invalid metadata format")

            bracket_index: int = content.find('[')
            zone_part: str = content[:bracket_index]
            metadata_txt: str = content[bracket_index:]

        else:
            zone_part = content

        parts: List[str] = zone_part.split()
        if len(parts) != 3:
            raise ValueError(
                F"ERROR on line {n}: zone format must be: name x y")

        name = parts[0]
        raw_x = parts[1]
        raw_y = parts[2]

        if name in self.zones:
            raise ValueError(f"ERROR on line {n}: Duplicate zone")

        try:
            x: int = int(raw_x)
            y: int = int(raw_y)
        except ValueError:
            raise ValueError(
                f"ERROR on line {n}: Zone coordinates must be integers")

        metadata: Dict[str, Any] = self._parse_metadata(metadata_txt, n)
        zone_type: str = metadata['zone']
        max_drones: int = metadata['max_drones']
        color: Optional[str] = metadata['color']

        zone: Zone = Zone(
            name,
            x,
            y,
            zone_type,
            max_drones,
            color
        )

        self.zones[name] = zone

        if prefix == 'start_hub':
            if self.start_zone:
                raise ValueError(
                    f"ERROR on line {n}: start_hub already defined")

            self.start_zone = zone

        elif prefix == 'end_hub':
            if self.end_zone:
                raise ValueError(
                    f"ERROR on line {n}: end_hub already defined")

            self.end_zone = zone

    def _parse_connection_line(self, line: str, n: int) -> None:
        if ':' not in line:
            raise ValueError(f"ERROR on line {n}: Invalid connection format")

        prefix, content = line.split(':', 1)
        prefix: str = prefix.strip()
        content: str = content.strip()

        if prefix != 'connection':
            raise ValueError(f"ERROR on line {n}: Invalid connection prefix")
        if not content:
            raise ValueError(f"ERROR on line {n}: Missing connection data")

        metadata_txt: str = ''
        if '[' in content:
            if not content.endswith(']'):
                raise ValueError(
                    f"ERROR on line {n}: Invalid connection metadata format")

            bracket_index: int = content.find('[')
            connection_part: str = content[:bracket_index]
            metadata_txt = content[bracket_index:]

        else:
            connection_part = content
            if '-' not in connection_part:
                raise ValueError(
                    f"ERROR on line {n}: Connection must use A-B format")

        zone_a_name, zone_b_name = connection_part.split('-', 1)
        zone_a_name: str = zone_a_name.strip()
        zone_b_name: str = zone_b_name.strip()

        if not zone_a_name or not zone_b_name:
            raise ValueError(
                f"ERROR on line {n}: Invalid connection endpoints")
        if zone_a_name == zone_b_name:
            raise ValueError(
                f"ERROR on line {n}: Self-connection is not allowed")

        zone_a: Optional[Zone] = self.zones.get(zone_a_name)
        zone_b: Optional[Zone] = self.zones.get(zone_b_name)

        if not zone_a or not zone_b:
            raise ValueError(f"ERROR on line {n}: Unknown zone")

        normalized_key: str = '-'.join(sorted([zone_a_name, zone_b_name]))
        if normalized_key in self.seen_connections:
            raise ValueError(f"ERROR on line {n}: Duplicate connections")

        metadata: Dict[str, Any] = self._parse_metadata(metadata_txt, n)

        max_link_capacity: int = metadata['max_link_capacity']

        connection: Connection = Connection(
            zone_a,
            zone_b,
            max_link_capacity
        )

        self.connections.append(connection)
        self.seen_connections.add(normalized_key)

    def _validate_final_result(self) -> None:
        if self.nb_drones <= 0:
            raise ValueError("Missing or invalid nb_drones")

        if not self.zones:
            raise ValueError("No zones found")

        if not self.connections:
            raise ValueError("No connections found")

        if not self.start_zone:
            raise ValueError("Missing start_zone")

        if not self.end_zone:
            raise ValueError("Missing end_zone")

        if self.start_zone == self.end_zone:
            raise ValueError("start_hub and end_hub cannot be the same zone")

        if self.start_zone.zone_type == 'blocked':
            raise ValueError("start_zone cannot be blocked")

        if self.end_zone.zone_type == 'blocked':
            raise ValueError("end_zone cannot be blocked")
