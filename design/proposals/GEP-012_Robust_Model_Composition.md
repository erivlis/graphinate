# GEP-012: Robust Model Composition

| Field       | Value                    |
|:------------|:-------------------------|
| **GEP**     | 12                       |
| **Title**   | Robust Model Composition |
| **Author**  | Eran Rivlis              |
| **Status**  | Draft                    |
| **Type**    | Standards Track          |
| **Created** | 2025-12-25               |

## Abstract

The `GraphModel` class supports composition via the `__add__` operator. Currently, this operation blindly merges
internal lists of node models and edge generators. This proposal seeks to define explicit conflict resolution strategies
to handle overlapping definitions safely.

## Motivation

When combining two `GraphModel` instances (e.g., `model_a + model_b`), it is possible that both models define the same
Node Type (e.g., 'User').

**Current Behavior:**
The lists of generators are concatenated. This results in multiple `NodeModel` instances for the same type ID.

**Issues:**

1. **Ambiguity:** Which definition is the "source of truth" for properties like `label` or `uniqueness`?
2. **Redundancy:** Generators might be duplicated.
3. **Unpredictability:** The behavior depends on the order of addition and implementation details of the builder.

## Specification

Define a `CompositionStrategy` enum and allow `__add__` (or a new `merge` method) to accept it.

### Strategies

1. **APPEND (Current):** Keep all definitions.
2. **OVERRIDE:** The right-hand operand overwrites the left-hand operand for matching types.
3. **MERGE:** Attempt to merge properties (e.g., union of parameters).
4. **FAIL:** Raise an error if duplicates are found.

## Backwards Compatibility

The default behavior should remain `APPEND` to preserve existing functionality, but a warning could be issued if
conflicts are detected.
