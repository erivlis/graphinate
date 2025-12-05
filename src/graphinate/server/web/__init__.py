import inspect
import pathlib
from collections.abc import Generator, Mapping
from typing import Any


def current_file() -> pathlib.Path | None:
    """Returns current file name"""
    if (current_frame := inspect.currentframe()) and current_frame.f_back is not None:
        return pathlib.Path(inspect.getfile(current_frame.f_back))
    return None


def _current_file_peers() -> Generator[tuple[str, pathlib.Path], Any, None]:
    _current_file = current_file()
    if _current_file is not None:
        for p in _current_file.parent.iterdir():
            yield p.name, p


paths_mapping: Mapping[str, pathlib.Path] = dict(_current_file_peers())


def get_static_path(relative_path: str) -> pathlib.Path:
    return paths_mapping['static'] / relative_path
