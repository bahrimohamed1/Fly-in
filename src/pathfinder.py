from . import Graph, ReservationTable, PathStep, Zone, SearchState
from typing import List, Optional, Tuple
import heapq


class Pathfinder:
    def __init__(self,
                 graph: Graph,
                 reservation_table: ReservationTable
                 ) -> None:
        self.graph: Graph = graph
        self.reservation_table: ReservationTable = reservation_table

    def find_path(self,
                  start_zone: Zone,
                  end_zone: Zone,
                  max_turns: int
                  ) -> Optional[List[PathStep]]:
        start_step: PathStep = PathStep(0, 'zone', start_zone.name)
        initial_state: SearchState = SearchState(start_zone, 0, [start_step])
        queue: List[Tuple[int, int, SearchState]] = []
        visited: List[Tuple[str, int]] = []
        
        heapq.heappush(queue, (0, 0, initial_state))


        while queue:
            _, _, current_state = heapq.heappop(queue)
            current_zone: Zone = current_state.zone
            current_turn: int = current_state.turn
            current_path: List[PathStep] = current_state.path_steps
            
            if current_turn > max_turns:
                continue
            
            state_key = (current_zone.name, current_turn)
            if state_key in visited:
                continue
            
            visited.append(state_key)
            
            #1 Wait
            new_turn: int = current_turn + 1
            new_step: PathStep = PathStep(new_turn, 'zone',  current_zone.name)
            new_path: List[PathStep] = current_path + [new_step]
            
            if self.reservation_table.can_reserve_zone(current_zone.name, new_turn):
                new_state: SearchState = SearchState(current_zone, new_turn, new_path)
                heapq.heappush(queue, (new_turn, new_turn, new_state))
