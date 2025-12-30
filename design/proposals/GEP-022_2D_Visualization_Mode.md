# GEP-022: 2D Visualization Mode

| Field       | Value                 |
|:------------|:----------------------|
| **GEP**     | 22                    |
| **Title**   | 2D Visualization Mode |
| **Author**  | Eran Rivlis           |
| **Status**  | Superseded            |
| **Type**    | Standards Track       |
| **Created** | 2025-12-26            |
| **Updated** | 2025-12-30            |

## Abstract

The current viewer uses `3d-force-graph` to render the graph in a 3D space. While visually impressive ("Wonder"), 3D
visualizations often suffer from occlusion and navigation difficulties, making them less effective for analytical
tasks ("Clarity"). This proposal advocated for adding a 2D visualization mode using the `force-graph` library.

## Status: Superseded

This proposal has been **Superseded by GEP-026 (Pluggable Visualization & Notebook Support)**.

Instead of hardcoding a toggle between 2D and 3D, the project will adopt a **Pluggable Renderer Architecture**. A 2D renderer (using `force-graph`, `sigma.js`, or `cytoscape.js`) will simply be one of many possible `engine` implementations available to the user via `graphinate.render(model, engine='2d')`.

## Motivation (Original)

**Issues with 3D Only:**

1. **Occlusion:** Nodes in the foreground hide nodes in the background.
2. **Navigation:** 3D camera controls (orbit, pan, zoom) are more complex than 2D pan/zoom.
3. **Readability:** Text labels and edge directions are often harder to read in perspective projection.

**Benefits of 2D:**

1. **Clarity:** Easier to see the overall structure and clusters without perspective distortion.
2. **Standard:** Most graph analysis tools default to 2D.

## Specification (Original)

### 1. Library Integration

Integrate `force-graph` (the 2D Canvas/SVG sibling of `3d-force-graph`). It shares a nearly identical API, making
integration straightforward.

### 2. UI Toggle

Add a control in the Tweakpane UI to switch between 2D and 3D modes.

* This might require reloading the graph instance or swapping the DOM container.

### 3. Shared State

Ensure that filtering, coloring, and physics parameters (where applicable) are shared between both modes.

## Backwards Compatibility

The 3D mode will remain the default to preserve the "Wow" factor. The 2D mode will be an opt-in feature.
