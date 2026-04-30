"""Class-based map file parser for the Fly-in drone routing simulation."""

import re
import sys

from src.connection import Connection
from src.graph import Graph
from src.zone import Zone, ZoneType

VALID_ZONE_TYPES: set[str] = {zt.value for zt in ZoneType}


class Parser:
    """Parses a Fly-in map file into a Graph and drone count.

    Usage::

        p = Parser("maps/easy/01_linear_path.txt")
        graph, nb_drones = p.parse()
    """

    def __init__(self, file_name: str) -> None:
        """Initialise the parser with the path to a map file.

        Args:
            file_name: Path to the map definition file.
        """
        self.file_name: str = file_name

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def parse(self) -> tuple[Graph, int]:
        """Parse the map file and return (Graph, nb_drones).

        Validates all directives and exits with a clear error message on
        any problem.

        Returns:
            A tuple of (Graph, nb_drones) where nb_drones is the number
            of drones specified in the map file.
        """
        raw_lines = self._read_file()

        graph = Graph()
        nb_drones: int = 0
        has_nb_drones = False
        has_start = False
        has_end = False
        defined_zones: set[str] = set()
        defined_connections: set[tuple[str, str]] = set()

        for line_num, raw_line in enumerate(raw_lines, 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue

            meta_match = re.search(r"\[([^\]]*)\]", line)
            meta_str = (
                "[" + meta_match.group(1) + "]" if meta_match else ""
            )
            line_clean = re.sub(r"\s*\[.*?\]", "", line).strip()

            if not has_nb_drones:
                if not line_clean.startswith("nb_drones:"):
                    self._error(
                        line_num,
                        "first non-comment line must be 'nb_drones: <N>'",
                    )
                raw_val = line_clean.split(":", 1)[1].strip()
                try:
                    nb_drones = int(raw_val)
                except ValueError:
                    self._error(
                        line_num, "nb_drones must be a positive integer"
                    )
                if nb_drones <= 0:
                    self._error(
                        line_num, "nb_drones must be a positive integer"
                    )
                has_nb_drones = True
                continue

            if line_clean.startswith("start_hub:"):
                if has_start:
                    self._error(line_num, "only one start_hub is allowed")
                parts = line_clean.split(":", 1)[1].strip().split()
                zone = self._parse_zone_line(parts, line_num, meta_str)
                if zone.name in defined_zones:
                    self._error(
                        line_num, f"zone '{zone.name}' already defined"
                    )
                graph.add_zone(zone)
                graph.start_zone = zone.name
                defined_zones.add(zone.name)
                has_start = True

            elif line_clean.startswith("end_hub:"):
                if has_end:
                    self._error(line_num, "only one end_hub is allowed")
                parts = line_clean.split(":", 1)[1].strip().split()
                zone = self._parse_zone_line(parts, line_num, meta_str)
                if zone.name in defined_zones:
                    self._error(
                        line_num, f"zone '{zone.name}' already defined"
                    )
                graph.add_zone(zone)
                graph.end_zone = zone.name
                defined_zones.add(zone.name)
                has_end = True

            elif line_clean.startswith("hub:"):
                parts = line_clean.split(":", 1)[1].strip().split()
                zone = self._parse_zone_line(parts, line_num, meta_str)
                if zone.name in defined_zones:
                    self._error(
                        line_num, f"zone '{zone.name}' already defined"
                    )
                graph.add_zone(zone)
                defined_zones.add(zone.name)

            elif line_clean.startswith("connection:"):
                conn_str = line_clean.split(":", 1)[1].strip()
                zone_a, zone_b = self._find_connection_zones(
                    conn_str, defined_zones, line_num
                )
                if (zone_a, zone_b) in defined_connections or (
                    zone_b,
                    zone_a,
                ) in defined_connections:
                    self._error(
                        line_num,
                        f"duplicate connection '{zone_a}-{zone_b}'",
                    )
                meta = self._parse_metadata(meta_str, line_num)
                raw_cap = meta.get("max_link_capacity", "1")
                try:
                    max_cap = int(raw_cap)
                except ValueError:
                    self._error(
                        line_num,
                        "max_link_capacity must be a positive integer",
                    )
                if max_cap <= 0:
                    self._error(
                        line_num,
                        "max_link_capacity must be a positive integer",
                    )
                conn = Connection(
                    zone_a=zone_a,
                    zone_b=zone_b,
                    max_link_capacity=max_cap,
                )
                graph.add_connection(conn)
                defined_connections.add((zone_a, zone_b))

            else:
                self._error(
                    line_num, f"unknown directive in: '{line_clean}'"
                )

        if not has_nb_drones:
            print("Error: missing nb_drones directive")
            sys.exit(1)
        if not has_start:
            print("Error: missing start_hub directive")
            sys.exit(1)
        if not has_end:
            print("Error: missing end_hub directive")
            sys.exit(1)

        return graph, nb_drones

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _read_file(self) -> list[str]:
        """Read the map file and return its lines."""
        try:
            with open(self.file_name, "r") as fh:
                return fh.readlines()
        except FileNotFoundError:
            print(f"Error: file not found: {self.file_name}")
            sys.exit(1)
        except OSError as exc:
            print(f"Error reading file: {exc}")
            sys.exit(1)

    @staticmethod
    def _error(line_num: int, msg: str) -> None:
        """Print a parse error message and exit."""
        print(f"Parse error at line {line_num}: {msg}")
        sys.exit(1)

    @staticmethod
    def _parse_metadata(meta_str: str, line_num: int) -> dict[str, str]:
        """Parse a ``[key=value ...]`` metadata block into a dict.

        Args:
            meta_str:  The raw metadata string including brackets.
            line_num:  Source line number (for error messages).

        Returns:
            Dictionary of key/value pairs.
        """
        meta: dict[str, str] = {}
        if not meta_str:
            return meta
        inner = meta_str.strip()[1:-1]
        for pair in inner.split():
            if "=" not in pair:
                Parser._error(
                    line_num, f"invalid metadata token '{pair}'"
                )
            k, v = pair.split("=", 1)
            meta[k.strip()] = v.strip()
        return meta

    def _parse_zone_line(
        self,
        parts: list[str],
        line_num: int,
        meta_str: str,
    ) -> Zone:
        """Parse a zone definition from token list and metadata string.

        Args:
            parts:    Whitespace-split tokens after the directive keyword.
            line_num: Source line number (for error messages).
            meta_str: Raw metadata block string (may be empty).

        Returns:
            A populated Zone instance.
        """
        if len(parts) < 3:
            self._error(line_num, "zone definition requires: name x y")
        name = parts[0]
        if "-" in name:
            self._error(
                line_num, f"zone name '{name}' must not contain dashes"
            )
        try:
            x = int(parts[1])
            y = int(parts[2])
        except ValueError:
            self._error(
                line_num, "x and y coordinates must be integers"
            )

        meta = self._parse_metadata(meta_str, line_num)

        zone_type_str = meta.get("zone", "normal")
        if zone_type_str not in VALID_ZONE_TYPES:
            self._error(
                line_num, f"unknown zone type '{zone_type_str}'"
            )
        zone_type = ZoneType(zone_type_str)

        color = meta.get("color", "none")

        raw_md = meta.get("max_drones", "1")
        try:
            max_drones = int(raw_md)
        except ValueError:
            self._error(line_num, "max_drones must be a positive integer")
        if max_drones <= 0:
            self._error(line_num, "max_drones must be a positive integer")

        return Zone(
            name=name,
            x=x,
            y=y,
            zone_type=zone_type,
            color=color,
            max_drones=max_drones,
        )

    def _find_connection_zones(
        self,
        conn_str: str,
        defined_zones: set[str],
        line_num: int,
    ) -> tuple[str, str]:
        """Split ``'zone_a-zone_b'`` into two known zone names.

        Zone names cannot contain dashes, so the separator is the unique
        dash that divides two valid, already-defined zone names.

        Args:
            conn_str:      The connection string from the directive.
            defined_zones: Set of already-defined zone names.
            line_num:      Source line number (for error messages).

        Returns:
            A tuple (zone_a, zone_b).
        """
        indices = [i for i, ch in enumerate(conn_str) if ch == "-"]
        for idx in indices:
            candidate_a = conn_str[:idx]
            candidate_b = conn_str[idx + 1:]
            if (
                candidate_a in defined_zones
                and candidate_b in defined_zones
            ):
                return candidate_a, candidate_b
        self._error(
            line_num,
            f"cannot resolve zones in connection '{conn_str}' "
            f"(are both zones defined?)",
        )
        raise RuntimeError(  # satisfy mypy
            f"failed to parse connection zones from '{conn_str}'"
        )
