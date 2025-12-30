# GEP-027: Advanced Three.js Visualizations

| Field       | Value                            |
|:------------|:---------------------------------|
| **GEP**     | 27                               |
| **Title**   | Advanced Three.js Visualizations |
| **Author**  | Eran Rivlis                      |
| **Status**  | Draft                            |
| **Type**    | Informational                    |
| **Created** | 2025-12-30                       |
| **Updated** | 2025-12-30                       |

## Abstract

This proposal explores advanced visualization concepts using raw Three.js to transcend standard force-directed layouts.
By leveraging shaders, particle systems, and custom geometries, Graphinate can offer specialized "Modes" for massive
scale, temporal analysis, and immersive exploration.

## Motivation

The standard node-link diagram is versatile but limited.

1. **Performance:** Mesh-based nodes choke at >10k elements.
2. **Context:** Abstract circles don't convey hierarchy or density well.
3. **Aesthetics:** Sometimes you need "Wow Factor" or specific metaphors (City, Brain).

## Concepts

### 1. The Galaxy (High Performance)

* **Concept:** Render the graph as a star cluster.
* **Tech:** `THREE.Points` + Custom Shaders.
* **Use Case:** Massive graphs (100k - 1M nodes).
* **Visuals:** Nodes are glowing particles. Edges are faint nebula lines (or omitted for density).
* **Interaction:** Fly-through controls, raycasting for selection.
* **Realtime:** Highly efficient. Updating particle positions in a `Float32Array` buffer is instant. Ideal for streaming
  massive datasets.

### 2. The Data City (Hierarchical)

* **Concept:** Procedural city generation based on graph metrics.
* **Tech:** `THREE.InstancedMesh` (for buildings).
* **Use Case:** Corporate structures, file systems, software architecture.
* **Mapping:**
    * **Height:** Degree centrality or file size.
    * **Color:** Node type.
    * **District:** Community/Cluster.
    * **Roads:** Edges.
* **Realtime:** Moderate. Growing buildings (animating height) is cheap. Adding new buildings requires rebuilding the
  instance buffer (expensive).

### 3. The Neural Network (Aesthetic)

* **Concept:** Biological/Cybernetic brain visualization.
* **Tech:** `THREE.TubeGeometry`, `UnrealBloomPass` (Post-processing).
* **Use Case:** AI/ML models, social networks.
* **Visuals:** Pulsing edges (synapses), glowing nodes.
* **Animation:** Signals traveling along edges.
* **Realtime:** High. The "pulse" animation is purely shader-based. Structural updates are expensive (geometry
  regeneration).

### 4. The Time Tunnel (Temporal)

* **Concept:** 4D visualization where Z-axis represents Time.
* **Tech:** Extruded geometries.
* **Use Case:** Evolution of networks, transaction flows.
* **Visuals:** Nodes trace "world lines" through the tunnel. Slicing the tunnel shows the graph state at `t`.
* **Realtime:** N/A. This is inherently a historical view, though new "slices" could be appended to the front of the
  tunnel.

### 5. The Topographic Map (Density)

* **Concept:** 3D Terrain representing node density.
* **Tech:** Grid-based density calculation + Vertex Displacement Shader.
* **Use Case:** Community detection, structural analysis.
* **Visuals:** Mountains = Dense clusters. Valleys = Sparse connections.
* **Realtime:** High. Updating the heightmap texture allows the terrain to "morph" organically as data flows in.

## Implementation Strategy

These concepts fit into the **Pluggable Renderer Architecture** defined in **GEP-026**.
Each concept would be a distinct `engine` implementation (e.g., `engine='galaxy'`, `engine='city'`).

## Feasibility

* **Galaxy:** High feasibility. Standard Three.js particle techniques.
* **Neural:** Medium. Requires post-processing pipeline.
* **City:** Medium/High. Requires layout algorithms (Treemap/Voronoi).
* **Time Tunnel:** Hard. Requires complex geometry generation.
* **Topographic Map:** High feasibility. Standard heightmap/displacement shader techniques.

## Recommendation

Start with **The Galaxy** as a performance-focused alternative to the default renderer.
