# GEP-026: Pluggable Visualization & Notebook Support

| Field       | Value                                       |
|:------------|:--------------------------------------------|
| **GEP**     | 26                                          |
| **Title**   | Pluggable Visualization & Notebook Support  |
| **Author**  | Eran Rivlis                                 |
| **Status**  | Draft                                       |
| **Type**    | Standards Track                             |
| **Created** | 2025-12-30                                  |
| **Updated** | 2025-12-30                                  |

## Abstract

This proposal aims to enable Graphinate to render graphs directly within Jupyter Notebooks, Google Colab, and ObservableHQ, as well as export standalone HTML files. This requires decoupling the frontend viewer from the live GraphQL server and allowing graph data to be embedded directly into the HTML payload. Additionally, it introduces a **Pluggable Renderer Architecture** to support different visualization engines (e.g., 3D Force Graph, Cosmograph, Sigma.js) in the future.

## Relations

*   **Supersedes:** [GEP-022: 2D Visualization Mode](GEP-022_2D_Visualization_Mode.md) - The 2D mode will be implemented as a pluggable engine.
*   **Implements Ideas From:** [GEP-027: Advanced Three.js Visualizations](GEP-027_Advanced_ThreeJS_Visualizations.md) - The "Galaxy" and "City" concepts will be implemented as engines.
*   **Related To:** [GEP-020: Modular Frontend Architecture](GEP-020_Modular_Frontend_Architecture.md) - This proposal accelerates the modularization of the frontend.
*   **Dependent On:** [GEP-024: The Graph Engine](GEP-024_The_Graph_Engine.md) - Realtime backend support is defined here.

## Motivation

Currently, Graphinate requires running a Uvicorn server (`graphinate.server`) to view a graph. This is a blocking operation that doesn't fit the interactive, cell-based workflow of data science notebooks. Furthermore, the visualization logic is hardcoded to `3d-force-graph`, limiting performance for massive graphs.

**Goals:**
1.  **Jupyter Integration:** `graphinate.show(model)` should render the interactive graph in the output cell.
2.  **Static Export:** `graphinate.export(model, "graph.html")` should produce a single, portable HTML file.
3.  **Pluggable Renderers:** Allow swapping the visualization engine (e.g., for higher performance or 2D mode).
4.  **Realtime Readiness:** Ensure the frontend architecture supports incremental updates.

## Specification

### 1. The "Static Mode" Viewer

The current `index.html` fetches data via `fetch('/graphql')`. We will refactor the frontend logic to support a **Data Injection Strategy**.

*   **Server Mode (Current):** `fetch('/graphql')`
*   **Static Mode (New):** Read from `window.GRAPHINATE_DATA` (injected JSON).

### 2. Python API

We will introduce a new `graphinate.widget` or `graphinate.jupyter` module.

```python
# graphinate/jupyter.py

def render(model: GraphModel, height: int = 600, engine: str = 'default'):
    """
    Renders the graph in a Jupyter Notebook.
    
    Args:
        model: The GraphModel to render.
        height: Height of the widget in pixels.
        engine: The visualization engine ('default', 'cosmograph', 'sigma', 'datashader').
    """
    from IPython.display import HTML
    
    # 1. Build the graph (NetworkX)
    # 2. Serialize to JSON (Nodes, Edges, Types)
    data = serialize_model(model)
    
    # 3. Select Template based on Engine
    template = get_template(engine)
    
    # 4. Generate HTML with embedded data
    html_content = template.render(data=data, height=height)
    
    return HTML(html_content)
```

### 3. Serialization Strategy

We need to bridge the gap between the Python graph model and the frontend's expected data structure. There are three approaches to consider:

#### Approach A: Adapt `D3Builder` (Recommended)
The `D3Builder` already produces a JSON-compatible dictionary (`nodes`, `links`, `graph`).
*   **Pros:** Reuses existing logic. Standard D3 format.
*   **Cons:** The frontend expects specific metadata (e.g., `nodeTypeCounts` as a list of objects) which `D3Builder` stores as a simple dict in `graph.node_types`.
*   **Fix:** Subclass or modify `D3Builder` to transform the metadata into the shape the frontend expects.

#### Approach B: Adapt GraphQL Schema
Use the existing `GraphQLBuilder` to execute a query internally (in Python) and dump the result to JSON.
*   **Pros:** Guarantees exact compatibility with the frontend (since it uses the same schema).
*   **Cons:** Heavy dependency. Requires spinning up a Strawberry execution context just to dump JSON. Overkill.

#### Approach C: Adapt Frontend (Polymorphic)
Modify the JavaScript in `index.html` to handle both formats.
*   **Logic:**
    ```javascript
    if (data.graph.nodeTypes is Array) {
        // Handle GraphQL format
    } else {
        // Handle D3/NetworkX format (convert dict to array)
    }
    ```
*   **Pros:** Keeps the Python backend simple. Makes the frontend more robust.
*   **Cons:** Adds complexity to the JS code.

**Decision:** We will likely use a hybrid of **A** and **C**. We will use `D3Builder` for serialization and slightly enhance the frontend to be more tolerant of standard D3 structures, or perform a lightweight transformation in Python before injection.

### 4. Pluggable Renderers

To support future engines (like Cosmograph for GPU acceleration), the `render` function will accept an `engine` argument.

*   **`default` (3d-force-graph):** The current Three.js based viewer. Good for small-medium graphs (< 5k nodes).
*   **`cosmograph` (Future):** GPU-accelerated renderer for massive graphs (1M+ nodes).
*   **`sigma` (Future):** 2D renderer for clean, flat layouts. (See [GEP-022](GEP-022_2D_Visualization_Mode.md))
*   **`datashader` (Future):** Python-based rasterization pipeline (Holoviz) for visualizing massive datasets (10M+ edges) as static or interactive images/heatmaps.

Each engine will have its own HTML template and JS logic, but they will all consume the same standardized JSON data structure (from Step 3).

### 5. Realtime & Incremental Updates

To support **Realtime Visualization** (streaming data from the backend or live updates in a notebook), the frontend architecture must support incremental updates without a full page reload.

**Requirements:**
1.  **JS API:** Each renderer MUST expose an `update(data)` or `addNodes(nodes)` / `addEdges(edges)` method.
2.  **Notebook Integration:** The `render()` function should return a widget object (e.g., `ipywidgets.DOMWidget`) that allows Python to call these JS methods.
    ```python
    widget = graphinate.render(model, live=True)
    display(widget)
    
    # Later...
    widget.add_node(id="new_node", ...)
    ```
3.  **Server Integration:** In Server Mode, the frontend should listen to a **GraphQL Subscription** (preferred) or WebSocket/SSE endpoint (defined in GEP-024) and call the renderer's update method.

### 6. Frontend Refactoring

The `index.html` logic will be extracted into a template (e.g., Jinja2 or simple string replacement).

```javascript
// viewer.js template
const data = {{ GRAPH_DATA_JSON }}; // Injected by Python

if (data) {
    // Static Mode
    initGraph(data);
} else {
    // Server Mode
    fetchGraphQL(...).then(initGraph);
}
```

### 7. Consideration: HTMX

We considered using **HTMX** to simplify the frontend interactions.
*   **Pros:** Great for server-driven UI updates (e.g., clicking a node to load details from Python).
*   **Cons:**
    *   **Static Export:** HTMX relies on server round-trips. It breaks the "Static Export" goal unless we pre-render everything or mock the server in JS (Service Workers), which is complex.
    *   **Canvas Interaction:** The core of the viewer is a WebGL Canvas (`3d-force-graph`). HTMX operates on DOM elements, not inside the Canvas.
*   **Verdict:** HTMX is not suitable for the core visualization (Canvas) or the static export use case. It might be useful for the "Control Panel" in Server Mode, but that would fragment the codebase (one UI for Server, one for Static). We will stick to client-side JS (Tweakpane) for the UI to ensure consistency across both modes.

## Backwards Compatibility

*   **Server:** The existing `graphinate.server` will continue to work as is, serving the same HTML (but now potentially using the unified template).
*   **API:** This adds new functions (`render`, `export`) without changing existing ones.

## Implementation Plan

1.  **Extract Serializer:** Create a Python function that converts a `GraphModel` (or `NetworkX` graph) into the JSON structure expected by the viewer.
2.  **Refactor Frontend:** Modify `index.html` to support data injection.
3.  **Create Template Registry:** A system to manage HTML templates for different engines.
4.  **Implement `render`:** Hook it up to `IPython.display`.

## Future Work (ObservableHQ)

For Observable, we can export the JSON data. The user can then import a generic "Graphinate Viewer" notebook and pass the JSON to it.
