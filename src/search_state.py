from typing import List

from . import PathStep, Zone


class SearchState:
    """
    Represent one state explored by the pathfinding algorithm.

    A search state stores:

    - the zone currently occupied by the drone;
    - the turn at which the drone occupies that zone;
    - the complete sequence of path steps used to reach the state;
    - the number of priority zones entered along the path.

    The priority count is used only as a tie-breaker between paths that
    reach the same location at the same turn. A higher priority count
    indicates that the path follows more preferred zones.
    """

    def __init__(
        self,
        zone: Zone,
        turn: int,
        path_steps: List[PathStep],
        priority_count: int = 0,
    ) -> None:
        """
        Initialize a search state.

        Args:
            zone:
                Zone currently occupied by the drone.

            turn:
                Turn at which the drone occupies ``zone``.

            path_steps:
                Complete sequence of path steps used to reach this state.

            priority_count:
                Number of priority zones entered while following this path.
                This value is used only to break ties between equally fast
                paths. A larger value represents a path that uses more
                preferred zones.

        Raises:
            ValueError:
                If ``turn`` is negative, ``path_steps`` is empty, or
                ``priority_count`` is negative.
        """
        self.zone: Zone = zone
        self.turn: int = turn
        self.path_steps: List[PathStep] = path_steps
        self.priority_count: int = priority_count

        if self.turn < 0:
            raise ValueError(
                f"Turn can't be negative: {self.turn}"
            )

        if not self.path_steps:
            raise ValueError(
                "Path steps can't be empty"
            )

        if self.priority_count < 0:
            raise ValueError(
                "Priority count can't be negative"
            )
