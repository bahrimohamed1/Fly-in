class PathStep:
    def __init__(self, turn: int, kind: str, name: str) -> None:
        self.turn: int = turn
        self.kind: str = kind
        self.name: str = name

        if self.turn < 0:
            raise ValueError("Turn cannot be negative")

        if self.kind != 'zone' and self.kind != 'connection':
            raise ValueError("Kind should be 'Zone' or 'Connection'")

        if not self.name:
            raise ValueError("Name cannot be empty")

    def is_zone(self) -> bool:
        return self.kind == 'zone'

    def is_connection(self) -> bool:
        return self.kind == 'connection'
