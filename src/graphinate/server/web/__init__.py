import pathlib
from collections.abc import Mapping

from ...tools.fs import current_file

paths_mapping: Mapping[str, pathlib.Path] = {p.name: p for p in current_file().parent.iterdir() if p.is_dir()}


def get_static_path(relative_path: str) -> pathlib.Path:
    return paths_mapping.get('static') / relative_path
