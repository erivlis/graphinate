import contextlib
import webbrowser
from typing import Any

import strawberry
from loguru import logger
from starlette.applications import Starlette
from starlette.datastructures import State
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response
from starlette.routing import Route, WebSocketRoute
from starlette.schemas import SchemaGenerator
from strawberry.asgi import GraphQL

from graphinate.server.starlette import routes

DEFAULT_PORT: int = 8072

GRAPHQL_ROUTE_PATH = "/graphql"


def _openapi_schema(request: Request[State]) -> Response:
    """
    Generates an OpenAPI schema for the GraphQL API and other routes.

    Args:
        request (Request): The HTTP request object.

    Returns:
        ASGIApp: An OpenAPI response containing the schema for the specified routes.
    """
    schema_data = {
        'openapi': '3.0.0',
        'info': {'title': 'Graphinate API', 'version': '0.10.1'},
        'paths': {
            '/graphql': {'get': {'responses': {200: {'description': 'GraphQL'}}}},
            '/graphiql': {'get': {'responses': {200: {'description': 'GraphiQL UI.'}}}},
            '/metrics': {'get': {'responses': {200: {'description': 'Prometheus metrics.'}}}},
            '/viewer': {'get': {'responses': {200: {'description': '3D Force-Directed Graph Viewer'}}}},
            '/voyager': {'get': {'responses': {200: {'description': 'Voyager GraphQL Schema Viewer'}}}}
        }
    }

    schema = SchemaGenerator(schema_data)
    response = schema.OpenAPIResponse(request=request)
    return response


def _graphql_app(graphql_schema: strawberry.Schema) -> GraphQL:
    """
    Creates a Strawberry GraphQL app with the provided schema.
    Args:
        graphql_schema:

    Returns:
        strawberry.asgi.GraphQL: The GraphQL app configured with the provided schema.
    """
    graphql_app: GraphQL = GraphQL(graphql_schema, graphql_ide='apollo-sandbox')
    return graphql_app


def _starlette_app(graphql_app: strawberry.asgi.GraphQL | None = None,
                   port: int = DEFAULT_PORT,
                   **kwargs: Any) -> Starlette:
    def open_url(endpoint):
        webbrowser.open(f'http://localhost:{port}/{endpoint}')

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):  # pragma: no cover
        if app.debug:
            logger.debug("Starting Starlette lifespan.")
        if kwargs.get('browse'):
            open_url('viewer')
        yield

    app_routes: list = [*routes()]

    def redirect_to_viewer(request: Request[State]) -> RedirectResponse:
        return RedirectResponse(url='/viewer')

    app_routes.append(Route(path='/', endpoint=redirect_to_viewer))

    if graphql_app:
        app_routes.extend([
            Route(path=GRAPHQL_ROUTE_PATH, endpoint=graphql_app),
            WebSocketRoute(path=GRAPHQL_ROUTE_PATH, endpoint=graphql_app),
            Route(path='/schema', endpoint=_openapi_schema, include_in_schema=False),
            Route(path='/openapi.json', endpoint=_openapi_schema, include_in_schema=False)
        ])

    app = Starlette(
        lifespan=lifespan,
        routes=app_routes
    )

    from starlette_prometheus import PrometheusMiddleware, metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics)

    return app


def server(graphql_schema: strawberry.Schema, port: int = DEFAULT_PORT, **kwargs: Any):
    """
    Args:
        graphql_schema: The Strawberry GraphQL schema.
        port: The port number to run the server on. Defaults to 8072.

    Returns:
    """

    graphql_app = _graphql_app(graphql_schema)

    app = _starlette_app(graphql_app, port=port, **kwargs)

    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)


__all__ = ['server']
