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

