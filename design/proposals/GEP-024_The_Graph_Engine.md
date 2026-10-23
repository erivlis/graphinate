---
title: "GEP-024: The Graph Engine"
description: "Decouple graph traversal and event generation from storage into an observable GraphEngine and GraphObserver architecture."
icon: lucide/cpu
status: active
---

# GEP-024: The Graph Engine

| Field        | Value            |
|:-------------|:-----------------|
| **GEP**      | 24               |
| **Title**    | The Graph Engine |
| **Author**   | Eran Rivlis      |
| **Delegate** | The Council      |
| **Status**   | Active           |
| **Type**     | Standards Track  |
| **Created**  | 2025-12-28       |
| **Updated**  | 2026-10-23       |
| **Replaces** | GEP-015          |

## Abstract

This proposal extracts graph execution logic (iterating generator functions, dependency injection via `ParentId`,
lineage calculation, and multiplicity metadata) out of [`NetworkxBuilder`](src/graphinate/builders/networkx.py)
into a dedicated, observable execution component: `GraphEngine`.

By separating execution (producer) from storage (consumer), Graphinate transforms from a NetworkX-only builder into a
universal Graph Synthesis Engine capable of streaming events to multiple consumers simultaneously (e.g. NetworkX,
GraphQL subscriptions, Kafka, or custom databases) and lays the required foundation for asynchronous execution ([GEP-023](GEP-023_Async_Support.md)).

## Motivation

In the previous architecture, [`NetworkxBuilder`](src/graphinate/builders/networkx.py) was tightly coupled to NetworkX in-memory graphs:
1. **Coupled Execution and Storage:** Graph generation could not occur without instantiating and mutating an in-memory `networkx.Graph`. Direct-to-disk streaming, WebSocket broadcasting, or custom database loading required building the entire graph in RAM first.
2. **Blocked Asynchrony:** Adding `async def` generator support ([GEP-023](GEP-023_Async_Support.md)) to `NetworkxBuilder` would require duplicating the entire recursion and lineage loop.
3. **Lack of Lifecycle Observability:** Users had no clean hooks for tracking ETL progress, logging item throughput, or inspecting generation events without monkey-patching `_populate_nodes`.

## Rationale

Evaluating the engine architecture against the **7 Council Pillars** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):

- **Symmetry (Noether):** Clear duality between event producers (`GraphEngine`) and event consumers (`GraphObserver`). A single engine run can dispatch symmetrically to one or more observers.
- **Falsifiability (Popper):** The engine is tested with a lightweight `RecordingObserver` recording exact event sequences, isolating traversal correctness from NetworkX graph structure.
- **Efficiency (Shannon):** Traversal happens once; events stream directly to subscribers with zero intermediate list allocations or duplicate passes.
- **Safety (The Golem):** The engine consumes an immutable compiled model ([GEP-032](GEP-032_GraphModel_Compilation_and_Validation_Lifecycle.md)).
- **Clarity (Feynman):** Removes traversal, recursion, and ID calculation code from `builders/networkx.py`. The builder becomes a clean, concise consumer of `NodeEvent` and `EdgeEvent`.
- **Consistency (Russell):** Lineage tuples and signed IDs remain deterministic whether emitted synchronously or asynchronously.
- **Harmony (The Steward):** Preserves 100% backwards compatibility for `build()` and `NetworkxBuilder(model).build()`.

## Specification

### 1. Data Contracts (Events)

Defined in [`src/graphinate/engine/events.py`](src/graphinate/engine/events.py):

```python
@dataclass(frozen=True, slots=True)
class NodeEvent:
    node_id: tuple[Hashable, ...]
    type: str
    label: Any
    value: Any
    magnitude: int = 1
    lineage: tuple[Hashable, ...] = ()
    multiplicity: Multiplicity = Multiplicity.ALL
    created: datetime = field(default_factory=utcnow)


@dataclass(frozen=True, slots=True)
class EdgeEvent:
    source_id: tuple[Hashable, ...]
    target_id: tuple[Hashable, ...]
    type: str | None = None
    label: Any = None
    value: Any = None
    weight: float = 1.0
    is_hierarchy: bool = False
    created: datetime = field(default_factory=utcnow)
```

### 2. The Graph Observer Protocol

Defined in [`src/graphinate/engine/observer.py`](src/graphinate/engine/observer.py):

```python
@runtime_checkable
class GraphObserver(Protocol):
    def on_start(self, name: str) -> None: ...
    def on_node(self, event: NodeEvent) -> None: ...
    def on_edge(self, event: EdgeEvent) -> None: ...
    def on_finish(self) -> None: ...
```

### 3. The Graph Engine

Defined in [`src/graphinate/engine/core.py`](src/graphinate/engine/core.py):

```python
class GraphEngine:
    def __init__(self, model: GraphModel, *, compile_model: bool = True, ...):
        self.model = model.compile(...) if compile_model else model
        self._observers: list[GraphObserver] = []

    def subscribe(self, observer: GraphObserver) -> None:
        self._observers.append(observer)

    def run(self, **kwargs: Any) -> None:
        ...
```

### 4. Refactored `NetworkxBuilder`

`NetworkxBuilder` implements `GraphObserver` and mutates `self._graph` in response to `on_start`, `on_node`, and `on_edge` events emitted by `GraphEngine`.

## Backwards Compatibility

- **Public API:** `build(...)` and `NetworkxBuilder(model).build(...)` retain identical method signatures and return identical `nx.Graph` instances.
- **Internal Helpers:** `_populate_node_type`, `_populate_nodes`, `_populate_edges`, and `_parent_node_id` on `NetworkxBuilder` delegate to `GraphEngine` so existing unit tests and subclasses continue working seamlessly.

## How to Teach This / Documentation Plan

- Added an architecture guide in [`docs/advanced/engine.md`](docs/advanced/engine.md) explaining custom observers (`GraphObserver`, `NodeEvent`, `EdgeEvent`).
- Exported `GraphEngine`, `GraphObserver`, `NodeEvent`, and `EdgeEvent` in `graphinate`.

## Reference Implementation

- Engine package: [`src/graphinate/engine/`](src/graphinate/engine/__init__.py)
- Builder adapter: [`src/graphinate/builders/networkx.py`](src/graphinate/builders/networkx.py)
- Test suite: [`tests/graphinate/test_engine.py`](tests/graphinate/test_engine.py)

## Rejected Ideas

- **Inheriting NetworkxBuilder directly from GraphEngine:**
  *Rejected.* An engine produces events; a builder consumes them. Conflating the two violates the Single Responsibility Principle and prevents running multiple observers.
- **Requiring Async by Default:**
  *Rejected.* Sync execution remains fundamental for fast in-memory builds and batch scripts. The engine provides `run()` for sync models and will provide `arun()` for async models in [GEP-023](GEP-023_Async_Support.md).

## Open Questions

- [x] Should `on_node` events distinguish between initial node creation vs. subsequent updates (when a non-unique node is revisited)? *Decision: `GraphEngine` emits stateless `NodeEvent` payloads carrying `multiplicity`, while stateful observers like `NetworkxBuilder` decide whether a `node_id` is new or existing in their backing store.*

## Change Log

* **2025-12-28:** Initial draft.
* **2025-12-30:** Superseded GEP-015.
* **2026-10-21:** Modernized to conform to GEP-000 and EP standard with explicit `NodeEvent` and `EdgeEvent` contracts.
* **2026-10-23:** Implemented `graphinate.engine` (`GraphEngine`, `GraphObserver`, `NodeEvent`, `EdgeEvent`), refactored `NetworkxBuilder` as a `GraphObserver`, and transitioned status to `Active`.

