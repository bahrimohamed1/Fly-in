from src.zone import Zone

hub = Zone("hub", 0, 0, "normal")  # max_drones=1, current=0
print(hub.can_drone_enter())  # True
print(hub.add_drone())  # Should return: True
print(hub.current_drones_count)  # Should be: 1
print(hub.can_drone_enter())  # Should be: False (now 1/1)
print(hub.add_drone())  # Should return: False (can't add, full!)
print(hub.current_drones_count)  # Should still be: 1