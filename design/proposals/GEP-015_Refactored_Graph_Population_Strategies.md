# GEP-015: Refactored Graph Population Strategies

| Field | Value |
| :--- | :--- |
| **GEP** | 15 |
| **Title** | Refactored Graph Population Strategies |
| **Author** | Eran Rivlis |
| **Status** | Draft |
| **Type** | Standards Track |
| **Created** | 2025-12-25 |

## Abstract

The `NetworkxBuilder` class currently contains complex, monolithic logic for node identity generation (lineage) and handling duplicates (multiplicity). This proposal suggests refactoring this logic into separate, testable Strategy classes.

## Motivation

The `_populate_nodes` method in `NetworkxBuilder` is difficult to read and test because it mixes:
1.  Iterating generators.
2.  Calculating node IDs based on hierarchy (Lineage).
3.  Deciding whether to add or update a node (Multiplicity).

## Specification

Introduce two new strategy interfaces:

### 1. IdentityStrategy
Responsible for calculating the unique ID of a node.
*   `calculate_id(node, parent_id, model) -> NodeID`

### 2. UpdateStrategy
Responsible for handling node collisions.
*   `handle_collision(graph, node_id, new_data, multiplicity) -> None`

The `NetworkxBuilder` will delegate to these strategies, making the core loop cleaner and allowing users to plug in custom behaviors (e.g., different ID schemes).

## Backwards Compatibility

This is an internal refactoring. The public API of `NetworkxBuilder` should remain largely unchanged, though subclasses might need updates.
