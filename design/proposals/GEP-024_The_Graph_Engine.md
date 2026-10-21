---
title: "GEP-024: The Graph Engine"
description: "Decouple graph traversal and event generation from storage into an observable GraphEngine and GraphObserver architecture."
icon: lucide/cpu
status: draft
---

# GEP-024: The Graph Engine

| Field       | Value                                      |
|:------------|:-------------------------------------------|
| **GEP**     | 24                                         |
| **Title**   | The Graph Engine                           |
| **Author**  | Eran Rivlis                                |
| **Delegate**| The Council                                |
| **Status**  | Draft                                      |
| **Type**    | Standards Track                            |
| **Created** | 2025-12-28                                 |
| **Updated** | 2026-10-21                                 |
| **Replaces**| GEP-015                                    |

## Abstract

This proposal extracts graph execution logic (iterating generator functions, dependency injection via `ParentId`,
lineage calculation, and multiplicity handling) out of [`NetworkxBuilder`](file:///C:/dev/erivlis/graphinate/src/graphinate/builders/networkx.py)
into a dedicated, observable execution component: `GraphEngine`.

By separating execution (producer) from storage (consumer), Graphinate transforms from a NetworkX-only builder into a
universal Graph Synthesis Engine capable of streaming events to multiple consumers simultaneously (e.g. NetworkX,
GraphQL subscriptions, Kafka, or custom databases) and lays the required foundation for asynchronous execution ([GEP-023](GEP-023_Async_Support.md)).

## Motivation

In the current architecture, [`NetworkxBuilder`](file:///C:/dev/erivlis/graphinate/src/graphinate/builders/networkx.py) is tightly coupled to NetworkX in-memory graphs:
1. **Coupled Execution and Storage:** Graph generation cannot occur without instantiating and mutating an in-memory `networkx.Graph`. Direct-to-disk streaming, WebSocket broadcasting, or custom database loading requires building the entire graph in RAM first.
2. **Blocked Asynchrony:** Adding `async def` generator support ([GEP-023](GEP-023_Async_Support.md)) to `NetworkxBuilder` requires duplicating the entire recursion and lineage loop.
3. **Lack of Lifecycle Observability:** Users have no clean hooks for tracking ETL progress, logging item throughput, or inspecting generation events without monkey-patching `_populate_nodes`.

## Rationale

Evaluating the engine architecture against the **7 Council Pillars** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):

- **Symmetry (Noether):** Clear duality between event producers (`GraphEngine`) and event consumers (`GraphObserver`). A single engine run can dispatch symmetrically to one or more observers.
- **Falsifiability (Popper):** The engine can be tested with a lightweight `MockObserver` recording exact event sequences, isolating traversal correctness from NetworkX graph structure.
- **Efficiency (Shannon):** Traversal happens once; events stream directly to subscribers with zero intermediate list allocations or duplicate passes.
- **Safety (The Golem):** The engine consumes an immutable compiled model ([GEP-032](GEP-032_GraphModel_Compilation_and_Validation_Lifecycle.md)). Generator exceptions are captured with explicit node/edge context.
- **Clarity (Feynman):** Removes all traversal, recursion, and ID calculation code from `builders/networkx.py`. The builder becomes a clean, concise consumer of `NodeEvent` and `EdgeEvent`.
- **Consistency (Russell):** Lineage tuples and signed IDs remain deterministic whether emitted synchronously or asynchronously.
- **Harmony (The Steward):** Preserves 100% backwards compatibility for `model.build()` and `NetworkxBuilder(model).build()`.

## Specification

### 1. Data Contracts (Events)

Defined in `graphinate.engine.events`:

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Hashable
from graphinate.model import Multiplicity


@dataclass(frozen=True, slots=True)
class NodeEvent:
    node_id: tuple[Hashable, ...]
    type: str
    label: str | None
    value: Any
    magnitude: int
    lineage: tuple[Hashable, ...]
    multiplicity: Multiplicity
    created: datetime = field(default_factory=datetime.utcnow)


@dataclass(frozen=True, slots=True)
class EdgeEvent:
    source_id: tuple[Hashable, ...]
    target_id: tuple[Hashable, ...]
    type: str
    label: str | None
    value: Any
    created: datetime = field(default_factory=datetime.utcnow)
```

### 2. The Graph Observer Protocol

Defined in `graphinate.engine.observer`:

```python
from typing import Protocol


class GraphObserver(Protocol):
    def on_start(self, name: str) -> None:
        """Called when graph execution starts."""
        ...

    def on_node(self, event: NodeEvent) -> None:
        """Called when a node is generated."""
        ...

    def on_edge(self, event: EdgeEvent) -> None:
        """Called when an edge is generated."""
        ...

    def on_finish(self) -> None:
        """Called when graph execution completes."""
        ...
```

### 3. The Graph Engine

Defined in `graphinate.engine.core`:

```python
class GraphEngine:
    def __init__(self, model: GraphModel):
        self.model = model.compile()
        self._observers: list[GraphObserver] = []

    def subscribe(self, observer: GraphObserver) -> None:
        self._observers.append(observer)

    def run(self, **kwargs: Any) -> None:
        # Handles parent resolution, recursive node generation, lineage injection,
        # multiplicity matching, and edge generation, dispatching events to all observers.
        ...
```

### 4. Refactored `NetworkxBuilder`

`NetworkxBuilder` implements `GraphObserver`:

```python
class NetworkxBuilder(Builder, GraphObserver):
    def on_node(self, event: NodeEvent) -> None:
        # Mutates self._graph according to event
        ...

    def on_edge(self, event: EdgeEvent) -> None:
        # Adds edge to self._graph
        ...

    def build(self, **kwargs: Any) -> nx.Graph:
        self._initialize_graph()
        engine = GraphEngine(self.model)
        engine.subscribe(self)
        engine.run(**kwargs)
        return self._graph
```

## Backwards Compatibility

- **Public API:** `model.build(...)` and `NetworkxBuilder(model).build(...)` retain identical method signatures and return identical `nx.Graph` instances.
- **Edge cases:** `_lineage` propagation and `ParentId` injection work identically via `GraphEngine`.

## How to Teach This / Documentation Plan

- Add an architecture guide in `docs/advanced/engine.md` explaining custom observers (e.g. streaming, progress bars, logging).
- Document `GraphEngine` in `reference/` and `SKILL.md`.

## Reference Implementation

- Engine package: `src/graphinate/engine/`
- Builder adapter: `src/graphinate/builders/networkx.py`
- Test suite: `tests/graphinate/engine/`

## Rejected Ideas

- **Inheriting NetworkxBuilder directly from GraphEngine:**
  *Rejected.* An engine produces events; a builder consumes them. Conflating the two violates the Single Responsibility Principle and prevents running multiple observers.
- **Requiring Async by Default:**
  *Rejected.* Sync execution remains fundamental for fast in-memory builds and batch scripts. The engine will provide `run()` for sync models and `arun()` for async models in [GEP-023](GEP-023_Async_Support.md).

## Open Questions

- [ ] Should `on_node` events distinguish between initial node creation vs. subsequent updates (when a non-unique node is revisited)?

## Change Log

* **2025-12-28:** Initial draft.
* **2025-12-30:** Superseded GEP-015.
* **2026-10-21:** Modernized to conform to GEP-000 and EP standard with explicit `NodeEvent` and `EdgeEvent` contracts.
