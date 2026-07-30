import heapq
from typing import Dict, List, Optional, Tuple

from graph import Graph
from path_step import PathStep
from reservation_table import ReservationTable 
from search_state import SearchState
from zone import Zone


class PathFinder:
    """
    Find a valid path for one drone while respecting reservations.

    The search uses a priority queue ordered according to:

    1. Lowest accumulated priority penalty.
    2. Lowest arrival turn.
    3. Insertion order for deterministic behaviour.

    A priority penalty is added whenever the drone chooses a
    non-priority exit while at least one priority exit is available.

    This means that a path respecting priority diversions may be selected
    even when it takes more turns.

    However, non-priority alternatives are never deleted from the search.
    They remain available as fallback routes when a priority branch leads
    to a trap, loop, dead end, or otherwise cannot reach the destination.
    """

    def __init__(
        self,
        graph: Graph,
        reservation_table: ReservationTable,
    ) -> None:
        """
        Initialize the pathfinder.

        Args:
            graph:
                Graph containing all zones and connections.

            reservation_table:
                Table containing zone and connection resources already
                reserved by previously scheduled drones.
        """
        self.graph: Graph = graph
        self.reservation_table: ReservationTable = reservation_table

    def find_path(
        self,
        start_zone: Zone,
        end_zone: Zone,
        max_turns: int,
    ) -> Optional[List[PathStep]]:
        """
        Find the earliest valid path.

        Priority zones are used only as a tie-breaker. A longer path through
        priority zones never beats a shorter path.

        Path ordering:

        1. Earliest arrival turn.
        2. Highest number of entered priority zones.
        3. Insertion order.
        """
        start_step = PathStep(
            0,
            "zone",
            start_zone.name,
        )

        initial_state = SearchState(
            start_zone,
            0,
            [start_step],
            priority_count=0,
        )

        # Queue entry:
        #
        # (
        #     arrival turn,
        #     negative priority count,
        #     insertion counter,
        #     state,
        # )
        queue: List[
            Tuple[int, int, int, SearchState]
        ] = []

        counter = 0

        heapq.heappush(
            queue,
            (
                0,
                0,
                counter,
                initial_state,
            ),
        )

        # For the same zone and turn, retain the path that entered the
        # greatest number of priority zones.
        best_priority: Dict[
            Tuple[str, int],
            int,
        ] = {}

        while queue:
            (
                _,
                queued_negative_priority,
                _,
                current_state,
            ) = heapq.heappop(queue)

            current_zone = current_state.zone
            current_turn = current_state.turn
            current_path = current_state.path_steps
            current_priority_count = current_state.priority_count

            if (
                queued_negative_priority
                != -current_priority_count
            ):
                continue

            state_key = (
                current_zone.name,
                current_turn,
            )

            previous_best = best_priority.get(state_key)

            if (
                previous_best is not None
                and previous_best >= current_priority_count
            ):
                continue

            best_priority[state_key] = current_priority_count

            if current_zone == end_zone:
                return current_path

            if current_turn >= max_turns:
                continue

            neighbors = self.graph.get_neighbors(
                current_zone.name
            )

            for neighbor_zone, connection in neighbors:
                if neighbor_zone.zone_type == "blocked":
                    continue

                new_priority_count = current_priority_count

                if neighbor_zone.zone_type == "priority":
                    new_priority_count += 1

                if neighbor_zone.zone_type == "restricted":
                    connection_turn = current_turn + 1
                    arrival_turn = current_turn + 2

                    if arrival_turn > max_turns:
                        continue

                    if not (
                        self.reservation_table
                        .is_restricted_move_valid(
                            current_zone,
                            neighbor_zone,
                            current_turn,
                        )
                    ):
                        continue

                    connection_step = PathStep(
                        connection_turn,
                        "connection",
                        connection.key(),
                    )

                    arrival_step = PathStep(
                        arrival_turn,
                        "zone",
                        neighbor_zone.name,
                    )

                    new_path = current_path + [
                        connection_step,
                        arrival_step,
                    ]

                else:
                    arrival_turn = current_turn + 1

                    if arrival_turn > max_turns:
                        continue

                    if not (
                        self.reservation_table
                        .is_normal_move_valid(
                            current_zone,
                            neighbor_zone,
                            current_turn,
                        )
                    ):
                        continue

                    arrival_step = PathStep(
                        arrival_turn,
                        "zone",
                        neighbor_zone.name,
                    )

                    new_path = current_path + [
                        arrival_step,
                    ]

                new_state = SearchState(
                    neighbor_zone,
                    arrival_turn,
                    new_path,
                    priority_count=new_priority_count,
                )

                counter += 1

                heapq.heappush(
                    queue,
                    (
                        arrival_turn,
                        -new_priority_count,
                        counter,
                        new_state,
                    ),
                )

            wait_turn = current_turn + 1

            if (
                wait_turn <= max_turns
                and self.reservation_table.is_wait_valid(
                    current_zone,
                    current_turn,
                )
            ):
                wait_step = PathStep(
                    wait_turn,
                    "zone",
                    current_zone.name,
                )

                new_path = current_path + [
                    wait_step,
                ]

                new_state = SearchState(
                    current_zone,
                    wait_turn,
                    new_path,
                    priority_count=current_priority_count,
                )

                counter += 1

                heapq.heappush(
                    queue,
                    (
                        wait_turn,
                        -current_priority_count,
                        counter,
                        new_state,
                    ),
                )

        return None
