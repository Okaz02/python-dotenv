"""
Thin wrapper around python-dotenv that adds a `dotenv_fixed_path` option.

A relative `dotenv_fixed_path` is resolved against the directory of the file that
calls `load_dotenv()` / `dotenv_values()`, instead of the current working directory.
Everything else is passed through to the installed python-dotenv unchanged.
"""

import os
import sys
from typing import Any, Dict, Optional, Union

import dotenv

StrPath = Union[str, "os.PathLike[str]"]

__all__ = ["load_dotenv", "dotenv_values", "resolve_fixed_path"]


def resolve_fixed_path(path: StrPath, _depth: int = 1) -> str:
    """
    Resolve `path` against the directory of the calling file.

    Absolute paths are returned as-is. When there is no caller file (REPL, IPython,
    `python -c`, frozen apps), the current working directory is used instead.
    """
    path = os.fspath(path)
    if os.path.isabs(path):
        return path

    caller_file = sys._getframe(_depth).f_code.co_filename
    if getattr(sys, "frozen", False) or not os.path.isfile(caller_file):
        return os.path.abspath(path)

    return os.path.join(os.path.dirname(os.path.abspath(caller_file)), path)


def _pop_fixed_path(args: tuple, kwargs: Dict[str, Any], depth: int) -> None:
    fixed_path = kwargs.pop("dotenv_fixed_path", None)
    if fixed_path is None:
        return
    if args or kwargs.get("dotenv_path") is not None:
        raise TypeError("dotenv_path and dotenv_fixed_path cannot be used together")
    kwargs["dotenv_path"] = resolve_fixed_path(fixed_path, _depth=depth + 1)


def load_dotenv(
    *args: Any, dotenv_fixed_path: Optional[StrPath] = None, **kwargs: Any
) -> bool:
    """
    Same as `dotenv.load_dotenv()`, plus `dotenv_fixed_path`: a path to the .env
    file that is resolved relative to the calling file, not the current directory.
    """
    kwargs["dotenv_fixed_path"] = dotenv_fixed_path
    _pop_fixed_path(args, kwargs, depth=2)
    return dotenv.load_dotenv(*args, **kwargs)


def dotenv_values(
    *args: Any, dotenv_fixed_path: Optional[StrPath] = None, **kwargs: Any
) -> Dict[str, Optional[str]]:
    """
    Same as `dotenv.dotenv_values()`, plus `dotenv_fixed_path`: a path to the .env
    file that is resolved relative to the calling file, not the current directory.
    """
    kwargs["dotenv_fixed_path"] = dotenv_fixed_path
    _pop_fixed_path(args, kwargs, depth=2)
    return dotenv.dotenv_values(*args, **kwargs)
