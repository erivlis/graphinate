# GEP-024: The Graph Engine (Observable Execution)

| Field       | Value            |
|:------------|:-----------------|
| **GEP**     | 24               |
| **Title**   | The Graph Engine |
| **Author**  | Eran Rivlis      |
| **Status**  | Draft            |
| **Type**    | Standards Track  |
| **Created** | 2025-12-28       |
| **Updated** | 2025-12-30       |

## Abstract

This proposal advocates for extracting the graph generation logic (iterating generators, resolving dependencies,
managing lineage) from the `NetworkxBuilder` into a standalone, observable component called the `GraphEngine`.

## Relations

*   **Enables:** [GEP-023: Async Support](GEP-023_Async_Support.md) - The engine will support async generators.
*   **Enables:** [GEP-026: Pluggable Visualization](GEP-026_Pluggable_Visualization_and_Notebook_Support.md) - The engine provides the realtime stream for the frontend.
*   **Adheres to:** [GEP-002: Modularization Strategy](GEP-002_Modularization_Strategy.md) - The engine is a distinct layer.

## Motivation

**Current Architecture:**
The `NetworkxBuilder` is monolithic. It is responsible for:

1. **Execution:** Calling generator functions and managing the loop.
2. **Logic:** Calculating IDs, handling lineage, and resolving multiplicity.
3. **Storage:** Storing the results in a `networkx.Graph`.

**Issues:**

1. **Coupling:** We cannot execute the model without building a NetworkX graph in memory. This makes streaming (
   Realtime) or direct-to-database loading impossible.
2. **Async:** Implementing async support (GEP-023) in a monolithic builder is complex.
3. **Extensibility:** Adding new behaviors (like logging progress or filtering) requires modifying the core loop.

## Specification

### 1. The Graph Engine (Producer)

A new class responsible solely for executing the `GraphModel`.

```python
class GraphEngine:
    def __init__(self, model: GraphModel):
        self.model = model
        self._observers = []

    def subscribe(self, observer: GraphObserver):
        self._observers.append(observer)

    async def run(self):
        # ... logic to iterate generators ...
        # ... logic to calculate IDs ...
        # Supports both sync and async generators (e.g., Kafka consumers)
        async for item in self._iterate_model():
             await self._notify(item)
```

### 2. The Graph Observer (Consumer)

An interface for handling graph events.

```python
class GraphObserver(Protocol):
    async def on_node(self, event: NodeCreatedEvent): ...

    async def on_edge(self, event: EdgeCreatedEvent): ...
```

### 3. Refactored Builders

The `NetworkxBuilder` becomes a concrete observer.

```python
class NetworkxBuilder(GraphObserver):
    def __init__(self):
        self.graph = nx.Graph()

    async def on_node(self, event):
        self.graph.add_node(event.node_id, **event.data)
```

### 4. Realtime Support (Kafka / WebSockets)

This architecture trivially supports realtime streaming.
*   **Input:** The `GraphEngine` can consume from **Async Generators** (e.g., `aiokafka` consumer).
*   **Output:** A `WebSocketObserver` (or GraphQL Subscription resolver) can push events to the frontend (GEP-026) as they happen.

## Design Considerations

### Event Hierarchy

We considered introducing an intermediate `ElementEvent` class (inheriting from `GraphEvent`) to serve as a common base
for `NodeEvent` and `EdgeEvent`.

* **Pros:** Allows polymorphic processing of elements (e.g., counting total elements).
* **Cons:** Adds complexity without immediate use cases (YAGNI).
* **Decision:** We will keep the hierarchy flat (`NodeEvent` and `EdgeEvent` inherit directly from `GraphEvent`) for
  now. This can be refactored later without breaking changes if needed.

## Backwards Compatibility

The existing `build()` API can be maintained as a facade that instantiates an Engine and a NetworkxBuilder, runs them,
and returns the graph.
