from .src import Zone, Connection, Drone
from typing import List


class Parser:
    def __init__(self, file_name: str):
        self.file_name: str = file_name
        self.nb_drones: int = 0
        self.hubs: List[Zone] = 

    # dict
    def parse(self):
        with open(self.file_name, "r") as file:
            for i, line in enumerate(1, file):
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line.startswith('nb_drones'):
                    try:
                        self.nb_drones = int(line.split(':', 1)[1].strip())
                        self.
                    except Exception:
                        print("")




kjsb = Parser()

kjsb.nb_drones