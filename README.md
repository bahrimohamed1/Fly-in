# Fly-in — Drone Routing Simulator

A discrete-turn drone routing simulation written in Python 3.10+.

## Requirements

- Python 3.10 or later
- `flake8` and `mypy` (installed via `requirements.txt`)

## Setup

```bash
make install
```

## Usage

```bash
# Run simulation on a map file
python3 main.py <map_file>

# Enable ANSI colour output
python3 main.py <map_file> --visual

# Show per-turn ASCII map state
python3 main.py <map_file> --debug

# Makefile shortcut (defaults to maps/easy/01_linear_path.txt)
make run MAP=maps/easy/01_linear_path.txt
```

## Map File Format

```
nb_drones: 5

start_hub: hub 0 0 [color=green]
end_hub:   goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=green max_drones=2]

connection: hub-roof1
connection: corridorA-goal [max_link_capacity=2]
```

- Lines starting with `#` are comments and are ignored.
- `nb_drones:` must be the first non-comment, non-empty line.
- Zone types: `normal` (default), `priority`, `restricted`, `blocked`.
- `blocked` zones are impassable.
- `restricted` zones take **2 turns** to enter (1 turn in transit,
  1 turn in the zone).
- Connections are bidirectional.

## Movement Rules

| Zone type  | Cost | Notes                          |
|------------|------|--------------------------------|
| priority   | 0.5  | Preferred by pathfinder        |
| normal     | 1.0  | Default                        |
| restricted | 2.0  | Two-turn transit               |
| blocked    | ∞    | Impassable                     |

- All drones move simultaneously each turn.
- Drones leaving a zone free its capacity in the **same** turn.
- Lower drone ID wins capacity conflicts.
- A drone in transit to a restricted zone **must** arrive the next turn.

## Output Format

Each line represents one turn:

```
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

- `D<id>-<zone>`: drone arrived at zone.
- `D<id>-<from>-<to>`: drone is in transit on a connection to a
  restricted zone.
- Drones that did not move are omitted.

## Development

```bash
make lint   # flake8 + mypy
make clean  # remove __pycache__ / .mypy_cache
```

## Project Structure

```
main.py        CLI entry point
graph.py       Data structures (Graph, Zone, Connection, ZoneType)
parser.py      Map file parser
router.py      Dijkstra pathfinder with usage-penalty diversification
simulator.py   Discrete-turn simulation engine
renderer.py    ANSI terminal renderer
Makefile
requirements.txt
maps/          Sample map files
```
