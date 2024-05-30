"""
This code snippet defines functions for converting objects into dictionaries using customizable key and value
converters.
It includes functions for handling key-value pairs, iterables, mappings, and classes.
The main function 'dictify' acts as a dispatcher to call the appropriate handler based on the type of the input object.
"""

import dataclasses
import inspect
from collections.abc import Iterable, Mapping
from typing import Any, Callable, Optional


def is_strict_iterable(obj: Any) -> bool:
    """
    Check if the input object is a strict iterable, meaning it is an instance of Iterable but not an instance of str,
    bytes, or bytearray.

    Parameters:
        obj (Any): The object to be checked for strict iterability.

    Returns:
        bool: True if the object is a strict iterable, False otherwise.
    """
    return isinstance(obj, Iterable) and not isinstance(obj, (str, bytes, bytearray))


def _process_obj(obj: Any,
                 mapping_handler: Optional[Callable] = None,
                 iterable_handler: Optional[Callable] = None,
                 class_handler: Optional[Callable] = None,
                 *args,
                 **kwargs):
    """
    Process the input object based on its type and handlers provided.

    Parameters:
        obj (Any): The object to be processed.
        mapping_handler (Optional[Callable], optional): Handler function for mappings. Defaults to None.
        iterable_handler (Optional[Callable], optional): Handler function for iterables. Defaults to None.
        class_handler (Optional[Callable], optional): Handler function for classes. Defaults to None.
        *args: Variable length argument list.
        **kwargs: Arbitrary keyword arguments.

    Returns:
        Any: Processed object based on the provided handlers or the original object if no suitable handler is found.
    """

    if mapping_handler and callable(mapping_handler) and isinstance(obj, Mapping):
        return mapping_handler(obj, *args, **kwargs)
    if iterable_handler and callable(iterable_handler) and is_strict_iterable(obj):
        return iterable_handler(obj, *args, **kwargs)
    if class_handler and callable(class_handler) and dataclasses.is_dataclass(obj):
        return class_handler(obj, *args, **kwargs)

    if (value_converter := kwargs.get('value_converter')) and callable(value_converter):
        return value_converter(obj)

    return obj


def dictify_key_value_pairs(items: Iterable[tuple[Any, Any]],
                            key_converter: Optional[Callable[[Any], str]] = None,
                            value_converter: Optional[Callable[[Any], Any]] = None):
    """
    Converts key-value pairs into a dictionary with optional key and value converters.

    Parameters:
        items (Iterable[tuple[Any, Any]]): The key-value pairs to be converted into a dictionary.
        key_converter (Optional[Callable[[Any], str]], optional): A function to convert keys. Defaults to None.
        value_converter (Optional[Callable[[Any], Any]], optional): A function to convert values. Defaults to None.

    Returns:
        dict: A dictionary with converted key-value pairs.
    """
    return {(key_converter(k) if key_converter and callable(key_converter) else k): dictify(v,
                                                                                            key_converter,
                                                                                            value_converter)
            for k, v in items}


def dictify_iterable(items: Iterable,
                     key_converter: Optional[Callable[[Any], str]] = None,
                     value_converter: Optional[Callable[[Any], Any]] = None) -> list:
    """
    Process an iterable of items by converting each item into a dictionary using the provided key and value converters.

    Parameters:
        items (Iterable): The iterable of items to be processed.
        key_converter (Optional[Callable[[Any], str]], optional): A function to convert keys. Defaults to None.
        value_converter (Optional[Callable[[Any], Any]], optional): A function to convert values. Defaults to None.

    Returns:
        list: A list of dictionaries where each dictionary represents an item from the input iterable after conversion.
    """
    return [dictify(value, key_converter, value_converter) for value in items]


def dictify_mapping(items: Mapping[Any, Any],
                    key_converter: Optional[Callable[[Any], str]] = None,
                    value_converter: Optional[Callable[[Any], Any]] = None) -> dict:
    """
    Converts a mapping object into a dictionary with optional key and value converters.

    Parameters:
        items (Mapping[Any, Any]): The mapping object to be converted into a dictionary.
        key_converter (Optional[Callable[[Any], str]], optional): A function to convert keys. Defaults to None.
        value_converter (Optional[Callable[[Any], Any]], optional): A function to convert values. Defaults to None.

    Returns:
        dict: A dictionary with converted key-value pairs from the mapping object.
    """
    return dictify_key_value_pairs(items.items(), key_converter, value_converter)


def dictify_class(obj,
                  key_converter: Optional[Callable[[Any], str]] = None,
                  value_converter: Optional[Callable[[Any], Any]] = None):
    """
    Converts attributes of a class object into a dictionary with optional key and value converters.

    Parameters:
        obj (Any): The class object whose attributes are to be converted into a dictionary.
        key_converter (Optional[Callable[[Any], str]], optional): A function to convert keys. Defaults to None.
        value_converter (Optional[Callable[[Any], Any]], optional): A function to convert values. Defaults to None.

    Returns:
        dict: A dictionary with converted key-value pairs representing the non-private attributes of the class object.
    """
    items = ((k, v) for k, v in inspect.getmembers(obj) if not k.startswith("_"))
    return dictify_key_value_pairs(items, key_converter, value_converter)


def dictify(obj,
            key_converter: Optional[Callable[[Any], str]] = None,
            value_converter: Optional[Callable[[Any], Any]] = None):
    """
    Converts an object into a dictionary using customizable key and value converters.

    Parameters:
        obj (Any): The object to be converted into a dictionary.
        key_converter (Optional[Callable[[Any], str]], optional): A function to convert keys. Defaults to None.
        value_converter (Optional[Callable[[Any], Any]], optional): A function to convert values. Defaults to None.

    Returns:
        Any: Processed object based on the provided handlers or the original object if no suitable handler is found.
    """
    return _process_obj(obj,
                        mapping_handler=dictify_mapping,
                        iterable_handler=dictify_iterable,
                        class_handler=dictify_class,
                        key_converter=key_converter,
                        value_converter=value_converter)
