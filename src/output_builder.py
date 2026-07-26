from . import PathStep
from typing import Dict, List


class OutputBuilder:
    """
    Builds the final simulation output from scheduled drone paths.

    The output format follows the subject requirements:
    - One line per simulation turn
    - Each line contains space-separated movements:
        D<id>-<zone> or D<id>-<connection>
    - Drones that wait (stay in same zone) are omitted
    - Empty turns are skipped (no output line)
    """

    def build_output(self, all_paths: Dict[int, List[PathStep]]) -> List[str]:
        """
        Convert a dictionary of drone paths into the required output format.

        The method processes all drone paths, extracts movements at each turn,
        and formats them as strings. Wait steps (consecutive zone steps with
        the same name) are omitted from the output.

        Args:
            all_paths: Dictionary mapping drone_id
            -> list of PathStep objects.
                      Each PathStep represents the drone's state
                      at a specific turn.

        Returns:
            List[str]: A list of strings, one per simulation turn.
                      Each string contains space-separated movements
                      for that turn.
                      Turns with no movements are represented as empty strings.

        Example:
            >>> output_builder = OutputBuilder()
            >>> paths = {1: [PathStep(0,'zone','start'),
                PathStep(1,'zone','A')]}
            >>> output_builder.build_output(paths)
            ['D1-A']
        """
        movement_by_turn: Dict[int, List[str]] = {}
        max_turns: int = 0

        # First pass: determine max turns and collect movements
        for drone_id, path_steps in sorted(all_paths.items()):
            # Update max_turns
            for step in path_steps:
                if step.turn > max_turns:
                    max_turns = step.turn

            # Process each transition (skip waits)
            for i in range(1, len(path_steps)):
                previous_step = path_steps[i - 1]
                current_step = path_steps[i]

                # Skip wait steps (drone stays in same zone)
                if (current_step.kind == 'zone' and
                    previous_step.kind == 'zone' and
                        current_step.name == previous_step.name):
                    continue

                # Format: D<id>-<resource_name>
                movement_text: str = f"D{drone_id}-{current_step.name}"

                # Group by turn
                if current_step.turn not in movement_by_turn:
                    movement_by_turn[current_step.turn] = []
                movement_by_turn[current_step.turn].append(movement_text)

        # Second pass: build output lines turn by turn
        output_lines: List[str] = []
        for turn in range(1, max_turns + 1):
            if turn in movement_by_turn:
                # Join all movements at this turn with a space
                line: str = " ".join(movement_by_turn[turn])
            else:
                # No movements at this turn (empty line)
                line = ""
            output_lines.append(line)

        return output_lines
