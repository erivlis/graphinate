---
title: "GEP-023: Async Support"
description: "Support asynchronous generators (async def) in GraphModel, GraphEngine.arun(), and Builder.abuild() for non-blocking I/O workloads."
icon: lucide/git-branch
status: active
---

# GEP-023: Async Support

| Field        | Value           |
|:-------------|:----------------|
| **GEP**      | 23              |
| **Title**    | Async Support   |
| **Author**   | Eran Rivlis     |
| **Delegate** | The Council     |
| **Status**   | Active          |
| **Type**     | Standards Track |
| **Created**  | 2025-12-25      |
| **Updated**  | 2026-10-23      |

## Abstract

This proposal adds native support for asynchronous generators (`async def ... yield`) and coroutine suppliers (`async def ... return`) in `GraphModel`, paired with `await engine.arun(...)` in `GraphEngine` and `await builder.abuild(...)` across all builders (`NetworkxBuilder`, `D3Builder`, `MermaidBuilder`, and `GraphQLBuilder`).

## Motivation

**Previous Limitation:**
Graphinate previously assumed all node and edge generators were synchronous iterables. When building a graph from I/O-bound sources (such as REST/GraphQL APIs, async database drivers, or filesystem crawlers), generators blocked the calling thread or could not be awaited inside running event loops (such as Starlette/FastAPI servers).

**Benefits of Async Support:**
- Native integration with async Python libraries (`httpx`, `aiohttp`, `asyncpg`) inside `@model.node` and `@model.edge`.
- Seamless mixed models combining synchronous in-memory generators and asynchronous I/O generators.
- First-class `await builder.abuild()` and `await graphinate.abuild(...)` entry points that run directly inside existing event loops.

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Symmetric `run()` / `arun()` methods on `GraphEngine`, `build()` / `abuild()` on `Builder` subclasses, and `elements()` / `aelements()` in `graphinate.modeling`.
- **Falsifiability (Popper):** Calling synchronous `run()` or `build()` on a model containing an async generator fails fast with an explicit, actionable `GraphModelError`.
- **Efficiency (Shannon):** Unlocks non-blocking I/O for API crawlers and streaming ingestion without intermediate thread-pool overhead.
- **Safety (The Golem):** Preserves the synchronous `build()` execution path with zero overhead or regressions for synchronous models.
- **Clarity (Feynman):** Users write standard `async def` functions with `@model.node` and `@model.edge` without special decorator flags.
- **Consistency (Russell):** Identical `ParentId` dependency injection, `_lineage` propagation, and `NodeEvent`/`EdgeEvent` emission across sync and async execution.
- **Harmony (The Steward):** Completes the Core Structural Spine (`GEP-010` → `GEP-032` → `GEP-012` → `GEP-024` → `GEP-023`).

## Specification

### 1. Async Element Supplier (`graphinate.modeling`)

- `aelements(iterable, element_type=None, **getters)` accepts either an `AsyncIterable` or a synchronous `Iterable` and yields `Element` instances asynchronously.
- `@model.node` and `@model.edge` inspect the decorated callable via `inspect.isasyncgenfunction` and `inspect.iscoroutinefunction`. When true, they wrap the callable in an async generator delegating to `aelements`.

### 2. Async Engine Execution (`graphinate.engine`)

- `GraphEngine.arun(**kwargs)` asynchronously traverses all registered node and edge generators, supporting both `AsyncIterable` and synchronous `Iterable` generators within the same model.
- If `GraphEngine.run(**kwargs)` encounters an `AsyncIterable` or awaitable generator, it raises `GraphModelError` directing the caller to `await engine.arun(...)` or `await builder.abuild(...)`.

### 3. Builder Async Facade (`graphinate.builders`)

- `Builder.abuild(**kwargs)` is implemented across `NetworkxBuilder`, `D3Builder`, `MermaidBuilder`, and `GraphQLBuilder`.
- Top-level `await graphinate.abuild(builder_cls, graph_model, ...)` mirrors `graphinate.build(...)`.

## Backwards Compatibility

- **Sync API:** `build()` and `GraphEngine.run()` remain 100% synchronous and unchanged for synchronous models.
- **Async API:** `abuild()` and `GraphEngine.arun()` execute both asynchronous and synchronous generators seamlessly.

## How to Teach This / Documentation Plan

- Documented asynchronous generators, `engine.arun()`, and `abuild()` in [`docs/advanced/engine.md`](docs/advanced/engine.md#L65-L85).
- Exported `abuild` in `graphinate` and `graphinate.builders`, and `aelements` in `graphinate.modeling`.

## Reference Implementation

- Async element stream & decorator detection: [`src/graphinate/modeling.py`](src/graphinate/modeling.py)
- Async engine execution: [`src/graphinate/engine/core.py`](src/graphinate/engine/core.py)
- Builder async methods: [`src/graphinate/builders/`](src/graphinate/builders/__init__.py)
- Unit tests: [`tests/graphinate/test_engine.py`](tests/graphinate/test_engine.py)

## Rejected Ideas

- **Separate `@model.anode` and `@model.aedge` Decorators:** Rejected because `inspect.isasyncgenfunction` / `inspect.iscoroutinefunction` detects async callables automatically without duplicating the decorator API surface.
- **Implicit `asyncio.run()` Inside Sync `build()`:** Rejected because calling `asyncio.run()` fails with `RuntimeError` when invoked from within an already-running event loop (e.g. FastAPI/Starlette/Jupyter). Raising an explicit `GraphModelError` and providing `await abuild()` is safer and more predictable.

## Open Questions

- [x] Should `arun()` and `abuild()` support hybrid models containing both `def` and `async def` generators? *Decision: Yes, `arun()` seamlessly iterates both synchronous and asynchronous generators.*

## Change Log

* **2025-12-25:** Initial draft.
* **2025-12-28:** Updated to reference GEP-024.
* **2026-10-22:** Rebased into GEP standard with frontmatter and Council alignment.
* **2026-10-23:** Implemented `aelements`, `GraphEngine.arun()`, and `abuild()` across all builders, and transitioned status to `Active`.

