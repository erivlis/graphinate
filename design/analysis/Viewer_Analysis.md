# Graphinate Viewer Analysis

## Overview
The `graphinate.server.web.viewer` module contains the frontend code for visualizing the graph. It is a Single Page Application (SPA) served as a static HTML file.

## Architecture
- **Format:** Single HTML file (`index.html`) containing embedded CSS and JavaScript (ES Modules).
- **Build System:** None. Relies on runtime imports from CDNs (esm.sh, jsdelivr).
- **Communication:** Fetches data from the backend via the `/graphql` endpoint using `fetch`.

## Key Libraries
1.  **3d-force-graph:** The core visualization engine (WebGL based).
2.  **Tweakpane:** Provides the UI control panel (Legend, Settings).
3.  **Three.js / D3:** Underlying dependencies for rendering and math.
4.  **MurmurHash:** Used for client-side ID hashing.

## Key Features
1.  **3D Visualization:** Interactive force-directed graph.
2.  **Control Panel:**
    - **Legend:** Toggle visibility and color of node types.
    - **Advanced:** Tweak physics parameters (node volume, link width, particles).
    - **Tools:** Open embedded tools (GraphiQL, Voyager) in floating iframe panels.
3.  **Floating Panels:** Custom implementation of draggable, resizable windows for external tools.

## Data Flow
1.  **Fetch:** Queries `/graphql` for `GenericGraph` (nodes/edges) and `GraphTypes` (metadata).
2.  **Process:** Hashes IDs using MurmurHash (likely for performance or compatibility).
3.  **Render:** Passes data to `ForceGraph3D`.
4.  **Update:** Tweakpane callbacks modify the graph data or parameters and trigger `Graph.refresh()`.
