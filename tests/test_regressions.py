import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import (
    Graph,
    Parser,
    PathFinder,
    PathStep,
    ReservationTable,
    Scheduler,
)


class ParserConnectionMetadataTests(unittest.TestCase):
    """Regression tests for connection metadata parsing."""

    def test_connection_rejects_zone_metadata_key(self) -> None:
        """A connection must reject metadata keys intended for zones."""
        map_content = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 1 0
connection: start-goal [zone=blocked]
"""

        with tempfile.TemporaryDirectory() as tmp_dir:
            map_path = Path(tmp_dir) / "bad_connection_metadata.txt"
            map_path.write_text(map_content, encoding="utf-8")

            with self.assertRaises(ValueError) as ctx:
                Parser(str(map_path)).parse()

            self.assertIn(
                "UNKNOWN CONNECTION METADATA KEY",
                str(ctx.exception),
            )

    def test_connection_accepts_max_link_capacity(self) -> None:
        """A connection must accept a valid max_link_capacity value."""
        map_content = """\
nb_drones: 1
start_hub: start 0 0
end_hub: goal 1 0
connection: start-goal [max_link_capacity=3]
"""

        with tempfile.TemporaryDirectory() as tmp_dir:
            map_path = Path(tmp_dir) / "good_connection_metadata.txt"
            map_path.write_text(map_content, encoding="utf-8")

            graph = Parser(str(map_path)).parse()

        self.assertEqual(len(graph.connections), 1)
        self.assertEqual(graph.connections[0].max_link_capacity, 3)


class SchedulerRetryProgressionTests(unittest.TestCase):
    """Regression tests for scheduler retry behaviour."""

    @staticmethod
    def _load_graph() -> Graph:
        """Load a small valid graph used by retry tests."""
        parser = Parser("maps/easy/01_linear_path.txt")
        return parser.parse()

    def test_retry_increases_turn_budget_until_limit(self) -> None:
        """The scheduler must retry with larger turn budgets until its limit."""
        graph = self._load_graph()
        scheduler = Scheduler(graph)
        orders = [[1], [2]]

        with patch.object(scheduler, "_generate_orders", return_value=orders):
            with patch.object(
                scheduler,
                "_schedule_with_order",
                side_effect=ValueError("forced failure"),
            ) as schedule_with_order:
                with self.assertRaises(ValueError) as ctx:
                    scheduler._schedule_with_retry(
                        start_zone=graph.start_zone,
                        end_zone=graph.end_zone,
                        nb_drones=2,
                        max_turns=1900,
                    )

        self.assertIn("No valid schedule found", str(ctx.exception))
        self.assertEqual(schedule_with_order.call_count, 4)

    def test_retry_eventually_succeeds_after_budget_increase(self) -> None:
        """The scheduler must return once a larger turn budget succeeds."""
        graph = self._load_graph()
        scheduler = Scheduler(graph)
        seen_max_turns = []

        def fake_schedule_with_order(
            start_zone: object,
            end_zone: object,
            order: object,
            max_turns: int,
        ) -> dict[int, list[PathStep]]:
            seen_max_turns.append(max_turns)
            if max_turns < 250:
                raise ValueError("still too low")
            return {1: [PathStep(0, "zone", "start")]}

        with patch.object(scheduler, "_generate_orders", return_value=[[1]]):
            with patch.object(
                scheduler,
                "_schedule_with_order",
                side_effect=fake_schedule_with_order,
            ):
                result = scheduler._schedule_with_retry(
                    start_zone=graph.start_zone,
                    end_zone=graph.end_zone,
                    nb_drones=1,
                    max_turns=200,
                )

        self.assertEqual(seen_max_turns, [200, 250])
        self.assertIn(1, result)


class PriorityPathfindingTests(unittest.TestCase):
    """
    Regression tests for priority-zone pathfinding.

    Priority zones still cost one turn. They only act as a tie-breaker
    between paths that require the same total number of turns.
    """

    @staticmethod
    def _find_path(map_content: str) -> list[PathStep]:
        """
        Parse a temporary map and return the path selected by PathFinder.

        The helper keeps each test focused on expected pathfinding behaviour.
        """
        with tempfile.TemporaryDirectory() as tmp_dir:
            map_path = Path(tmp_dir) / "priority_test.txt"
            map_path.write_text(map_content, encoding="utf-8")

            graph = Parser(str(map_path)).parse()
            reservation_table = ReservationTable(graph)
            path_finder = PathFinder(graph, reservation_table)

            path = path_finder.find_path(
                start_zone=graph.start_zone,
                end_zone=graph.end_zone,
                max_turns=10,
            )

        if path is None:
            raise AssertionError("PathFinder unexpectedly returned no path")

        return path

    @staticmethod
    def _zone_names(path: list[PathStep]) -> list[str]:
        """Return only zone names from a path, ignoring connection steps."""
        return [
            step.name
            for step in path
            if step.kind == "zone"
        ]

    def test_equal_length_path_prefers_priority_zone(self) -> None:
        """
        Prefer the priority route when both available routes take two turns.

        The normal route is deliberately declared first. This ensures the
        result is based on priority semantics rather than adjacency order.
        """
        map_content = """\
nb_drones: 1
start_hub: start 0 0
hub: normal_path 1 0
hub: priority_path 1 1 [zone=priority]
end_hub: goal 2 0
connection: start-normal_path
connection: normal_path-goal
connection: start-priority_path
connection: priority_path-goal
"""

        path = self._find_path(map_content)

        self.assertEqual(
            self._zone_names(path),
            ["start", "priority_path", "goal"],
        )

    def test_shorter_normal_path_beats_longer_priority_path(self) -> None:
        """
        Ensure priority never overrides the shortest-time requirement.

        The direct normal route takes one turn, while the route through the
        priority zone takes two turns. The direct route must still win.
        """
        map_content = """\
nb_drones: 1
start_hub: start 0 0
hub: priority_path 1 1 [zone=priority]
end_hub: goal 2 0
connection: start-goal
connection: start-priority_path
connection: priority_path-goal
"""

        path = self._find_path(map_content)

        self.assertEqual(
            self._zone_names(path),
            ["start", "goal"],
        )

    def test_more_priority_zones_win_between_equal_turn_paths(self) -> None:
        """
        Prefer the equal-time route that enters more priority zones.

        Both routes take three turns:
            start -> normal_a -> normal_b -> goal
            start -> priority_a -> priority_b -> goal

        The route containing two priority zones must be selected.
        """
        map_content = """\
nb_drones: 1
start_hub: start 0 0
hub: normal_a 1 0
hub: normal_b 2 0
hub: priority_a 1 1 [zone=priority]
hub: priority_b 2 1 [zone=priority]
end_hub: goal 3 0
connection: start-normal_a
connection: normal_a-normal_b
connection: normal_b-goal
connection: start-priority_a
connection: priority_a-priority_b
connection: priority_b-goal
"""

        path = self._find_path(map_content)

        self.assertEqual(
            self._zone_names(path),
            ["start", "priority_a", "priority_b", "goal"],
        )
    def test_priority_diversion_beats_shorter_normal_route(self) -> None:
        """
        A priority exit must be selected even when the normal route is shorter.
        """
        map_content = """\
    nb_drones: 1
    start_hub: start 0 0
    hub: junction 1 0
    hub: priority_path 2 1 [zone=priority]
    hub: detour 3 1
    end_hub: goal 4 0
    connection: start-junction
    connection: junction-goal
    connection: junction-priority_path
    connection: priority_path-detour
    connection: detour-goal
    """

        path = self._find_path(map_content)

        self.assertEqual(
            self._zone_names(path),
            [
                "start",
                "junction",
                "priority_path",
                "detour",
                "goal",
            ],
        )

if __name__ == "__main__":
    unittest.main()
