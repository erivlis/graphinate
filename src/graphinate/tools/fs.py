import inspect
import pathlib


def current_file():
    return pathlib.Path(inspect.getfile(inspect.currentframe().f_back))
