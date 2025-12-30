# GEP-002: Modularization Strategy

| Field       | Value                   |
|:------------|:------------------------|
| **GEP**     | 2                       |
| **Title**   | Modularization Strategy |
| **Author**  | Eran Rivlis             |
| **Status**  | Active                  |
| **Type**    | Process                 |
| **Created** | 2025-12-30              |

## Abstract

This document defines the architectural strategy for managing Graphinate's growth. As the library expands to support new features (Jupyter, Realtime, Pluggable Renderers), the risk of dependency bloat and tight coupling increases. This GEP establishes the principle of **"Internal Modularization with Optional Dependencies"** to maintain a lightweight core while enabling a rich ecosystem.

## Motivation

Graphinate is currently a monolith. While convenient for development, this poses risks:
1.  **Dependency Bloat:** A user who only wants to model a graph shouldn't need to install `uvicorn`, `strawberry`, or `datashader`.
2.  **Coupling:** Tightly coupled modules make refactoring (like GEP-026) difficult.

## The Strategy

We will **NOT** split the repository into multiple packages (e.g., `graphinate-core`, `graphinate-server`) at this time. The overhead of managing multiple release cycles is too high for the current team size.

Instead, we will adopt a **Virtual Split** strategy:

1.  **Strict Internal Boundaries:** Code modules must adhere to a layered architecture.
2.  **Optional Dependencies:** Use `pyproject.toml` extras to manage heavy dependencies.

## Architectural Layers

The codebase shall be organized into the following logical layers, with dependencies flowing **downwards only**.

### Layer 1: The Core (`graphinate.modeling`)
*   **Responsibility:** Declarative API (`GraphModel`, decorators).
*   **Dependencies:** Zero (Standard Library only).
*   **Imports:** Cannot import from any other layer.

### Layer 2: The Engine (`graphinate.engine`)
*   **Responsibility:** Iterating the model, generating IDs, managing state.
*   **Dependencies:** `networkx` (Core dependency).
*   **Imports:** Can import from `modeling`.

### Layer 3: The Builders (`graphinate.builders`)
*   **Responsibility:** Converting the engine's output into specific formats (D3, GraphQL, Mermaid).
*   **Dependencies:** `networkx`.
*   **Imports:** Can import from `engine`, `modeling`.

### Layer 4: The Integrations (Optional Extras)
These modules are only importable if the user installs the corresponding extra.

*   **`graphinate.server`**:
    *   **Extra:** `server`
    *   **Deps:** `uvicorn`, `starlette`, `strawberry-graphql`.
*   **`graphinate.jupyter`** (Proposed in GEP-026):
    *   **Extra:** `jupyter`
    *   **Deps:** `ipywidgets`.
*   **`graphinate.renderers.datashader`** (Proposed in GEP-026):
    *   **Extra:** `plot`
    *   **Deps:** `datashader`, `holoviews`.

## Implementation Guidelines

### 1. Lazy Imports
Modules in Layer 4 must use lazy imports or `try/except ImportError` blocks to prevent crashing the application if the extra is not installed.

```python
# graphinate/server/__init__.py

def start_server():
    try:
        import uvicorn
    except ImportError:
        raise ImportError("Please install 'graphinate[server]' to use this feature.")
    ...
```

### 2. `pyproject.toml` Management
All heavy dependencies must be moved to `[project.optional-dependencies]`. The `dependencies` list should remain minimal (e.g., `networkx`, `inflect`).

## Future Considerations

If a specific layer (e.g., the Frontend assets) grows too large or requires a different release cadence, we may consider splitting it into a separate PyPI package (`graphinate-web`) in the future. For now, the Monorepo + Extras approach provides the best balance of Agility and Hygiene.
