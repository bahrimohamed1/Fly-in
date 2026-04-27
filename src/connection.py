from dataclasses import dataclass, field


@dataclass
class Connection:
    """Represents a bidirectional connection between two zones."""

    zone_a: str
    zone_b: str
    max_link_capacity: int = field(default=1)
