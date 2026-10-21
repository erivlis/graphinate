---
title: "GEP-017: Decoupled Server Architecture"
description: "The `graphinate.renderers.graphql.server` function currently constructs the ASGI application and immediately runs it"
icon: lucide/git-branch
status: active
---

# GEP-017: Decoupled Server Architecture

| Field       | Value                         |
|:------------|:------------------------------|
| **GEP**     | 17                            |
| **Title**   | Decoupled Server Architecture |
| **Author**  | Eran Rivlis                   |
| **Delegate**| The Council                   |
| **Status**  | Active                        |
| **Type**    | Standards Track               |
| **Created** | 2025-12-25                    |
| **Updated** | 2026-10-22                    |

## Abstract

The `graphinate.renderers.graphql.server` function currently constructs the ASGI application and immediately runs it
using `uvicorn`. This coupling prevents users from embedding the application in other contexts or testing it easily.
This proposal suggests separating the app creation from the server execution.

## Motivation

**Issues:**

1. **Coupling:** The renderer is tied to `uvicorn`.
2. **Embeddability:** Users cannot mount the Graphinate app inside their own FastAPI or Starlette application.
3. **Testing:** Testing the server logic requires spinning up a full server process or mocking `uvicorn`.

## Rationale

Evaluating against the **Council Framework** ([GEP-001](GEP-001_The_Graphinate_Mission.md)):
- **Symmetry (Noether):** Standard ASGI application factory pattern aligns with the Python web ecosystem (e.g., FastAPI, Starlette).
- **Falsifiability (Popper):** Enables in-process HTTP integration testing via Starlette's `TestClient` without launching real server processes or network sockets.
- **Safety (The Golem):** Decouples application state and configuration from global server lifecycles.
- **Harmony (The Steward):** Preserves `server()` signature, making `create_app()` a purely additive change.

## Specification

Refactor `renderers.graphql` to expose a factory function:

```python
def create_app(
    graphql_schema: strawberry.Schema,
    port: int = DEFAULT_PORT,
    debug: bool = False,
    **kwargs: Any,
) -> Starlette:
    # ... construct and return the app ...
    return app


def server(
    graphql_schema: strawberry.Schema,
    port: int = DEFAULT_PORT,
    debug: bool = False,
    **kwargs: Any,
) -> None:
    app = create_app(graphql_schema, port=port, debug=debug, **kwargs)
    uvicorn.run(app, ...)
```

## Backwards Compatibility

The `server` function signature will remain the same, ensuring backward compatibility. The new `create_app` function
will be an additive change.

## Reference Implementation

- [`src/graphinate/renderers/graphql.py`](file:///C:/dev/erivlis/graphinate/src/graphinate/renderers/graphql.py)
- [`tests/graphinate/renderers/test_graphql_server.py`](file:///C:/dev/erivlis/graphinate/tests/graphinate/renderers/test_graphql_server.py)

## Change Log

- **2025-12-25:** Initial draft.
- **2026-10-17:** Implemented `create_app` in `graphinate.renderers.graphql` and refactored `server()` to delegate to `create_app`. Updated status to `Active`.
