from . import Graph, ReservationTable, PathFinder, Zone, PathStep
from typing import Dict, List


class Scheduler:
    def __init__(self, graph: Graph) -> None:
        self.graph: Graph = graph
        self.reservation_table: ReservationTable = ReservationTable(self.graph)
        self.pathfinder: PathFinder = PathFinder(
            self.graph, self.reservation_table)

    def schedule_drones(self,
                        start_zone: Zone,
                        end_zone: Zone,
                        nb_drones: int,
                        max_turns: int) -> Dict[int, List[PathStep]]:
        """
        Schedule all drones using multiple order attempts and retry with
        increasing max_turns if needed.
        """
        # Try different drone orders
        orders = self._generate_orders(nb_drones)

        for order in orders:
            print(f"Trying order: {order}")
            try:
                # Reset reservation table for each attempt
                self.reservation_table = ReservationTable(self.graph)
                self.pathfinder = PathFinder(
                    self.graph, self.reservation_table)

                return self._schedule_with_order(
                    start_zone, end_zone, order, max_turns
                )
            except ValueError as e:
                print(f"  Order failed: {e}")
                continue

        # If all orders fail, try with increasing max_turns
        print("All orders failed, retrying with increased max_turns...")
        return self._schedule_with_retry(
            start_zone, end_zone, nb_drones, max_turns)

    def _generate_orders(self, nb_drones: int) -> List[List[int]]:
        """
        Generate different drone orders to try.
        """
        drone_ids = list(range(1, nb_drones + 1))
        orders = []

        # Order 1: Normal order (1, 2, 3, ...)
        orders.append(drone_ids.copy())

        # Order 2: Reverse order (n, n-1, ...)
        orders.append(drone_ids.copy()[::-1])

        # Order 3: Alternating (1, 3, 5, ..., 2, 4, 6, ...)
        odd = [i for i in drone_ids if i % 2 == 1]
        even = [i for i in drone_ids if i % 2 == 0]
        orders.append(odd + even)

        # Order 4: Alternating reverse (even first, then odd)
        orders.append(even + odd)

        # Order 5: Middle out (3, 4, 2, 5, 1, 6, ...)
        if nb_drones > 2:
            middle = nb_drones // 2
            left = drone_ids[:middle][::-1]
            right = drone_ids[middle:]
            orders.append(left + right)

        # Order 6: Random shuffle (if more than 2 drones)
        if nb_drones > 2:
            import random
            shuffled = drone_ids.copy()
            random.shuffle(shuffled)
            orders.append(shuffled)

        return orders

    def _schedule_with_order(self,
                             start_zone: Zone,
                             end_zone: Zone,
                             order: List[int],
                             max_turns: int) -> Dict[int, List[PathStep]]:
        """
        Schedule drones in a specific order.
        """
        all_paths: Dict[int, List[PathStep]] = {}

        for drone_id in order:
            path = self.pathfinder.find_path(start_zone, end_zone, max_turns)

            if not path:
                raise ValueError(f"No path found for drone {drone_id}")

            self.reservation_table.reserve_path(path)
            all_paths[drone_id] = path

        return all_paths

    def _schedule_with_retry(self,
                             start_zone: Zone,
                             end_zone: Zone,
                             nb_drones: int,
                             max_turns: int) -> Dict[int, List[PathStep]]:
        """
        Retry scheduling with increasing max_turns.
        """
        while max_turns < 2000:
            print(f"Retrying with max_turns={max_turns}")
            # Reset reservation table
            self.reservation_table = ReservationTable(self.graph)
            self.pathfinder = PathFinder(self.graph, self.reservation_table)

            # Try all orders again with the current max_turns.
            # If every order fails, increase max_turns and retry.
            for order in self._generate_orders(nb_drones):
                try:
                    return self._schedule_with_order(
                        start_zone, end_zone, order, max_turns
                    )
                except ValueError:
                    continue

            max_turns += 50

        raise ValueError("No valid schedule found after multiple retries")
