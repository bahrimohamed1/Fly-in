from src import Zone, Connection, Graph, Parser, ReservationTable, DronePath, PathStep
from typing import Dict, List


def main():
    parser: Parser = Parser('maps/easy/01_linear_path.txt')
    parser.parse()
    zones: Dict[str, Zone] = parser.get_zones()
    connections: List[Connection] = parser.get_connections()
    graph: Graph = Graph(zones, connections)
    # reservation_table: ReservationTable = ReservationTable(graph)
    path: DronePath = DronePath(1)
    path.add_step(PathStep(1, 'zone', 'start'))
    path.add_step(PathStep(2, 'connection', 'start-hellgate'))
    path.add_step(PathStep(3, 'zone', 'hellgate'))
    print(path.get_last_step().turn)
    print(path.get_last_step().kind)
    print(path.get_last_step().name)


if __name__ == '__main__':
    main()
