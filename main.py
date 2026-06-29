from src import *
from typing import Dict, List
import sys


def main() -> None:
    map_file = sys.argv[1]
    try:
        parser = Parser(map_file)

        graph = parser.parse()
        scheduler = Scheduler(graph)
        all_paths = scheduler.schedule_drones(parser.nb_drones, 10)
        output_builder = OutputBuilder()
        output_lines = output_builder.build_output(all_paths)
        for output_line in output_lines:
            print(output_line)
    except Exception as e:
        print(e)


if __name__ == '__main__':
    main()
