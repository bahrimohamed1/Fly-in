from graph import Graph
from path_step import PathStep
from connection import Connection
from zone import Zone

from typing import Dict, List, Optional


class Validator:
    """
    Validate the paths produced for all scheduled drones.

    The validator checks three independent aspects of a schedule:

    1. Path structure:
       Every drone starts at turn 0 in the graph's start zone, finishes in
       the graph's end zone, uses valid step kinds, and has strictly
       increasing turn numbers.

    2. Path transitions:
       Every movement follows an existing connection and respects the
       special representation used for normal, waiting, and restricted
       movements.

    3. Resource capacities:
       The number of drones occupying each zone or connection at every turn
       does not exceed that resource's configured capacity.

    Attributes:
        graph:
            Graph containing the zones and connections referenced by the
            paths being validated.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the validator.

        Args:
            graph:
                Graph against which drone paths will be checked.
        """
        self.graph: Graph = graph

    def validate_paths_structure(
        self,
        all_paths: Dict[int, List[PathStep]],
    ) -> bool:
        """
        Validate the general structure of every drone path.

        This method checks that:

        - at least one drone path is present;
        - every drone has a non-empty path;
        - the first step occurs at turn 0;
        - the first step is the graph's start zone;
        - the final step is the graph's end zone;
        - every step kind is either ``"zone"`` or ``"connection"``;
        - turn values are strictly increasing inside each path.

        This method does not check whether consecutive zones are connected
        or whether resource capacities are respected. Those checks are
        performed by ``validate_transitions`` and ``validate_capacities``.

        Args:
            all_paths:
                Dictionary mapping each drone identifier to its ordered list
                of path steps.

        Returns:
            ``True`` when every path has a valid general structure.

        Raises:
            ValueError:
                If any path is empty, starts or ends incorrectly, contains an
                invalid step kind, or contains non-increasing turn numbers.
        """
        if not all_paths:
            raise ValueError("No drone path to validate")

        for drone_id, path_steps in all_paths.items():
            if not path_steps:
                raise ValueError(
                    f"Drone{drone_id} has empty path"
                )

            first_step: PathStep = path_steps[0]

            if first_step.turn != 0:
                raise ValueError(
                    f"Drone {drone_id} does not start at turn 0"
                )

            if first_step.kind != 'zone':
                raise ValueError(
                    f"Drone {drone_id} does not start in a zone"
                )

            if first_step.name != self.graph.start_zone.name:
                raise ValueError(
                    f"Drone {drone_id} does not start at start zone"
                )

            last_step: PathStep = path_steps[-1]

            if last_step.kind != 'zone':
                raise ValueError(
                    f"Drone {drone_id} does not end in a zone"
                )

            if last_step.name != self.graph.end_zone.name:
                raise ValueError(
                    f"Drone {drone_id} does not end at end zone"
                )

            previous_turn: int = -1

            for step in path_steps:
                if step.kind != 'zone' and step.kind != 'connection':
                    raise ValueError(
                        f"Drone {drone_id} has invalid step kind"
                    )

                if step.turn <= previous_turn:
                    raise ValueError(
                        f"Drone {drone_id} turns are not strictly increasing"
                    )

                previous_turn = step.turn

        return True

    def validate_transitions(
        self,
        all_paths: Dict[int, List[PathStep]],
    ) -> bool:
        """
        Validate every transition inside every drone path.

        The path format supports three transition types:

        Waiting:
            ``zone -> same zone`` in one turn.

        Normal movement:
            ``zone -> connected non-restricted zone`` in one turn.

        Restricted movement:
            ``zone -> connection -> restricted zone`` over two turns.

        This method checks that referenced zones and connections exist, that
        blocked zones are never entered, and that restricted movements use
        the required intermediate connection step and timing.

        Args:
            all_paths:
                Dictionary mapping drone identifiers to ordered path steps.

        Returns:
            ``True`` when every transition is valid.

        Raises:
            ValueError:
                If a transition starts incorrectly, references a missing
                resource, enters a blocked zone, enters a restricted zone
                without the required connection step, or has invalid timing.
        """
        for drone_id, path_steps in all_paths.items():
            i: int = 0

            while i < len(path_steps) - 1:
                previous: PathStep = path_steps[i]
                current: PathStep = path_steps[i + 1]

                if previous.kind != 'zone':
                    raise ValueError(
                        f"Drone {drone_id} has invalid "
                        "transition starting from non-zone"
                    )

                previous_zone: Optional[Zone] = self.graph.get_zone(
                    previous.name
                )

                if not previous_zone:
                    raise ValueError(
                        f"{previous.name} does not exist"
                    )

                if current.kind == 'zone':
                    current_zone: Optional[Zone] = self.graph.get_zone(
                        current.name
                    )

                    if not current_zone:
                        raise ValueError(
                            f"{current.name} does not exist"
                        )

                    if current_zone.name == previous_zone.name:
                        if current_zone.zone_type == 'blocked':
                            raise ValueError(
                                f"{current_zone.name} is blocked"
                            )

                        i += 1
                        continue

                    if current_zone.zone_type == 'blocked':
                        raise ValueError(
                            f"{current_zone.name} is blocked"
                        )

                    if current_zone.zone_type == 'restricted':
                        raise ValueError(
                            "Restricted zone entered without connection step"
                        )

                    connection: Connection | None = (
                        self.graph.get_connection(
                            previous_zone,
                            current_zone,
                        )
                    )

                    if not connection:
                        raise ValueError(
                            "Illegal move: zones are not connected"
                        )

                    i += 1
                    continue

                if current.kind == 'connection':
                    if i + 2 >= len(path_steps):
                        raise ValueError(
                            "Connection step missing arrival zone"
                        )

                    arrival: PathStep = path_steps[i + 2]

                    if arrival.kind != 'zone':
                        raise ValueError(
                            "Restricted zone must end in a zone"
                        )

                    arrival_zone: Optional[Zone] = self.graph.get_zone(
                        arrival.name
                    )

                    if not arrival_zone:
                        raise ValueError(
                            f"{arrival.name} does not exist"
                        )

                    if arrival_zone.zone_type != 'restricted':
                        raise ValueError(
                            f"{arrival_zone.zone_type} must be"
                            "a restricted zone"
                        )

                    connection = self.graph.get_connection(
                        previous_zone,
                        arrival_zone,
                    )

                    if not connection:
                        raise ValueError(
                            "No connection for restricted movement"
                        )

                    if current.name != connection.key():
                        raise ValueError(
                            "Wrong connection step"
                        )

                    if current.turn != previous.turn + 1:
                        raise ValueError(
                            "Wrong connection turn"
                        )

                    if arrival.turn != previous.turn + 2:
                        raise ValueError(
                            "Wrong arrival turn"
                        )

                    i += 2
                    continue

                raise ValueError("Invalid step kind")

        return True

    def validate_capacities(
        self,
        all_paths: Dict[int, List[PathStep]],
    ) -> bool:
        """
        Validate zone and connection capacities at every turn.

        Zone occupancy is collected directly from all ``"zone"`` path
        steps. Connection occupancy is reconstructed from transitions:

        - a normal movement uses its connection at the arrival turn;
        - a restricted movement uses its connection for two turns;
        - waiting does not use a connection.

        Start and end zones are excluded from normal zone-capacity checks
        because they follow special capacity rules in this project.

        Args:
            all_paths:
                Dictionary mapping drone identifiers to ordered path steps.

        Returns:
            ``True`` when no zone or connection capacity is exceeded.

        Raises:
            ValueError:
                If a referenced resource does not exist, a transition is
                malformed, or a zone or connection exceeds its configured
                capacity.
        """
        zone_usage: Dict[int, Dict[str, int]] = {}
        conn_usage: Dict[int, Dict[str, int]] = {}

        for _, path_steps in all_paths.items():
            for step in path_steps:
                if step.kind == 'zone':
                    zone_name: str = step.name
                    turn: int = step.turn

                    if turn not in zone_usage:
                        zone_usage[turn] = {}

                    zone_usage[turn][zone_name] = (
                        zone_usage[turn].get(zone_name, 0) + 1
                    )

        for drone_id, path_steps in all_paths.items():
            i: int = 0

            while i < len(path_steps) - 1:
                current_step: PathStep = path_steps[i]
                next_step: PathStep = path_steps[i + 1]

                if current_step.kind != 'zone':
                    raise ValueError(
                        f"Drone {drone_id} transition starts from non-zone"
                    )

                current_zone: Optional[Zone] = self.graph.get_zone(
                    current_step.name
                )

                if current_zone is None:
                    raise ValueError(
                        f"Zone {current_step.name} not found"
                    )

                if next_step.kind == 'zone':
                    next_zone: Optional[Zone] = self.graph.get_zone(
                        next_step.name
                    )

                    if next_zone is None:
                        raise ValueError(
                            f"Zone {next_step.name} not found"
                        )

                    if next_zone.name != current_zone.name:
                        connection: Optional[Connection] = (
                            self.graph.get_connection(
                                current_zone,
                                next_zone,
                            )
                        )

                        if connection is None:
                            raise ValueError(
                                f"No connection between "
                                f"{current_zone.name} and {next_zone.name}"
                            )

                        connection_key: str = connection.key()
                        usage_turn: int = next_step.turn

                        if usage_turn not in conn_usage:
                            conn_usage[usage_turn] = {}

                        conn_usage[usage_turn][connection_key] = (
                            conn_usage[usage_turn].get(
                                connection_key,
                                0,
                            ) + 1
                        )

                    i += 1

                elif next_step.kind == 'connection':
                    if i + 2 >= len(path_steps):
                        raise ValueError(
                            f"Drone {drone_id} restricted move "
                            "missing arrival zone"
                        )

                    arrival_step: PathStep = path_steps[i + 2]

                    if arrival_step.kind != 'zone':
                        raise ValueError(
                            f"Drone {drone_id} "
                            "restricted move must end with zone"
                        )

                    arrival_zone: Optional[Zone] = self.graph.get_zone(
                        arrival_step.name
                    )

                    if arrival_zone is None:
                        raise ValueError(
                            f"Zone {arrival_step.name} not found"
                        )

                    if arrival_zone.zone_type != 'restricted':
                        raise ValueError(
                            f"Arrival zone {arrival_zone.name} "
                            "is not restricted"
                        )

                    connection = self.graph.get_connection(
                        current_zone,
                        arrival_zone,
                    )

                    if connection is None:
                        raise ValueError(
                            f"No connection between {current_zone.name} "
                            f"and {arrival_zone.name}"
                        )

                    connection_key = connection.key()
                    connection_turn_one: int = current_step.turn + 1
                    connection_turn_two: int = current_step.turn + 2

                    for turn in (
                        connection_turn_one,
                        connection_turn_two,
                    ):
                        if turn not in conn_usage:
                            conn_usage[turn] = {}

                        conn_usage[turn][connection_key] = (
                            conn_usage[turn].get(
                                connection_key,
                                0,
                            ) + 1
                        )

                    i += 2

                else:
                    raise ValueError(
                        f"Drone {drone_id} invalid step kind: "
                        f"{next_step.kind}"
                    )

        for turn, zones in zone_usage.items():
            for zone_name, count in zones.items():
                zone: Optional[Zone] = self.graph.get_zone(
                    zone_name
                )

                if zone is None:
                    raise ValueError(
                        f"Zone {zone_name} not found"
                    )

                if zone_name == self.graph.start_zone.name:
                    continue

                if zone_name == self.graph.end_zone.name:
                    continue

                if count > zone.max_drones:
                    raise ValueError(
                        f"Zone {zone_name} capacity exceeded at turn {turn}: "
                        f"{count} > {zone.max_drones}"
                    )

        for turn, connections in conn_usage.items():
            for connection_key, count in connections.items():
                parts: List[str] = connection_key.split('-')

                if len(parts) != 2:
                    raise ValueError(
                        f"Invalid connection key: {connection_key}"
                    )

                zone_a: Optional[Zone] = self.graph.get_zone(
                    parts[0]
                )
                zone_b: Optional[Zone] = self.graph.get_zone(
                    parts[1]
                )

                if zone_a is None or zone_b is None:
                    raise ValueError(
                        f"Zone missing for connection key: {connection_key}"
                    )

                connection = (
                    self.graph.get_connection(
                        zone_a,
                        zone_b,
                    )
                )

                if connection is None:
                    raise ValueError(
                        f"Connection {connection_key} not found"
                    )

                if count > connection.max_link_capacity:
                    raise ValueError(
                        f"Connection {connection_key} capacity exceeded "
                        f"at turn {turn}: "
                        f"{count} > {connection.max_link_capacity}"
                    )

        return True

    def validate_all(
        self,
        all_paths: Dict[int, List[PathStep]],
    ) -> bool:
        """
        Run every validator check on the complete drone schedule.

        Validation is performed in this order:

        1. General path structure.
        2. Movement transitions.
        3. Zone and connection capacities.

        Args:
            all_paths:
                Dictionary mapping drone identifiers to ordered path steps.

        Returns:
            ``True`` when every validation stage succeeds.

        Raises:
            ValueError:
                Propagates the first validation error raised by any of the
                individual validation methods.
        """
        self.validate_paths_structure(all_paths)
        self.validate_transitions(all_paths)
        self.validate_capacities(all_paths)

        return True
