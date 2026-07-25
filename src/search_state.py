from typing import List, Optional

from . import PathStep, Zone


class SearchState:
    """
    Represent one state explored by the pathfinding algorithm.

    Attributes:
        zone:
            Zone currently occupied by the drone.

        turn:
            Turn at which the drone occupies the zone.

        path_steps:
            Complete sequence of path steps used to reach this state.

        priority_penalty:
            Number of times the path ignored a forward priority option.

        previous_zone_name:
            Name of the zone occupied immediately before the current zone.
            It is used to prevent the edge leading backward from being
            interpreted as a new priority diversion.
    """

    def __init__(
        self,
        zone: Zone,
        turn: int,
        path_steps: List[PathStep],
        priority_penalty: int = 0,
        previous_zone_name: Optional[str] = None,
    ) -> None:
        """
        Initialize a search state.

        Args:
            zone:
                Current zone.

            turn:
                Current arrival turn.

            path_steps:
                Steps used to reach the current state.

            priority_penalty:
                Number of ignored forward priority choices.

            previous_zone_name:
                Zone occupied before entering the current zone. ``None``
                is used for the initial state.

        Raises:
            ValueError:
                If the turn or priority penalty is negative, or if the
                path contains no steps.
        """
        self.zone: Zone = zone
        self.turn: int = turn
        self.path_steps: List[PathStep] = path_steps
        self.priority_penalty: int = priority_penalty
        self.previous_zone_name: Optional[str] = previous_zone_name

        if self.turn < 0:
            raise ValueError(
                f"Turn can't be negative: {self.turn}"
            )

        if not self.path_steps:
            raise ValueError(
                "Path steps can't be empty"
            )

        if self.priority_penalty < 0:
            raise ValueError(
                "Priority penalty can't be negative"
            )