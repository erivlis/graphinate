# GEP-029: Extraction Strategies

| Field       | Value                 |
|:------------|:----------------------|
| **GEP**     | 29                    |
| **Title**   | Extraction Strategies |
| **Author**  | Eran Rivlis           |
| **Status**  | Draft                 |
| **Type**    | Standards Track       |
| **Created** | 2026-01-01            |

## Abstract

This proposal formalizes the "Extraction" (E) phase of Graphinate. It introduces a set of algorithmic primitives—**Scan**, **Walk**, and **Listen**—to standardize how data is ingested from various sources. By treating Extraction as the **Traversal of an Implicit Graph**, we can provide robust tooling for common patterns like crawling, streaming, and querying, without coupling the core to specific data formats.

## Motivation

Currently, Graphinate relies on user-defined generators for data extraction. While flexible, this places the burden of implementing traversal logic (recursion, state management, concurrency) on the user.

**The Problem:**
*   Writing a web crawler requires manually managing a queue and a visited set.
*   Reading a CSV requires writing a loop.
*   Consuming a stream requires writing an async loop.

**The Solution:**
Provide high-level **Strategies** that encapsulate these patterns.

## Theory: The Implicit Graph

We define Extraction as the process of visiting nodes in an **Implicit Graph** (the data source) to construct an **Explicit Graph** (the model).

This process has two primary dimensions:
1.  **Topology:** How nodes are connected.
    *   **Linear:** Nodes are independent or sequential (List, Stream).
    *   **Recursive:** Nodes lead to other nodes (Tree, Graph).
2.  **Agency:** Who drives the traversal.
    *   **Pull:** The engine requests data (Active).
    *   **Push:** The source sends data (Reactive).

## Specification

We will introduce `graphinate.strategies` containing three core primitives.

### 1. `Scan` (Linear Pull)
Iterates over a flat collection.

*   **Input:** `Iterable[T]`
*   **Logic:** `for item in iterable: yield item`
*   **Use Case:** CSV rows, SQL result sets, JSON lists.

```python
@model.node()
def my_nodes():
    yield from strategies.scan(csv.reader(f))
```

### 2. `Walk` (Recursive Pull)
Traverses a connected structure.

*   **Input:**
    *   `start`: The root node(s).
    *   `expand(node) -> Iterable[Node]`: Function to find neighbors.
    *   `key(node) -> Hashable`: Function to identify nodes (for visited set).
*   **Configuration:**
    *   `strategy`: 'bfs' (Queue) or 'dfs' (Stack).
    *   `depth`: Max recursion depth.
    *   `concurrency`: Number of concurrent workers (Async).
*   **Logic:** Maintains a Frontier and a Memory (Visited Set).
*   **Yields:** `(parent, child)` tuples (Edges) or `child` (Nodes).
*   **Use Case:** Web crawling, File system walking, Dependency analysis.

```python
@model.node()
async def my_crawler():
    async for parent, child in strategies.walk(
        start="https://example.com",
        expand=get_links,
        strategy='bfs',
        concurrency=5
    ):
        yield {'source': parent, 'target': child}
```

### 3. `Listen` (Linear Push)
Consumes an asynchronous stream.

*   **Input:** `AsyncIterable[T]`
*   **Logic:** `async for item in source: yield item`
*   **Use Case:** Kafka topics, Redis streams, WebSockets.

```python
@model.node()
async def my_stream():
    async for msg in strategies.listen(kafka_consumer):
        yield msg
```

## Mechanics

### The Traverser
The `Walk` strategy will be implemented as a `Traverser` class that manages:
1.  **Frontier:** A `collections.deque` (BFS) or `list` (DFS).
2.  **Memory:** A `set` of visited keys.
3.  **Workers:** An `asyncio.TaskGroup` for concurrent expansion.

### Frontier Crossing & Multiplicity (The "Dennis Point")

A critical design decision is how to handle **Convergence** (multiple paths leading to the same node) and **Multiplicity** (multiple edges between the same nodes).

We must distinguish between **Traversal Topology** (the process) and **Graph Topology** (the data).

1.  **Traversal Topology (Efficiency):**
    *   **Goal:** Visit every reachable node exactly once to prevent infinite loops and redundant work.
    *   **Mechanism:** The `visited` set filters the **Frontier**.
    *   **Rule:** "If I have already *expanded* Node B, do not add it to the queue again."

2.  **Graph Topology (Structure):**
    *   **Goal:** Capture every relationship present in the source.
    *   **Mechanism:** The `yield` statement.
    *   **Rule:** "If I encounter a link from A to B, yield `(A, B)` immediately, regardless of whether B has been seen before."

3.  **Load Phase (Flexibility):**
    *   **Goal:** Decide how to store the yielded relationships.
    *   **Mechanism:** The `Builder` (e.g., `NetworkxBuilder`).
    *   **Rule:** The Builder receives the stream of edges.
        *   If building a `nx.Graph`, it updates the existing edge (e.g., increments weight).
        *   If building a `nx.MultiGraph`, it adds a new parallel edge.

**Pseudo-Code Implementation:**

```python
def walk(start):
    queue = [start]
    visited = {start}
    
    while queue:
        parent = queue.pop()
        children = expand(parent)
        
        for child in children:
            # 1. YIELD ALWAYS (Preserve Structure for MultiGraph/Aggregation)
            yield (parent, child)
            
            # 2. FILTER EXPANSION (Preserve Sanity/Termination)
            if child not in visited:
                visited.add(child)
                queue.append(child)
```

This separation ensures the Extractor is "dumb" about the final graph structure (it just reports what it sees) but "smart" about the traversal (it doesn't get lost).

### Parallelism
Parallelism is treated as a property of the traversal loop. By using `asyncio`, we can spawn multiple "Expanders" that feed off a shared Frontier.

## Future Considerations: Real-World Optimizations

While the core abstraction handles the topology and agency, real-world constraints often require secondary optimizations to the **Processing Mechanics** of the Traverser. These are candidates for future enhancements:

1.  **Transformation Pipeline (ETL Fusion):**
    *   *Concept:* Integrating transformation logic (e.g., parsing HTML, filtering fields) directly into the traversal loop to avoid multiple passes over the data.
    *   *Mechanism:* Middleware or hooks (`on_visit`, `on_yield`).

2.  **Granularity (Batching):**
    *   *Concept:* Yielding chunks of items instead of single atoms to reduce overhead in high-throughput scenarios (e.g., database inserts).
    *   *Mechanism:* `yield_batch(size=100)`.

3.  **Memory Management (State Optimization):**
    *   *Concept:* For massive graphs, the `visited` set can exceed RAM.
    *   *Mechanism:*
        *   **Bloom Filters:** Probabilistic deduplication (small RAM footprint).
        *   **External Storage:** Redis/Disk-based set.
        *   **TTL / LRU:** Memoization with expiration. Useful for infinite streams or slowly changing graphs where re-visiting a node after X minutes is desirable.

## Use Cases Discussion

This section explores how the proposed strategies map to common real-world scenarios.

### 1. The Web Crawler (Recursive / Walk)
*   **Scenario:** Crawl a website to map internal linking structure.
*   **Strategy:** `Walk`.
*   **Configuration:** `strategy='bfs'`, `depth=3`, `concurrency=10`.
*   **Key Challenge:** Cycles (A->B->A) and Convergence (A->C, B->C).
*   **Solution:** The `visited` set prevents infinite loops. The `yield (parent, child)` logic ensures `C` is recorded as a child of both `A` and `B`, preserving the PageRank structure.

### 2. The Dependency Analyzer (Recursive / Walk)
*   **Scenario:** Analyze Python imports in a project.
*   **Strategy:** `Walk`.
*   **Configuration:** `strategy='dfs'` (often more natural for dependency trees).
*   **Key Challenge:** Shared dependencies (Diamond problem).
*   **Solution:** Similar to the crawler, we need to record that both `Module A` and `Module B` import `Library X`. The `MultiGraph` support in the Load phase allows capturing multiple import statements if needed (e.g., different versions).

### 3. The Log Monitor (Stream / Listen)
*   **Scenario:** Visualize microservice interactions from a Kafka stream of trace logs.
*   **Strategy:** `Listen`.
*   **Configuration:** `async_iterator=kafka_consumer`.
*   **Key Challenge:** Infinite data, duplicate events.
*   **Solution:** The `Listen` strategy yields events as they come. The Builder (Load phase) handles aggregation (e.g., incrementing edge weight for every request between Service A and Service B). Memory management (TTL) might be needed if we track "active sessions".

### 4. The Database Dump (Linear / Scan)
*   **Scenario:** Build a graph from a CSV export of a User table and a Friendship table.
*   **Strategy:** `Scan`.
*   **Configuration:** `iterable=csv_reader`.
*   **Key Challenge:** Data volume.
*   **Solution:** `Scan` is low overhead. Future "Granularity" optimizations (batching) would speed up the transfer to the Builder.

## Integration

These strategies are **Helpers**. They return generators (sync or async) that fit naturally into the existing `GraphModel` API. They do not require changing the core engine, but they empower the user to write complex extractors declaratively.

## Roadmap

1.  Implement `scan` (Trivial).
2.  Implement `walk` (Sync version).
3.  Implement `walk` (Async version with concurrency).
4.  Implement `listen` (Async iterator wrapper).
