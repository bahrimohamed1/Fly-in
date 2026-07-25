from typing import List
from . import PathStep, Zone


class SearchState:
    """Represent one zone-and-turn state explored by PathFinder."""

    def __init__(
        self,
        zone: Zone,
        turn: int,
        path_steps: List[PathStep],
    ) -> None:
        self.zone = zone
        self.turn = turn
        self.path_steps = path_steps

        if self.turn < 0:
            raise ValueError(
                f"Turn can't be negative: {self.turn}"
            )

        if not self.path_steps:
            raise ValueError(
                "Path steps can't be empty"
            )
