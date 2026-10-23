---
title: Performance Optimization
icon: lucide/zap
---

# Performance Optimization

## NetworkX Backends (GraphQL & Analysis)

Graphinate leverages [NetworkX](https://networkx.org/) for graph data structures and algorithms. For large graphs,
standard Python execution of graph algorithms (like centrality, diameter, etc.) can be slow.

The `GraphQLBuilder` exposes many of these algorithms as fields (e.g., `measure(measure: radius)`). To significantly
speed up these calculations, you can install a high-performance NetworkX backend.

For more details, see the
official [NetworkX Backends documentation](https://networkx.org/documentation/stable/reference/backends.html).

**Recommended Backend:** `graphblas-algorithms`

1. **Install:**
   ```bash
   pip install graphblas-algorithms
   ```

2. **Enable:**

   Set the environment variable before running your application:

   ```bash
   export NETWORKX_BACKEND_PRIORITY=graphblas
   ```
   Or configure it programmatically:

   ```python
   import networkx as nx
   nx.config.backend_priority = ["graphblas"]
   ```

**Pros:**

- **Speed:** Orders of magnitude faster for complex algorithms (e.g., PageRank, Betweenness Centrality) on large graphs.
- **Parallelism:** Some backends support multi-threading or GPU acceleration.

**Cons/Disclaimers:**

- **Overhead:** There is a conversion cost to move data from the standard NetworkX graph to the backend's internal
  representation. For small graphs or simple queries, this might actually be slower.
- **Compatibility:** Not all NetworkX algorithms are implemented in every backend. NetworkX will seamlessly fall back to
  the default Python implementation if a backend doesn't support a specific algorithm.

## Vectorized Color & Attribute Operations (`graphinate[perf]`)

For graphs with thousands of nodes, batch attribute derivations such as mapping node types onto colormaps
(`node_color_mapping`) and converting RGBA float arrays into hexadecimal color strings (`convert_colors_to_hex`) can
become a bottleneck in pure Python loops.

Graphinate uses a progressive enhancement strategy in `graphinate.color`: when [NumPy](https://numpy.org/) is installed,
colormap index arrays and batch RGBA-to-HEX conversions automatically use vectorized NumPy operations, while falling
back transparently to pure Python when NumPy is absent.

1. **Install the Optional Extra:**
   ```bash
   pip install "graphinate[perf]"
   # or equivalently:
   pip install "graphinate[numpy]"
   ```
2. **Automatic Runtime Detection:**
   No code changes are required—`graphinate.color.HAS_NUMPY` detects `numpy` at import time and dispatches to the
   vectorized code path automatically.

## Synchronous vs. Asynchronous Execution Performance

Graphinate supports both synchronous (`builder.build()` / `engine.run()`) and asynchronous
(`await graphinate.abuild()` / `await engine.arun()`) execution pipelines. Choosing between them depends on whether
the bottleneck is in-memory CPU processing or external I/O latency.

### Benchmark Comparison

Benchmark suites located in `benchmarks/` measure execution across both CPU-bound and I/O-bound workloads:

| Workload                                                       | Synchronous (`build`) | Asynchronous (`abuild`)   | Difference / Speedup             |
|:---------------------------------------------------------------|:----------------------|:--------------------------|:---------------------------------|
| **In-Memory CPU** (20,000 nodes + 19,999 edges)                | 520 ms                | 603 ms                    | +16% coroutine protocol overhead |
| **Concurrent I/O** (5 graphs &times; 4 batches @ 50ms latency) | 1.03 s (sequential)   | 0.26 s (`asyncio.gather`) | **~4.0x faster**                 |

### Performance Characteristics

1. **In-Memory / CPU-Bound Pipelines**:
   - Synchronous generators (`def ... yield`) execute in Python's optimized `FOR_ITER` bytecode loop with zero coroutine
     frame allocation or event loop context switching.
   - Asynchronous generators (`async def ... yield`) incur a small overhead due to coroutine scheduling and
     the async generator protocol (`anext()`). For pure in-memory transformations without I/O, synchronous builds offer
     the highest raw throughput.

2. **I/O-Bound Pipelines & Concurrency**:
   - When node or edge suppliers fetch data from remote APIs, microservices, databases, or cloud storage, synchronous
     pipelines block the executing thread for the duration of each network round-trip.
   - Asynchronous pipelines (`await abuild(...)`) overlap I/O latency across batches and allow multiple independent
     subgraphs to be hydrated simultaneously using `asyncio.gather()`, achieving near-linear speedups.
   - In web frameworks (such as FastAPI or Strawberry GraphQL), `abuild` ensures the event loop remains unblocked,
     preventing latency spikes across concurrent requests.

### When to Choose Sync vs. Async

| Scenario                                         | Recommendation              | Rationale                                                              |
|:-------------------------------------------------|:----------------------------|:-----------------------------------------------------------------------|
| **Local scripts, CLI tools, offline batch data** | `builder.build()`           | Zero coroutine overhead, maximum single-threaded throughput.           |
| **Network APIs, databases, remote files**        | `await graphinate.abuild()` | Overlaps network latency and unlocks concurrent fetches.               |
| **Web servers (FastAPI / Starlette / GraphQL)**  | `await graphinate.abuild()` | Prevents event loop starvation and handles concurrent queries cleanly. |

To run the benchmark suite locally:

```bash
uv run pytest benchmarks --codspeed
# Or run the standalone reporting script:
uv run python benchmarks/async_benchmark.py
```


