import webbrowser

import strawberry
import uvicorn
from starlette.applications import Starlette
from strawberry.asgi import GraphQL

from .starlette import routes


def run_graphql(graphql_schema: strawberry.Schema, port: int = 8000):
    def open_url():
        for app_name in ('voyager', 'graphiql', 'viewer'):
            webbrowser.open(f'http://localhost:{port}/{app_name}')

    graphql_app = GraphQL(graphql_schema)
    app = Starlette(
        routes=routes(),
        on_startup=[open_url])
    app.add_route("/graphql", graphql_app)
    app.add_websocket_route("/graphql", graphql_app)

    uvicorn.run(app, host='0.0.0.0', port=port)
