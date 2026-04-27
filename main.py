from src import Zone, Connection

hub = Zone("hub", 0, 0, "normal")
roof1 = Zone("roof1", 3, 4, "normal")

road = Connection(hub, roof1, 2)
print(road.zone1.name)
print(road.zone2.name)
print(road.max_link_capacity)
print(road.current_drones_using)
