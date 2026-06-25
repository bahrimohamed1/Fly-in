from src import *
from typing import Dict, List


def main() -> None:
    start: Zone = Zone('start', 0, 0, 'normal', 3, None)
    zone_a: Zone = Zone('a', 1, 0, 'normal', 1, None)
    zone_r: Zone = Zone('r', 2, 0, 'restricted', 1, None)
    end: Zone = Zone('end', 3, 0, 'normal', 3, None)

    zones: Dict[str, Zone] = {
        'start': start,
        'a': zone_a,
        'r': zone_r,
        'end': end,
    }

    connections: List[Connection] = [
        Connection(start, zone_a),
        Connection(zone_a, zone_r),
        Connection(zone_r, end),
    ]

    graph: Graph = Graph(zones, connections, start, end)
    scheduler: Scheduler = Scheduler(graph)
    all_paths: Dict[int, List[PathStep]] = scheduler.schedule_drones(3, 20)
    validator: Validator = Validator(graph)
    validator.validate_all(all_paths)
    output_builder: OutputBuilder = OutputBuilder()
    output_line: List[str] = output_builder.build_output(all_paths)
    for line in output_line:
        print(line)


if __name__ == '__main__':
    main()
