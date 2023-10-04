import contextlib
import webbrowser

import strawberry
from starlette.applications import Starlette
from strawberry.asgi import GraphQL
from strawberry.extensions.tracing import OpenTelemetryExtension

from .starlette import routes

DEFAULT_PORT: int = 8072


def graphql(graphql_schema: strawberry.Schema, port: int = DEFAULT_PORT):
    """

    Args:
        graphql_schema:
        port:

    Returns:

    """
    graphql_schema.extensions.append(OpenTelemetryExtension)

    @contextlib.asynccontextmanager
    async def lifespan(app: Starlette):  # pragma: no cover
        def open_url():
            for app_name in ('voyager', 'graphiql', 'viewer'):
                webbrowser.open(f'http://localhost:{port}/{app_name}')

        open_url()
        yield

    graphql_app: GraphQL = GraphQL(graphql_schema)
    app = Starlette(
        lifespan=lifespan,
        routes=routes()
    )
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    from starlette_prometheus import PrometheusMiddleware, metrics
    app.add_middleware(PrometheusMiddleware)
    app.add_route("/metrics", metrics)

    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=port)
