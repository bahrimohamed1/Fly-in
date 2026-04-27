"""Pathfinding for the Fly-in drone routing simulation.

Uses Dijkstra with zone-type costs and per-drone usage penalties to
distribute drones across multiple paths.
"""

import heapq
from graph import Graph, ZoneType

# Cost to traverse (enter) a zone, by type
ZONE_COSTS: dict[ZoneType, float] = {
    ZoneType.PRIORITY: 0.5,
    ZoneType.NORMAL: 1.0,
    ZoneType.RESTRICTED: 2.0,
    ZoneType.BLOCKED: float("inf"),
}

# Penalty added per existing drone using a zone (path diversification)
USAGE_PENALTY: float = 1.0


def find_path(
    graph: Graph,
    start: str,
    end: str,
    drone_id: int,
    usage_counts: dict[str, int],
) -> list[str]:
    """Return the lowest-cost path from start to end using Dijkstra.

    Zone costs are adjusted by usage_counts to steer this drone away from
    zones heavily used by previously routed drones.  Blocked zones are
    never entered.

    Args:
        graph:        The flight-network graph.
        start:        Name of the starting zone.
        end:          Name of the destination zone.
        drone_id:     1-indexed drone identifier (unused in cost; kept for
                      interface consistency and future extensions).
        usage_counts: Mapping of zone name → number of previously routed
                      drones that pass through that zone.

    Returns:
        Ordered list of zone names from start to end (inclusive).
        Returns [start, end] as a minimal fallback if no path is found.
    """
    _ = drone_id  # reserved for future use

    dist: dict[str, float] = {start: 0.0}
    prev: dict[str, str | None] = {start: None}
    # heap entries: (cost, zone_name)
    heap: list[tuple[float, str]] = [(0.0, start)]

    while heap:
        cost, u = heapq.heappop(heap)
        if cost > dist.get(u, float("inf")):
            continue
        if u == end:
            break
        for v in graph.get_neighbors(u):
            zone = graph.zones.get(v)
            if zone is None:
                continue
            base = ZONE_COSTS.get(zone.zone_type, float("inf"))
            if base == float("inf"):
                continue  # never enter blocked zones
            penalty = USAGE_PENALTY * usage_counts.get(v, 0)
            new_cost = cost + base + penalty
            if new_cost < dist.get(v, float("inf")):
                dist[v] = new_cost
                prev[v] = u
                heapq.heappush(heap, (new_cost, v))

    # Reconstruct path
    if end not in prev:
        # No path found – return trivial two-node path as fallback
        return [start, end]

    path: list[str] = []
    node: str | None = end
    while node is not None:
        path.append(node)
        node = prev[node]
    path.reverse()
    return path


def plan_all_routes(
    graph: Graph,
    start: str,
    end: str,
    nb_drones: int,
) -> list[list[str]]:
    """Compute one path per drone, diversifying across the network.

    Each successive drone's path is computed with usage penalties that
    reflect how many previous drones already pass through each zone.
    This steers later drones onto alternate routes.

    Args:
        graph:     The flight-network graph.
        start:     Name of the start hub.
        end:       Name of the end hub.
        nb_drones: Total number of drones to route.

    Returns:
        List of nb_drones paths; each path is an ordered list of zone
        names from start to end.
    """
    usage_counts: dict[str, int] = {}
    paths: list[list[str]] = []

    for i in range(1, nb_drones + 1):
        path = find_path(graph, start, end, i, usage_counts)
        paths.append(path)
        for zone_name in path:
            usage_counts[zone_name] = usage_counts.get(zone_name, 0) + 1

    return paths
