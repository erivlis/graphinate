# Graphinate Builders Analysis

## Overview
The `graphinate.builders` package provides a set of classes responsible for transforming a `GraphModel` into various graph representations. It follows a hierarchical structure where a base `Builder` class defines the contract, and specialized builders implement the logic for specific target formats (NetworkX, D3, GraphQL, Mermaid).

## Class Hierarchy

### 1. `Builder` (Abstract Base Class)
- **File**: `_builder.py`
- **Role**: Defines the interface for all builders.
- **Key Attributes**:
    - `model`: The `GraphModel` instance being built.
    - `graph_type`: Enum specifying the type of graph (e.g., Graph, DiGraph).
    - `default_node_attributes`: Default properties for nodes (type, label, value, lineage).
    - `default_edge_attributes`: Default properties for edges (type, label, value, weight).
- **Key Methods**:
    - `build(**kwargs)`: Abstract method that must be implemented by subclasses.

### 2. `NetworkxBuilder` (Concrete Implementation)
- **File**: `_networkx.py`
- **Inherits from**: `Builder`
- **Role**: Builds a `networkx.Graph` (or subclass) from the model. This serves as the intermediate representation for other builders.
- **Key Logic**:
    - **Initialization**: Creates an empty NetworkX graph based on `graph_type`.
    - **Node Population**: Iterates through `model.node_models`, generates nodes, and adds them to the graph. Handles hierarchy (parent/child nodes) and multiplicity (updating existing nodes).
    - **Edge Population**: Iterates through `model.edge_generators`, generates edges, and adds them to the graph.
    - **Rectification**: Ensures all nodes and edges have consistent attributes (e.g., colors, types) and computes aggregate statistics (node/edge type counts).
    - **Build Process**: `_initialize_graph` -> `_populate_node_type` -> `_populate_edges` -> `_finalize_graph`.

### 3. `D3Builder`
- **File**: `_d3.py`
- **Inherits from**: `NetworkxBuilder`
- **Role**: Converts the generated NetworkX graph into a dictionary format suitable for D3.js visualization.
- **Key Logic**:
    - Calls `super().build()` to get the NetworkX graph.
    - Converts colors to hex format.
    - Uses `nx.node_link_data` to serialize the graph.
    - Supports `json` (stringified) or `python` (dict) output formats.

### 4. `GraphQLBuilder`
- **File**: `_graphql.py`
- **Inherits from**: `NetworkxBuilder`
- **Role**: Generates a Strawberry GraphQL schema to query the graph data.
- **Key Logic**:
    - **Dynamic Type Creation**: Generates GraphQL types for each node type in the graph at runtime.
    - **Resolvers**: Implements resolvers for nodes, edges, neighbors, and graph metrics (radius, diameter, etc.).
    - **Schema Generation**: Creates a `Query` type with fields for accessing the graph, nodes, and edges, and a `Mutation` type for refreshing the graph.
    - **Integration**: Uses `strawberry` to define the schema and types.

### 5. `MermaidBuilder`
- **File**: `_mermaid.py`
- **Inherits from**: `NetworkxBuilder`
- **Role**: Generates a Mermaid diagram definition from the graph.
- **Key Logic**:
    - Calls `super().build()` to get the NetworkX graph.
    - Uses `networkx_mermaid` library to convert the graph into a Mermaid diagram string.
    - Allows customization of orientation, node shape, and title.

## Summary of Flow
1.  A `GraphModel` is defined (declarative structure).
2.  A specific `Builder` is instantiated with this model.
3.  The `build()` method is called.
4.  `NetworkxBuilder` (the workhorse) populates a `networkx` graph by executing the model's generators.
5.  If a specialized builder (D3, GraphQL, Mermaid) is used, it further processes the `networkx` graph into the target format.
