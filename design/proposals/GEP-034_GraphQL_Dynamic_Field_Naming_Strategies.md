---
title: "GEP-034: GraphQL Dynamic Field and Type Naming Strategies"
description: "Configurable dynamic query field naming strategies and idiomatic PascalCase dynamic type names in GraphQLBuilder to align with Strawberry auto_camel_case and GraphQL specifications."
icon: lucide/share-2
status: active
---

# GEP-034: GraphQL Dynamic Field and Type Naming Strategies

| Field        | Value                                                   |
|:-------------|:--------------------------------------------------------|
| **GEP**      | 34                                                      |
| **Title**    | GraphQL Dynamic Field and Type Naming Strategies        |
| **Author**   | Eran Rivlis                                             |
| **Delegate** | The Council                                             |
| **Status**   | Active                                                  |
| **Type**     | Standards Track                                         |
| **Created**  | 2026-10-29                                              |
| **Updated**  | 2026-10-29                                              |

## Abstract

This proposal specifies the introduction of configurable dynamic field naming strategies and idiomatic type naming in `GraphQLBuilder`.
In `SchemaMode.DYNAMIC`, `GraphQLBuilder` generates pluralized root query fields and GraphQL object types corresponding to each node type
defined in a `GraphModel`. Previously, dynamic query fields were constructed with explicit field names (`strawberry.field(name=...)`),
which Strawberry interprets as an explicit user override, thereby bypassing Strawberry's automatic camel-casing
(`StrawberryConfig.auto_camel_case`). Consequently, dynamic fields were exposed in `snake_case` (e.g., `user_accounts`,
`git_commits`) even while built-in fields and arguments adopt standard GraphQL `camelCase`. This GEP
introduces a `dynamic_field_naming` configuration option supporting `explicit` (default, backward-compatible) and
`auto` (delegating to Strawberry's auto-casing pipeline), and exposes `StrawberryConfig` customization in `schema()`.

Additionally, this proposal standardizes dynamically generated GraphQL node types (`GraphQLBuilder._graphql_types`) to
idiomatic `PascalCase`. Previously, type names were constructed using Python's `str.capitalize()`, retaining internal
underscores (e.g., `Git_commitNode`, `User_accountNode`). This proposal standardizes dynamic node types to idiomatic `PascalCase`
(e.g., `GitCommitNode`, `UserAccountNode`), aligning fully with official GraphQL schema design specifications.

## Motivation

GraphQL conventions and specifications (including Apollo, Relay, and the GraphQL Foundation style guidelines) universally
standardize on `camelCase` for fields and arguments.

In Graphinate, `GraphQLBuilder` translates a `GraphModel` into an executable Strawberry schema. Throughout the built-in
types, fields and arguments adhere to standard camel-casing:
- Root query arguments: `node_id` becomes `nodeId`, `edge_id` becomes `edgeId`.
- Attributes on `Graph`: `node_type_counts` becomes `nodeTypeCounts`, `average_degree` becomes `averageDegree`.
- Attributes on `GraphNode`: `node_id` becomes `nodeId`.

However, in `SchemaMode.DYNAMIC`, root query fields for registered node types are synthesized dynamically:

```python
for node_type, graphql_type in self._graphql_types.items():
    field_name = field_name_manager.make_valid(inflection.plural(node_type))
    query_fields.append(
        strawberry.field(
            name=field_name,
            resolver=graph_nodes_resolver(graphql_type, node_type, resolver_name=field_name),
        )
    )
```

Because `name=field_name` is explicitly passed to `strawberry.field()`, Strawberry assigns `StrawberryField.graphql_name = field_name`.
During Strawberry schema compilation, the schema converter respects explicit `graphql_name` definitions as immutable user overrides,
completely bypassing `StrawberryConfig.auto_camel_case`.

### Problems Caused by Current Behavior

1. **Inconsistent Schema Casing**:
   A single GraphQL schema produced by Graphinate contains a mixture of casing conventions:
   ```graphql
   type Query {
     graph: Graph!
     nodes(nodeId: ID): [GraphNode!]! # camelCase argument
     edges(edgeId: ID): [GraphEdge!]! # camelCase argument
     user_accounts: [UserAccountNode!]! # snake_case dynamic field
     git_commits: [GitCommitNode!]! # snake_case dynamic field
   }
   ```
2. **Client Tooling Friction**:
   Modern GraphQL client libraries, frontend generators (such as GraphQL Code Generator, Relay Compiler, and Apollo iOS/Kotlin),
   and linting tools (such as `graphql-eslint`) expect uniform `camelCase` identifiers. Mixed casing forces frontend developers
   to write irregular client queries and disallows automated lint rules.
3. **Inability to Opt In to Strawberry Auto-Casing**:
   Users who desire idiomatic camelCase dynamic fields currently have no configuration hook or strategy to enable it without
   monkeypatching `GraphQLBuilder._graphql_query`.
4. **Non-Idiomatic GraphQL Type Names (`Git_commitNode`)**:
   In `GraphQLBuilder._graphql_types`, dynamic node GraphQL type names were generated via Python's built-in `str.capitalize()`:
   ```python
   class_name = class_name_manager.make_valid(node_type.capitalize())
   type_name = f"{class_name}{'' if node_type.lower().endswith('node') else 'Node'}"
   ```
   Because `str.capitalize()` only modifies the initial character, compound and snake_case node types retained internal underscores:
   `"git_commit"` became `Git_commitNode`, and `"user_account"` became `User_accountNode`.
   The official GraphQL specification prescribes `PascalCase` for all Object types, Interfaces, and Unions. Retaining raw underscores
   in GraphQL type names violates schema design standards and creates awkward, non-idiomatic types in typed client SDKs.

## Rationale

This proposal is designed in direct alignment with the **Council Framework (GEP-001)**:

* **Clarity (Feynman)**:
  Eliminates the confusing discrepancy where some parts of the schema use `camelCase` while dynamic root queries
  are stuck in `snake_case`. A consistent schema is easier to reason about, query, and consume.
* **Consistency (Russell)**:
  Harmonizes `GraphQLBuilder` with the Strawberry ecosystem and GraphQL conventions. Both fields and types should adhere
  to standard GraphQL casing (`camelCase` for fields, `PascalCase` for types like `GraphNode`, `GraphEdge`, and dynamic node types).
* **Symmetry (Noether)**:
  Static fields (`nodeTypeCounts`) and dynamic fields (`userAccounts`) should be governed by symmetric naming rules
  rather than being treated as disparate architectural regimes.
* **Simplicity (Ockham)**:
  Unconditionally standardizing dynamic node type names to `PascalCase` fixes a formatting anomaly directly without adding
  superfluous configuration parameters, since GraphQL object types universally require `PascalCase`.
* **Safety (The Golem)**:
  Maintaining backward compatibility is paramount for field queries. Existing client queries in production systems may already query
  `user_accounts`. By defaulting to `DynamicFieldNaming.EXPLICIT` (or `"explicit"`), existing queries remain completely
  unbroken. Users explicitly opt into `auto` mode when they are ready.

## Specification

### 1. `DynamicFieldNaming` Strategy Enum

A new enumeration will be added to `graphinate.builders.graphql` (and exported from `graphinate`):

```python
from enum import Enum

class DynamicFieldNaming(str, Enum):
    """Naming strategy for dynamically generated GraphQL query fields."""
    EXPLICIT = "explicit"
    AUTO = "auto"
```

* `EXPLICIT` (Default): Passes `name=field_name` explicitly to `strawberry.field()`, preserving current `snake_case`
  behavior (e.g. `user_accounts`, `git_commits`).
* `AUTO`: Omits `name=...` and instead sets `resolver.__name__ = field_name`. This allows Strawberry's configured
  `auto_camel_case` transformation to process the field name (yielding `userAccounts`, `gitCommits` by default).

### 2. `GraphQLBuilder` Parameterization

`GraphQLBuilder.__init__` will accept `dynamic_field_naming`:

```python
def __init__(
    self,
    model: GraphModel,
    graph_type: GraphType = GraphType.Graph,
    mode: SchemaMode = SchemaMode.DYNAMIC,
    dynamic_field_naming: DynamicFieldNaming = DynamicFieldNaming.EXPLICIT,
    node_value_graphql_type_supplier: Callable[[str], type | None] | None = None,
):
    ...
    self.dynamic_field_naming = DynamicFieldNaming(dynamic_field_naming)
```

Consistent with other builder configuration parameters (such as `mode: SchemaMode`), the parameter strongly types `DynamicFieldNaming`. Because `DynamicFieldNaming` inherits from `StrEnum`, passing string values `"explicit"` or `"auto"` at runtime is seamlessly coerced.

### 3. Dynamic Field Construction

In `GraphQLBuilder._graphql_query`, dynamic fields are constructed cleanly by parameterizing `strawberry.field`:

```python
if self.mode == SchemaMode.DYNAMIC:
    field_name_manager = VariableNameManager()
    for node_type, graphql_type in self._graphql_types.items():
        field_name = field_name_manager.make_valid(inflection.plural(node_type))
        resolver = graph_nodes_resolver(graphql_type, node_type, resolver_name=field_name)

        field_params: dict[str, Any] = {'resolver': resolver}
        if self.dynamic_field_naming == DynamicFieldNaming.EXPLICIT:
            field_params['name'] = field_name

        query_fields.append(strawberry.field(**field_params))
```

### 4. `StrawberryConfig` Pass-Through in `schema()`

`GraphQLBuilder.schema()` will be enhanced to accept an optional `config: strawberry.schema.config.StrawberryConfig` instance:

```python
def schema(self, config: strawberry.schema.config.StrawberryConfig | None = None) -> strawberry.Schema:
    unique_types = list({id(t): t for t in self._graphql_types.values()}.values())
    return strawberry.Schema(
        query=self._graphql_query(),
        mutation=self._graphql_mutation(),
        types=unique_types,
        config=config,
        extensions=[
            lambda: ParserCache(maxsize=100),
            lambda: QueryDepthLimiter(max_depth=10),
            lambda: MaxAliasesLimiter(max_alias_count=15),
            lambda: MaxTokensLimiter(max_token_count=1000),
        ],
    )
```

When `config` is omitted, Strawberry defaults to `auto_camel_case=True`. When a custom config is supplied (such as `StrawberryConfig(auto_camel_case=False)`), Strawberry honors the user's setting across all auto-named fields.

### 5. Idiomatic `PascalCase` Dynamic Node Type Names

In `GraphQLBuilder._graphql_types`, dynamic node GraphQL type names are normalized and converted into idiomatic `PascalCase` using Strawberry's native string conversion utilities (`to_camel_case` and `capitalize_first` from `strawberry.utils.str_converters`):

```python
from strawberry.utils.str_converters import capitalize_first, to_camel_case

# Inside _graphql_types:
for node_type in node_types:
    pascal_name = capitalize_first(to_camel_case(node_type.replace('-', '_')))
    class_name = class_name_manager.make_valid(pascal_name)
    type_name = f"{class_name}{'' if class_name.lower().endswith('node') else 'Node'}"
```

Key characteristics:
1. **Separator Normalization**: Hyphens and underscores are converted to camelCase before capitalizing the initial character, producing clean `PascalCase`.
2. **Suffix Deduplication**: Checking `class_name.lower().endswith('node')` ensures node types already ending in `_node` or `Node` (e.g., `user_node`) result in `UserNode` rather than duplicating the suffix (e.g., `UserNodeNode`).
3. **Decoupled Resolver Lookups**: Internal resolvers and mappings retrieve types from `self._graphql_types` using the raw `node_type` string key (e.g., `self._graphql_types.get(node_type)`). Modifying `type_name` only alters the GraphQL schema type identifier and does not affect internal node model lookups or edge traversal.

## Backwards Compatibility

* **Field Queries (Zero Breaking Changes)**: The default naming strategy for fields remains `DynamicFieldNaming.EXPLICIT`. Existing
  applications, tests, and client queries continue to receive `snake_case` dynamic query field names unless explicitly opted into `auto`.
* **Dynamic Node Type Names**: Single-word node types (`user` -> `UserNode`, `city` -> `CityNode`) remain completely unchanged.
  Multi-word node types (such as `git_commit` -> `GitCommitNode`, previously `Git_commitNode`) are standardized to `PascalCase`.
  GraphQL queries using inline type fragments specifically targeting the type (e.g., `... on Git_commitNode`) will need to query
  `... on GitCommitNode`. This change directly aligns Graphinate with the GraphQL specification for Object type naming.
* **API Stability**: All constructor signatures and builder interfaces remain backwards compatible.

## How to Teach This / Documentation Plan

* **Documentation Guide Update**: Update `docs/advanced/graphql.md` to document the `dynamic_field_naming` option with an
  explicit code sample comparing `SchemaMode.DYNAMIC` output under `explicit` vs `auto`.
* **Client Best Practices Note**: Add a callout box in documentation recommending `DynamicFieldNaming.AUTO` when integrating
  with React Relay, Apollo Client, or TypeScript GraphQL code generators.
* **Docstrings**: Provide Google-style docstrings with examples on `DynamicFieldNaming` and `GraphQLBuilder.__init__`.

## Reference Implementation

### Prototype Implementation

```python
from enum import StrEnum
from typing import Any
import strawberry
from strawberry.schema.config import StrawberryConfig
from strawberry.utils.str_converters import capitalize_first, to_camel_case

class DynamicFieldNaming(StrEnum):
    EXPLICIT = "explicit"
    AUTO = "auto"

# In _graphql_types():
pascal_name = capitalize_first(to_camel_case(node_type.replace('-', '_')))
class_name = class_name_manager.make_valid(pascal_name)
type_name = f"{class_name}{'' if class_name.lower().endswith('node') else 'Node'}"

# In _graphql_query():
field_params: dict[str, Any] = {'resolver': resolver}
if self.dynamic_field_naming == DynamicFieldNaming.EXPLICIT:
    field_params['name'] = field_name
query_fields.append(strawberry.field(**field_params))
```

### Dynamic Node Type Transformation Matrix

| Raw `node_type` | Previous Generated Type | New `PascalCase` Type |
| :--- | :--- | :--- |
| `"user"` | `UserNode` | `UserNode` |
| `"git_commit"` | `Git_commitNode` | `GitCommitNode` |
| `"user_account"` | `User_accountNode` | `UserAccountNode` |
| `"data_doc_biz_model"` | `Data_doc_biz_modelNode` | `DataDocBizModelNode` |
| `"user_node"` | `User_node` | `UserNode` |
| `"UserNode"` | `UserNode` | `UserNode` |
| `"user-account"` | `User_accountNode` | `UserAccountNode` |

### Test Scenarios

1. **Explicit Mode (Default)**:
   A node type `git_commit` yields root field `git_commits` in schema and type `GitCommitNode`.
2. **Auto Mode + Default Strawberry Config (`auto_camel_case=True`)**:
   A node type `git_commit` yields root field `gitCommits` in schema and type `GitCommitNode`.
3. **Auto Mode + Explicit Strawberry Config (`auto_camel_case=False`)**:
   A node type `git_commit` yields root field `git_commits` in schema and type `GitCommitNode`.
4. **Constructor Default Guarantee**:
   Instantiating `GraphQLBuilder(model)` without `dynamic_field_naming` produces identical schema to `dynamic_field_naming="explicit"`.

## Rejected Ideas

* **Make `auto` the Default Immediately**:
  Rejected because changing the default casing of query fields in a minor release would silently break existing
  client queries and frontend applications in production.
* **Custom Field Name Formatter Callback (`Callable[[str], str]`)**:
  Rejected as premature generalization. Strawberry's native `StrawberryConfig.auto_camel_case` and name converters
  already provide standard, thoroughly tested identifier transformations.
* **Boolean Flag (`auto_camel_case: bool`) on `GraphQLBuilder`**:
  Rejected because Strawberry itself already owns the `auto_camel_case` setting in `StrawberryConfig`. Having a duplicate
  boolean on Graphinate's builder causes confusion over whether it controls Graphinate's naming strategy or overrides
  Strawberry's configuration. An enum (`DynamicFieldNaming`) accurately conveys that it governs how Graphinate registers
  fields with Strawberry.
* **Configurable Type Naming Option (e.g. `DynamicTypeNaming` or flag)**:
  Rejected. Unlike query fields where some API architectures intentionally employ `snake_case` fields, GraphQL
  specifications and community best practices universally prescribe `PascalCase` for Object types without exception.
  Retaining underscores in type names (`Git_commitNode`) was an unintended side-effect of `str.capitalize()`, not a designed
  feature. Adding a configuration flag for type names would introduce unnecessary cognitive load and perpetuate non-standard schemas.

## Open Questions

- [ ] Should `DynamicFieldNaming.AUTO` become the default in a future major version (e.g. Graphinate 1.0 or 2.0)?
- [ ] Should `dynamic_field_naming` also affect field names in custom node types if dynamic attributes are introduced in the future?

## Change Log

* **2026-10-29:**
  * Initial draft created proposing `DynamicFieldNaming` (`explicit` vs `auto`) and StrawberryConfig integration in `GraphQLBuilder`.
  * Implemented and activated: Added `DynamicFieldNaming` enum, `dynamic_field_naming` parameter in `GraphQLBuilder`, `StrawberryConfig` pass-through in `schema()`, `abuild()`, and `build()`, comprehensive tests, and user documentation.
  * Addendum (Under Review): Standardized dynamic GraphQL Object type naming to idiomatic `PascalCase` (e.g. `GitCommitNode`, `UserAccountNode`) using Strawberry string converters with suffix deduplication.

