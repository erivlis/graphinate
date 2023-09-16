import inspect
import pathlib


def current_file() -> pathlib.Path:
    return pathlib.Path(inspect.getfile(inspect.currentframe().f_back))
