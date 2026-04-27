from src import Zone, Connection

hub = Zone("hub", 0, 0, "normal")
roof1 = Zone("roof1", 3, 4, "normal")

road = Connection(hub, roof1, 2)
print(road.zone1.name)  # Should print: hub
print(road.zone2.name)  # Should print: roof1
print(road.max_link_capacity)  # Should print: 2
print(road.current_drones_using)  # Should print: 0