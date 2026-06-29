import sys
from src import Parser, Scheduler, OutputBuilder, Validator


def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        print("Example: python main.py maps/01_linear_path.txt")
        sys.exit(1)

    map_file = sys.argv[1]

    # ===== 1. Parse the map file =====
    print(f"Parsing map: {map_file}")
    parser = Parser(map_file)
    graph = parser.parse()

    print(f"  Drones: {parser.nb_drones}")
    print(f"  Start: {graph.start_zone.name}")
    print(f"  End: {graph.end_zone.name}")
    print(f"  Zones: {len(graph.zones)}")
    print(f"  Connections: {len(graph.connections)}")

    # Check if a path exists from start to end
    if not graph.has_path(graph.start_zone, graph.end_zone):
        print("ERROR: No path exists from start to end zone!")
        sys.exit(1)

    # ===== 2. Schedule drones =====
    print("\nScheduling drones...")
    scheduler = Scheduler(graph)
    max_turns = 200

    try:
        all_paths = scheduler.schedule_drones(
            start_zone=graph.start_zone,
            end_zone=graph.end_zone,
            nb_drones=parser.nb_drones,
            max_turns=max_turns
        )
    except ValueError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

    print(f"  Scheduled {len(all_paths)} drones")

    # ===== 3. Validate paths =====
    print("\nValidating paths...")
    validator = Validator(graph)

    try:
        validator.validate_all(all_paths)
        print("  ✅ All paths are valid!")
    except ValueError as e:
        print(f"  ❌ Validation failed: {e}")
        sys.exit(1)

    # ===== 4. Generate output =====
    print("\nGenerating output...")
    output_builder = OutputBuilder()
    output_lines = output_builder.build_output(all_paths)

    # Calculate max turns (makespan)
    max_turn = 0
    for path in all_paths.values():
        for step in path:
            if step.turn > max_turn:
                max_turn = step.turn

    print(f"  Total turns: {max_turn}")
    print(f"  Output lines: {len(output_lines)}")
    print("\n" + "=" * 50)
    print("OUTPUT:")
    print("=" * 50)

    # Print the output
    for line in output_lines:
        print(line)

    print("=" * 50)
    print(f"✅ Done! Total turns: {max_turn}")


if __name__ == "__main__":
    main()