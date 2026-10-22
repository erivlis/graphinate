---
title: "GEP-012: Robust Model Composition"
description: "Explicit conflict resolution strategies (APPEND, OVERRIDE, MERGE, FAIL) when composing GraphModel instances via GraphModel.merge()."
icon: lucide/git-branch
status: active
---

# GEP-012: Robust Model Composition

| Field        | Value                    |
|:-------------|:-------------------------|
| **GEP**      | 12                       |
| **Title**    | Robust Model Composition |
| **Author**   | Eran Rivlis              |
| **Delegate** | The Council              |
| **Status**   | Active                   |
| **Type**     | Standards Track          |
| **Created**  | 2025-12-25               |
| **Updated**  | 2026-10-22               |

## Abstract

The `GraphModel` class supports composition via the `__add__` operator (`model_a + model_b`), which concatenates internal lists of node models and edge generators. This proposal introduces the `CompositionStrategy` enum (`APPEND`, `OVERRIDE`, `MERGE`, `FAIL`) and the explicit `GraphModel.merge(other, strategy=..., name=...)` method to handle overlapping definitions deterministically and safely.

## Motivation

When combining two `GraphModel` instances (e.g., `model_a + model_b`), both models may define the same Node Type `(parent_type, type)` or Edge Type.

**Previous Behavior:**
The lists of generators were always concatenated.

**Issues:**

1. **Ambiguity:** When overriding a base model in tests or specialized pipelines, users could not replace a node definition without mutating private `_node_models` state.
2. **Redundancy:** Composing diamond-dependency sub-models could duplicate identical generator functions.
3. **Lack of Strictness:** In modular architectures where sub-models must own disjoint domains, silent collisions could go unnoticed.

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Model addition (`ModelA + ModelB`) acts as a categorical pushout over shared node types, with `merge()` parameterizing the universal resolution rule.
- **Falsifiability (Popper):** `CompositionStrategy.FAIL` turns silent type collisions into immediate, testable `GraphModelError` exceptions.
- **Efficiency (Shannon):** `CompositionStrategy.MERGE` deduplicates identical node and edge generator functions when composing shared sub-models.
- **Safety (The Golem):** Always returns a new `GraphModel` instance without mutating either input operand.
- **Clarity (Feynman):** `model_a.merge(model_b, strategy=CompositionStrategy.OVERRIDE)` expresses intent clearly at the call site.
- **Consistency (Russell):** Resolves naming collisions deterministically across `_node_models`, `_node_children`, and `_edge_generators`.
- **Harmony (The Steward):** Preserves `model_a + model_b` as an ergonomic shorthand for `CompositionStrategy.APPEND`.

## Specification

### 1. `CompositionStrategy` Enum (`graphinate.enums`)

```python
class CompositionStrategy(Enum):
    APPEND = auto()
    OVERRIDE = auto()
    MERGE = auto()
    FAIL = auto()
```

Exported at the top-level `graphinate` package (`from graphinate import CompositionStrategy`).

### 2. `GraphModel.merge()` (`graphinate.modeling`)

```python
def merge(
    self,
    other: 'GraphModel',
    strategy: CompositionStrategy = CompositionStrategy.APPEND,
    name: str | None = None,
) -> 'GraphModel':
```

* **`APPEND` (Default & `__add__`):** Concatenates all `NodeModel` entries and edge generators from `self` and `other`.
* **`OVERRIDE`:** Right-hand operand (`other`) replaces left-hand definitions for matching `(parent_type, type)` node keys and edge types, rebuilding `_node_children` consistently.
* **`MERGE`:** Retains distinct generators from both models (deduplicating identical generator references) while updating matching `NodeModel` metadata (`label`, `uniqueness`, `multiplicity`) from the right-hand operand and taking the union of `dependencies`.
* **`FAIL`:** Raises `GraphModelError` if any `(parent_type, type)` key in `_node_models` or edge type in `_edge_generators` exists in both `self` and `other`.

## Backwards Compatibility

`model_a + model_b` delegates to `model_a.merge(model_b, strategy=CompositionStrategy.APPEND)`, preserving 100% backwards compatibility with existing code.

## How to Teach This / Documentation Plan

- Document `CompositionStrategy` and `GraphModel.merge()` in `docs/advanced/modeling.md` under **Model Composition**.
- Export `CompositionStrategy` in `graphinate.__init__`.

## Reference Implementation

- Enum definition: [`src/graphinate/enums.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/enums.py)
- Composition implementation: [`src/graphinate/modeling.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/modeling.py)
- Unit tests: [`tests/graphinate/test_modeling.py`](file:///C:/dev/erivlis/graphinate/tests/graphinate/test_modeling.py)

## Rejected Ideas

- **Mutating `self` In-Place:** Rejected because mutating an existing `GraphModel` violates immutability expectations when sub-models are reused across multiple pipelines.
- **Changing `__add__` Default to `FAIL` or `OVERRIDE`:** Rejected because multiple generators for the same `(parent_type, type)` are a core feature of Graphinate (e.g., populating the same node type from multiple data sources).

## Open Questions

- [x] Should `CompositionStrategy` be exported at the root `graphinate` namespace? *Decision: Yes, alongside `GraphType` and `Multiplicity`.*

## Change Log

* **2025-12-25:** Initial draft.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment. Implemented `CompositionStrategy` and `GraphModel.merge()` and transitioned status to `Active`.

