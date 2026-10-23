---
title: GraphQL Schema Modes & Context
icon: lucide/share-2
---

# GraphQL Schema Modes & Context Injection

`GraphQLBuilder` compiles a `GraphModel` into an executable [Strawberry GraphQL](https://strawberry.rocks/) schema. You
can control how node types are mapped onto the GraphQL schema using `SchemaMode`, and override the active graph per
request using GraphQL execution context.

## Schema Modes (`SchemaMode`)

### 1. Dynamic Mode (`SchemaMode.DYNAMIC`, Default)

In `SchemaMode.DYNAMIC`, `GraphQLBuilder` generates a dedicated GraphQL object type implementing `GraphNode` for each
registered node type in the graph (for example, `ServiceNode`, `EndpointNode`), along with pluralized root query fields
on `Query` (such as `services`, `endpoints`):

```python
from graphinate import SchemaMode, model
from graphinate.builders import GraphQLBuilder

m = model(name='Architecture')


@m.node(type_='service')
def services():
    yield 'auth'


@m.node(type_='endpoint', parent_type='service')
def endpoints(service_id):
    yield f'{service_id}/login'


builder = GraphQLBuilder(m, mode=SchemaMode.DYNAMIC)
schema = builder.build()

result = schema.execute_sync('{ services { label neighbors { label } } }')
```

### 2. Static Mode (`SchemaMode.STATIC`)

In `SchemaMode.STATIC`, `GraphQLBuilder` uses a single `GenericGraphNode` type implementing `GraphNode` for all nodes
and exposes a fixed root `Query` interface (`graph`, `nodes`, `edges`, `measure`). This mode is useful when node types
are highly dynamic or when clients prefer a fixed GraphQL schema:

```python
from graphinate import SchemaMode
from graphinate.builders import GraphQLBuilder

builder = GraphQLBuilder(m, mode=SchemaMode.STATIC)
schema = builder.build()

result = schema.execute_sync('{ nodes { type label neighbors { label } } }')
```

## Context-Injected Graph Execution

By default, resolvers query the internal NetworkX graph built by `GraphQLBuilder`. You can also pass a custom `nx.Graph`
at execution time via `context_value={'graph': custom_graph}` without rebuilding the `strawberry.Schema`:

```python
from graphinate.builders import GraphQLBuilder, NetworkxBuilder

schema = GraphQLBuilder(m).build()
custom_graph = NetworkxBuilder(m).build()

result = schema.execute_sync(
    '{ graph { nodeCount edgeCount } nodes { label } }',
    context_value={'graph': custom_graph},
)
```
