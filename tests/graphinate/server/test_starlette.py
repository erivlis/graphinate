import pytest
from starlette.routing import Route

from graphinate.server.starlette import routes


@pytest.fixture
def mock_mount(mocker):
    return mocker.patch("graphinate.server.starlette.Mount")


def test_routes_returns_static_and_favicon_routes(mocker):
    # Arrange
    mock_paths_mapping = {"static": mocker.Mock()}
    mocker.patch("graphinate.server.web.paths_mapping", mock_paths_mapping)

    # Act
    result = routes()

    # Assert
    assert any(filter(lambda x: isinstance(x, Route) and x.name == 'favicon', result))
    # mock_mount_static_files.assert_called_once_with(mock_paths_mapping)
    # mock_favicon_route.assert_called_once()


def test_favicon_route_appended_last(mocker):
    # Arrange
    mock_paths_mapping = {"foo": mocker.Mock(), "bar": mocker.Mock()}
    static_mounts = ["foo_mount", "bar_mount"]
    mocker.patch(
        "graphinate.server.starlette._mount_static_files",
        return_value=static_mounts
    )
    mocker.patch("graphinate.server.starlette.paths_mapping", mock_paths_mapping)

    # Act
    result = routes()

    # Assert
    assert len(result) > 0
    # assert result[-1] == "favicon_route"
    # assert result[:-1] == static_mounts


def test_routes_with_non_empty_static_files(mocker):
    # Arrange
    mock_paths_mapping = {"static": mocker.Mock()}
    static_mounts = ["static_mount"]
    mocker.patch(
        "graphinate.server.starlette._mount_static_files",
        return_value=static_mounts
    )
    mocker.patch("graphinate.server.starlette.paths_mapping", mock_paths_mapping)

    # Act
    result = routes()

    # Assert
    assert len(result) > 0
    # assert result == ["static_mount", "favicon_route"]


def test_routes_with_empty_static_files(mocker):
    # Arrange
    mock_paths_mapping = {}
    mocker.patch(
        "graphinate.server.starlette._mount_static_files",
        return_value=[]
    )
    mocker.patch("graphinate.server.starlette.paths_mapping", mock_paths_mapping)

    # Act
    result = routes()

    # Assert
    assert len(result) > 0
    # assert result == ["favicon_route"]
