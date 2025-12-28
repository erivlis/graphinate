# GEP-017: Decoupled Server Architecture

| Field       | Value                         |
|:------------|:------------------------------|
| **GEP**     | 17                            |
| **Title**   | Decoupled Server Architecture |
| **Author**  | Eran Rivlis                   |
| **Status**  | Draft                         |
| **Type**    | Standards Track               |
| **Created** | 2025-12-25                    |

## Abstract

The `graphinate.renderers.graphql.server` function currently constructs the ASGI application and immediately runs it
using `uvicorn`. This coupling prevents users from embedding the application in other contexts or testing it easily.
This proposal suggests separating the app creation from the server execution.

## Motivation

**Issues:**

1. **Coupling:** The renderer is tied to `uvicorn`.
2. **Embeddability:** Users cannot mount the Graphinate app inside their own FastAPI or Starlette application.
3. **Testing:** Testing the server logic requires spinning up a full server process or mocking `uvicorn`.

## Specification

Refactor `renderers.graphql` to expose a factory function:

```python
def create_app(schema: Schema, **kwargs) -> Starlette:
    # ... construct and return the app ...
    return app


def server(schema: Schema, **kwargs):
    app = create_app(schema, **kwargs)
    uvicorn.run(app, ...)
```

## Backwards Compatibility

The `server` function signature will remain the same, ensuring backward compatibility. The new `create_app` function
will be an additive change.
