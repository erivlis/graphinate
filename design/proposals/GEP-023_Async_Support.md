# GEP-023: Async Support

| Field       | Value           |
|:------------|:----------------|
| **GEP**     | 23              |
| **Title**   | Async Support   |
| **Author**  | Eran Rivlis     |
| **Status**  | Draft           |
| **Type**    | Standards Track |
| **Created** | 2025-12-25      |
| **Updated** | 2025-12-28      |

## Abstract

This proposal advocates for adding support for asynchronous generators (`async def`) in `GraphModel`. This will allow
users to define graph generators that perform non-blocking I/O operations (e.g., fetching data from APIs or databases),
significantly improving performance for I/O-bound workloads.

## Motivation

**Current Limitation:**
Graphinate currently assumes all generators are synchronous. When building a graph from a slow API (like GitHub), the
builder blocks on every request.

**Benefit of Async:**
By supporting `async` generators, the builder can potentially fetch data concurrently (if architected correctly) or at
least not block the main thread, enabling better integration with async web frameworks (FastAPI/Starlette).

## Specification

> **Note:** The implementation of this feature should leverage the **Graph Engine** architecture defined in **GEP-024**.

### 1. Model Detection

The `GraphModel` must detect if a registered generator is asynchronous using `inspect.isasyncgenfunction`.

### 2. Builder Update

The `NetworkxBuilder` (and subclasses) needs an asynchronous build method.

```python
class NetworkxBuilder:
    async def abuild(self, **kwargs) -> nx.Graph:
        # ...
        if inspect.isasyncgenfunction(generator):
            async for item in generator(**kwargs):
        # ... process item
        else:
            for item in generator(**kwargs):
        # ... process item
```

### 3. Concurrency (Future)

Initially, `abuild` might just `await` each generator sequentially. A future optimization could use `asyncio.gather` to
process independent branches of the hierarchy in parallel.

## Backwards Compatibility

* **Sync API:** The existing `build()` method must remain synchronous. It can either:
    * Raise an error if the model contains async generators.
    * Use `asyncio.run()` to execute the async build (if not already in a loop).
* **Async API:** The new `abuild()` method provides the async interface.

## Change Log

* 2025-12-25: Initial Draft
* 2025-12-28: Updated to reference GEP-024
