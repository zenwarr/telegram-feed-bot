import importlib

import sys

from src.generic_filter import generic_content_filter


def get_content_filter(name: str | None):
    if name is None or name == "generic":
        return generic_content_filter

    try:
        filter_func = getattr(sys.modules[__name__], name + "_content_filter")
    except AttributeError:
        filter_func = None

    if not filter_func:
        try:
            filter_func = getattr(
                importlib.import_module("src.builtin_filters." + name), "content_filter"
            )
        except (AttributeError, ImportError):
            filter_func = None

    if not filter_func:
        try:
            filter_func = getattr(
                importlib.import_module("src.custom_filters." + name), "content_filter"
            )
        except (AttributeError, ImportError):
            filter_func = None

    if not filter_func:
        raise RuntimeError(f"No content filter {name} found")

    return filter_func
