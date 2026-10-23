---
title: "GEP-031: High-Performance Vectorized Operations"
description: "Progressive enhancement via optional NumPy vectorization for batch node attribute and color operations."
icon: lucide/git-branch
status: active
---

# GEP-031: High-Performance Vectorized Operations

| Field        | Value                                  |
|:-------------|:---------------------------------------|
| **GEP**      | 31                                     |
| **Title**    | High-Performance Vectorized Operations |
| **Author**   | Eran Rivlis                            |
| **Delegate** | The Council                            |
| **Status**   | Active                                 |
| **Type**     | Standards Track                        |
| **Created**  | 2023-10-27                             |
| **Updated**  | 2026-10-23                             |

## Abstract

This proposal establishes progressive enhancement via optional **NumPy** vectorization to accelerate computationally
intensive batch graph operations (such as colormap index generation and batch RGBA-to-HEX conversion in
`graphinate.color`). The library remains 100% functional and lightweight in pure Python without NumPy installed, and
automatically dispatches to vectorized operations when `numpy` is present (`graphinate[perf]` / `graphinate[numpy]`).

## Motivation

Graphinate aims to handle graphs of varying sizes. While pure Python is sufficient for small to medium graphs (e.g., <
10k nodes), it hits performance bottlenecks with larger datasets, particularly in:

1. **Attribute Calculation:** Deriving attributes (like colors, positions, or metrics) for thousands of nodes.
2. **Color Mapping & Normalization:** Computing colormap indices (`np.fromiter`), min/max bounds, and batch RGBA-to-HEX
   conversions (`convert_colors_to_hex`).
3. **Graph Analysis:** Computing centrality, clustering, or other metrics.

Benchmarks on `color.py` showed a **450%** speedup using NumPy over pure Python for color mapping on 10k nodes.

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):

- **Symmetry (Noether):** Both the `HAS_NUMPY = True` and `HAS_NUMPY = False` code paths adhere to identical
  input/output contracts.
- **Falsifiability (Popper):** Unit tests explicitly exercise both the vectorized path and the `HAS_NUMPY = False`
  fallback path via monkeypatching, asserting bit-for-bit identical results.
- **Efficiency (Shannon):** Vectorized C-level loops via `np.fromiter` and array arithmetic eliminate per-node Python
  loop overhead on large graphs.
- **Safety (The Golem):** Keeping `numpy` optional avoids forcing C-extension wheels onto constrained or minimal
  environments.
- **Clarity (Feynman):** The `HAS_NUMPY` feature-toggle pattern at the module level is explicit, localized, and easy to
  audit.
- **Consistency (Russell):** Both `graphinate[perf]` and `graphinate[numpy]` extras in `pyproject.toml` install the
  optional dependency cleanly.
- **Harmony (The Steward):** Progressive enhancement scales Graphinate without bloating the core dependency footprint
  ([GEP-002](GEP-002_Modularization_Strategy.md)).

## Specification

### 1. Optional Dependencies (`pyproject.toml`)

NumPy is treated as an **optional** dependency under `[project.optional-dependencies]`:

- `pip install "graphinate[perf]"` (or `pip install "graphinate[numpy]"`)

### 2. Progressive Enhancement Pattern (`graphinate.color`)

```python
try:
    import numpy as np

    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
```

- `node_color_mapping(graph, cmap="tab20")` uses `np.fromiter` and `color_indices.min()` / `color_indices.max()` when
  `HAS_NUMPY` is `True`, and falls back to a Python list comprehension and `min()` / `max()` when `HAS_NUMPY` is
  `False`.
- `convert_colors_to_hex(graph, color="color")` vectorizes `[0, 1]` float RGBA/RGB sequences across all nodes into
  integer `[0, 255]` triplets in a single NumPy array operation when `HAS_NUMPY` is `True`, falling back to
  `color_hex()` otherwise.

## Backwards Compatibility

100% backwards compatible. The public signatures and return values of `node_color_mapping`, `color_hex`, and
`convert_colors_to_hex` are identical whether `numpy` is installed or not.

## Security Implications

None.

## How to Teach This / Documentation Plan

- Document `pip install "graphinate[perf]"` and `pip install "graphinate[numpy]"` in [`docs/advanced/optimization.md`](docs/advanced/optimization.md).

## Reference Implementation

- Optional extras: [`pyproject.toml`](pyproject.toml)
- Vectorized color operations: [`src/graphinate/color.py`](src/graphinate/color.py)
- Unit tests (vectorized + fallback): [
  `tests/graphinate/test_color.py`](tests/graphinate/test_color.py)
- User documentation: [`docs/advanced/optimization.md`](docs/advanced/optimization.md)

## Rejected Ideas

- **Making `numpy` a Mandatory Core Dependency:** Rejected to keep the base install lightweight and faithful
  to [GEP-002](GEP-002_Modularization_Strategy.md).
- **Requiring Numba JIT Compilation in Core:** Deferred because Numba adds LLVM cold-start compilation latency and
  stricter Python version constraints (especially on bleeding-edge Python 3.14/3.15 and free-threaded builds), whereas
  NumPy vectorization provides immediate speedups with zero JIT warm-up cost.

## Open Questions

- [x] Should both `graphinate[numpy]` and `graphinate[perf]` extras be supported in `pyproject.toml`? *Decision: Yes,
  supporting both aliases ensures compatibility with existing scripts and this specification.*

## Change Log

* **2026-06-22:** Initial Draft.
* **2026-10-17:** Vectorized color map benchmarks documented in `color.py`.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
* **2026-10-23:** Added `perf` extra, vectorized `convert_colors_to_hex`, updated `docs/advanced/optimization.md`, and
  transitioned status to `Active`.
