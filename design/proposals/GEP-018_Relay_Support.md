---
title: "GEP-018: Relay Support"
description: "This proposal advocates for adding support for"
icon: lucide/git-branch
status: draft
---

# GEP-018: Relay Support

| Field       | Value           |
|:------------|:----------------|
| **GEP**     | 18              |
| **Title**   | Relay Support   |
| **Author**  | Eran Rivlis     |
| **Delegate**| The Council                   |
| **Status**  | Draft           |
| **Type**    | Standards Track |
| **Created** | 2025-12-25      |
| **Updated** | 2026-10-22                    |

## Abstract

This proposal advocates for adding support for
the [GraphQL Relay Specification](https://relay.dev/docs/guides/graphql-server-specification/) to the `GraphQLBuilder`.
This involves implementing Global Object Identification (Global IDs) and Cursor-based Pagination (Connections).

## Motivation

**Issues with Current Implementation:**

1. **Pagination:** Currently, `neighbors` and `edges` return simple lists. For large graphs, this is inefficient and can
   cause performance issues.
2. **Client Compatibility:** Many modern GraphQL clients (Relay, Apollo) rely on the Relay spec for efficient caching,
   pagination, and data fetching.

## Specification

### 1. Global Object Identification

The `GraphNode` type (and generated dynamic types) must implement the `strawberry.relay.Node` interface.

* The `id` field must be a globally unique ID (Base64 encoded type + ID).

### 2. Connections (Pagination)

Replace `List[GraphNode]` return types with `strawberry.relay.Connection[GraphNode]`.

**Current:**

```python
@strawberry.field
def neighbors(self) -> list[GraphNode]: ...
```

**Proposed:**

```python
@strawberry.field
def neighbors(self) -> strawberry.relay.Connection[GraphNode]: ...
```

### 3. Mapping Graph Edges to Relay Edges

In Graphinate, an "Edge" is a first-class entity with properties (weight, label). In Relay, an "Edge" is a structural
wrapper containing the target node and a cursor.

We can map Graphinate's edge data directly onto the Relay Edge type by extending it.

```python
@strawberry.type
class GraphRelayEdge(strawberry.relay.Edge):
    # Standard Relay fields
    node: GraphNode
    cursor: str

    # Graphinate Custom Fields
    weight: float
    label: str
    data: JSON
```

This provides a semantic match: The Relay Edge *is* the relationship, so it is the correct place to store relationship
properties.

## Backwards Compatibility

This is a **Breaking Change** for the GraphQL API.

* Clients expecting lists will break.
* IDs will change format (Global ID).

**Migration Strategy:**

* Introduce a configuration flag `relay=True` in `GraphQLBuilder`.
* Eventually make it the default in a major version (v1.0).

## Reference Implementation

Strawberry provides built-in support for Relay via `strawberry.relay`. We will leverage this to minimize boilerplate.
## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Conforms Graphinate's GraphQL schema to the standard Relay Object Identification and Cursor Connections specifications.
- **Efficiency (Shannon):** Replaces unbounded list allocations with scalable cursor-based pagination for large graphs.
- **Clarity (Feynman):** Global IDs make any node universally fetchable across client caches.

## Reference Implementation

- Relay interfaces and connection resolvers: `src/graphinate/builders/graphql.py`

## Change Log

* **2025-12-25:** Initial draft.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
