from typing import List
from . import PathStep, Zone


class SearchState:
    """
    Represent one candidate state explored by PathFinder.

    Attributes:
        zone:
            The zone occupied by the drone in this state.

        turn:
            The simulation turn at which the drone occupies ``zone``.

        path_steps:
            All zone and connection steps followed from the starting zone
            to reach this state.

        priority_count:
            Number of priority zones entered while following ``path_steps``.

            This value does not change when the drone waits inside a priority
            zone. It increases only when the drone moves into a priority zone.
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

        Raises:
            ValueError:
                If ``turn`` is negative, ``path_steps`` is empty, or
                ``priority_count`` is negative.
        """
        self.zone: Zone = zone
        self.turn: int = turn
        self.path_steps: List[PathStep] = path_steps
        self.priority_count: int = priority_count

        # A search state cannot exist before the beginning of the simulation.
        if self.turn < 0:
            raise ValueError(
                f"Turn can't be negative: {self.turn}"
            )

        # Every state must include at least the initial starting-zone step.
        if not self.path_steps:
            raise ValueError(
                f"Path steps can't be empty: {self.path_steps}"
            )

        # The number of entered priority zones can never be negative.
        if self.priority_count < 0:
            raise ValueError(
                "Priority count can't be negative: "
                f"{self.priority_count}"
            )
