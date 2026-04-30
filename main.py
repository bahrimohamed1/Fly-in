from src import Zone, Connection, Drone, Parser

# print()
# parser = Parser("maps/easy/01_linear_path.txt")
# parser.parse()

# print(f"Number of drones: {parser.nb_drones}")
# print(f"Hubs: {parser.hubs}")
# print(f"Connections: {parser.connections}")

# parsing = Parser("maps/easy/01_linear_path.txt")
# parsing.parse()
zone = Zone('start', 0, 0, None, None, None)
print(Drone(1, zone))
