from starlette.responses import FileResponse
from starlette.routing import Route

from ..web import get_static_path


async def favicon(request):
    path = get_static_path('images/logo-128.png').absolute().as_posix()
    return FileResponse(path)


def favicon_route() -> Route:
    return Route('/favicon.ico', endpoint=favicon, include_in_schema=False)
