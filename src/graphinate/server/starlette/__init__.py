from collections.abc import Mapping, Sequence
from pathlib import Path

from starlette.routing import BaseRoute, Mount
from starlette.staticfiles import StaticFiles

from ..web import paths_mapping
from .views import favicon_route


def _mount_static_files(named_paths: Mapping[str, Path]) -> list[Mount]:
    mounts = []
    for name, path in named_paths.items():
        if not name.startswith('__'):
            index_file = path / 'index.html'
            static_files = StaticFiles(directory=path, html=index_file.exists(), check_dir=True)
            mount = Mount(path=f"/{name}", app=static_files, name=name)
            mounts.append(mount)
    return mounts


def routes() -> Sequence[BaseRoute]:
    route_list: list[BaseRoute] = [
        *_mount_static_files(paths_mapping),
        favicon_route()
    ]

    return route_list


__all__ = ('routes',)
