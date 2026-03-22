# GEP-010: Explicit Dependency Injection

| Field       | Value                         |
|:------------|:------------------------------|
| **GEP**     | 10                            |
| **Title**   | Explicit Dependency Injection |
| **Author**  | Eran Rivlis                   |
| **Status**  | Draft                         |
| **Type**    | Standards Track               |
| **Created** | 2025-12-25                    |
| **Updated** | 2026-03-22                    |

## Abstract

This proposal introduces an explicit mechanism for defining dependencies between graph nodes in `GraphModel`. It aims to
replace the current implicit naming convention (`{node_type}_id`) with a robust system that supports type safety,
flexibility, and clear declaration of intent.

## Motivation

The current implementation of `GraphModel` relies on "magic" to inject parent node IDs into child node generators. A
generator function must name its arguments exactly as `{node_type}_id` to receive the corresponding parent ID.

**Issues with the current approach:**

1. **Brittle:** It relies on exact string matching. A typo in the argument name leads to a runtime error or missing
   data.
2. **Restrictive:** The validation logic forbids *any* argument that does not follow this convention. This prevents
   users from adding configuration arguments (e.g., `limit`, `since_date`) to their generators.
3. **Implicit:** The relationship between the argument and the node type is not visible in the code structure, relying
   entirely on a hidden convention.
4. **Coupled:** It forces the variable name to match the node type, preventing aliasing or conflict resolution.

## Rationale

The **Council Framework** emphasizes **Clarity (Feynman)** and **Safety (The Golem)**. The current "magic" violates
Clarity by hiding the dependency logic and Safety by relying on brittle string matching.

A new solution must:

* Be **Explicit**: The user should declare what they need.
* Be **Flexible**: Allow arbitrary arguments alongside dependencies.
* Be **Pythonic**: Leverage modern Python features like Type Hinting.

## Specification

We propose three potential approaches to solve this problem.

### Option 1: Decorator-based Binding

Introduce a `bindings` or `dependencies` argument to the `@model.node` decorator.

```python
@model.node(
    parent_type='repository',
    bindings={'repo_id': 'repository'}
)
def commit(repo_id):
    ...
```

* **Pros:** Explicit, decouples names from types.
* **Cons:** Verbose, requires repeating information if names match.

### Option 2: Type Hinting (Preferred)

Use Python's type system to declare dependencies.

```python
from typing import Annotated
from graphinate import ParentId


@model.node(parent_type='repository')
def commit(rid: Annotated[str, ParentId('repository')]):
    ...
```

* **Pros:** Self-documenting, leverages IDE support, very Pythonic, allows arbitrary argument names.
* **Cons:** Requires runtime inspection of type hints (reflection).

### Option 3: Context Object

Pass a single context object containing all state.

```python
@model.node(parent_type='repository')
def commit(ctx: GenerationContext):
    repo_id = ctx.parents['repository'].id
    ...
```

* **Pros:** Simple signature, extensible.
* **Cons:** "God object" anti-pattern, less clear what specific data the function needs.

## Architectural Impact & Execution Plan (Option 2)

Implementing the type-hinting approach requires changes across the modeling and execution layers.

### 1. The Semantic Primitive (`graphinate.typing`)
We will introduce `ParentId` as an annotation marker. Using `typing.Annotated` is the modern Pythonic way to attach runtime metadata to type hints without breaking static type checkers.

### 2. The Modeling Layer (`graphinate.modeling`)
*   **Inspection:** The `@model.node` decorator will use `typing.get_type_hints(..., include_extras=True)` to parse the signature of the generator function.
*   **State Restructuring:** The `NodeModel` class will be updated. Instead of storing a simple `parameters: set[str]`, it will store a `dependencies: dict[str, str]` mapping the parameter name to the required parent node type.
*   **Validation:** The draconian `_validate_node_parameters` will be relaxed. It will allow arbitrary arguments, ensuring only that required parent dependencies are satisfied by the declared type hints or the fallback naming convention.

### 3. The Execution Layer (`graphinate.builders.networkx`)
*   The `_populate_nodes` engine loop currently builds the child `kwargs` by strictly appending `{node_type}_id`.
*   It will be updated to consult the `NodeModel.dependencies` map, injecting the parent ID into the exact parameter name requested by the child generator.
*   Arbitrary `**kwargs` passed from the CLI or Server will flow through the generators without triggering validation errors.

## Backwards Compatibility

The current naming convention (`{node_type}_id`) should be preserved as a "default fallback" to maintain backward
compatibility. If a generator argument has no type hint but matches the `_id` suffix rule, it will be treated as an implicit dependency. The new explicit mechanisms will take precedence if present.

## Reference Implementation

(To be determined)

## Copyright

This document has been placed in the public domain.