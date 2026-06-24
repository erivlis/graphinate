# GEP-010: Explicit Dependency Injection

| Field       | Value                         |
|:------------|:------------------------------|
| **GEP**     | 10                            |
| **Title**   | Explicit Dependency Injection |
| **Author**  | Eran Rivlis                   |
| **Status**  | Accepted                      |
| **Type**    | Standards Track               |
| **Created** | 2025-12-25                    |
| **Updated** | 2026-06-21                    |

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

# Also supports Enums/StrEnums directly:
class NodeTypes(Enum):
    REPOSITORY = 'repository'

@model.node(parent_type=NodeTypes.REPOSITORY)
def commit(rid: Annotated[str, ParentId(NodeTypes.REPOSITORY)]):
    ...
```

* **Pros:** Self-documenting, leverages IDE support, very Pythonic, allows arbitrary argument names, and accepts enums/StrEnums directly (by resolving their `.value` strings at runtime) to prevent typo-based bugs.
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

We will introduce `ParentId` as an annotation marker. Using `typing.Annotated` is the modern Pythonic way to attach
runtime metadata to type hints without breaking static type checkers.

### 2. The Modeling Layer (`graphinate.modeling`)

* **Inspection:** The `@model.node` decorator will use `typing.get_type_hints(..., include_extras=True)` to parse the
  signature of the generator function.
* **State Restructuring:** The `NodeModel` class will be updated. Instead of storing a simple `parameters: set[str]`, it
  will store a `dependencies: dict[str, str]` mapping the parameter name to the required parent node type.
* **Validation:** The draconian `_validate_node_parameters` will be relaxed. It will allow arbitrary arguments, ensuring
  only that required parent dependencies are satisfied by the declared type hints or the fallback naming convention.

### 3. The Execution Layer (`graphinate.builders.networkx`)

* The `_populate_nodes` engine loop currently builds the child `kwargs` by strictly appending `{node_type}_id`.
* It will be updated to consult the `NodeModel.dependencies` map, injecting the parent ID into the exact parameter name
  requested by the child generator.
* Arbitrary `**kwargs` passed from the CLI or Server will flow through the generators without triggering validation
  errors.

## Backwards Compatibility

The current naming convention (`{node_type}_id`) should be preserved as a "default fallback" to maintain backward
compatibility. If a generator argument has no type hint but matches the `_id` suffix rule, it will be treated as an
implicit dependency. The new explicit mechanisms will take precedence if present.

## Reference Implementation

Exposed via `ParentId` annotation primitive in [typing.py](file:///C:/dev/erivlis/graphinate/src/graphinate/typing.py)
and resolved within [modeling.py](file:///C:/dev/erivlis/graphinate/src/graphinate/modeling.py).

## Change Log

* 2025-12-25: Initial Draft
* 2026-06-21: Accepted Option 2 (Type Hinting) and implemented the injection engine.
* 2026-06-22: Documented remaining structural and validation constraints as open issues/future work.

## Open Issues & Future Work

During the design review of the GEP-010 implementation, the Council of Principles identified the following remaining issues and areas for future work:

1. **Eager Registration Validation:** Parameter validation (`_validate_node_dependency_registration`) currently runs eagerly at decorator execution time. This creates a strict topological import/decoration order constraint and prevents modular model composition (e.g., merging `ModelA + ModelB` where cross-dependencies are resolved only after composition). Future work will explore deferring validation to graph build time.
2. **In-place Model Mutation (`rectify`):** The builder mutates the shared `GraphModel` instance in-place during the build phase via `rectify()`. This represents a potential concurrency side-effect. Future updates should clone the model or perform mutations on localized registries.
3. **Recursive Lineage Namespace Collision:** In recursive structures (e.g., `folder -> folder`), overwriting the `folder_id` key in `kwargs` destroys the parent lineage chain, which causes parent ID resolution to fail when nodes are registered with `unique=False`. Passing an explicit lineage tuple during traversal will solve this collision.
4. **Lineage Casing Asymmetry:** While injection lookup is case-insensitive, the early-break check in `_parent_node_id` remains case-sensitive, creating potential lineage pollution for mixed-case types.
5. **Dead Code Cleanup (`NodeModel.parameters`):** The `parameters` attribute on `NodeModel` is currently obsolete and should be cleaned up.

## Copyright

This document has been placed in the public domain.