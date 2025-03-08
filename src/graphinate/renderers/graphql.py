import contextlib
import webbrowser

import strawberry
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import RedirectResponse
from starlette.schemas import SchemaGenerator
from starlette.types import ASGIApp
from strawberry.asgi import GraphQL
from strawberry.extensions.tracing import OpenTelemetryExtension

from graphinate.server.starlette import routes

DEFAULT_PORT: int = 8072

GRAPHQL_ROUTE_PATH = "/graphql"


def _openapi_schema(request: Request) -> ASGIApp:
    """
    Generates an OpenAPI schema for the GraphQL API and other routes.

    Args:
        request (Request): The HTTP request object.

    Returns:
        ASGIApp: An OpenAPI response containing the schema for the specified routes.
    """
    schema_data = {
        'openapi': '3.0.0',
        'info': {'title': 'Graphinate API', 'version': '0.6.0'},
        'paths': {
            '/graphql': {'get': {'responses': {200: {'description': 'GraphQL'}}}},
            '/graphiql': {'get': {'responses': {200: {'description': 'GraphiQL UI.'}}}},
            '/metrics': {'get': {'responses': {200: {'description': 'Prometheus metrics.'}}}},
            '/viewer': {'get': {'responses': {200: {'description': '3D Force-Directed Graph Viewer'}}}},
            '/voyager': {'get': {'responses': {200: {'description': 'Voyager GraphQL Schema Viewer'}}}}
        }
    }

    schema = SchemaGenerator(schema_data)
    return schema.OpenAPIResponse(request=request)


def server(graphql_schema: strawberry.Schema, port: int = DEFAULT_PORT, **kwargs):
    """
    Args:
        graphql_schema: The Strawberry GraphQL schema.
        port: The port number to run the server on. Defaults to 8072.

    Returns:
    """
    graphql_schema.extensions.append(OpenTelemetryExtension)

    def open_url():
        for app_name in ('viewer',):
            webbrowser.open(f'http://localhost:{port}/{app_name}')

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):  # pragma: no cover
        if kwargs.get('browse'):
            open_url()
        yield

    graphql_app = GraphQL(graphql_schema, graphiql=True, graphql_ide='pathfinder')
    app = Starlette(
        lifespan=lifespan,
        routes=routes()
    )
    app.add_route(GRAPHQL_ROUTE_PATH, graphql_app)
    app.add_websocket_route(GRAPHQL_ROUTE_PATH, graphql_app)

    from starlette_prometheus import PrometheusMiddleware, metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics)
    app.add_route("/schema", route=_openapi_schema, include_in_schema=False)
    app.add_route("/openapi.json", route=_openapi_schema, include_in_schema=False)

    async def redirect_to_viewer(request):
        return RedirectResponse(url='/viewer')

    app.add_route('/', redirect_to_viewer)

    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
