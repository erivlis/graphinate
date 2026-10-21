---
title: "GEP-011: Standardized Element Factory"
description: "The current `element` factory function exhibits polymorphic return behavior, returning either a `tuple` or a"
icon: lucide/git-branch
status: draft
---

# GEP-011: Standardized Element Factory

| Field       | Value                        |
|:------------|:-----------------------------|
| **GEP**     | 11                           |
| **Title**   | Standardized Element Factory |
| **Author**  | Eran Rivlis                  |
| **Delegate**| The Council                   |
| **Status**  | Draft                        |
| **Type**    | Standards Track              |
| **Created** | 2025-12-25                   |
| **Updated** | 2026-10-22                    |

## Abstract

The current `element` factory function exhibits polymorphic return behavior, returning either a `tuple` or a
`namedtuple` class depending on the input arguments. This proposal aims to standardize the return type to improve type
safety, clarity, and IDE support.

## Motivation

The `element` function in `graphinate.modeling` is designed to create data carriers for graph elements. However, its
behavior is "magical":

* If `element_type` and `field_names` are provided, it returns a `namedtuple` class.
* Otherwise, it returns the built-in `tuple` class.

**Issues:**

1. **Type Instability:** Static analysis tools (mypy, PyCharm) cannot easily infer the return type.
2. **Inconsistency:** Users must handle two distinct interface types (indexed access vs. attribute access) depending on
   how the factory was called.
3. **Magic:** It violates the **Symmetry** and **Clarity** pillars of the Council Framework by hiding complexity behind
   a single function name.

## Specification

### Option 1: Split Factories (Preferred)

Split the function into two explicit factories:

* `tuple_element()` -> Returns `tuple`
* `named_element(name, fields)` -> Returns `namedtuple`

### Option 2: Unified Return Type

Always return a `namedtuple`. If fields are missing, use a default schema (e.g., `Element(data=...)`) or generate
generic field names.

## Backwards Compatibility

The existing `element` function can be deprecated and aliased to the new implementations for a transition period.
## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Standard tuple factory guarantees symmetric handling of source/target/type/attributes across all node and edge generators.
- **Safety (The Golem):** Named factories prevent subtle index misalignment when instantiating raw tuples.
- **Clarity (Feynman):** Provides explicit, readable constructors instead of opaque magic tuples.

## Reference Implementation

- Modeling factory: `src/graphinate/modeling.py`

## Change Log

* **2025-12-25:** Initial draft.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
