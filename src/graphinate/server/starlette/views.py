from starlette.responses import FileResponse
from starlette.routing import Route

from ..web import get_static_path


async def favicon(request):
    path = get_static_path('images/network_graph.png').absolute().as_posix()
    response = FileResponse(path)
    return response


def favicon_route():
    return Route('/favicon.ico', endpoint=favicon, include_in_schema=False)
