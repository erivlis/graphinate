---
title: "GEP-011: Standardized Element Factory"
description: "Split polymorphic element factory into explicit tuple_element and named_element constructors to improve type stability and clarity."
icon: lucide/git-branch
status: active
---

# GEP-011: Standardized Element Factory

| Field        | Value                        |
|:-------------|:-----------------------------|
| **GEP**      | 11                           |
| **Title**    | Standardized Element Factory |
| **Author**   | Eran Rivlis                  |
| **Delegate** | The Council                  |
| **Status**   | Active                       |
| **Type**     | Standards Track              |
| **Created**  | 2025-12-25                   |
| **Updated**  | 2026-10-22                   |

## Abstract

The legacy `element` factory function exhibited polymorphic return behavior, returning either a `tuple` or a
`namedtuple` class depending on the input arguments. This proposal standardizes element creation by introducing two
explicit factories—`tuple_element()` and `named_element(element_type, field_names)`—while retaining `element()` as a
backwards-compatible dispatcher.

## Motivation

The `element` function in `graphinate.modeling` is designed to create data carriers for graph elements. However, its
behavior was polymorphic:

* If `element_type` and `field_names` were provided, it returned a `namedtuple` class.
* Otherwise, it returned the built-in `tuple` class.

**Issues:**

1. **Type Instability:** Static analysis tools (mypy, PyCharm) could not infer a narrow return type without branching.
2. **Inconsistency:** Callers had to handle two distinct constructor signatures (`tuple(iterable)` vs. `NamedTuple(**kwargs)`).
3. **Magic:** It violated the **Symmetry** and **Clarity** pillars of the Council Framework by hiding two distinct contracts behind a single function name.

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Dedicated factories guarantee symmetric, predictable constructors across node and edge generators.
- **Falsifiability (Popper):** `named_element` eagerly validates identifier names and non-empty field specifications, failing fast with `ValueError`.
- **Efficiency (Shannon):** `named_element` delegates to the `@lru_cache(maxsize=128)` `_get_namedtuple_element_class` cache, avoiding repeated dynamic class creation.
- **Safety (The Golem):** Named factories prevent subtle index misalignment when instantiating raw tuples.
- **Clarity (Feynman):** Provides explicit, readable constructors (`tuple_element` and `named_element`) instead of opaque polymorphic dispatch.
- **Consistency (Russell):** `elements()` uses `named_element` when field getters are supplied and cleanly falls back to `tuple_element` when none are provided.
- **Harmony (The Steward):** Preserves zero-breaking backwards compatibility by keeping `element()` wired to the new factories.

## Specification

### Explicit Factories (Option 1 — Implemented)

Split the factory contract into two explicit functions exported in `graphinate.modeling`:

* `tuple_element() -> type[tuple]`: Returns the built-in `tuple` constructor.
* `named_element(element_type: str, field_names: Iterable[str] | str) -> type[Element]`: Validates that `element_type` is a valid Python identifier and `field_names` is non-empty, then returns a cached `namedtuple` class.

`elements()` in `graphinate.modeling` calls `named_element` when field getters are provided and `tuple_element` otherwise.

## Backwards Compatibility

The existing `element(element_type, field_names)` function is retained and delegates directly to `named_element` when both `element_type` and `field_names` are truthy, or `tuple_element` otherwise.

## How to Teach This / Documentation Plan

- Document `named_element` and `tuple_element` in `docs/advanced/modeling.md` under the **Element Factories** section.
- Export `named_element` and `tuple_element` in `graphinate.modeling.__all__` so API reference pages (`docs/reference/graphinate/modeling.md`) include them automatically.

## Reference Implementation

- Element factories: [`src/graphinate/modeling.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/modeling.py)
- Unit tests: [`tests/graphinate/test_modeling.py`](file:///C:/dev/erivlis/graphinate/tests/graphinate/test_modeling.py)

## Rejected Ideas

- **Option 2 (Unified Return Type with Synthetic Field Names):** Always returning a `namedtuple` with synthetic field names (e.g., `Element(field_0=...)`) when `field_names` is empty was rejected because `namedtuple` requires at least one field name to instantiate keyword arguments, adding unnecessary overhead when an empty tuple is requested.
- **Hard Removal of `element()`:** Immediately removing `element()` was rejected to avoid breaking external callers or existing tests that import `element` directly.

## Open Questions

- [x] Should `element()` remain available for backwards compatibility? *Decision: Yes, `element()` delegates to `named_element()` and `tuple_element()`.*

## Change Log

* **2025-12-25:** Initial draft.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment. Implemented `tuple_element` and `named_element` in `src/graphinate/modeling.py` and transitioned status to `Active`.

