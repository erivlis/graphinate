import dataclasses
import functools
import inspect
from typing import Callable, Any, Mapping, Iterable


def is_strict_iterable(obj: Any) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray))


def _process_obj(obj: Any,
                 mapping_handler: Callable | None = None,
                 iterable_handler: Callable | None = None,
                 class_handler: Callable | None = None,
                 *args,
                 **kwargs):
    if callable(mapping_handler) and isinstance(obj, Mapping):
        return mapping_handler(obj, *args, **kwargs)
    elif callable(iterable_handler) and is_strict_iterable(obj):
        return iterable_handler(obj, *args, **kwargs)
    elif callable(class_handler) and inspect.isclass(obj):
        return class_handler(obj, *args, **kwargs)
    else:
        return obj


def dictify_mapping(obj: Mapping[Any, Any], key_converter: Callable[[Any], str] | None = None) -> dict:
    return {(key_converter(k) if key_converter else k): dictify(v, key_converter) for k, v in obj.items()}


def dictify_iterable(obj: Iterable, key_converter: Callable[[Any], str] | None = None) -> list:
    return [dictify(v, key_converter) for v in obj]


def dictify_class(obj, key_converter: Callable[[Any], str] | None = None):
    if dataclasses.is_dataclass(obj):
        return {key_converter(k) if key_converter else k: dictify(v, key_converter)
                for k, v in inspect.getmembers(obj) if not k.startswith("_")}
    else:
        return str(obj)


def dictify(obj, key_converter: Callable[[Any], str] | None = None):
    return _process_obj(obj,
                        mapping_handler=dictify_mapping,
                        iterable_handler=dictify_iterable,
                        class_handler=dictify_class,
                        key_converter=key_converter)


def tuple_converter(k):
    return str(k) if isinstance(k, tuple) else k


dictify_tuple = functools.partial(dictify, key_converter=tuple_converter)
