"""CLI entry point for the Fly-in drone routing simulation."""

import argparse
import sys

from graph import Graph
from parser import parse_map
from renderer import render_debug_map, render_turn
from router import plan_all_routes
from simulator import MAX_TURNS, Drone, Simulator, _process_turn


def _build_drone_positions(
    drones: list[Drone],
) -> dict[str, str]:
    """Build a zone → drone-labels mapping for the debug renderer."""
    positions: dict[str, str] = {}
    for d in drones:
        if d.delivered:
            continue
        key = d.current_zone if d.current_zone else (
            f"{d.in_transit_from}->{d.in_transit_to}"
        )
        if key:
            existing = positions.get(key, "")
            positions[key] = (
                f"{existing} D{d.id}" if existing else f"D{d.id}"
            )
    return positions


def _run_visual(
    graph: Graph,
    paths: list[list[str]],
    nb_drones: int,
    debug: bool,
) -> None:
    """Run simulation and print coloured / debug output.

    Unlike the plain run path, this version steps turn-by-turn so it can
    show per-turn map state when ``--debug`` is active.
    """
    start = graph.start_zone
    drones: list[Drone] = []
    for i in range(1, nb_drones + 1):
        path = paths[i - 1] if i - 1 < len(paths) else [start]
        drones.append(Drone(id=i, path=path, current_zone=start))

    for turn_num in range(1, MAX_TURNS + 1):
        if all(d.delivered for d in drones):
            break

        if debug:
            positions = _build_drone_positions(drones)
            print(render_debug_map(graph, positions, turn_num))

        turn_moves = _process_turn(drones, graph)
        if turn_moves:
            raw_line = " ".join(turn_moves)
            positions = _build_drone_positions(drones)
            print(render_turn(raw_line, graph, positions))


def main() -> None:
    """Parse arguments, run the simulation, and print output."""
    parser = argparse.ArgumentParser(
        prog="main.py",
        description="Fly-in drone routing simulator",
    )
    parser.add_argument(
        "map_file",
        help="Path to the map definition file",
    )
    parser.add_argument(
        "--visual",
        action="store_true",
        help="Enable ANSI colour output",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Show per-turn ASCII map state (implies --visual)",
    )
    args = parser.parse_args()

    if args.debug:
        args.visual = True

    graph, nb_drones = parse_map(args.map_file)

    paths = plan_all_routes(graph, graph.start_zone, graph.end_zone, nb_drones)

    if args.visual:
        _run_visual(graph, paths, nb_drones, args.debug)
    else:
        sim = Simulator()
        output_lines = sim.run(graph, paths, nb_drones)
        for line in output_lines:
            print(line)

    sys.exit(0)


if __name__ == "__main__":
    main()
