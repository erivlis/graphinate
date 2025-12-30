# GraphModel Class Analysis

## Overview
The `GraphModel` class in `graphinate.modeling` is designed to declaratively define the structure and data sources for a graph. It serves as a registry for node and edge generators, allowing users to build a graph model by decorating functions that supply data.

## Key Features

### 1. Declarative Registration
The class provides two main decorators:
- `@node(...)`: Registers a function as a source of nodes. It creates a `NodeModel` instance capturing metadata like type, parent type, uniqueness, and how to extract attributes (key, value, label).
- `@edge(...)`: Registers a function as a source of edges. It captures how to extract source, target, label, weight, etc., from the supplied data.

### 2. Model Composition
The `__add__` method allows combining two `GraphModel` instances into a new one, merging their node models, hierarchy, and edge generators. This supports modular graph definitions.

### 3. Hierarchy Management
The model maintains a hierarchy of node types via `parent_type`. The `node_children_types` method allows querying this hierarchy.

### 4. Validation
- **Type Validation**: Ensures node and edge types are valid Python identifiers.
- **Parameter Validation**: The `_validate_node_parameters` method enforces a naming convention for node generator arguments (must be lowercase, end with `_id`, and correspond to an existing node type).

### 5. Rectification
The `rectify` method ensures the model is usable even if only edges are defined, by injecting a default node model if necessary.

## Internal Structure
- `_node_models`: Stores `NodeModel` instances indexed by `(parent_type, type)`.
- `_node_children`: Maps parent types to lists of child node types.
- `_edge_generators`: Stores edge generator functions indexed by edge type.
- `_networkx_graph`: Initialized to `None`, appears to be a placeholder or unused in this specific file.

## Usage Pattern
Users typically instantiate `GraphModel` (or use the `model()` factory), then use the `@model.node` and `@model.edge` decorators on functions that yield data items. These functions are then invoked when the graph is built (logic for building likely resides elsewhere, consuming this model).
