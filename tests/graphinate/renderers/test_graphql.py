from collections.abc import Generator
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import strawberry
from starlette.requests import Request
from starlette.testclient import TestClient

from graphinate.renderers import graphql
from graphinate.renderers.graphql import (
    GRAPHQL_ROUTE_PATH,
    _graphql_app,
    _openapi_schema,
    _starlette_app,
)

# region --- Helper Classes ---


@strawberry.type
class Query:
    """A simple GraphQL Query type for testing purposes."""

    @strawberry.field
    def hello(self) -> str:
        """A simple test field."""
        return "world"


# Create a fake schema for testing
FAKE_SCHEMA = strawberry.Schema(query=Query)


class ReceiveStub:
    """A ASGI receive callable that does nothing."""

    async def __call__(self):
        return {}


class SendStub:
    """A ASGI send callable that does nothing."""

    async def __call__(self, message):
        pass


class RequestStub(Request):
    """A Starlette Request object for testing purposes."""

    def __init__(self, method="GET", path="/openapi.json", query_string=b""):
        scope = {
            "type": "http",
            "asgi.version": "3.0",
            "asgi.spec_version": "2.1",
            "method": method,
            "path": path,
            "raw_path": path.encode(),
            "query_string": query_string,
            "headers": [],
            "client": ("testclient", 1234),
            "server": ("testserver", 80),
            "scheme": "http",
            "root_path": "",
            "app": None,
        }
        super().__init__(scope, ReceiveStub())


# endregion --- Helper Classes ---

# region --- Pytest Fixtures ---

@pytest.fixture
def client() -> Generator[TestClient, Any, None]:
    """
    Pytest fixture that creates a TestClient for the full Starlette app
    with a dummy GraphQL schema.
    """
    # Arrange
    graphql_app = _graphql_app(FAKE_SCHEMA)
    app = _starlette_app(graphql_app)
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def fake_schema():
    return FAKE_SCHEMA


@pytest.fixture
def request_stub():
    return RequestStub()


# endregion --- Pytest Fixtures ---

# region --- Test Cases ---

def test_graphql_query_success(client: TestClient):
    """
    Tests a successful GraphQL query to the /graphql endpoint.
    """
    # Arrange
    query = {"query": "query TestHello { hello }"}

    # Act
    response = client.post(GRAPHQL_ROUTE_PATH, json=query)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"data": {"hello": "world"}}


def test_graphql_query_error_gracefully(client: TestClient):
    """
    Tests that an invalid GraphQL query is handled gracefully.
    """
    # Arrange
    query = {"query": "{ nonExistentField }"}

    # Act
    response = client.post(GRAPHQL_ROUTE_PATH, json=query)

    # Assert
    # The server should return 200 OK, but the body will contain an 'errors' key.
    assert response.status_code == 200
    response_data = response.json()
    assert "data" in response_data
    assert response_data["data"] is None
    assert "errors" in response_data
    assert len(response_data["errors"]) > 0
    assert "nonExistentField" in response_data["errors"][0]["message"]


def test_metrics_endpoint(client: TestClient):
    """
    Tests that the /metrics endpoint is available and serves Prometheus metrics.
    """
    # Arrange (client is provided by the fixture)

    # Act
    response = client.get("/metrics")

    # Assert
    assert response.status_code == 200
    # Check for a known metric provided by starlette-prometheus
    assert "starlette_requests_total" in response.text


@patch("graphinate.renderers.graphql.webbrowser.open")
def test_browse_flag_opens_browser(mock_webbrowser_open: MagicMock):
    """
    Ensures the browser is opened on startup when the 'browse' kwarg is True.
    """
    # Arrange
    # The lifespan event that opens the browser is triggered when the TestClient
    # is used as a context manager.
    app = _starlette_app(port=1234, browse=True)

    # Act
    with TestClient(app):
        pass  # Startup runs, then shutdown

    # Assert
    mock_webbrowser_open.assert_called_once_with('http://localhost:1234/viewer')


def test_schema_generator_or_response_error_handling(monkeypatch, request_stub):
    from graphinate.renderers import graphql as graphql_mod

    # mock strawberry-graphql schema module
    class FailingSchemaGenerator:
        def __init__(self, data):
            pass

        def OpenAPIResponse(self, request):  # noqa: N802
            raise RuntimeError("Schema generation failed")

    monkeypatch.setattr(graphql_mod, "SchemaGenerator", FailingSchemaGenerator)
    with pytest.raises(RuntimeError):
        _openapi_schema(request_stub)


def test_server_missing_required_arguments():
    # server requires at least graphql_schema
    with pytest.raises(TypeError):
        graphql.server()


def test_server_uvicorn_import_or_runtime_error(mocker, fake_schema):
    mocker.patch("graphinate.renderers.graphql._graphql_app", autospec=True)
    mocker.patch("graphinate.renderers.graphql._starlette_app", autospec=True)
    import builtins
    original_import = builtins.__import__

    def import_side_effect(name, *args, **kwargs):
        if name == "uvicorn":
            raise ImportError("No module named 'uvicorn'")
        return original_import(name, *args, **kwargs)

    mocker.patch("builtins.__import__", side_effect=import_side_effect)
    with pytest.raises(ImportError, match="No module named 'uvicorn'"):
        graphql.server(fake_schema)


def test_server_prometheus_middleware_integration():
    # We'll check that PrometheusMiddleware is added to the app

    # Arrange
    graphql_app = MagicMock()

    # Act
    app = graphql._starlette_app(graphql_app)
    middleware_names = [mw.cls.__name__ for mw in app.user_middleware]
    client = TestClient(app)
    response = client.get("/metrics")

    # Assert
    assert "PrometheusMiddleware" in middleware_names
    assert response.status_code == 200

# endregion --- Test Cases ---
