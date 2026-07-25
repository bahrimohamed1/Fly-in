import heapq
from typing import Dict, List, Optional, Tuple

from . import Graph, PathStep, ReservationTable, SearchState, Zone


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
        Find a valid route from ``start_zone`` to ``end_zone``.

        Priority zones are preferred, but they are not mandatory.

        When a drone has a forward priority option, choosing a non-priority
        neighbor adds one priority penalty. The zone the drone just came from
        is ignored when detecting priority diversions because moving backward
        is not considered a new route choice.

        Paths are ordered by:

        1. Lowest accumulated priority penalty.
        2. Lowest arrival turn.
        3. Insertion order for deterministic behaviour.

        Args:
            start_zone:
                Zone from which the drone starts.

            end_zone:
                Destination zone.

            max_turns:
                Maximum allowed arrival turn.

        Returns:
            The path steps when a valid route is found, otherwise ``None``.
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
            priority_penalty=0,
            previous_zone_name=None,
        )

        # Queue entries contain:
        #
        # (
        #     accumulated priority penalty,
        #     arrival turn,
        #     insertion counter,
        #     search state,
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

        # For the same zone, turn, and previous zone, retain only the
        # smallest priority penalty encountered.
        #
        # previous_zone_name must be part of the key because priority
        # diversion detection depends on the direction from which the
        # current zone was entered.
        best_penalty: Dict[
            Tuple[str, int, Optional[str]],
            int,
        ] = {}

        while queue:
            (
                queued_penalty,
                _,
                _,
                current_state,
            ) = heapq.heappop(queue)

            current_zone = current_state.zone
            current_turn = current_state.turn
            current_path = current_state.path_steps
            current_penalty = current_state.priority_penalty
            previous_zone_name = current_state.previous_zone_name

            # Ignore inconsistent or outdated queue entries.
            if queued_penalty != current_penalty:
                continue

            state_key = (
                current_zone.name,
                current_turn,
                previous_zone_name,
            )

            previous_best = best_penalty.get(state_key)

            if (
                previous_best is not None
                and previous_best <= current_penalty
            ):
                continue

            best_penalty[state_key] = current_penalty

            # Because the queue prioritizes penalty before turn count,
            # the first destination removed from the queue is the best
            # priority-respecting route available.
            if current_zone == end_zone:
                return current_path

            if current_turn >= max_turns:
                continue

            neighbors = self.graph.get_neighbors(
                current_zone.name
            )

            # Blocked zones can never be entered.
            passable_neighbors = [
                (neighbor_zone, connection)
                for neighbor_zone, connection in neighbors
                if neighbor_zone.zone_type != "blocked"
            ]

            # Exclude the zone the drone just came from when deciding whether
            # the current position contains a priority diversion.
            #
            # Example:
            #
            # priority_A -> priority_B -> goal
            #
            # At priority_B, priority_A is behind the drone. It must not cause
            # the move to goal to be treated as ignoring a priority option.
            forward_neighbors = [
                (neighbor_zone, connection)
                for neighbor_zone, connection in passable_neighbors
                if neighbor_zone.name != previous_zone_name
            ]

            has_forward_priority_exit = any(
                neighbor_zone.zone_type == "priority"
                for neighbor_zone, _ in forward_neighbors
            )

            # Explore every passable neighbor.
            #
            # Priority is preferred through the penalty system, but normal and
            # restricted routes remain available as fallback paths.
            for neighbor_zone, connection in passable_neighbors:
                is_backtracking = (
                    neighbor_zone.name == previous_zone_name
                )

                # A penalty is added only when:
                #
                # 1. a forward priority exit exists;
                # 2. the selected movement is not backtracking;
                # 3. the selected destination is not a priority zone.
                #
                # Backtracking remains available without being interpreted as
                # deliberately selecting a competing forward branch.
                ignores_priority = (
                    has_forward_priority_exit
                    and not is_backtracking
                    and neighbor_zone.zone_type != "priority"
                )

                move_penalty = (
                    1 if ignores_priority else 0
                )

                new_penalty = (
                    current_penalty + move_penalty
                )

                if neighbor_zone.zone_type == "restricted":
                    # Entering a restricted zone takes two turns:
                    #
                    # turn + 1: the drone occupies the connection;
                    # turn + 2: the drone arrives in the restricted zone.
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
                    # Normal and priority zones both take one turn to enter.
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
                    priority_penalty=new_penalty,
                    previous_zone_name=current_zone.name,
                )

                counter += 1

                heapq.heappush(
                    queue,
                    (
                        new_penalty,
                        arrival_turn,
                        counter,
                        new_state,
                    ),
                )

            # Waiting is allowed when the reservation table permits it.
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

                # Waiting does not select a competing route, so it does not
                # increase the priority penalty. The previous zone remains
                # unchanged because the drone did not move.
                new_state = SearchState(
                    current_zone,
                    wait_turn,
                    new_path,
                    priority_penalty=current_penalty,
                    previous_zone_name=previous_zone_name,
                )

                counter += 1

                heapq.heappush(
                    queue,
                    (
                        current_penalty,
                        wait_turn,
                        counter,
                        new_state,
                    ),
                )

        return None
