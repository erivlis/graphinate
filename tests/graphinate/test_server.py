import pytest
from starlette.responses import FileResponse

import graphinate.server.starlette.views
from graphinate.server.web import get_static_path


def test_get_static_path():
    path = 'this_is_a_path'
    actual_path = get_static_path(path)
    assert f'static/{path}' in actual_path.as_posix()


@pytest.mark.asyncio
async def test_favicon():
    actual = await graphinate.server.starlette.views.favicon(None)

    assert isinstance(actual, FileResponse)
    assert actual.media_type == 'image/png'
    assert 'src/graphinate/server/web/static/images/logo-128.png' in actual.path

