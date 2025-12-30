# Graphinate Renderers Analysis

## Overview
The `graphinate.renderers` namespace handles the execution and serving of the graph representations. Currently, it focuses on GraphQL serving.

## Modules

### 1. `renderers.graphql`
- **Role**: Sets up and runs the GraphQL server.
- **Key Logic**:
    - **OpenAPI**: Generates an OpenAPI schema for the API (`_openapi_schema`).
    - **GraphQL App**: Creates a `strawberry.asgi.GraphQL` app (`_graphql_app`).
    - **Starlette App**: Assembles the full web application (`_starlette_app`):
        - Mounts the GraphQL app.
        - Adds Prometheus metrics middleware.
        - Sets up a redirect from root `/` to `/viewer`.
        - Configures a `lifespan` to open the browser automatically if requested.
    - **Server**: `server` function orchestrates the setup and runs `uvicorn`.

## Dependencies
- `strawberry`: For GraphQL schema and ASGI app.
- `starlette`: For the web framework.
- `uvicorn`: For the ASGI server.
- `starlette_prometheus`: For metrics.
