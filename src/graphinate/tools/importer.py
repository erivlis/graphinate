import importlib
from typing import Any


class ImportFromStringError(Exception):
    pass


def import_from_string(import_str: Any) -> Any:
    """Import an object from a string reference {module-name}:{variable-name}
    For example given a var `model=GraphModel()` defined in app.py file,
    then the reference would be app:model
    """

    if not isinstance(import_str, str):
        return import_str

    module_str, _, attrs_str = import_str.partition(":")
    if not module_str or not attrs_str:
        message = f"Import string '{import_str}' must be in format '<module>:<attribute>'."
        raise ImportFromStringError(message)

    try:
        module = importlib.import_module(module_str)
    except ModuleNotFoundError as exc:
        if exc.name != module_str:
            raise exc from None
        message = f"Could not import module '{module_str}'."
        raise ImportFromStringError(message) from exc

    instance = module
    try:
        for attr_str in attrs_str.split("."):
            instance = getattr(instance, attr_str)
    except AttributeError as exc:
        message = f"Attribute '{attrs_str}' not found in module '{module_str}'."
        raise ImportFromStringError(message) from exc

    return instance
