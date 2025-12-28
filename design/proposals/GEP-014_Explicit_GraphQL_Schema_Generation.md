# GEP-014: Explicit GraphQL Schema Generation

| Field       | Value                              |
|:------------|:-----------------------------------|
| **GEP**     | 14                                 |
| **Title**   | Explicit GraphQL Schema Generation |
| **Author**  | Eran Rivlis                        |
| **Status**  | Draft                              |
| **Type**    | Standards Track                    |
| **Created** | 2025-12-25                         |

## Abstract

The current `GraphQLBuilder` dynamically generates Python classes at runtime to represent GraphQL types for each node
type in the graph. While this provides a tailored API experience ("Magic"), it is fragile, hard to debug, and lacks IDE
support. This proposal advocates for a two-pronged approach:

1. Introducing a "Static Mode" that uses a generic schema for robustness.
2. Refactoring the "Dynamic Mode" to use safer meta-programming practices and standard context injection.

## Motivation

The current implementation inspects the `GraphModel` and uses `type()` to create new classes (e.g., `UserNode`,
`PostNode`) on the fly, manually manipulating `__annotations__`. Furthermore, resolvers are defined as closures that
capture the builder instance, tightly coupling the schema to the specific builder object.

**Issues:**

1. **Opacity:** Developers cannot see the schema definition in the code.
2. **Tooling:** IDEs and static analysis tools cannot understand these dynamic types.
3. **Fragility:** The implementation relies on internal details of how `strawberry` parses annotations.
4. **Coupling:** Resolvers rely on closure-captured state (`self._graph`), making them hard to test and reuse.

## Specification

We propose supporting two modes of operation and hardening the implementation.

### 1. Static Mode (Generic)

Use a single, pre-defined `GraphNode` type for all nodes. This mode is robust, IDE-friendly, and easier to debug.

```python
@strawberry.type
class GraphNode:
    id: strawberry.ID
    type: str
    label: str
    data: JSON  # Generic payload

    @strawberry.field
    def neighbors(self, info, type: str | None = None) -> list['GraphNode']:
        # Access graph via context
        graph = info.context['graph']
        ...
```

### 2. Dynamic Mode (Refactored)

Preserve the current behavior but refactor the implementation to be safer and more standard.

#### A. Use `strawberry.tools.create_type`

Instead of manually constructing class dictionaries and annotations, use the official utility provided by Strawberry.

```python
from strawberry.tools import create_type

# Create the type safely
UserNode = create_type(
    name="UserNode",
    fields=fields,
    interfaces=[GraphNode],
    description="A User Graph Node"
)
```

#### B. Stateless Resolvers & Context Injection

Move resolver logic out of closures into standalone functions. Pass the graph data via the GraphQL execution context (
`info.context`) rather than capturing it.

**Current (Closure):**

```python
def neighbors_resolver():
    graph = self._graph  # Captured from builder

    def resolve(root):
        return graph.neighbors(root.id)

    return resolve
```

**Proposed (Context):**

```python
def resolve_neighbors(root, info, type: str | None = None) -> list[GraphNode]:
    graph = info.context['graph']  # Injected via ASGI app context
    return [n for n in graph.neighbors(root.id) if ...]


# Usage in create_type
fields = [
    strawberry.field(name="neighbors", resolver=resolve_neighbors, type=list[GraphNode])
]
```

This decouples the schema definition from the builder instance, making the resolvers testable and the architecture
cleaner.

### Configuration

The `GraphQLBuilder` will accept a configuration flag:

```python
class SchemaMode(Enum):
    DYNAMIC = auto()
    STATIC = auto()


builder = GraphQLBuilder(model, mode=SchemaMode.STATIC)
```

## Backwards Compatibility

By making `DYNAMIC` the default, we preserve full backwards compatibility. The refactoring of the dynamic mode should be
functionally equivalent to the current implementation.
