*This project has been created as part of the 42 curriculum by mbahri.*

# Fly-in

---

# Table of Contents

- [How Fly-in Works](#how-fly-in-works)
- [Project Objectives](#project-objectives)
- [Key Features](#key-features)
- [Project Architecture](#project-architecture)
- [Input File Format](#input-file-format)
- [Zone Types](#zone-types)
- [Scheduling Strategy](#scheduling-strategy)
- [PathFinder](#pathfinder)
- [Reservation System](#reservation-system)
- [Validation](#validation)
- [Algorithmic Choices](#algorithmic-choices)
- [Complexity Analysis](#complexity-analysis)
- [Project Structure](#project-structure)
- [Compilation & Execution](#compilation--execution)
- [Resources](#resources)
- [AI Usage](#ai-usage)

---

# How Fly-in Works

Fly-in is a graph-based scheduling and pathfinding project developed as part of the **42 curriculum**.

The objective is to transport **multiple drones** from a single **start hub** to a single **destination hub** while respecting a collection of operational constraints.

Unlike a traditional shortest-path problem, Fly-in must coordinate **multiple moving entities** that share the same transportation network.

Every drone occupies network resources while travelling.

These resources include:

- zones;
- connections;
- restricted areas.

Once a resource has been allocated to one drone during a specific turn, another drone may no longer use that resource if doing so would violate its capacity.

Consequently, each drone influences every drone scheduled after it.

Finding a valid solution therefore requires combining:

- graph traversal;
- temporal planning;
- collision avoidance;
- resource reservation;
- scheduling.

The result is significantly more complex than finding a shortest path inside a graph.

---

# Project Objectives

The project aims to solve five independent problems simultaneously.

## 1. Find valid paths

Every drone must successfully travel from the start hub to the destination hub.

```text
Start
  │
  ▼
Goal
```

---

## 2. Prevent collisions

Example:

```text
Turn 4

Drone 1 ──► Zone A

Drone 2 ──► Zone A
```

If Zone A has capacity **1**, the schedule is invalid.

---

## 3. Respect every zone type

Different zones behave differently.

Examples include:

- blocked zones;
- restricted zones;
- priority zones.

Each of them changes how the pathfinder evaluates possible movements.

---

## 4. Respect capacities

Every resource has its own capacity.

Examples:

| Resource | Example Capacity |
|-----------|-----------------:|
| Zone | 1 drone |
| Connection | 2 drones |
| Start hub | Unlimited |
| End hub | Unlimited |

The scheduler must ensure these capacities are never exceeded.

---

## 5. Produce an optimal schedule

The objective is not simply to find **a** valid schedule.

The scheduler attempts to minimise the total completion time while satisfying every project constraint.

---

# Key Features

✔ Graph-based network representation

✔ Multiple zone types

✔ Reservation-based scheduling

✔ Collision avoidance

✔ Waiting support

✔ Restricted-zone traversal

✔ Priority-zone preference

✔ Multiple scheduling attempts

✔ Automatic retry with increasing search horizon

✔ Path validation

✔ Modular object-oriented architecture

---

# Project Architecture

The project is divided into several independent components.

Each class has a single responsibility.

```text
                    Input Map
                        │
                        ▼
                   ┌──────────┐
                   │  Parser  │
                   └──────────┘
                        │
                        ▼
                   ┌──────────┐
                   │  Graph   │
                   └──────────┘
                        │
        ┌───────────────┼────────────────┐
        ▼                                ▼
┌──────────────────┐            ┌──────────────────┐
│ ReservationTable │            │    PathFinder    │
└──────────────────┘            └──────────────────┘
        ▲                                │
        └───────────────┬────────────────┘
                        ▼
                 ┌──────────────┐
                 │  Scheduler   │
                 └──────────────┘
                        │
                        ▼
                 ┌──────────────┐
                 │  Validator   │
                 └──────────────┘
```

The design follows a modular architecture where every component performs one clearly defined task.

This separation makes the project easier to understand, maintain and extend.

---

# Component Overview

## Parser

The parser reads the input map file and converts it into internal objects.

Responsibilities include:

- validating syntax;
- creating every zone;
- creating every connection;
- detecting malformed maps;
- constructing the graph.

The parser performs **no scheduling**.

Its only responsibility is transforming the input file into an in-memory representation.

---

## Graph

The graph represents the drone transportation network.

It stores:

- every zone;
- every connection;
- adjacency information;
- the start hub;
- the destination hub.

The graph is considered immutable after construction.

Its responsibility is to answer questions such as:

- Which neighbours does this zone have?
- Does this connection exist?

The graph never performs scheduling decisions.

---

## PathFinder

The PathFinder searches for one valid path.

It is responsible for:

- graph traversal;
- reservation checking;
- restricted movement;
- waiting;
- priority-zone preference.

The PathFinder searches only for **one drone at a time**.

It has no knowledge of future drones.

---

## ReservationTable

The ReservationTable stores every resource already allocated to previously scheduled drones.

Whenever the PathFinder considers a movement, it consults the ReservationTable to determine whether that movement is still possible.

This completely separates **pathfinding** from **resource management**.

---

## Scheduler

The Scheduler coordinates the entire planning process.

For every drone it:

1. asks the PathFinder for a path;
2. reserves that path;
3. repeats for the next drone.

If scheduling fails, it automatically retries using different scheduling orders before increasing the search horizon.

---

## Validator

The Validator independently verifies that every generated solution satisfies the project rules.

Validation includes:

- path structure;
- legal transitions;
- resource capacities.

This provides an additional safety layer after scheduling.

---

# Input File Format

Fly-in receives the network description from a text file.

The parser reads this file and constructs the complete graph before any scheduling begins.

A minimal example is shown below.

```text
nb_drones: 3

start_hub: start 0 0 [color=green]

hub: A 1 0

hub: B 2 0 [zone=priority]

hub: C 3 0 [zone=restricted]

end_hub: goal 4 0 [color=red]

connection: start-A
connection: A-B
connection: B-C
connection: C-goal
```

Every line describes one element of the transportation network.

---

# Network Components

## Number of Drones

```text
nb_drones: 5
```

Defines how many drones must be transported from the start hub to the destination hub.

---

## Start Hub

```text
start_hub: start 0 0
```

The start hub is the origin of every drone.

Characteristics:

- exactly one start hub exists;
- unlimited capacity;
- every drone begins here at turn **0**.

---

## End Hub

```text
end_hub: goal 8 3
```

The destination of every drone.

Characteristics:

- exactly one end hub exists;
- unlimited capacity;
- every drone must eventually reach this zone.

---

## Hub

```text
hub: A 3 5
```

Represents a normal intermediate zone.

Additional metadata may also be specified.

Example:

```text
hub: A 3 5 [zone=priority color=yellow max_drones=2]
```

---

## Connections

```text
connection: A-B
```

Represents a bidirectional edge between two zones.

Connections also have capacities.

Example:

```text
connection: A-B [max_link_capacity=2]
```

This means two drones may simultaneously traverse that connection.

---

# Zone Types

Every zone belongs to one of four categories.

---

## Normal Zone

```text
zone=normal
```

Characteristics:

- movement cost = 1 turn;
- fully traversable;
- no special behaviour.

---

## Blocked Zone

```text
zone=blocked
```

Characteristics:

- cannot be entered;
- ignored by the PathFinder;
- behaves like an obstacle.

Example

```text
A ──► Blocked Zone
```

The algorithm immediately discards this movement.

---

## Restricted Zone

Restricted zones require **two turns** to enter.

Instead of:

```text
Zone
     │
     ▼
Zone
```

the movement becomes

```text
Zone
     │
     ▼
Connection
     │
     ▼
Restricted Zone
```

This produces two PathSteps:

```text
Turn 4

connection

Turn 5

restricted zone
```

Restricted movements therefore reserve both:

- the connection;
- the destination zone.

---

## Priority Zone

Priority zones are preferred whenever two candidate paths are otherwise equally good.

Example:

```text
          Priority

Start ─────────────► A ───► Goal

Start ───► B ───► Goal
```

If both paths require the same number of turns, the path containing the priority zone is selected.

Priority zones **do not** reduce movement cost.

Priority zones are **not mandatory**.

They simply influence tie-breaking.

---

# Scheduling Strategy

Scheduling multiple drones simultaneously is considerably harder than finding a path for a single drone.

Instead of searching for all drones at once, Fly-in schedules drones sequentially.

```text
Drone 1

Find path

↓

Reserve resources

↓

Drone 2

Find path

↓

Reserve resources

↓

Drone 3

...
```

Every successful path immediately reserves every occupied resource.

Later drones therefore search inside an environment that changes after every scheduled drone.

---

# Search State

The PathFinder does not search only through graph vertices.

Instead, it searches through **states**.

A state contains four pieces of information.

```text
SearchState

├── current zone
├── current turn
├── complete path
└── priority count
```

Example

```text
Zone

Waypoint3

Turn

7

Priority count

2
```

Two states occupying the same zone are considered different whenever they occur at different turns.

```text
Waypoint A
Turn 3

≠

Waypoint A
Turn 5
```

This allows the algorithm to reason about resource availability over time.

---

# PathFinder

The PathFinder is responsible for finding one valid path while respecting all existing reservations.

It performs a best-first search using a binary heap.

Unlike classical Dijkstra's algorithm, every explored state represents both:

- a graph location;
- a point in time.

The search therefore occurs inside a **space-time graph**.

---

# Priority Queue

Every candidate state is inserted into a binary heap.

Each queue entry has the following structure.

```python
(
    arrival_turn,
    -priority_count,
    insertion_counter,
    SearchState,
)
```

The heap always removes the **smallest** tuple.

Python compares tuples from left to right.

---

## First comparison

```text
arrival_turn
```

The search primarily minimizes arrival turn. Among states that arrive at the same turn, the algorithm prefers the one that has entered more priority zones.

Example

```text
(3, ...)

(5, ...)
```

The first path wins immediately because

```text
3 < 5
```

---

## Second comparison

If arrival turns are identical, Python compares

```text
-priority_count
```

Example

```text
(4, -2)

(4, 0)
```

Because

```text
-2 < 0
```

the first path is explored first.

This corresponds to

```text
priority_count = 2
```

versus

```text
priority_count = 0
```

The negative sign is required because Python's heap is a **min-heap**.

Without negation,

```text
0 < 2
```

would incorrectly favour the path containing fewer priority zones.

---

## Third comparison

If both previous values are identical, the insertion counter is compared.

This guarantees deterministic behaviour.

Two identical executions therefore always produce identical schedules.

---

# Priority Count

Priority count records how many priority zones have been entered by the current path.

Example

```text
Start

↓

Priority

↓

Normal

↓
Priority

↓

Goal
```

Evolution

```text
Start

0

↓

Priority

1

↓

Normal

1

↓

Priority

2
```

Priority count never changes movement cost.

It exists only to distinguish equally fast paths.

---

# Why Priority Zones Are Only a Tie-breaker

The Fly-in subject specifies that priority zones are **preferred**.

It does **not** state that drones must always traverse them.

Consider the following example.

```text
Priority path

4 turns

Normal path

2 turns
```

Choosing the priority path would deliberately produce a worse schedule.

Instead, Fly-in follows this policy:

1. minimise arrival time;
2. among equally fast paths, maximise the number of priority zones.

This exactly matches the intended behaviour described by the project specification.

---

# Waiting

Waiting is treated as an ordinary search action.

Instead of moving,

```text
Turn 4

Zone A
```

becomes

```text
Turn 5

Zone A
```

Waiting allows a drone to postpone movement until another resource becomes available.

Without waiting, many otherwise valid schedules would become impossible.

---

# Reservation System

The reservation system is the core component that allows multiple drones to safely share the same transportation network.

Instead of planning every drone simultaneously, Fly-in schedules drones **one after another**.

After a valid path has been found for a drone, every resource used by that path is immediately reserved.

Future drones must respect these reservations.

This transforms a difficult multi-agent planning problem into a sequence of constrained single-agent searches.

---

# Why Reservations Are Necessary

Consider the following example.

```text
            A

Drone 1 ─────────► Goal

Drone 2 ─────────► Goal
```

Suppose zone **A** has capacity **1**.

Without reservations, both drones would attempt to occupy the zone during the same turn.

```text
Turn 4

Drone 1 → Zone A

Drone 2 → Zone A
```

This creates a collision.

Instead, the ReservationTable records that:

```text
Turn 4

Zone A

occupied
```

When Drone 2 searches for a path, entering Zone A during Turn 4 is no longer considered a valid move.

The PathFinder must therefore:

- wait,
- take another route,
- or fail if no alternative exists.

---

# Reserved Resources

The ReservationTable manages two independent resource types.

## Zone Reservations

Zone reservations record how many drones occupy each zone at every turn.

Conceptually, the table behaves as follows.

```text
Turn 3

Zone A

2 drones
```

Whenever another drone wishes to enter Zone A during Turn 3, the reservation table compares:

```text
current occupancy

vs

zone capacity
```

If the capacity would be exceeded, the movement is rejected.

---

## Connection Reservations

Connections are also treated as resources.

Example

```text
A ───────────► B
```

If a connection has capacity **1**, only one drone may traverse it during the corresponding turn.

The ReservationTable therefore stores information such as:

```text
Turn 8

Connection A-B

occupied
```

---

# Waiting

Waiting is handled exactly like movement.

Instead of changing zones, the drone simply remains where it is.

Example

```text
Turn 5

Zone A

↓

Turn 6

Zone A
```

Waiting is allowed only when:

- the zone still has available capacity;
- remaining in the zone does not violate any reservation.

Waiting is essential because another drone may free a resource during the following turn.

Without waiting, many valid schedules could never be found.

---

# Restricted Movements

Restricted zones require two turns to enter.

Instead of

```text
Zone

↓

Restricted Zone
```

the movement becomes

```text
Turn t

Zone

↓

Turn t + 1

Connection

↓

Turn t + 2

Restricted Zone
```

During those two turns, the ReservationTable reserves:

- the connection;
- the restricted zone.

This prevents another drone from entering the same restricted movement simultaneously.

---

# Scheduler

The Scheduler coordinates the complete scheduling process.

It does not compute paths itself.

Instead, it repeatedly asks the PathFinder to find one valid path.

The overall workflow is:

```text
Drone 1

↓

Find path

↓

Reserve path

↓

Drone 2

↓

Find path

↓

Reserve path

↓

Drone 3

↓

...
```

Once a path has been reserved, it never changes during that scheduling attempt.

---

# Multiple Scheduling Orders

Scheduling greedily in only one order can easily fail.

Example

```text
Drone 1

takes the only useful shortcut

↓

Drone 2

no path remains
```

However, reversing the order may produce a valid solution.

For this reason the Scheduler automatically generates several drone orders.

Examples include:

```text
Normal

1 2 3 4 5
```

```text
Reverse

5 4 3 2 1
```

```text
Odd / Even

1 3 5 2 4
```

```text
Even / Odd

2 4 1 3
```

```text
Middle-first
```

```text
Random shuffle
```

Every ordering begins with a completely empty ReservationTable.

No failed attempt influences later attempts.

---

# Retry Strategy

Occasionally, every scheduling order fails simply because the search horizon is too small.

Example

```text
Maximum turns

20
```

A solution may exist in

```text
24 turns
```

Rather than immediately reporting failure, the Scheduler progressively increases the search horizon.

Example

```text
20 turns

↓

70 turns

↓

120 turns

↓

...
```

After each increase:

- reservations are cleared;
- scheduling restarts;
- every ordering is tested again.

This continues until:

- a complete schedule is found;
- or the configured maximum search limit is reached.

---

# Validator

After scheduling finishes, every generated solution is independently verified.

Validation is divided into three independent stages.

```text
Path Structure

↓

Transitions

↓

Capacities
```

Separating validation into independent stages simplifies debugging because every error belongs to one clearly defined category.

---

# Path Structure Validation

The validator first checks that every path has the expected format.

Examples include:

- starts at turn 0;
- starts in the start hub;
- ends in the destination hub;
- turn numbers are strictly increasing;
- every PathStep uses a valid type.

Example

```text
Turn 4

↓

Turn 4
```

This immediately fails because turns must always increase.

---

# Transition Validation

The validator then checks every movement.

Examples include:

- connected zones;
- legal waiting;
- valid restricted movement;
- existing connections.

Example

```text
Zone A

↓

Zone C
```

If no connection exists between A and C, the schedule is invalid.

---

# Capacity Validation

Finally, resource usage is reconstructed from every drone path.

For each turn, the validator counts:

- drones occupying each zone;
- drones using each connection.

Those values are compared against the configured capacities.

Example

```text
Zone A

Capacity

1

Occupancy

2
```

The validator immediately rejects the schedule.

---

# Algorithmic Choices

The architecture of Fly-in was designed around three fundamental principles:

1. **Separation of responsibilities**
2. **Deterministic behaviour**
3. **Extensibility**

Rather than combining every responsibility into one large algorithm, the project is divided into several independent components.

Each component performs exactly one task.

This approach makes the project easier to:

- understand;
- debug;
- test;
- extend;
- maintain.

---

# Why Represent the Network as a Graph?

The transportation network naturally forms a graph.

```text
           Connection

Zone A ─────────────── Zone B
           │
           │
           ▼
        Zone C
```

This representation provides several advantages.

- Every zone becomes a graph vertex.
- Every connection becomes a graph edge.
- Neighbour lookup is efficient.
- Standard graph algorithms can be applied.

The graph itself never changes during scheduling.

Instead, dynamic information such as occupied resources is stored separately inside the ReservationTable.

---

# Why Search in Space and Time?

Traditional graph search only considers location.

Example:

```text
Current state

Zone A
```

For Fly-in this is insufficient.

Consider two states:

```text
Zone A
Turn 3
```

and

```text
Zone A
Turn 8
```

Although both represent the same physical location, they are completely different scheduling states.

The zone may already be occupied during Turn 3 while becoming free again during Turn 8.

For this reason every search state stores both:

```text
(zone,
turn)
```

instead of only

```text
zone
```

This transforms the search into a **space-time search**, allowing the algorithm to reason about future resource availability.

---

# Why Use SearchState?

The PathFinder explores SearchState objects instead of raw graph vertices.

Each SearchState stores:

```text
SearchState

├── Current zone
├── Current turn
├── Complete path
└── Priority count
```

Keeping all required information together makes the search algorithm significantly simpler.

Each state contains everything required to continue the search without reconstructing previous movements.

---

# Why Use a Priority Queue?

The search explores candidate paths using a binary heap.

Each queue entry is represented as:

```python
(
    arrival_turn,
    -priority_count,
    insertion_counter,
    SearchState,
)
```

Using a heap provides efficient retrieval of the most promising candidate.

The queue ordering is:

1. Earliest arrival turn.
2. Highest priority count.
3. Earliest insertion.

This ensures deterministic behaviour while still preferring priority zones whenever multiple equally fast paths exist.

---

# Why Is Priority Count Used?

The Fly-in subject specifies that priority zones are **preferred**.

It does **not** require drones to always enter priority zones.

Instead of modifying movement cost, the implementation stores:

```text
priority_count
```

inside every SearchState.

Whenever a path enters a priority zone,

```text
priority_count += 1
```

Example:

```text
Start

↓

Priority

↓

Normal

↓

Priority

↓

Goal
```

Evolution:

```text
0

↓

1

↓

1

↓

2
```

The value never changes travel time.

Instead, it serves only as a tie-breaker.

Suppose two candidate paths arrive simultaneously.

```text
Path A

Turn 6

Priority count 0
```

```text
Path B

Turn 6

Priority count 2
```

Both satisfy the primary objective of earliest arrival.

Since their arrival turns are identical, the algorithm selects Path B because it follows more preferred zones.

---

# Why Store the Negative Priority Count?

Python's `heapq` is implemented as a **min-heap**.

This means the smallest tuple is removed first.

If positive values were stored:

```text
(4, 0)

(4, 2)
```

Python would incorrectly choose

```text
0
```

before

```text
2
```

resulting in paths with fewer priority zones being preferred.

Instead, the implementation stores

```text
-priority_count
```

Example:

```text
Priority count

2

↓

Stored value

-2
```

Now

```text
-2 < 0
```

which correctly causes the path containing more priority zones to be explored first.

---

# Why Keep Reservations Separate?

The graph describes only the transportation network.

It never changes during scheduling.

Dynamic information such as:

- occupied zones;
- occupied connections;
- waiting drones;

is stored inside the ReservationTable.

This separation provides several benefits.

- The graph remains immutable.
- Scheduling logic stays independent.
- Reservation rules can evolve without modifying graph code.

---

# Why Schedule Drones Sequentially?

Scheduling every drone simultaneously would require solving a considerably more difficult optimisation problem.

Instead, Fly-in schedules drones one after another.

```text
Drone 1

↓

Reserve path

↓

Drone 2

↓

Reserve path

↓

Drone 3
```

This greedy strategy greatly reduces implementation complexity while still producing valid schedules.

---

# Why Try Multiple Scheduling Orders?

Greedy scheduling depends on the order in which drones are planned.

Example:

```text
Drone 1

takes shortcut

↓

Drone 2

blocked
```

However,

```text
Drone 2

first

↓

Drone 1

second
```

may produce a valid schedule.

Rather than relying on one arbitrary ordering, Fly-in automatically tries several different scheduling orders before declaring failure.

This significantly increases the probability of finding a complete schedule.

---

# Complexity Analysis

The following table summarizes the asymptotic complexity of the project's principal operations.

| Operation | Complexity |
|-----------|------------|
| Graph construction | **O(V + E)** |
| Zone lookup | **O(1)** |
| Connection lookup* | **O(E)** |
| Neighbour lookup | **O(1)** |
| Reservation lookup | **O(1)** average |
| Single path search | **O((V × T + E × T) log(V × T))** |
| Validation | **O(P)** |

Where:

- **V** = number of zones
- **E** = number of connections
- **T** = explored turns (bounded by `max_turns`)
- **P** = total number of generated path steps

*The current implementation performs a linear scan through all connections. This could be reduced to O(1) by storing connections in a dictionary indexed by their endpoints.

---

# Compilation & Execution

## Build

```bash
make
```

---

## Clean object files

```bash
make clean
```

---

## Remove executable

```bash
make fclean
```

---

## Rebuild everything

```bash
make re
```

---

## Run the project

```bash
python3 main.py map_path.txt
```

---

# Project Structure

```text
.
├── README.md
├── Makefile
├── main.py
├── parser.py
├── graph.py
├── zone.py
├── connection.py
├── search_state.py
├── path_step.py
├── reservation_table.py
├── path_finder.py
├── scheduler.py
├── validator.py
├── output_builder.py
└── requirements.txt
```

---

# Resources

- [Python documentation](https://docs.python.org/3/)
- [heapq — Heap queue algorithm](https://docs.python.org/3/library/heapq.html)
- [Dijkstra's algorithm](https://en.wikipedia.org/wiki/Dijkstra%27s_algorithm)

---

# AI Usage

AI was used as a development assistant for documentation, algorithm discussions, code reviews, and educational explanations. All architectural decisions, implementation, debugging, testing, and final validation were performed by the project author.
