import dataclasses
import inspect
from collections.abc import Iterable, Mapping
from typing import Any, Callable, Optional


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
    if callable(iterable_handler) and is_strict_iterable(obj):
        return iterable_handler(obj, *args, **kwargs)
    if callable(class_handler) and inspect.isclass(obj):
        return class_handler(obj, *args, **kwargs)

    if (value_converter := kwargs.get('value_converter')) and callable(value_converter):
        return value_converter(obj)

    return obj


def dictify_key_value_pairs(items: Iterable[tuple[Any, Any]],
                            key_converter: Optional[Callable[[Any], str]] = None,
                            value_converter: Optional[Callable[[Any], Any]] = None):
    return {(key_converter(k) if callable(key_converter) else k): dictify(v, key_converter, value_converter)
            for k, v in items}


def dictify_iterable(items: Iterable,
                     key_converter: Optional[Callable[[Any], str]] = None,
                     value_converter: Optional[Callable[[Any], Any]] = None) -> list:
    return [dictify(value, key_converter, value_converter) for value in items]


def dictify_mapping(items: Mapping[Any, Any],
                    key_converter: Optional[Callable[[Any], str]] = None,
                    value_converter: Optional[Callable[[Any], Any]] = None) -> dict:
    return dictify_key_value_pairs(items.items(), key_converter, value_converter)
    # return  {(key_converter(k) if callable(key_converter) else k): dictify(v, key_converter, value_converter)
    #          for k, v in obj.items()}


def dictify_class(obj,
                  key_converter: Optional[Callable[[Any], str]] = None,
                  value_converter: Optional[Callable[[Any], Any]] = None):
    if dataclasses.is_dataclass(obj):
        items = ((k, v) for k, v in inspect.getmembers(obj) if not k.startswith("_"))
        return dictify_key_value_pairs(items, key_converter, value_converter)
        # return {(key_converter(k) if callable(key_converter) else k): dictify(v, key_converter, value_converter)
        #         for (k, v) in inspect.getmembers(obj) if not k.startswith("_")}

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
