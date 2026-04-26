"""Map file parser for the Fly-in drone routing simulation."""

import re
import sys
from graph import Connection, Graph, Zone, ZoneType

VALID_ZONE_TYPES: set[str] = {zt.value for zt in ZoneType}


def _error(line_num: int, msg: str) -> None:
    """Print a parse error and exit."""
    print(f"Parse error at line {line_num}: {msg}")
    sys.exit(1)


def _parse_metadata(meta_str: str, line_num: int) -> dict[str, str]:
    """Parse [key=value ...] metadata string into a dict."""
    meta: dict[str, str] = {}
    if not meta_str:
        return meta
    inner = meta_str.strip()[1:-1]
    for pair in inner.split():
        if "=" not in pair:
            _error(line_num, f"invalid metadata token '{pair}'")
        k, v = pair.split("=", 1)
        meta[k.strip()] = v.strip()
    return meta


def _parse_zone_line(
    parts: list[str],
    line_num: int,
    meta_str: str,
) -> Zone:
    """Parse zone definition from token list and metadata string."""
    if len(parts) < 3:
        _error(line_num, "zone definition requires: name x y")
    name = parts[0]
    if "-" in name:
        _error(line_num, f"zone name '{name}' must not contain dashes")
    try:
        x = int(parts[1])
        y = int(parts[2])
    except ValueError:
        _error(line_num, "x and y coordinates must be integers")

    meta = _parse_metadata(meta_str, line_num)

    zone_type_str = meta.get("zone", "normal")
    if zone_type_str not in VALID_ZONE_TYPES:
        _error(line_num, f"unknown zone type '{zone_type_str}'")
    zone_type = ZoneType(zone_type_str)

    color = meta.get("color", "none")

    raw_md = meta.get("max_drones", "1")
    try:
        max_drones = int(raw_md)
    except ValueError:
        _error(line_num, "max_drones must be a positive integer")
    if max_drones <= 0:
        _error(line_num, "max_drones must be a positive integer")

    return Zone(
        name=name,
        x=x,
        y=y,
        zone_type=zone_type,
        color=color,
        max_drones=max_drones,
    )


def _find_connection_zones(
    conn_str: str,
    defined_zones: set[str],
    line_num: int,
) -> tuple[str, str]:
    """Split 'zone_a-zone_b' into two known zone names.

    Zone names cannot contain dashes, so the separator is the unique dash
    that divides two valid, already-defined zone names.
    """
    # Collect all dash positions and test each as the split point once.
    indices = [i for i, ch in enumerate(conn_str) if ch == "-"]
    for idx in indices:
        candidate_a = conn_str[:idx]
        candidate_b = conn_str[idx + 1:]
        if candidate_a in defined_zones and candidate_b in defined_zones:
            return candidate_a, candidate_b
    _error(
        line_num,
        f"cannot resolve zones in connection '{conn_str}' "
        f"(are both zones defined?)",
    )
    raise RuntimeError("unreachable")  # satisfy mypy


def parse_map(filepath: str) -> tuple[Graph, int]:
    """Parse a map file and return (Graph, nb_drones).

    Validates all directives and exits with a clear message on any error.
    """
    try:
        with open(filepath, "r") as fh:
            raw_lines = fh.readlines()
    except FileNotFoundError:
        print(f"Error: file not found: {filepath}")
        sys.exit(1)
    except OSError as exc:
        print(f"Error reading file: {exc}")
        sys.exit(1)

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

        # Extract optional metadata block [...]
        meta_match = re.search(r"\[([^\]]*)\]", line)
        meta_str = (
            "[" + meta_match.group(1) + "]" if meta_match else ""
        )
        line_clean = re.sub(r"\s*\[.*?\]", "", line).strip()

        # --- nb_drones must be the first meaningful line ---
        if not has_nb_drones:
            if not line_clean.startswith("nb_drones:"):
                _error(
                    line_num,
                    "first non-comment line must be 'nb_drones: <N>'",
                )
            raw_val = line_clean.split(":", 1)[1].strip()
            try:
                nb_drones = int(raw_val)
            except ValueError:
                _error(line_num, "nb_drones must be a positive integer")
            if nb_drones <= 0:
                _error(line_num, "nb_drones must be a positive integer")
            has_nb_drones = True
            continue

        # --- hub directives ---
        if line_clean.startswith("start_hub:"):
            if has_start:
                _error(line_num, "only one start_hub is allowed")
            parts = line_clean.split(":", 1)[1].strip().split()
            zone = _parse_zone_line(parts, line_num, meta_str)
            if zone.name in defined_zones:
                _error(line_num, f"zone '{zone.name}' already defined")
            graph.add_zone(zone)
            graph.start_zone = zone.name
            defined_zones.add(zone.name)
            has_start = True

        elif line_clean.startswith("end_hub:"):
            if has_end:
                _error(line_num, "only one end_hub is allowed")
            parts = line_clean.split(":", 1)[1].strip().split()
            zone = _parse_zone_line(parts, line_num, meta_str)
            if zone.name in defined_zones:
                _error(line_num, f"zone '{zone.name}' already defined")
            graph.add_zone(zone)
            graph.end_zone = zone.name
            defined_zones.add(zone.name)
            has_end = True

        elif line_clean.startswith("hub:"):
            parts = line_clean.split(":", 1)[1].strip().split()
            zone = _parse_zone_line(parts, line_num, meta_str)
            if zone.name in defined_zones:
                _error(line_num, f"zone '{zone.name}' already defined")
            graph.add_zone(zone)
            defined_zones.add(zone.name)

        elif line_clean.startswith("connection:"):
            conn_str = line_clean.split(":", 1)[1].strip()
            zone_a, zone_b = _find_connection_zones(
                conn_str, defined_zones, line_num
            )
            if (zone_a, zone_b) in defined_connections or (
                zone_b,
                zone_a,
            ) in defined_connections:
                _error(
                    line_num,
                    f"duplicate connection '{zone_a}-{zone_b}'",
                )
            meta = _parse_metadata(meta_str, line_num)
            raw_cap = meta.get("max_link_capacity", "1")
            try:
                max_cap = int(raw_cap)
            except ValueError:
                _error(
                    line_num,
                    "max_link_capacity must be a positive integer",
                )
            if max_cap <= 0:
                _error(
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
            _error(line_num, f"unknown directive in: '{line_clean}'")

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
