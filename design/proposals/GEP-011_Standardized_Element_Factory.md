# GEP-011: Standardized Element Factory

| Field       | Value                        |
|:------------|:-----------------------------|
| **GEP**     | 11                           |
| **Title**   | Standardized Element Factory |
| **Author**  | Eran Rivlis                  |
| **Status**  | Draft                        |
| **Type**    | Standards Track              |
| **Created** | 2025-12-25                   |

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
