from parser import Parser
from scheduler import Scheduler
from output_builder import OutputBuilder

import sys
import time
from typing import Any


def main() -> Any:
    # Check command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <map_file>")
        print("Example: python main.py maps/01_linear_path.txt")
        sys.exit(1)

    map_file = sys.argv[1]
    max_turns = 200  # Default max turns

    # ===== 1. Parse the map =====
    try:
        parser = Parser(map_file)
        graph = parser.parse()

    except Exception as e:
        print(f"  ❌ Parse error: {e}")
        sys.exit(1)
        
    # ===== 2. Get shortest path distance =====
    dist = graph.get_distance(graph.start_zone.name, graph.end_zone.name)
    if dist == float('inf'):
        print("  ❌ No path found!")
        sys.exit(1)

    # ===== 3. Schedule drones =====
    scheduler = Scheduler(graph)

    try:
        all_paths = scheduler.schedule_drones(
            start_zone=graph.start_zone,
            end_zone=graph.end_zone,
            nb_drones=parser.nb_drones,
            max_turns=max_turns
        )

        # Calculate makespan (max turns)
        max_turn = 0
        for path in all_paths.values():
            for step in path:
                if step.turn > max_turn:
                    max_turn = step.turn

    except Exception as e:
        print(f"  ❌ Scheduling failed: {e}")
        sys.exit(1)

    # ===== 4. Generate output =====
    output_builder = OutputBuilder()
    output_lines = output_builder.build_output(all_paths)

    for line in output_lines:
        print(line)

    print("=" * 60)

    # ===== 5. Summary =====
    print("\n📊 SUMMARY")
    print("-" * 40)
    print(f"  Map: {map_file}")
    print(f"  Drones: {parser.nb_drones}")
    print(f"  Turns: {max_turn}")
    print(f"  Output lines: {len(output_lines)}")
    print("-" * 40)


if __name__ == "__main__":
    main()