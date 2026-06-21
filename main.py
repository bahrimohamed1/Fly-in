from src import Zone, Connection, Graph, Parser, ReservationTable, DronePath, PathStep, PathFinder, Scheduler
from typing import Dict, List


def test_find_path():
    # --- Setup graph (same as before) ---
    start_zone = Zone('start', 0, 0, 'normal', 9, "Yellow")
    zone_a = Zone('A', 1, 0, 'normal', 1, "Green")
    zone_r = Zone('R', 2, 0, 'restricted', 1, "Blue")
    end_zone = Zone('end', 3, 0, 'normal', 9, "red")

    conn_start_a = Connection(start_zone, zone_a, 1)
    conn_a_r = Connection(zone_a, zone_r, 1)
    conn_r_end = Connection(zone_r, end_zone, 1)

    zones: Dict[str, Zone] = {
        'start': start_zone,
        'A': zone_a,
        'R': zone_r,
        'end': end_zone
    }
    connections: List[Connection] = [conn_start_a, conn_a_r, conn_r_end]

    graph = Graph(zones, connections)
    
    main_scheduler: Scheduler = Scheduler(graph)
    all_paths: Dict[int, List[PathStep]] = main_scheduler.schedule_drones(start_zone, end_zone, 3, 10)
    for id, path in all_paths.items():
        print(f"D{id}:")
        for step in path:
            print(f"    Turn {step.turn}: {step.name}")    


def main():
    start_zone: Zone = Zone('start', 0, 0, 'normal', 9, None)
    zone_a: Zone = Zone('A', 1, 0, 'normal', 1, None)
    zone_r: Zone = Zone('R', 2, 0, 'restricted', 1, None)
    end_zone: Zone = Zone('end', 3, 0, 'normal', 9, None)

    connection_1: Connection = Connection(start_zone, zone_a)
    connection_2: Connection = Connection(zone_a, zone_r)
    connection_3: Connection = Connection(zone_r, end_zone)

    zones: Dict[str, Zone] = {
        'start': start_zone,
        'A': zone_a,
        'R': zone_r,
        'end': end_zone
    }
    connections: List[Connection] = [
        connection_1,
        connection_2,
        connection_3
    ]

    graph: Graph = Graph(zones, connections)

    reservation_table: ReservationTable = ReservationTable(graph)

    path_steps: List[PathStep] = [
        PathStep(0, 'zone', start_zone.name),
        PathStep(1, 'zone', zone_a.name),
        PathStep(2, 'connection', connection_2.key()),
        PathStep(3, 'zone', zone_r.name),
        PathStep(4, 'zone', end_zone.name)
    ]

    reservation_table.reserve_path(path_steps)

    print(f"{start_zone.name} @ 0 : {reservation_table.get_zone_count(start_zone.name, 0)}")
    print()
    print('Turn 1:')
    print(f"{start_zone.name} @ 1 : {reservation_table.get_zone_count(start_zone.name, 1)}")
    print(f"{zone_a.name} @ 1 : {reservation_table.get_zone_count(zone_a.name, 1)}")
    print()
    print('Turn 2:')
    print(f"{zone_a.name} @ 2 : {reservation_table.get_zone_count(zone_a.name, 2)}")
    print(f"{zone_r.name} @ 2 : {reservation_table.get_zone_count(zone_r.name, 2)}")
    print()
    print('Turn 3:')
    print(f"{zone_r.name} @ 3 : {reservation_table.get_zone_count(zone_r.name, 3)}")
    print(f"{end_zone.name} @ 3 : {reservation_table.get_zone_count(end_zone.name, 3)}")
    print()
    print('Turn 4:')
    print(f"{end_zone.name} @ 4 : {reservation_table.get_zone_count(end_zone.name, 4)}")
    print()
    print()

    print(
        f"start-A @ 1 : {reservation_table.get_connection_count('start-A', 1)}"
    )

    print(
        f"A-R @ 2 : {reservation_table.get_connection_count('A-R', 2)}")
    print(f"A-R @ 3: {reservation_table.get_connection_count('A-R', 3)}")
    print(f"R-end @ 4: {reservation_table.get_connection_count('R-end', 4)}")


if __name__ == '__main__':
    test_find_path()
