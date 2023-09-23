from graphinate.server.web import get_static_path


def test_get_static_path():
    path = 'this_is_a_path'
    actual_path = get_static_path(path)
    assert f'static/{path}' in actual_path.as_posix()
