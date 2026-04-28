from src import Zone, Connection, Drone

hub = Zone("hub", 0, 0, "normal")
roof1 = Zone("roof1", 3, 4, "normal", 2)

d1 = Drone(1, hub)
print(d1.get_position())  # Should print: (0, 0)
print(d1.current_zone.name)  # Should print: hub

d1.move_to(roof1)
print(d1.get_position())  # Should print: (3, 4)
print(d1.current_zone.name)  # Should print: roof1
