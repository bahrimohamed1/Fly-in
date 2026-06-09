from typing import List
from . import Zone, PathStep


class SearchState:
    def __init__(self,
                 zone: Zone,
                 turn: int,
                 path_steps: List[PathStep]
                 ) -> None:
        self.zone: Zone = zone
        self.turn: int = turn
        self.path_steps: List[PathStep] = path_steps

        if self.turn < 0:
            raise ValueError(f"Turn can't be negative: {self.turn}")

        if not self.path_steps:
            raise ValueError(f"Path steps can't be empty: {self.path_steps}")
