import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src import Parser, PathStep, Scheduler, Graph


class ParserConnectionMetadataTests(unittest.TestCase):
    def test_connection_rejects_zone_metadata_key(self) -> None:
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
    @staticmethod
    def _load_graph() -> Graph:
        parser = Parser("maps/easy/01_linear_path.txt")
        return parser.parse()

    def test_retry_increases_turn_budget_until_limit(self) -> None:
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


if __name__ == "__main__":
    unittest.main()
