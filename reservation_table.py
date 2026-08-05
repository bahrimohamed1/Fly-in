from graph import Graph
from path_step import PathStep
from zone import Zone
from connection import Connection

from typing import Dict, List, Optional


class ReservationTable:
    """
    Track zone and connection usage for every turn of a drone schedule.

    The reservation table prevents several drones from using a resource
    beyond its configured capacity. Reservations are stored separately for:

    - zones, indexed by zone name and turn;
    - connections, indexed by a normalized connection key and turn.

    The class also validates and records the three supported actions:

    - waiting in the current zone for one turn;
    - moving normally to a non-restricted zone in one turn;
    - moving to a restricted zone over two turns.
    """

    def __init__(self, graph: Graph) -> None:
        """
        Initialize an empty reservation table for a graph.

        Args:
            graph:
                Graph containing the zones and connections whose capacities
                will be checked and reserved.
        """
        self.zone_reservations: Dict[str, Dict[int, int]] = {}
        self.connection_reservations: Dict[str, Dict[int, int]] = {}
        self.graph: Graph = graph

    def get_zone_count(self, zone_name: str, turn: int) -> int:
        """
        Return the number of drones reserving a zone at a given turn.

        Args:
            zone_name:
                Name of the zone to inspect.

            turn:
                Turn for which the reservation count is requested.

        Returns:
            The number of reservations for the zone at that turn. Returns
            ``0`` when the zone or turn has no recorded reservation.
        """
        if zone_name not in self.zone_reservations:
            return 0

        if turn not in self.zone_reservations[zone_name]:
            return 0

        return self.zone_reservations[zone_name][turn]

    def can_reserve_zone(self, zone_name: str, turn: int) -> bool:
        """
        Check whether one more drone may reserve a zone at a given turn.

        The start zone is always considered reservable. Every other zone is
        available only while its current reservation count is lower than its
        ``max_drones`` capacity.

        Args:
            zone_name:
                Name of the zone to check.

            turn:
                Turn at which the reservation would be made.

        Returns:
            ``True`` when the zone can accept another drone; otherwise
            ``False``.

        Raises:
            ValueError:
                If ``zone_name`` does not identify a zone in the graph.
        """
        if zone_name == self.graph.start_zone.name:
            return True

        current: int = self.get_zone_count(zone_name, turn)

        zone: Zone | None = self.graph.get_zone(zone_name)
        if not zone:
            raise ValueError("Unknown zone")

        return current < zone.max_drones

    def reserve_zone(self, zone_name: str, turn: int) -> None:
        """
        Reserve one place in a zone at a given turn.

        Args:
            zone_name:
                Name of the zone to reserve.

            turn:
                Turn at which the drone occupies the zone.

        Raises:
            ValueError:
                If the zone cannot accept another reservation at ``turn``.
        """
        if not self.can_reserve_zone(zone_name, turn):
            raise ValueError(f"Cannot reserve {zone_name} at turn {turn}")

        if zone_name not in self.zone_reservations:
            self.zone_reservations[zone_name] = {}

        if turn not in self.zone_reservations[zone_name]:
            self.zone_reservations[zone_name][turn] = 0

        self.zone_reservations[zone_name][turn] += 1

    @staticmethod
    def _normalize_key(connection_key: str) -> str:
        """
        Return a direction-independent key for a connection.

        Connection names are normalized alphabetically so that ``A-B`` and
        ``B-A`` refer to the same undirected connection.

        Args:
            connection_key:
                Connection key in ``zone_a-zone_b`` format.

        Returns:
            A normalized connection key whose zone names are sorted.
        """
        zone_a, zone_b = connection_key.split('-', 1)
        zone_a, zone_b = sorted([zone_a, zone_b])
        return f"{zone_a}-{zone_b}"

    def get_connection_count(self, connection_key: str, turn: int) -> int:
        """
        Return the number of drones reserving a connection at a given turn.

        Args:
            connection_key:
                Key of the connection to inspect. Either endpoint order is
                accepted because the key is normalized internally.

            turn:
                Turn for which the reservation count is requested.

        Returns:
            The number of reservations for the connection at that turn.
            Returns ``0`` when no reservation is recorded.
        """
        normalized_key: str = self._normalize_key(connection_key)

        if normalized_key not in self.connection_reservations:
            return 0

        if turn not in self.connection_reservations[normalized_key]:
            return 0

        return self.connection_reservations[normalized_key][turn]

    def can_reserve_connection(
            self,
            connection_key: str, turn: int
    ) -> bool:
        """
        Check whether one more drone may reserve a connection at a turn.

        Args:
            connection_key:
                Key identifying the connection. Endpoint order does not
                matter.

            turn:
                Turn at which the connection would be occupied.

        Returns:
            ``True`` when the current number of reservations is below the
            connection's ``max_link_capacity``; otherwise ``False``.

        Raises:
            ValueError:
                If either endpoint zone or the connection itself does not
                exist in the graph.
        """
        normalized_key: str = self._normalize_key(connection_key)

        current_count: int = self.get_connection_count(connection_key, turn)

        zone_a, zone_b = normalized_key.split('-', 1)

        zone_a_obj: Zone | None = self.graph.get_zone(zone_a)
        zone_b_obj: Zone | None = self.graph.get_zone(zone_b)
        if not zone_a_obj or not zone_b_obj:
            raise ValueError("Unknown zone")

        connection: Connection | None = self.graph.get_connection(
            zone_a_obj, zone_b_obj)
        if not connection:
            raise ValueError("Unknown connection")

        return current_count < connection.max_link_capacity

    def reserve_connection(self, connection_key: str, turn: int) -> None:
        """
        Reserve one place on a connection at a given turn.

        Args:
            connection_key:
                Key identifying the connection. It is normalized before
                being stored.

            turn:
                Turn at which the drone occupies the connection.

        Raises:
            ValueError:
                If the connection cannot accept another reservation at the
                requested turn.
        """
        normalized_key: str = self._normalize_key(connection_key)

        if not self.can_reserve_connection(normalized_key, turn):
            raise ValueError(f"Cannot reserve {normalized_key} at turn {turn}")

        if normalized_key not in self.connection_reservations:
            self.connection_reservations[normalized_key] = {}

        if turn not in self.connection_reservations[normalized_key]:
            self.connection_reservations[normalized_key][turn] = 0

        self.connection_reservations[normalized_key][turn] += 1

    def is_wait_valid(self, zone: Zone, turn: int) -> bool:
        """
        Check whether a drone may remain in a zone for one more turn.

        Args:
            zone:
                Zone currently occupied by the drone.

            turn:
                Current turn before the wait occurs.

        Returns:
            ``True`` when the zone is not blocked and can be reserved at
            ``turn + 1``; otherwise ``False``.
        """
        next_turn: int = turn + 1

        if zone.zone_type == 'blocked':
            return False

        if not self.can_reserve_zone(zone.name, next_turn):
            return False

        return True

    def is_normal_move_valid(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> bool:
        """
        Check whether a one-turn movement to a neighbor is valid.

        A normal movement may enter a passable, non-restricted zone. The
        destination zone and connecting link must both have capacity at the
        next turn.

        Args:
            current_zone:
                Zone from which the drone moves.

            neighbor_zone:
                Destination zone reached after one turn.

            turn:
                Turn at which the drone leaves ``current_zone``.

        Returns:
            ``True`` when the move is valid; otherwise ``False``.

        Raises:
            ValueError:
                If no graph connection exists between the two zones.
        """
        next_turn: int = turn + 1

        if neighbor_zone.zone_type == 'blocked':
            return False

        if neighbor_zone.zone_type == 'restricted':
            return False

        if not self.can_reserve_zone(neighbor_zone.name, next_turn):
            return False

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            raise ValueError("Unknown connection")

        connection_key: str = connection.key()
        if not self.can_reserve_connection(connection_key, next_turn):
            return False

        return True

    def is_restricted_move_valid(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> bool:
        """
        Check whether a two-turn movement into a restricted zone is valid.

        The drone occupies the connection at both ``turn + 1`` and
        ``turn + 2``, then occupies the restricted destination at
        ``turn + 2``.

        Args:
            current_zone:
                Zone from which the drone begins the restricted movement.

            neighbor_zone:
                Restricted destination zone.

            turn:
                Turn at which the drone leaves ``current_zone``.

        Returns:
            ``True`` when the destination and connection are available for
            all required turns; otherwise ``False``.
        """
        next_turn: int = turn + 1
        arrival_turn: int = next_turn + 1

        if neighbor_zone.zone_type == 'blocked':
            return False

        if neighbor_zone.zone_type != 'restricted':
            return False

        if not self.can_reserve_zone(neighbor_zone.name, arrival_turn):
            return False

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            return False

        connection_key: str = connection.key()
        if not self.can_reserve_connection(connection_key, next_turn):
            return False

        if not self.can_reserve_connection(connection_key, arrival_turn):
            return False

        return True

    def reserve_wait(self, zone: Zone, turn: int) -> None:
        """
        Reserve a one-turn wait in the current zone.

        Args:
            zone:
                Zone in which the drone remains.

            turn:
                Current turn before the wait.

        Raises:
            ValueError:
                If the zone cannot be occupied at ``turn + 1``.
        """
        next_turn: int = turn + 1
        zone_name: str = zone.name

        if not self.is_wait_valid(zone, turn):
            raise ValueError(f"Cannot reserve wait: Zone {zone_name} "
                             f"is not available at turn {next_turn}")

        self.reserve_zone(zone_name, next_turn)

    def reserve_normal_move(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> None:
        """
        Reserve a one-turn movement to a non-restricted neighboring zone.

        The connection and destination zone are both reserved at
        ``turn + 1``.

        Args:
            current_zone:
                Zone from which the drone moves.

            neighbor_zone:
                Destination zone.

            turn:
                Turn at which the drone leaves ``current_zone``.

        Raises:
            ValueError:
                If the movement is invalid or the graph connection does not
                exist.
        """
        next_turn: int = turn + 1
        current_zone_name: str = current_zone.name
        neighbor_zone_name: str = neighbor_zone.name

        if not self.is_normal_move_valid(current_zone, neighbor_zone, turn):
            raise ValueError("Cannot reserve normal move: "
                             f"drone cannot move from {current_zone_name} to "
                             f"{neighbor_zone_name} at turn {next_turn}")

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            raise ValueError("Unknown connection")
        connection_key: str = connection.key()

        self.reserve_connection(connection_key, next_turn)
        self.reserve_zone(neighbor_zone_name, next_turn)

    def reserve_restricted_move(
        self, current_zone: Zone, neighbor_zone: Zone, turn: int
    ) -> None:
        """
        Reserve a two-turn movement into a restricted neighboring zone.

        The connection is reserved at ``turn + 1`` and ``turn + 2``. The
        restricted destination zone is reserved at ``turn + 2``.

        Args:
            current_zone:
                Zone from which the drone begins the move.

            neighbor_zone:
                Restricted destination zone.

            turn:
                Turn at which the drone leaves ``current_zone``.

        Raises:
            ValueError:
                If the movement is invalid or the graph connection does not
                exist.
        """
        next_turn: int = turn + 1
        arrival_turn: int = turn + 2
        current_zone_name: str = current_zone.name
        neighbor_zone_name: str = neighbor_zone.name

        if not self.is_restricted_move_valid(
                current_zone, neighbor_zone, turn):
            raise ValueError("Cannot reserve restricted move: "
                             f"drone cannot move from {current_zone_name} to "
                             f"{neighbor_zone_name} at turn {arrival_turn}")

        connection: Connection | None = self.graph.get_connection(
            current_zone, neighbor_zone)
        if not connection:
            raise ValueError("Unknown connection")
        connection_key: str = connection.key()

        self.reserve_connection(connection_key, next_turn)
        self.reserve_connection(connection_key, arrival_turn)
        self.reserve_zone(neighbor_zone_name, arrival_turn)

    def reserve_path(self, path_steps: List[PathStep]) -> None:
        """
        Validate and reserve every action contained in a complete path.

        The path must begin with a zone step at turn ``0``. The remaining
        steps are interpreted as one of the following forms:

        - ``zone -> same zone``: a one-turn wait;
        - ``zone -> different zone``: a one-turn normal movement;
        - ``zone -> connection -> restricted zone``: a two-turn restricted
          movement.

        Each action is validated immediately before its resources are
        reserved.

        Args:
            path_steps:
                Ordered sequence of zone and connection steps describing the
                drone's complete path.

        Raises:
            ValueError:
                If the path is empty, contains an unknown resource, starts
                incorrectly, has invalid timing, contains an unsupported step
                pattern, or requests a reservation that cannot be made.
        """
        if not path_steps:
            raise ValueError("ERROR: Path is empty")

        first_step: PathStep = path_steps[0]
        if first_step.kind != 'zone':
            raise ValueError(
                f"ERROR: First step '{first_step.name}' is not a zone")

        if first_step.turn != 0:
            raise ValueError(
                f"ERROR: First step '{first_step.name}' turn is not 0:"
                f"got {first_step.turn}")

        start_zone: Optional[Zone] = self.graph.get_zone(first_step.name)
        if not start_zone:
            raise ValueError(f"ERROR: zone '{first_step.name}' does not exist")
        if self.get_zone_count(start_zone.name, 0) == 0:
            self.reserve_zone(start_zone.name, 0)

        i: int = 0
        while i < len(path_steps) - 1:
            current_step: PathStep = path_steps[i]

            if current_step.kind != 'zone':
                raise ValueError(
                    f"ERROR: Current step '{current_step.name}' is not a zone")

            current_zone: Optional[Zone] = self.graph.get_zone(
                current_step.name)
            if not current_zone:
                raise ValueError(
                    f"ERROR: zone '{current_step.name}' does not exist")

            next_step: PathStep = path_steps[i+1]

            # wait / normal
            if next_step.kind == 'zone':
                next_zone: Optional[Zone] = self.graph.get_zone(next_step.name)

                if not next_zone:
                    raise ValueError(
                        f"ERROR: zone '{next_step.name}' does not exist")

                expected_turn: int = current_step.turn + 1
                if expected_turn != next_step.turn:
                    raise ValueError("ERROR: Invalid wait/normal move timing")

                # wait
                if next_zone.name == current_step.name:
                    self.reserve_wait(current_zone, current_step.turn)

                # normal
                else:
                    self.reserve_normal_move(
                        current_zone, next_zone, current_step.turn)

                i += 1

            # restricted
            elif next_step.kind == 'connection':
                if i + 2 >= len(path_steps):
                    raise ValueError(
                        "ERROR: Not enough steps for arrival zone")

                arrival_step: PathStep = path_steps[i+2]
                if arrival_step.kind != 'zone':
                    raise ValueError(
                        "ERROR: Restricted move must end with a zone step")

                arrival_zone: Optional[Zone] = self.graph.get_zone(
                    arrival_step.name)
                if not arrival_zone:
                    raise ValueError(
                        f"ERROR: zone '{arrival_step.name}' does not exist")
                if arrival_zone.zone_type != 'restricted':
                    raise ValueError(
                        f"ERROR: Zone '{arrival_zone.name}' is not restricted")

                next_conn: Optional[Connection] = self.graph.get_connection(
                    current_zone, arrival_zone)
                if not next_conn:
                    raise ValueError(
                        f"ERROR: Connection '{next_step.name}' does not exist")

                connection_key: str = next_conn.key()
                if connection_key != next_step.name:
                    raise ValueError(
                        "Connection step does not match actual connection")

                next_turn: int = current_step.turn + 1
                arrival_turn: int = current_step.turn + 2

                if next_step.turn != next_turn:
                    raise ValueError(
                        "ERROR: Invalid restricted connection timing")

                if arrival_step.turn != arrival_turn:
                    raise ValueError(
                        "ERROR: Invalid restricted arrival timing")

                self.reserve_restricted_move(
                    current_zone, arrival_zone, current_step.turn)

                i += 2

            else:
                raise ValueError("ERROR: Invalid path step kind")
