# GEP-013: Stable ID Serialization

| Field       | Value                   |
|:------------|:------------------------|
| **GEP**     | 13                      |
| **Title**   | Stable ID Serialization |
| **Author**  | Eran Rivlis             |
| **Status**  | Withdrawn               |
| **Type**    | Standards Track         |
| **Created** | 2025-12-25              |
| **Updated** | 2025-12-29              |

## Abstract

The current ID encoding mechanism in `graphinate.converters` relies on Python's `repr()` combined with Base64 encoding
and `ast.literal_eval()` for decoding. This proposal advocated for replacing it with a deterministic, JSON-based
serialization strategy.

## Status: Withdrawn

This proposal has been withdrawn. The complexity of handling Python's rich type system (tuples, sets, custom objects) in
JSON outweighs the benefits of "purity". The original `repr()` implementation, while having theoretical downsides (
stability, security), is practically robust for the project's current needs and handles type round-tripping natively.

## Motivation (Original)

Graphinate uses encoded IDs to represent nodes and edges in external systems (like GraphQL). These IDs must be:

1. **Stable:** The same object should always produce the same ID.
2. **Reversible:** We must be able to reconstruct the object from the ID.
3. **Safe:** Decoding should not execute arbitrary code or be vulnerable to DoS.

**Issues with the current approach (`repr` + `ast.literal_eval`):**

1. **Instability:** `repr()` is not guaranteed to be deterministic. For objects without a custom `__repr__`, it includes
   the memory address (e.g., `<MyObj at 0x123>`), which changes every run. Even for standard types, dictionary order was
   not guaranteed before Python 3.7.
2. **Safety:** While `ast.literal_eval` is safer than `eval`, it can still be exploited for Denial of Service (DoS) via
   deeply nested structures (stack overflow) or excessive memory consumption.
3. **Opacity:** The resulting Base64 string is opaque and hard to debug.

## Specification (Original)

We propose switching to a **Canonical JSON** serialization format.

### Encoding Strategy

1. **Format:** JSON.
2. **Determinism:**
    * Dictionaries must be sorted by key (`sort_keys=True`).
    * Separators should be compact (`(',', ':')`).
3. **Type Handling:**
    * Since JSON only supports strings, numbers, bools, lists, and dicts, we need a protocol for other Python types (
      tuples, sets, custom objects).
    * **Tuples:** Encode as lists with a type tag or infer based on context (if schema is known).
    * **Custom Objects:** Require a `to_json` / `from_json` protocol or registration mechanism.

### Proposed Implementation

```python
import json


def stable_encode(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), default=custom_encoder)


def custom_encoder(obj):
    if isinstance(obj, tuple):
        return {'__type__': 'tuple', 'items': list(obj)}
    if isinstance(obj, set):
        return {'__type__': 'set', 'items': sorted(list(obj))}
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")
```

## Backwards Compatibility

This is a breaking change. IDs generated with the old method will not be decodable by the new method.

* **Migration:** A version flag in the ID (e.g., prefixing with `v1:`) could allow supporting both during a transition
  period.
* **Cutover:** Alternatively, since IDs are often transient in session-based graphs, a hard cutover might be acceptable
  for a major version bump.

## Reference Implementation

(Withdrawn)
