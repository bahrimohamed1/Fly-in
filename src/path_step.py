class PathStep:
    """
    Represents a single step in a drone's path at a specific turn.

    A PathStep captures the drone's location at a given simulation turn.
    The location can be either a zone (drone is in a zone) or a connection
    (drone is in transit toward a restricted zone).

    Attributes:
        turn (int): The simulation turn number when this step occurs.
        kind (str): The type of resource - either 'zone' or 'connection'.
        name (str): The name of the zone or connection.

    Raises:
        ValueError: If turn is negative, kind is invalid, or name is empty.
    """

    def __init__(self, turn: int, kind: str, name: str) -> None:
        """
        Initialize a PathStep with turn, kind, and name.

        Args:
            turn: The simulation turn number (must be >= 0).
            kind: The resource type - must be 'zone' or 'connection'.
            name: The name of the zone or connection (cannot be empty).

        Raises:
            ValueError: If turn < 0, kind is not 'zone' or 'connection',
                       or name is empty.
        """
        self.turn: int = turn
        self.kind: str = kind
        self.name: str = name

        if self.turn < 0:
            raise ValueError("Turn cannot be negative")

        if self.kind != 'zone' and self.kind != 'connection':
            raise ValueError("Kind should be 'zone' or 'connection'")

        if not self.name:
            raise ValueError("Name cannot be empty")

    def is_zone(self) -> bool:
        """
        Check if this step represents a zone.

        Returns:
            bool: True if the step is a zone, False otherwise.
        """
        return self.kind == 'zone'

    def is_connection(self) -> bool:
        """
        Check if this step represents a connection.

        Returns:
            bool: True if the step is a connection, False otherwise.
        """
        return self.kind == 'connection'

    def __repr__(self) -> str:
        """
        Return a string representation of the PathStep.

        Returns:
            str: A string in the format "(turn, kind, name)".
        """
        return f"PathStep(turn={self.turn}, kind='{self.kind}', name='{self.name}')"

    def __str__(self) -> str:
        """
        Return a human-readable string representation.

        Returns:
            str: A string showing the turn and resource.
        """
        return f"Turn {self.turn}: {self.kind} -> {self.name}"
