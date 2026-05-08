from src import Zone, Connection, Graph, Parser, ReservationTable
from typing import Dict, List


def main():
    parser: Parser = Parser('maps/easy/01_linear_path.txt')
    parser.parse()
    zones: Dict[str, Zone] = parser.get_zones()
    connections: List[Connection] = parser.get_connections()
    graph: Graph = Graph(zones, connections)
    reservation_table: ReservationTable = ReservationTable(graph)
    print(reservation_table)


if __name__ == '__main__':
    main()
