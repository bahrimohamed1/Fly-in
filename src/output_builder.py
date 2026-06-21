from . import PathStep
from typing import Dict, List, Optional


class OutputBuilder:
    def __init__(self) -> None:
        pass

    def build_output(self, all_paths: Dict[int, List[PathStep]]) -> List[str]:
        movement_by_turn: Dict[int, List[str]] = {}

        for drone_id, path_steps in all_paths.items():
            for i in range(1, len(path_steps)):
                previous_step = path_steps[i-1]
                current_step = path_steps[i]

                if current_step.kind == 'zone' and \
                        previous_step.kind == 'zone' and \
                        current_step.name == previous_step.name:
                    continue

                movement_text: str = f"D{drone_id}-{current_step.name}"

                if current_step.turn not in movement_by_turn:
                    movement_by_turn[current_step.turn] = []

                movement_by_turn[current_step.turn].append(movement_text)

        output_lines: List[str] = []

        for turn in range(1, max(movement_by_turn.keys()) + 1):
            if turn in movement_by_turn:
                line: str = " ".join(movement_by_turn[turn])
            else:
                line: str = ""

            output_lines.append(line)

        return output_lines
