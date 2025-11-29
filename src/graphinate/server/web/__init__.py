import inspect
import pathlib
from collections.abc import Mapping


def current_file() -> pathlib.Path | None:
    """Returns current file name"""
    if current_frame := inspect.currentframe():
        return pathlib.Path(inspect.getfile(current_frame.f_back))
    return None


paths_mapping: Mapping[str, pathlib.Path] = {p.name: p for p in current_file().parent.iterdir() if p.is_dir()}


def get_static_path(relative_path: str) -> pathlib.Path:
    return paths_mapping['static'] / relative_path
