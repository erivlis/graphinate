import dataclasses
import inspect
from typing import Any, Callable, Iterable, Mapping, Optional


def is_strict_iterable(obj: Any) -> bool:
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray))


def _process_obj(obj: Any,
                 mapping_handler: Optional[Callable] = None,
                 iterable_handler: Optional[Callable] = None,
                 class_handler: Optional[Callable] = None,
                 *args,
                 **kwargs):
    if callable(mapping_handler) and isinstance(obj, Mapping):
        return mapping_handler(obj, *args, **kwargs)
    elif callable(iterable_handler) and is_strict_iterable(obj):
        return iterable_handler(obj, *args, **kwargs)
    elif callable(class_handler) and inspect.isclass(obj):
        return class_handler(obj, *args, **kwargs)
    else:
        if (value_converter := kwargs.get('value_converter')) and callable(value_converter):
            return value_converter(obj)
        return obj


def dictify_mapping(obj: Mapping[Any, Any],
                    key_converter: Optional[Callable[[Any], str]] = None,
                    value_converter: Optional[Callable[[Any], Any]] = None) -> dict:
    return {(key_converter(k) if key_converter else k): dictify(v, key_converter, value_converter)
            for k, v in obj.items()}


def dictify_iterable(obj: Iterable,
                     key_converter: Optional[Callable[[Any], str]] = None,
                     value_converter: Optional[Callable[[Any], Any]] = None) -> list:
    return [dictify(v, key_converter, value_converter) for v in obj]


def dictify_class(obj,
                  key_converter: Optional[Callable[[Any], str]] = None,
                  value_converter: Optional[Callable[[Any], Any]] = None):
    if dataclasses.is_dataclass(obj):
        return {key_converter(k) if key_converter else k: dictify(v, key_converter, value_converter)
                for k, v in inspect.getmembers(obj) if not k.startswith("_")}
    else:
        return str(obj)


def dictify(obj,
            key_converter: Optional[Callable[[Any], str]] = None,
            value_converter: Optional[Callable[[Any], Any]] = None):
    return _process_obj(obj,
                        mapping_handler=dictify_mapping,
                        iterable_handler=dictify_iterable,
                        class_handler=dictify_class,
                        key_converter=key_converter,
                        value_converter=value_converter)
