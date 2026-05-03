from src import Zone, Connection, Graph, Parser
from typing import Dict, Tuple, List

def main():
    parser: Parser = Parser('maps/easy/01_linear_path.txt')
    parser.parse()
    zones: Dict[str, Zone] = parser.get_zones()
    connections: List[Connection] = parser.get_connections()
    graph: Graph = Graph(zones, connections)
    


if __name__ == '__main__':
    main()