from . import Graph, ReservationTable, PathStep, Zone, SearchState
from typing import List, Optional, Tuple
import heapq


class PathFinder:
    def __init__(self,
                 graph: Graph,
                 reservation_table: ReservationTable
                 ) -> None:
        self.graph: Graph = graph
        self.reservation_table: ReservationTable = reservation_table

    def find_path(self,
                  start_zone: Zone,
                  end_zone: Zone,
                  max_turns: int) -> Optional[List[PathStep]]:
        start_step: PathStep = PathStep(0, 'zone', start_zone.name)
        initial_state: SearchState = SearchState(start_zone, 0, [start_step])
        queue: List[Tuple[int, int, SearchState]] = []
        visited: set[Tuple[str, int]] = set()
        counter: int = 0

        heapq.heappush(queue, (0, counter, initial_state))

        while queue:
            _, _, current_state = heapq.heappop(queue)
            current_zone: Zone = current_state.zone
            current_turn: int = current_state.turn
            current_path: List[PathStep] = current_state.path_steps

            if current_turn >= max_turns:
                continue

            state_key: Tuple[str, int] = (current_zone.name, current_turn)
            if state_key in visited:
                continue

            visited.add(state_key)

            if current_zone == end_zone:
                return current_path

            # check neibors
            for neighbor_zone, connection in self.graph.get_neighbors(
                    current_zone.name):
                # blocked
                if neighbor_zone.zone_type == 'blocked':
                    continue

                # restricted
                if neighbor_zone.zone_type == 'restricted':
                    next_turn: int = current_turn + 1
                    arrival_turn: int = current_turn + 2
                    if next_turn > max_turns or arrival_turn > max_turns:
                        continue
                    if self.reservation_table.is_restricted_move_valid(
                            current_zone, neighbor_zone, current_turn):
                        connection_step: PathStep = PathStep(
                            next_turn, 'connection', connection.key())
                        arrival_step: PathStep = PathStep(
                            arrival_turn, 'zone', neighbor_zone.name)
                        new_path: List[PathStep] = current_path + \
                            [connection_step, arrival_step]
                        new_state: SearchState = SearchState(
                            neighbor_zone, arrival_turn, new_path)
                        counter += 1
                        heapq.heappush(
                            queue, (arrival_turn, counter, new_state))
                # normal
                else:
                    next_turn: int = current_turn + 1
                    if next_turn > max_turns:
                        continue
                    if self.reservation_table.is_normal_move_valid(
                            current_zone, neighbor_zone, current_turn):
                        new_step: PathStep = PathStep(
                            next_turn, 'zone', neighbor_zone.name)
                        new_path: List[PathStep] = current_path + [new_step]
                        new_state: SearchState = SearchState(
                            neighbor_zone, next_turn, new_path)
                        counter += 1

                        heapq.heappush(queue, (next_turn, counter, new_state))

            # wait
            next_turn: int = current_turn + 1
            if next_turn > max_turns:
                continue
            if self.reservation_table.is_wait_valid(
                    current_zone, current_turn):
                new_step: PathStep = PathStep(
                    next_turn, 'zone', current_zone.name)
                new_path: List[PathStep] = current_path + [new_step]
                new_state: SearchState = SearchState(
                    current_zone, next_turn, new_path)
                counter += 1

                heapq.heappush(queue, (next_turn, counter, new_state))

        return None
