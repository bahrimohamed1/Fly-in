from . import PathStep
from typing import List


class DronePath:
    def __init__(self, drone_id: int) -> None:
        self.drone_id: int = drone_id
        self.steps: List[PathStep] = []

    def add_step(self, step: PathStep) -> None:
        self.steps.append(step)

    def get_last_step(self) -> PathStep | None:
        if not self.steps:
            return None

        return self.steps[-1]
