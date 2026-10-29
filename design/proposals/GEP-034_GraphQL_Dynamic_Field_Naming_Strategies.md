---
title: "GEP-034: GraphQL Dynamic Field Naming Strategies"
description: "Configurable dynamic query field naming strategies in GraphQLBuilder to support Strawberry auto_camel_case while preserving backward compatibility."
icon: lucide/share-2
status: active
---

# GEP-034: GraphQL Dynamic Field Naming Strategies

| Field        | Value                                          |
|:-------------|:-----------------------------------------------|
| **GEP**      | 34                                             |
| **Title**    | GraphQL Dynamic Field Naming Strategies        |
| **Author**   | Eran Rivlis                                    |
| **Delegate** | The Council                                    |
| **Status**   | Active                                         |
| **Type**     | Standards Track                                |
| **Created**  | 2026-10-29                                     |
| **Updated**  | 2026-10-29                                     |

## Abstract

This proposal specifies the introduction of configurable dynamic field naming strategies in `GraphQLBuilder`.
In `SchemaMode.DYNAMIC`, `GraphQLBuilder` generates pluralized root query fields corresponding to each node type
defined in a `GraphModel`. Currently, these fields are constructed with explicit field names (`strawberry.field(name=...)`),
which Strawberry interprets as an explicit user override, thereby bypassing Strawberry's automatic camel-casing
(`StrawberryConfig.auto_camel_case`). Consequently, dynamic fields are exposed in `snake_case` (e.g., `user_accounts`,
`git_commits`) even while built-in fields and arguments adopt standard GraphQL `camelCase`. This GEP
introduces a `dynamic_field_naming` configuration option supporting `explicit` (default, backward-compatible) and
`auto` (delegating to Strawberry's auto-casing pipeline), and exposes `StrawberryConfig` customization in `schema()`.

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

## Rationale

This proposal is designed in direct alignment with the **Council Framework (GEP-001)**:

* **Clarity (Feynman)**:
  Eliminates the confusing discrepancy where some parts of the schema use `camelCase` while dynamic root queries
  are stuck in `snake_case`. A consistent schema is easier to reason about, query, and consume.
* **Consistency (Russell)**:
  Harmonizes `GraphQLBuilder` with the Strawberry ecosystem. When users configure Strawberry or expect standard
  Strawberry behavior, Graphinate should respect Strawberry's native conventions rather than bypassing them.
* **Symmetry (Noether)**:
  Static fields (`nodeTypeCounts`) and dynamic fields (`userAccounts`) should be governed by symmetric naming rules
  rather than being treated as disparate architectural regimes.
* **Safety (The Golem)**:
  Maintaining backward compatibility is paramount. Existing client queries in production systems may already query
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

## Backwards Compatibility

* **Zero Breaking Changes**: The default naming strategy is `DynamicFieldNaming.EXPLICIT`. Existing applications, tests,
  and client queries continue to receive `snake_case` dynamic query field names unless explicitly opted into `auto`.
* **API Stability**: All existing arguments to `GraphQLBuilder` and `GraphQLBuilder.schema()` remain unchanged. The new
  parameters are strictly additive with sensible defaults.

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
import strawberry
from strawberry.schema.config import StrawberryConfig

class DynamicFieldNaming(StrEnum):
    EXPLICIT = "explicit"
    AUTO = "auto"

# Inside GraphQLBuilder:
# self.dynamic_field_naming = DynamicFieldNaming(dynamic_field_naming)

# In _graphql_query():
field_params: dict[str, Any] = {'resolver': resolver}
if self.dynamic_field_naming == DynamicFieldNaming.EXPLICIT:
    field_params['name'] = field_name
query_fields.append(strawberry.field(**field_params))
```

### Test Scenarios

1. **Explicit Mode (Default)**:
   A node type `git_commit` yields root field `git_commits` in schema.
2. **Auto Mode + Default Strawberry Config (`auto_camel_case=True`)**:
   A node type `git_commit` yields root field `gitCommits` in schema.
3. **Auto Mode + Explicit Strawberry Config (`auto_camel_case=False`)**:
   A node type `git_commit` yields root field `git_commits` in schema.
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

## Open Questions

- [ ] Should `DynamicFieldNaming.AUTO` become the default in a future major version (e.g. Graphinate 1.0 or 2.0)?
- [ ] Should `dynamic_field_naming` also affect field names in custom node types if dynamic attributes are introduced in the future?

## Change Log

* **2026-10-29:**
  * Initial draft created proposing `DynamicFieldNaming` (`explicit` vs `auto`) and StrawberryConfig integration in `GraphQLBuilder`.
  * Implemented and activated: Added `DynamicFieldNaming` enum, `dynamic_field_naming` parameter in `GraphQLBuilder`, `StrawberryConfig` pass-through in `schema()`, `abuild()`, and `build()`, comprehensive tests, and user documentation.

