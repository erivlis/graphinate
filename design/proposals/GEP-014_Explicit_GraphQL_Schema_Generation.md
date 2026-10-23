---
title: "GEP-014: Explicit GraphQL Schema Generation"
description: "Refactor GraphQLBuilder to use strawberry.tools.create_type, context-injected resolvers, and an optional SchemaMode.STATIC."
icon: lucide/git-branch
status: active
---

# GEP-014: Explicit GraphQL Schema Generation

| Field        | Value                              |
|:-------------|:-----------------------------------|
| **GEP**      | 14                                 |
| **Title**    | Explicit GraphQL Schema Generation |
| **Author**   | Eran Rivlis                        |
| **Delegate** | The Council                        |
| **Status**   | Active                             |
| **Type**     | Standards Track                    |
| **Created**  | 2025-12-25                         |
| **Updated**  | 2026-10-23                         |

## Abstract

`GraphQLBuilder` previously used manual `type(name, bases, class_dict)` and `__annotations__` mutation to generate GraphQL types at runtime. This proposal replaces ad-hoc class dictionary metaprogramming with Strawberry's official `strawberry.tools.create_type`, supports GraphQL execution context injection (`info.context["graph"]`), and introduces `SchemaMode` (`DYNAMIC` and `STATIC`) for generic vs. per-node-type schemas.

## Motivation

The legacy implementation inspected the `GraphModel` and used raw `type()` calls to construct classes (`UserNode`, `PostNode`) on the fly while mutating `__annotations__` and capturing `self._graph` exclusively inside nested closures.

**Issues:**

1. **Fragility:** Relying on internal details of how `strawberry` parses manually mutated `__annotations__`.
2. **Coupling:** Resolvers could only read `self._graph` from closure scope, preventing callers from passing a per-request graph via `info.context['graph']`.
3. **Lack of Static Mode:** Users with highly dynamic or schema-agnostic graphs had no option to use a single, uniform `GenericGraphNode` type.

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Both `SchemaMode.DYNAMIC` and `SchemaMode.STATIC` implement the same `GraphNode` interface and share the same resolver factories.
- **Falsifiability (Popper):** Context injection (`context_value={"graph": custom_nx_graph}`) allows executing the same compiled `strawberry.Schema` against arbitrary test graphs without rebuilding the schema.
- **Efficiency (Shannon):** `SchemaMode.STATIC` avoids generating N distinct Strawberry types when per-type root fields are not needed.
- **Safety (The Golem):** Eliminates manual `__annotations__` dictionary mutation in favor of `strawberry.tools.create_type`.
- **Clarity (Feynman):** Replacing runtime `type()` metaprogramming with `create_type` and `info.context` resolution makes schema construction transparent and maintainable.
- **Consistency (Russell):** Resolvers uniformly resolve the active graph via `_resolve_graph(info)` across `graph`, `nodes`, `edges`, `measure`, `neighbors`, and `node.edges`.
- **Harmony (The Steward):** Preserves `SchemaMode.DYNAMIC` and fallback to `self._graph` by default so all existing callers and queries work without modification.

## Specification

### 1. `SchemaMode` Enum (`graphinate.enums`)

```python
class SchemaMode(Enum):
    DYNAMIC = auto()
    STATIC = auto()
```

Exported at the top-level `graphinate` package (`from graphinate import SchemaMode`).

### 2. `strawberry.tools.create_type` & Context-Aware Resolvers

- `GraphQLBuilder.__init__(model, graph_type=GraphType.Graph, mode=SchemaMode.DYNAMIC)` accepts `mode: SchemaMode`.
- Both node types and the root `Query` type are constructed using `strawberry.tools.create_type`.
- Resolvers accept `info: strawberry.types.Info` and resolve the backing `nx.Graph` via `self._resolve_graph(info)`, which checks `info.context['graph']` when provided and falls back to `self._graph`.

### 3. Static Mode (`SchemaMode.STATIC`)

- When `mode=SchemaMode.STATIC`, `GraphQLBuilder` registers a single `GenericGraphNode` implementing `GraphNode` for all nodes and exposes the standard root fields (`graph`, `nodes`, `edges`, `measure`).

## Backwards Compatibility

- `SchemaMode.DYNAMIC` is the default mode.
- When `context_value` is not supplied to `schema.execute_sync()` / `schema.execute()`, resolvers automatically fall back to `self._graph`, maintaining 100% compatibility with existing tests and ASGI routes.

## How to Teach This / Documentation Plan

- Export `SchemaMode` in `graphinate`.
- Document `SchemaMode.DYNAMIC`, `SchemaMode.STATIC`, and `context_value={"graph": ...}` in [`docs/advanced/graphql.md`](file:///C:/dev/erivlis/graphinate/docs/advanced/graphql.md) and [`docs/usage/lib.md`](file:///C:/dev/erivlis/graphinate/docs/usage/lib.md).

## Reference Implementation

- Enum definition: [`src/graphinate/enums.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/enums.py)
- Schema builder: [`src/graphinate/builders/graphql.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/builders/graphql.py)
- User documentation: [`docs/advanced/graphql.md`](file:///C:/dev/erivlis/graphinate/docs/advanced/graphql.md)
- Unit tests: [`tests/graphinate/builders/test_graphql.py`](file:///C:/dev/erivlis/graphinate/tests/graphinate/builders/test_graphql.py)

## Rejected Ideas

- **Removing Dynamic Mode Entirely:** Rejected because pluralized per-node-type root queries (e.g., `countries`, `cities`, `repositories`) are a signature ergonomic feature of Graphinate's GraphQL API.
- **Requiring `context_value={'graph': ...}` on Every Call:** Rejected because standalone scripts calling `schema.execute_sync(query)` expect the schema built by `GraphQLBuilder` to work out-of-the-box without mandatory boilerplate.

## Open Questions

- [x] Should resolvers fall back to `self._graph` when `info.context` does not contain `'graph'`? *Decision: Yes, falling back to `self._graph` preserves zero-config ergonomics while enabling context injection.*

## Change Log

* **2025-12-25:** Initial draft.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
* **2026-10-23:** Implemented `SchemaMode`, refactored `GraphQLBuilder` to use `strawberry.tools.create_type` and context-aware resolvers, and transitioned status to `Active`.

