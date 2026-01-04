import pytest
from starlette.responses import FileResponse

import graphinate.server.starlette.views
from graphinate.server.web import get_static_path


def test_get_static_path():
    # Arrange
    path = 'this_is_a_path'

    # Act
    actual_path = get_static_path(path)

    # Assert
    assert f'static/{path}' in actual_path.as_posix()


@pytest.mark.asyncio
async def test_favicon():
    # Act
    actual = graphinate.server.starlette.views.favicon(None)

    # Assert
    assert isinstance(actual, FileResponse)
    assert actual.media_type == 'image/png'
    assert 'src/graphinate/server/web/static/images/logo-128.png' in actual.path
