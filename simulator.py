"""Simulation engine for the Fly-in drone routing simulation.

Implements discrete-turn movement with capacity constraints, restricted-zone
two-turn transit, and lower-ID priority conflict resolution.
"""

from dataclasses import dataclass, field
from graph import Graph, ZoneType

# Safety limit to prevent infinite loops on unsolvable maps
MAX_TURNS: int = 10_000


@dataclass
class Drone:
    """Represents a single drone in the simulation.

    Attributes:
        id:             1-indexed drone identifier.
        path:           Ordered list of zone names to traverse.
        path_index:     Index of the drone's confirmed current zone in path.
        current_zone:   Zone the drone occupies; empty string when in transit.
        in_transit_to:  Destination zone name during restricted-zone transit.
        in_transit_from: Source zone name during restricted-zone transit.
        delivered:      True once the drone has reached the end hub.
    """

    id: int
    path: list[str]
    path_index: int = field(default=0)
    current_zone: str = field(default="")
    in_transit_to: str = field(default="")
    in_transit_from: str = field(default="")
    delivered: bool = field(default=False)


def _compute_occupancy(drones: list[Drone]) -> dict[str, int]:
    """Return a mapping of zone → number of drones physically present."""
    occ: dict[str, int] = {}
    for d in drones:
        if not d.delivered and d.current_zone:
            occ[d.current_zone] = occ.get(d.current_zone, 0) + 1
    return occ


def _process_turn(
    drones: list[Drone],
    graph: Graph,
) -> list[str]:
    """Advance all drones by one turn and return movement strings.

    Movement strings have the form:
        ``D<id>-<zone>``          normal arrival / restricted arrival
        ``D<id>-<from>-<to>``    start of restricted-zone transit

    Returns:
        Sorted (by drone ID) list of movement strings for this turn.
        An empty list means no drone moved.
    """
    end_zone = graph.end_zone

    # Current physical occupancy (in-transit drones count for nothing)
    occupancy = _compute_occupancy(drones)

    # Deltas accumulated during this turn
    entering: dict[str, int] = {}   # drones arriving this turn
    leaving: dict[str, int] = {}    # drones departing this turn
    # drones starting a restricted-zone transit this turn (arrive NEXT turn)
    transit_to: dict[str, int] = {}
    conn_usage: dict[tuple[str, str], int] = {}

    move_reports: list[tuple[int, str]] = []
    # IDs of drones that just completed a transit this turn;
    # they may not start a new move in the same turn.
    just_arrived: set[int] = set()

    # ── Step 1: forced arrivals (drones already in transit) ──────────────
    in_transit = [
        d for d in drones if d.in_transit_to and not d.delivered
    ]
    for d in sorted(in_transit, key=lambda x: x.id):
        dest = d.in_transit_to
        # These MUST arrive; capacity was guaranteed when transit started
        entering[dest] = entering.get(dest, 0) + 1
        d.current_zone = dest
        d.path_index += 1
        d.in_transit_to = ""
        d.in_transit_from = ""
        move_reports.append((d.id, f"D{d.id}-{dest}"))
        just_arrived.add(d.id)
        if dest == end_zone:
            d.delivered = True

    # ── Step 2: voluntary moves (ordered by drone ID = priority) ─────────
    stationary = [
        d for d in drones
        if not d.in_transit_to
        and not d.delivered
        and d.current_zone
        and d.id not in just_arrived  # cannot move on restricted-arrival turn
    ]
    stationary.sort(key=lambda x: x.id)

    for d in stationary:
        # Check whether there is a next step in the path
        next_idx = d.path_index + 1
        if next_idx >= len(d.path):
            continue  # already at final zone (edge case)

        next_zone = d.path[next_idx]
        zone_obj = graph.zones.get(next_zone)
        if zone_obj is None:
            continue

        if zone_obj.zone_type == ZoneType.BLOCKED:
            continue  # impassable

        conn = graph.get_connection(d.current_zone, next_zone)
        if conn is None:
            continue  # no connection (should not happen with valid paths)

        conn_key = graph.get_connection_key(d.current_zone, next_zone)
        if conn_key is None:
            continue

        # Check connection capacity for this turn
        if conn_usage.get(conn_key, 0) >= conn.max_link_capacity:
            continue  # connection saturated

        is_end = next_zone == end_zone

        if zone_obj.zone_type == ZoneType.RESTRICTED:
            # Two-turn transit: drone leaves source now, arrives next turn
            if not is_end:
                # Estimate next-turn occupancy of restricted zone
                after_this = (
                    occupancy.get(next_zone, 0)
                    - leaving.get(next_zone, 0)
                    + entering.get(next_zone, 0)
                )
                # Add drones already committed to transit there this turn
                projected = (
                    after_this
                    + transit_to.get(next_zone, 0)
                    + 1
                )
                if projected > zone_obj.max_drones:
                    continue  # no room next turn

            # Commit transit
            leaving[d.current_zone] = (
                leaving.get(d.current_zone, 0) + 1
            )
            conn_usage[conn_key] = conn_usage.get(conn_key, 0) + 1
            transit_to[next_zone] = transit_to.get(next_zone, 0) + 1

            from_z = d.current_zone
            d.in_transit_from = from_z
            d.in_transit_to = next_zone
            d.current_zone = ""
            move_reports.append(
                (d.id, f"D{d.id}-{from_z}-{next_zone}")
            )

        else:
            # Normal / priority: one-turn move
            if not is_end:
                net = (
                    occupancy.get(next_zone, 0)
                    - leaving.get(next_zone, 0)
                    + entering.get(next_zone, 0)
                    + 1
                )
                if net > zone_obj.max_drones:
                    continue  # zone full

            leaving[d.current_zone] = (
                leaving.get(d.current_zone, 0) + 1
            )
            conn_usage[conn_key] = conn_usage.get(conn_key, 0) + 1
            entering[next_zone] = entering.get(next_zone, 0) + 1

            d.current_zone = next_zone
            d.path_index += 1
            move_reports.append((d.id, f"D{d.id}-{next_zone}"))
            if next_zone == end_zone:
                d.delivered = True

    move_reports.sort(key=lambda x: x[0])
    return [r for _, r in move_reports]


class Simulator:
    """Runs the discrete-turn simulation for all drones."""

    def run(
        self,
        graph: Graph,
        paths: list[list[str]],
        nb_drones: int,
    ) -> list[str]:
        """Simulate drone movements and return one output line per turn.

        Each turn line lists moving drones separated by spaces.
        Drones that do not move are omitted.
        Turns where no drone moves are omitted.

        Args:
            graph:     The flight-network graph.
            paths:     One path per drone (output of plan_all_routes).
            nb_drones: Total number of drones.

        Returns:
            List of turn output strings.
        """
        # Initialise drones at the start zone
        drones: list[Drone] = []
        start = graph.start_zone
        for i in range(1, nb_drones + 1):
            path = paths[i - 1] if i - 1 < len(paths) else [start]
            d = Drone(id=i, path=path, current_zone=start)
            drones.append(d)

        output_lines: list[str] = []

        for _ in range(MAX_TURNS):
            all_delivered = all(d.delivered for d in drones)
            if all_delivered:
                break

            turn_moves = _process_turn(drones, graph)
            if turn_moves:
                output_lines.append(" ".join(turn_moves))

        return output_lines
