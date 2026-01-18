# GEP-031: High-Performance Vectorized Operations

*   **Status:** Draft
*   **Type:** Standards Track
*   **Created:** 2023-10-27

## Abstract

This proposal advocates for the optional integration of high-performance numerical libraries, specifically **NumPy** and **Numba**, to accelerate computationally intensive graph operations. The core philosophy is "Progressive Enhancement": the library should remain functional and lightweight without these dependencies, but significantly faster when they are present.

## Motivation

Graphinate aims to handle graphs of varying sizes. While pure Python is sufficient for small to medium graphs (e.g., < 10k nodes), it hits performance bottlenecks with larger datasets, particularly in:

1.  **Attribute Calculation:** Deriving attributes (like colors, positions, or metrics) for thousands of nodes.
2.  **Layout Algorithms:** Force-directed layouts or other geometric calculations.
3.  **Graph Analysis:** Computing centrality, clustering, or other metrics.

Our recent benchmark on `color.py` showed a **450%** performance difference between pure Python and NumPy for a simple color mapping operation on 10k nodes. This gap widens as complexity increases.

## Specification

### 1. Optional Dependencies

NumPy and Numba will be treated as **optional** dependencies. They should not be required for the core functionality of Graphinate.

*   **Installation:** Users can opt-in via extras, e.g., `pip install graphinate[perf]`.
*   **Runtime Detection:** The code must gracefully check for the existence of these libraries at runtime.

### 2. Implementation Pattern

We will adopt a "Strategy Pattern" or "Feature Toggle" approach at the module level.

**Example Pattern:**

```python
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

def calculate_metrics(data):
    if HAS_NUMPY:
        return _calculate_metrics_numpy(data)
    else:
        return _calculate_metrics_pure(data)
```

### 3. Target Areas

We will prioritize vectorization in the following areas:

*   **`graphinate.color`:** (Already implemented) Mapping values to colormaps.
*   **`graphinate.builders`:** Batch processing of node/edge attributes during graph construction.
*   **`graphinate.layout` (Future):** If we implement custom layout algorithms, Numba JIT compilation will be critical.
*   **`graphinate.converters`:** Bulk type conversion or ID generation.

### 4. Numba Integration

For tight loops that cannot be easily vectorized with NumPy (e.g., complex procedural generation logic), we will explore **Numba**.

*   **JIT Compilation:** Use `@jit(nopython=True)` for critical paths.
*   **Cold Start:** Be mindful of compilation time; Numba is best for long-running or repeated tasks.

## Rationale

*   **Performance:** Vectorized operations in C (via NumPy) are orders of magnitude faster than Python loops.
*   **Accessibility:** Keeping the core lightweight ensures Graphinate remains easy to install in constrained environments (e.g., serverless, CI/CD, simple scripts).
*   **Scalability:** Allows Graphinate to scale from "scripting tool" to "data engineering tool" without changing the API.

## Backwards Compatibility

This proposal is fully backwards compatible. The public API remains unchanged; only the internal execution strategy changes based on the environment.

## Security Implications

None.

## Reference Implementation

See `src/graphinate/color.py` for the initial implementation of this pattern.
