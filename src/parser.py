class Parser:
    def __init__(self, file_name: str):
        self.file_name: str = file_name

    def parse(self):
        with open(self.file_name, "r") as file:
            for line in file:
                line = line.strip()
                if line.startswith('#'):
                    continue
                if line.startswith('nb_drones'):
                    try:
                        nb_drones = int(line.split(':', 1)[1].strip())
                    except TypeError:
                        print("")
