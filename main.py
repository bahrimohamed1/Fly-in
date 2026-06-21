from src import *
from typing import Dict, List


def test_find_path():
    start_zone = Zone('start', 0, 0, 'normal', 9, "Yellow")
    zone_a = Zone('A', 1, 0, 'normal', 1, "Green")
    zone_r = Zone('R', 2, 0, 'restricted', 1, "Blue")
    end_zone = Zone('goal', 3, 0, 'normal', 9, "red")

    conn_start_a = Connection(start_zone, zone_a, 1)
    conn_a_r = Connection(zone_a, zone_r, 1)
    conn_r_end = Connection(zone_r, end_zone, 1)

    zones: Dict[str, Zone] = {
        'start': start_zone,
        'A': zone_a,
        'R': zone_r,
        'goal': end_zone
    }
    connections: List[Connection] = [conn_start_a, conn_a_r, conn_r_end]

    graph = Graph(zones, connections, start_zone, end_zone)
    
    main_scheduler: Scheduler = Scheduler(graph)
    all_paths: Dict[int, List[PathStep]] = main_scheduler.schedule_drones(3, 10)

    output = OutputBuilder().build_output(all_paths)
    print(*output, sep='\n')

    # for id, path in all_paths.items():
    #     print(f"D{id}:")
    #     for step in path:
    #         print(f"    {step.turn} {step.kind} {step.name}")

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

def impossible_map():
    # === LAYER 0: The Nightmare Begins ===
    start = Zone('start', 0, 0, 'normal', 25, 'green')

    # Single-file entry gates
    gate_hell1 = Zone('gate_hell1', 1, 0, 'normal', 1, 'red')
    gate_hell2 = Zone('gate_hell2', 2, 0, 'normal', 1, 'red')
    gate_hell3 = Zone('gate_hell3', 3, 0, 'normal', 1, 'red')
    gate_hell4 = Zone('gate_hell4', 4, 0, 'normal', 1, 'red')
    gate_hell5 = Zone('gate_hell5', 5, 0, 'normal', 1, 'red')

    # === LAYER 1: The Maze of Despair ===
    maze_trap_a1 = Zone('maze_trap_a1', 1, 1, 'normal', 1, 'purple')
    maze_trap_a2 = Zone('maze_trap_a2', 2, 1, 'normal', 1, 'purple')
    maze_trap_a3 = Zone('maze_trap_a3', 3, 1, 'normal', 1, 'purple')
    maze_dead_a = Zone('maze_dead_a', 4, 1, 'normal', 1, 'black')

    maze_trap_b1 = Zone('maze_trap_b1', 1, -1, 'normal', 1, 'purple')
    maze_trap_b2 = Zone('maze_trap_b2', 2, -1, 'normal', 1, 'purple')
    maze_trap_b3 = Zone('maze_trap_b3', 3, -1, 'normal', 1, 'purple')
    maze_dead_b = Zone('maze_dead_b', 4, -1, 'normal', 1, 'black')

    maze_loop1 = Zone('maze_loop1', 1, 2, 'restricted', 1, 'brown')
    maze_loop2 = Zone('maze_loop2', 2, 2, 'restricted', 1, 'brown')
    maze_loop3 = Zone('maze_loop3', 3, 2, 'restricted', 1, 'brown')
    maze_loop4 = Zone('maze_loop4', 4, 2, 'restricted', 1, 'brown')
    maze_loop5 = Zone('maze_loop5', 5, 2, 'restricted', 1, 'brown')
    maze_loop6 = Zone('maze_loop6', 5, 1, 'restricted', 1, 'brown')

    # === LAYER 2: The Capacity Nightmare ===
    micro_gate1 = Zone('micro_gate1', 6, 0, 'normal', 1, 'orange')
    micro_gate2 = Zone('micro_gate2', 7, 0, 'normal', 1, 'orange')
    micro_gate3 = Zone('micro_gate3', 8, 0, 'normal', 1, 'orange')

    overflow_hell1 = Zone('overflow_hell1', 6, 1, 'restricted', 2, 'maroon')
    overflow_hell2 = Zone('overflow_hell2', 7, 1, 'restricted', 2, 'maroon')
    overflow_hell3 = Zone('overflow_hell3', 8, 1, 'restricted', 2, 'maroon')
    overflow_hell4 = Zone('overflow_hell4', 6, -1, 'restricted', 2, 'maroon')
    overflow_hell5 = Zone('overflow_hell5', 7, -1, 'restricted', 2, 'maroon')
    overflow_hell6 = Zone('overflow_hell6', 8, -1, 'restricted', 2, 'maroon')

    # === LAYER 3: The False Hope Section ===
    false_hope1 = Zone('false_hope1', 9, 0, 'priority', 3, 'gold')
    false_hope2 = Zone('false_hope2', 10, 0, 'priority', 2, 'gold')
    false_hope3 = Zone('false_hope3', 11, 0, 'priority', 1, 'gold')

    priority_trap1 = Zone('priority_trap1', 9, 1, 'priority', 1, 'gold')
    priority_trap2 = Zone('priority_trap2', 10, 1, 'priority', 1, 'gold')
    priority_dead = Zone('priority_dead', 11, 1, 'normal', 1, 'black')

    priority_trap3 = Zone('priority_trap3', 9, -1, 'priority', 1, 'gold')
    priority_trap4 = Zone('priority_trap4', 10, -1, 'priority', 1, 'gold')
    priority_dead2 = Zone('priority_dead2', 11, -1, 'normal', 1, 'black')

    # === LAYER 4: The Convergence Hell ===
    conv_restricted1 = Zone('conv_restricted1', 12, 2, 'restricted', 1, 'darkred')
    conv_restricted2 = Zone('conv_restricted2', 13, 2, 'restricted', 1, 'darkred')
    conv_restricted3 = Zone('conv_restricted3', 14, 2, 'restricted', 1, 'darkred')

    conv_restricted4 = Zone('conv_restricted4', 12, 0, 'restricted', 1, 'darkred')
    conv_restricted5 = Zone('conv_restricted5', 13, 0, 'restricted', 1, 'darkred')
    conv_restricted6 = Zone('conv_restricted6', 14, 0, 'restricted', 1, 'darkred')

    conv_restricted7 = Zone('conv_restricted7', 12, -2, 'restricted', 1, 'darkred')
    conv_restricted8 = Zone('conv_restricted8', 13, -2, 'restricted', 1, 'darkred')
    conv_restricted9 = Zone('conv_restricted9', 14, -2, 'restricted', 1, 'darkred')

    # === LAYER 5: The Final Gauntlet of Doom ===
    final_merge = Zone('final_merge', 15, 0, 'normal', 5, 'violet')
    final_torture1 = Zone('final_torture1', 16, 0, 'normal', 2, 'crimson')
    final_torture2 = Zone('final_torture2', 17, 0, 'normal', 1, 'crimson')
    final_torture3 = Zone('final_torture3', 18, 0, 'normal', 1, 'crimson')
    final_torture4 = Zone('final_torture4', 19, 0, 'normal', 1, 'crimson')
    final_torture5 = Zone('final_torture5', 20, 0, 'normal', 1, 'crimson')

    impossible_goal = Zone('impossible_goal', 21, 0, 'normal', 25, 'rainbow')

    zones = {
    'start': start,
    'gate_hell1': gate_hell1,
    'gate_hell2': gate_hell2,
    'gate_hell3': gate_hell3,
    'gate_hell4': gate_hell4,
    'gate_hell5': gate_hell5,
    'maze_trap_a1': maze_trap_a1,
    'maze_trap_a2': maze_trap_a2,
    'maze_trap_a3': maze_trap_a3,
    'maze_dead_a': maze_dead_a,
    'maze_trap_b1': maze_trap_b1,
    'maze_trap_b2': maze_trap_b2,
    'maze_trap_b3': maze_trap_b3,
    'maze_dead_b': maze_dead_b,
    'maze_loop1': maze_loop1,
    'maze_loop2': maze_loop2,
    'maze_loop3': maze_loop3,
    'maze_loop4': maze_loop4,
    'maze_loop5': maze_loop5,
    'maze_loop6': maze_loop6,
    'micro_gate1': micro_gate1,
    'micro_gate2': micro_gate2,
    'micro_gate3': micro_gate3,
    'overflow_hell1': overflow_hell1,
    'overflow_hell2': overflow_hell2,
    'overflow_hell3': overflow_hell3,
    'overflow_hell4': overflow_hell4,
    'overflow_hell5': overflow_hell5,
    'overflow_hell6': overflow_hell6,
    'false_hope1': false_hope1,
    'false_hope2': false_hope2,
    'false_hope3': false_hope3,
    'priority_trap1': priority_trap1,
    'priority_trap2': priority_trap2,
    'priority_dead': priority_dead,
    'priority_trap3': priority_trap3,
    'priority_trap4': priority_trap4,
    'priority_dead2': priority_dead2,
    'conv_restricted1': conv_restricted1,
    'conv_restricted2': conv_restricted2,
    'conv_restricted3': conv_restricted3,
    'conv_restricted4': conv_restricted4,
    'conv_restricted5': conv_restricted5,
    'conv_restricted6': conv_restricted6,
    'conv_restricted7': conv_restricted7,
    'conv_restricted8': conv_restricted8,
    'conv_restricted9': conv_restricted9,
    'final_merge': final_merge,
    'final_torture1': final_torture1,
    'final_torture2': final_torture2,
    'final_torture3': final_torture3,
    'final_torture4': final_torture4,
    'final_torture5': final_torture5,
    'impossible_goal': impossible_goal,
}

    connections = [
        # Layer 0
        Connection(start, gate_hell1, 1),
        Connection(gate_hell1, gate_hell2, 1),
        Connection(gate_hell2, gate_hell3, 1),
        Connection(gate_hell3, gate_hell4, 1),
        Connection(gate_hell4, gate_hell5, 1),

        # Layer 1
        Connection(gate_hell1, maze_trap_a1, 1),
        Connection(gate_hell2, maze_trap_b1, 1),
        Connection(gate_hell3, maze_loop1, 1),
        Connection(maze_trap_a1, maze_trap_a2, 1),
        Connection(maze_trap_a2, maze_trap_a3, 1),
        Connection(maze_trap_a3, maze_dead_a, 1),
        Connection(maze_trap_b1, maze_trap_b2, 1),
        Connection(maze_trap_b2, maze_trap_b3, 1),
        Connection(maze_trap_b3, maze_dead_b, 1),
        Connection(maze_loop1, maze_loop2, 1),
        Connection(maze_loop2, maze_loop3, 1),
        Connection(maze_loop3, maze_loop4, 1),
        Connection(maze_loop4, maze_loop5, 1),
        Connection(maze_loop5, maze_loop6, 1),
        Connection(maze_loop6, maze_loop1, 1),

        # Escape routes from maze
        Connection(maze_trap_a2, micro_gate1, 1),
        Connection(maze_trap_b2, micro_gate1, 1),
        Connection(maze_loop3, micro_gate2, 1),

        # Layer 2
        Connection(gate_hell5, micro_gate1, 1),
        Connection(micro_gate1, micro_gate2, 1),
        Connection(micro_gate2, micro_gate3, 1),

        # Overflow hell
        Connection(micro_gate1, overflow_hell1, 1),
        Connection(micro_gate2, overflow_hell2, 1),
        Connection(micro_gate3, overflow_hell3, 1),
        Connection(micro_gate1, overflow_hell4, 1),
        Connection(micro_gate2, overflow_hell5, 1),
        Connection(micro_gate3, overflow_hell6, 1),
        Connection(overflow_hell1, overflow_hell2, 1),
        Connection(overflow_hell2, overflow_hell3, 1),
        Connection(overflow_hell4, overflow_hell5, 1),
        Connection(overflow_hell5, overflow_hell6, 1),
        Connection(overflow_hell3, false_hope1, 1),
        Connection(overflow_hell6, false_hope1, 1),

        # Layer 3
        Connection(micro_gate3, false_hope1, 1),
        Connection(false_hope1, false_hope2, 1),
        Connection(false_hope2, false_hope3, 1),

        # False hope traps
        Connection(false_hope1, priority_trap1, 1),
        Connection(false_hope2, priority_trap2, 1),
        Connection(false_hope3, priority_dead, 1),
        Connection(false_hope1, priority_trap3, 1),
        Connection(false_hope2, priority_trap4, 1),
        Connection(false_hope3, priority_dead2, 1),
        Connection(priority_trap1, priority_trap2, 1),
        Connection(priority_trap3, priority_trap4, 1),

        # Layer 4
        Connection(false_hope3, conv_restricted1, 1),
        Connection(false_hope3, conv_restricted4, 1),
        Connection(false_hope3, conv_restricted7, 1),
        Connection(conv_restricted1, conv_restricted2, 1),
        Connection(conv_restricted2, conv_restricted3, 1),
        Connection(conv_restricted4, conv_restricted5, 1),
        Connection(conv_restricted5, conv_restricted6, 1),
        Connection(conv_restricted7, conv_restricted8, 1),
        Connection(conv_restricted8, conv_restricted9, 1),
        Connection(conv_restricted3, final_merge, 1),
        Connection(conv_restricted6, final_merge, 1),
        Connection(conv_restricted9, final_merge, 1),

        # Layer 5
        Connection(final_merge, final_torture1, 1),
        Connection(final_torture1, final_torture2, 1),
        Connection(final_torture2, final_torture3, 1),
        Connection(final_torture3, final_torture4, 1),
        Connection(final_torture4, final_torture5, 1),
        Connection(final_torture5, impossible_goal, 1),

        # Emergency bypass routes
        Connection(overflow_hell1, conv_restricted1, 1),
        Connection(overflow_hell4, conv_restricted7, 1),
        Connection(priority_trap1, conv_restricted4, 1),
    ]
    
    graph = Graph(zones, connections, start, impossible_goal)
    scheduler = Scheduler(graph)
    
    all_paths = scheduler.schedule_drones(
        nb_drones=25,
        max_turns=45
    )
    
    output = OutputBuilder().build_output(all_paths)
    print(*output, sep='\n')
    

if __name__ == '__main__':
    # impossible_map()
    test_find_path()
