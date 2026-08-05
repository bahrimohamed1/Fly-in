from graph import Graph
from path_step import PathStep
from reservation_table import ReservationTable
from zone import Zone
from path_finder import PathFinder

from typing import Dict, List


class Scheduler:
    """
    Schedule multiple drones from a start zone to an end zone.

    Drones are scheduled one at a time. After a path is found for a drone,
    all zones and connections used by that path are stored in a
    ``ReservationTable``. Later drones must then find paths that do not
    conflict with those existing reservations.

    Because scheduling drones greedily in only one order may fail, the
    scheduler tries several drone orders. If none succeed within the initial
    maximum-turn limit, it retries with progressively larger limits.

    Attributes:
        graph:
            Graph containing the zones and connections through which drones
            may travel.

        reservation_table:
            Stores zone and connection reservations for paths that have
            already been scheduled during the current attempt.

        pathfinder:
            Finds one valid path at a time while respecting the current
            reservation table.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the scheduler.

        A new empty reservation table is created for the graph, and a
        ``PathFinder`` is connected to that table.

        Args:
            graph:
                Graph on which all drones will be scheduled.
        """
        self.graph: Graph = graph

        self.reservation_table: ReservationTable = ReservationTable(
            self.graph
        )

        self.pathfinder: PathFinder = PathFinder(
            self.graph,
            self.reservation_table,
        )

    def schedule_drones(
        self,
        start_zone: Zone,
        end_zone: Zone,
        nb_drones: int,
        max_turns: int,
    ) -> Dict[int, List[PathStep]]:
        """
        Schedule all drones between two zones.

        Several drone orders are tested because paths are reserved
        sequentially. A path selected for an early drone may affect whether
        later drones can reach the destination.

        Each order starts with a fresh reservation table. The first order
        that successfully schedules every drone is returned.

        If all generated orders fail, scheduling is retried while increasing
        ``max_turns``.

        Args:
            start_zone:
                Zone from which every drone starts.

            end_zone:
                Destination zone for every drone.

            nb_drones:
                Total number of drones to schedule. Drone identifiers range
                from ``1`` through ``nb_drones``.

            max_turns:
                Initial maximum number of turns available to each path search.

        Returns:
            A dictionary mapping each drone identifier to its complete list
            of path steps.

            Example::

                {
                    1: [PathStep(...), PathStep(...)],
                    2: [PathStep(...), PathStep(...)],
                }

        Raises:
            ValueError:
                If no valid schedule can be found after trying all orders and
                increasing the maximum-turn limit.
        """
        # Generate several possible orders in which drones can be scheduled.
        orders = self._generate_orders(nb_drones)

        for order in orders:
            try:
                # Every order must begin with no existing reservations.
                self.reservation_table = ReservationTable(self.graph)

                self.pathfinder = PathFinder(
                    self.graph,
                    self.reservation_table,
                )

                return self._schedule_with_order(
                    start_zone,
                    end_zone,
                    order,
                    max_turns,
                )

            except ValueError as error:
                print(f"  Order failed: {error}")
                continue

        # None of the generated orders worked with the original turn limit.
        return self._schedule_with_retry(
            start_zone,
            end_zone,
            nb_drones,
            max_turns,
        )

    def _generate_orders(
        self,
        nb_drones: int,
    ) -> List[List[int]]:
        """
        Generate different drone scheduling orders.

        Scheduling is sequential, so changing which drone is assigned first
        can produce a different set of reservations. Several ordering
        strategies are therefore generated to reduce the chance that one
        unlucky greedy order prevents a valid complete schedule.

        Generated strategies include:

        1. Normal ascending order.
        2. Reverse descending order.
        3. Odd identifiers followed by even identifiers.
        4. Even identifiers followed by odd identifiers.
        5. A middle-oriented arrangement.
        6. One randomly shuffled order when more than two drones exist.

        Args:
            nb_drones:
                Number of drones for which identifiers must be generated.

        Returns:
            A list of drone-order lists.

            For example, with four drones, some generated orders include::

                [1, 2, 3, 4]
                [4, 3, 2, 1]
                [1, 3, 2, 4]
                [2, 4, 1, 3]
        """
        drone_ids: List[int] = list(
            range(1, nb_drones + 1)
        )

        orders: List[List[int]] = []

        # Order 1: Normal ascending order.
        #
        # Example:
        # [1, 2, 3, 4, 5]
        orders.append(drone_ids.copy())

        # Order 2: Reverse descending order.
        #
        # Example:
        # [5, 4, 3, 2, 1]
        orders.append(drone_ids.copy()[::-1])

        # Separate identifiers into odd and even groups.
        odd: List[int] = [
            drone_id
            for drone_id in drone_ids
            if drone_id % 2 == 1
        ]

        even: List[int] = [
            drone_id
            for drone_id in drone_ids
            if drone_id % 2 == 0
        ]

        # Order 3: Odd identifiers first, then even identifiers.
        #
        # Example:
        # [1, 3, 5, 2, 4, 6]
        orders.append(odd + even)

        # Order 4: Even identifiers first, then odd identifiers.
        #
        # Example:
        # [2, 4, 6, 1, 3, 5]
        orders.append(even + odd)

        # Order 5: Reverse the first half, then append the second half.
        #
        # Example with six drones:
        #
        # first half:  [1, 2, 3]
        # reversed:    [3, 2, 1]
        # second half: [4, 5, 6]
        # result:      [3, 2, 1, 4, 5, 6]
        if nb_drones > 2:
            middle: int = nb_drones // 2

            left: List[int] = drone_ids[:middle][::-1]
            right: List[int] = drone_ids[middle:]

            orders.append(left + right)

        # Order 6: Add one random scheduling order.
        #
        # This can discover an arrangement not represented by the
        # deterministic strategies above.
        if nb_drones > 2:
            import random

            shuffled: List[int] = drone_ids.copy()
            random.shuffle(shuffled)

            orders.append(shuffled)

        return orders

    def _schedule_with_order(
        self,
        start_zone: Zone,
        end_zone: Zone,
        order: List[int],
        max_turns: int,
    ) -> Dict[int, List[PathStep]]:
        """
        Schedule every drone using one specific identifier order.

        For each drone, a path is found using the current reservation table.
        Once found, that path is reserved immediately before scheduling the
        next drone.

        This means paths selected earlier influence which paths remain
        available to later drones.

        Args:
            start_zone:
                Starting zone shared by all drones.

            end_zone:
                Destination zone shared by all drones.

            order:
                Drone identifiers in the exact order in which they should be
                scheduled.

            max_turns:
                Maximum arrival turn allowed for each path search.

        Returns:
            A dictionary mapping each drone identifier to its path.

        Raises:
            ValueError:
                If the pathfinder cannot find a path for any drone in the
                supplied order.
        """
        all_paths: Dict[int, List[PathStep]] = {}

        for drone_id in order:
            # Find a path that respects all paths reserved for previous
            # drones in this scheduling attempt.
            path: List[PathStep] | None = self.pathfinder.find_path(
                start_zone,
                end_zone,
                max_turns,
            )

            if not path:
                raise ValueError(
                    f"No path found for drone {drone_id}"
                )

            # Reserve the path before searching for the next drone.
            self.reservation_table.reserve_path(path)

            all_paths[drone_id] = path

        return all_paths

    def _schedule_with_retry(
        self,
        start_zone: Zone,
        end_zone: Zone,
        nb_drones: int,
        max_turns: int,
    ) -> Dict[int, List[PathStep]]:
        """
        Retry scheduling while progressively increasing the turn limit.

        Starting from the supplied ``max_turns``, all generated drone orders
        are tested. If none succeeds, the limit is increased by 50 turns and
        every order is tried again.

        Each retry and each scheduling order starts from a fresh reservation
        table so that failed attempts do not affect later attempts.

        Retrying stops when:

        - a complete schedule is found; or
        - ``max_turns`` reaches 2000.

        Args:
            start_zone:
                Starting zone shared by all drones.

            end_zone:
                Destination zone shared by all drones.

            nb_drones:
                Number of drones that must be scheduled.

            max_turns:
                Initial maximum-turn limit for the retry process.

        Returns:
            A dictionary mapping every drone identifier to its scheduled
            path.

        Raises:
            ValueError:
                If no complete schedule can be found before the turn limit
                reaches 2000.
        """
        while max_turns < 2000:
            print(f"Retrying with max_turns={max_turns}")

            # Begin this retry with no previous reservations.
            self.reservation_table = ReservationTable(
                self.graph
            )

            self.pathfinder = PathFinder(
                self.graph,
                self.reservation_table,
            )

            # Try all generated orders with the current maximum-turn limit.
            for order in self._generate_orders(nb_drones):
                try:
                    return self._schedule_with_order(
                        start_zone,
                        end_zone,
                        order,
                        max_turns,
                    )

                except ValueError:
                    # This order failed. Try the next available order.
                    continue

            # No order succeeded, so allow paths to use 50 more turns.
            max_turns += 50

        raise ValueError(
            "No valid schedule found after multiple retries"
        )
