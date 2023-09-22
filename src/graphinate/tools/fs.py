import inspect
import pathlib


def current_file() -> pathlib.Path:
    """Returns current file name"""
    return pathlib.Path(inspect.getfile(inspect.currentframe().f_back))
