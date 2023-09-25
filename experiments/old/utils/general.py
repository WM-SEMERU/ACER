from collections.abc import Mapping
from typing import List


def map_dict(maybe_dict, f):
    """
    Execute `f` on all nested dicts within `maybe_dict`
    """

    if isinstance(maybe_dict, Mapping):
        return f({k: map_dict(v, f) for k, v in maybe_dict.items()})
    else:
        return maybe_dict


import os


def walkDirectoryForFileNames(directory: str) -> List[str]:
    walk = os.walk(directory)
    return [
        os.path.join(subdir, filename)
        for subdir, _, files in walk
        for filename in files
    ]
