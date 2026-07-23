import sys
import time
from src import Parser, Scheduler, OutputBuilder, Validator


def main():
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        print("Example: python main.py maps/01_linear_path.txt")
        sys.exit(1)

    map_file = sys.argv[1]
    max_turns = 200  # Default max turns

    print("=" * 60)
    print(f"Testing map: {map_file}")
    print("=" * 60)

    # ===== 1. Parse the map =====
    print("\n[1] Parsing map...")
    try:
        parser = Parser(map_file)
        graph = parser.parse()
        print(f"  ✅ Parsed successfully")
        print(f"     Drones: {parser.nb_drones}")
        print(f"     Zones: {len(graph.zones)}")
        print(f"     Connections: {len(graph.connections)}")
        print(f"     Start: {graph.start_zone.name}")
        print(f"     End: {graph.end_zone.name}")
    except Exception as e:
        print(f"  ❌ Parse error: {e}")
        sys.exit(1)

    # ===== 2. Check if path exists =====
    print("\n[2] Checking path existence...")
    if not graph.has_path(graph.start_zone, graph.end_zone):
        print("  ❌ No path exists from start to end zone!")
        sys.exit(1)
    print("  ✅ Path exists")

    # ===== 3. Get shortest path distance =====
    print("\n[3] Calculating shortest path distance...")
    dist = graph.get_distance(graph.start_zone.name, graph.end_zone.name)
    if dist == float('inf'):
        print("  ❌ No path found!")
        sys.exit(1)
    print(f"  ✅ Shortest distance: {dist} turns")

    # ===== 4. Schedule drones =====
    print(f"\n[4] Scheduling {parser.nb_drones} drones (max_turns={max_turns})...")
    start_time = time.time()
    scheduler = Scheduler(graph)

    try:
        all_paths = scheduler.schedule_drones(
            start_zone=graph.start_zone,
            end_zone=graph.end_zone,
            nb_drones=parser.nb_drones,
            max_turns=max_turns
        )
        elapsed = time.time() - start_time
        print(f"  ✅ Scheduled {len(all_paths)} drones in {elapsed:.2f}s")

        # Calculate makespan (max turns)
        max_turn = 0
        for path in all_paths.values():
            for step in path:
                if step.turn > max_turn:
                    max_turn = step.turn
        print(f"     Makespan: {max_turn} turns")

    except Exception as e:
        print(f"  ❌ Scheduling failed: {e}")
        sys.exit(1)

    # ===== 5. Validate paths =====
    print("\n[5] Validating paths...")
    validator = Validator(graph)
    try:
        validator.validate_all(all_paths)
        print("  ✅ All paths are valid!")
    except Exception as e:
        print(f"  ❌ Validation failed: {e}")
        sys.exit(1)

    # ===== 6. Generate output =====
    print("\n[6] Generating output...")
    output_builder = OutputBuilder()
    output_lines = output_builder.build_output(all_paths)

    print(f"  ✅ Generated {len(output_lines)} lines of output")
    print("\n" + "=" * 60)
    print("OUTPUT:")
    print("=" * 60)

    # Print first 20 lines (or all if <= 20)
    if len(output_lines) <= 20:
        for line in output_lines:
            print(line)
    else:
        for i, line in enumerate(output_lines[:10]):
            print(line)
        print("  ...")
        for line in output_lines[-5:]:
            print(line)

    print("=" * 60)

    # ===== 7. Summary =====
    print("\n📊 SUMMARY")
    print("-" * 40)
    print(f"  Map: {map_file}")
    print(f"  Drones: {parser.nb_drones}")
    print(f"  Turns: {max_turn}")
    print(f"  Output lines: {len(output_lines)}")
    print(f"  Time: {elapsed:.2f}s")
    print("-" * 40)

    # Map-specific benchmarks
    benchmarks = {
        "01_linear_path.txt": 6,
        "02_simple_fork.txt": 8,
        "01_dead_end_trap.txt": 12,
        "02_circular_loop.txt": 15,
        "01_maze_nightmare.txt": 30,
        "02_capacity_hell.txt": 35,
        "03_ultimate_challenge.txt": 45,
        "impossible_dream.txt": 45,
    }

    # Get benchmark for current map
    map_name = map_file.split("/")[-1]
    benchmark = benchmarks.get(map_name, 60)

    if max_turn <= benchmark:
        print(f"  🏆 Excellent! Beat the benchmark ({max_turn} ≤ {benchmark})")
    else:
        print(f"  ⚠️ Below benchmark ({max_turn} > {benchmark})")


if __name__ == "__main__":
    main()