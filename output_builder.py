from path_step import PathStep
from graph import Graph

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

    Colors are always enabled.
        Zones use their metadata color if specified,
    otherwise a default zone color is used.
        Connections use a separate default color.
    """

    # ANSI color codes
    RESET = '\033[0m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    GRAY = '\033[90m'
    DARK_RED = '\033[31m'
    BROWN = '\033[33m'
    GOLD = '\033[93m'
    MAROON = '\033[31m'
    VIOLET = '\033[95m'
    CRIMSON = '\033[91m'
    ORANGE = '\033[38;5;208m'

    # Default colors
    DEFAULT_ZONE_COLOR = WHITE
    DEFAULT_CONNECTION_COLOR = YELLOW

    # Map zone type to default color (if no metadata color)
    ZONE_TYPE_COLORS = {
        'normal': WHITE,
        'priority': GREEN,
        'restricted': RED,
        'blocked': GRAY,
    }

    # Map metadata color names to ANSI codes
    METADATA_COLORS = {
        'green': GREEN,
        'red': RED,
        'blue': BLUE,
        'yellow': YELLOW,
        'purple': PURPLE,
        'cyan': CYAN,
        'white': WHITE,
        'gray': GRAY,
        'black': GRAY,
        'brown': BROWN,
        'gold': GOLD,
        'maroon': MAROON,
        'violet': VIOLET,
        'crimson': CRIMSON,
        'orange': ORANGE,
        'darkred': DARK_RED,
    }

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the OutputBuilder with a graph.

        Args:
            graph: The Graph object containing zone metadata (colors, etc.)
        """
        self.graph = graph

    def build_output(self, all_paths: Dict[int, List[PathStep]]) -> List[str]:
        """
        Convert a dictionary of drone paths into the required output format.

        The method processes all drone paths, extracts movements at each turn,
        and formats them as strings. Wait steps (consecutive zone steps with
        the same name) are omitted from the output.

        Colors are always applied. Zones use their metadata color if specified,
        otherwise a default zone color is used.
            Connections use a separate default color.

        Args:
            all_paths: Dictionary mapping drone_id -> list of PathStep objects.
                      Each PathStep represents the drone's
                        state at a specific turn.

        Returns:
            List[str]: A list of strings, one per simulation turn.
                      Each string contains space-separated movements
                      for that turn.
                      Turns with no movements are represented as empty strings.

        Example:
            >>> output_builder = OutputBuilder(graph)
            >>> paths = {1: [PathStep(0,'zone','start'),
                    PathStep(1,'zone','A')]}
            >>> output_builder.build_output(paths)
            ['\x1b[92mD1-A\x1b[0m']
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

                # Apply color based on resource type
                movement_text = self._color_movement(
                    movement_text,
                    current_step.kind,
                    current_step.name,
                )

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

    def _color_movement(
            self,
            movement: str,
            kind: str,
            resource_name: str
            ) -> str:
        """
        Apply ANSI color codes to a movement string.

        Args:
            movement: The movement string (e.g., "D1-waypoint1")
            kind: The resource kind ('zone' or 'connection')
            resource_name: The name of the zone or connection

        Returns:
            The movement string wrapped with ANSI color codes.
        """
        if kind == 'zone':
            color = self._get_zone_color(resource_name)
        else:
            color = self.DEFAULT_CONNECTION_COLOR

        return f"{color}{movement}{self.RESET}"

    def _get_zone_color(self, zone_name: str) -> str:
        """
        Get the color for a zone.

        Priority:
        1. Metadata color (if specified in the map file)
        2. Default color based on zone type
        3. Fallback default zone color

        Args:
            zone_name: The name of the zone.

        Returns:
            ANSI color code string.
        """
        zone = self.graph.get_zone(zone_name)
        if zone is None:
            return self.DEFAULT_ZONE_COLOR

        # Check for metadata color
        if zone.color is not None and zone.color in self.METADATA_COLORS:
            return self.METADATA_COLORS[zone.color]

        # Fallback to zone type color
        return self.ZONE_TYPE_COLORS.get(
            zone.zone_type, self.DEFAULT_ZONE_COLOR)
