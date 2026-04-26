"""ANSI terminal renderer for the Fly-in drone routing simulation."""

from graph import Graph

# ANSI escape sequences
_RESET = "\033[0m"
_BOLD = "\033[1m"
_YELLOW = "\033[33m"

# Map colour names from map files to ANSI foreground codes
_COLOR_CODES: dict[str, str] = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "orange": "\033[91m",
    "gray": "\033[90m",
    "grey": "\033[90m",
    "brown": "\033[33m",
    "maroon": "\033[31m",
    "gold": "\033[93m",
    "lime": "\033[92m",
    "violet": "\033[35m",
    "crimson": "\033[31m",
    "darkred": "\033[31m",
    "black": "\033[90m",
    "rainbow": "\033[96m",
    "none": "",
}


def _drone_color(token: str) -> str:
    """Wrap a drone token in bold yellow ANSI formatting."""
    return f"{_BOLD}{_YELLOW}{token}{_RESET}"


def _zone_color(zone_name: str, graph: Graph) -> str:
    """Wrap a zone name in its configured colour."""
    zone = graph.zones.get(zone_name)
    if zone is None:
        return zone_name
    code = _COLOR_CODES.get(zone.color.lower(), "")
    if not code:
        return zone_name
    return f"{code}{zone_name}{_RESET}"


def render_turn(
    turn_line: str,
    graph: Graph,
    drone_positions: dict[str, str],
) -> str:
    """Return a coloured version of a turn output line.

    Drone identifiers (``D<n>``) are rendered in bold yellow.
    Zone names are coloured according to their ``color`` field in the graph.
    In-transit tokens (``D<n>-<from>-<to>``) have both zone names coloured.

    Args:
        turn_line:       Raw turn line, e.g. ``"D1-roof1 D2-corridorA"``.
        graph:           The flight-network graph (for colour lookup).
        drone_positions: Mapping of drone token to zone name (unused in
                         basic rendering; reserved for debug overlay).

    Returns:
        Coloured string suitable for terminal output.
    """
    _ = drone_positions  # reserved for debug overlay
    parts = turn_line.split()
    rendered: list[str] = []
    for part in parts:
        segments = part.split("-")
        if not segments:
            rendered.append(part)
            continue
        drone_id = _drone_color(segments[0])
        if len(segments) == 2:
            # D<n>-<zone>
            zone_part = _zone_color(segments[1], graph)
            rendered.append(f"{drone_id}-{zone_part}")
        elif len(segments) >= 3:
            # D<n>-<from>-<to>  (in-transit to restricted zone)
            from_part = _zone_color(segments[1], graph)
            to_part = _zone_color(segments[2], graph)
            rendered.append(f"{drone_id}-{from_part}-{to_part}")
        else:
            rendered.append(part)
    return " ".join(rendered)


def render_debug_map(
    graph: Graph,
    drone_positions: dict[str, str],
    turn_num: int,
) -> str:
    """Return a simple ASCII map showing drone positions for debugging.

    Args:
        graph:           The flight-network graph.
        drone_positions: Mapping of zone name → drone label(s).
        turn_num:        Current turn number (for the header).

    Returns:
        Multi-line string representing the map state.
    """
    lines: list[str] = [f"── Turn {turn_num} ──"]
    for zone_name, zone in sorted(graph.zones.items()):
        drones_here = drone_positions.get(zone_name, "")
        marker = f" [{drones_here}]" if drones_here else ""
        lines.append(
            f"  {zone_name:20s} ({zone.x:3d},{zone.y:3d})"
            f"  {zone.zone_type.value:10s}{marker}"
        )
    return "\n".join(lines)
