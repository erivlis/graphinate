# Graphinate Renderers Grading

This document evaluates the `graphinate.renderers` namespace against the **Council Framework** values.

## 1. `renderers.graphql`

*   **Symmetry (Noether):** 3/5.
    *   It hardcodes `Starlette` and `Uvicorn` as the serving infrastructure. While pragmatic, it couples the renderer to a specific server implementation.
*   **Clarity (Feynman):** 4/5.
    *   The separation between `_graphql_app`, `_starlette_app`, and `server` is clear.
    *   The `lifespan` context manager for opening the browser is a nice convenience.
*   **Safety (The Golem):** 3/5.
    *   **Hardcoded Paths:** Routes like `/viewer`, `/voyager` are hardcoded in the OpenAPI schema but not all are explicitly defined in the `routes()` call (which we haven't seen fully, but `_starlette_app` adds some).
    *   **Global State:** `uvicorn.run` blocks the thread.
*   **Verdict:** **B**. A solid integration module, but slightly coupled.

## Overall Assessment

The renderers namespace acts as the "glue" between the builders and the runtime environment (web server). It's functional but could benefit from more flexibility (e.g., returning the ASGI app instead of running it directly).

## Recommendations

1.  **Decouple Server:** Allow `server` to return the `Starlette` app instance so it can be mounted in other applications or tested without starting a server.
