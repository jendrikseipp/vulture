"""module: utils"""

# standard imports
import ast
import os
import sys
import tokenize
from pathlib import Path
from typing import Union

from .config import RELATIVE_PATH_FORMAT, ABSOLUTE_PATH_FORMAT

# EMPTY_PATH = ""


class VultureInputException(Exception):
    pass


def _safe_eval(node, default):
    """
    Safely evaluate the Boolean expression under the given AST node.

    Substitute `default` for all sub-expressions that cannot be
    evaluated (because variables or functions are undefined).

    We could use eval() to evaluate more sub-expressions. However, this
    function is not safe for arbitrary Python code. Even after
    overwriting the "__builtins__" dictionary, the original dictionary
    can be restored
    (https://nedbatchelder.com/blog/201206/eval_really_is_dangerous.html).

    """
    if isinstance(node, ast.BoolOp):
        results = [_safe_eval(value, default) for value in node.values]
        if isinstance(node.op, ast.And):
            return all(results)
        return any(results)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _safe_eval(node.operand, not default)

    try:
        return ast.literal_eval(node)
    except ValueError:
        return default


def condition_is_always_false(condition):
    return not _safe_eval(condition, True)


def condition_is_always_true(condition):
    return _safe_eval(condition, False)


def format_path(
    filename_path: Union[str, os.PathLike],
    format_str: str,
    *args,
    format_id: str = RELATIVE_PATH_FORMAT,
) -> str:
    if not filename_path:
        raise ValueError("Empty filename/path.")
    if format_id not in (RELATIVE_PATH_FORMAT, ABSOLUTE_PATH_FORMAT):
        raise ValueError(f"path format {format_id} unknown.")
    if not isinstance(filename_path, str) and not isinstance(
        filename_path, os.PathLike
    ):
        raise ValueError(
            f"filename/path type {type(filename_path)} not supported."
        )
    _path = Path(filename_path)
    if format_id == RELATIVE_PATH_FORMAT:
        _path_str = str(filename_path)
        _relpath_str = os.path.relpath(_path_str, start=os.curdir)
        _use_path_str = (
            _path_str if _relpath_str.startswith("..") else _relpath_str
        )
        _formatted_path_str = (
            format_str.format(_use_path_str, *args)
            if format_str
            else _use_path_str
        )
        return _formatted_path_str
    if format_id == ABSOLUTE_PATH_FORMAT:
        _abs_path = _path.resolve(strict=True)
        if format_str:
            return format_str.format(str(_abs_path), *args)
        return str(_abs_path)
    # should never get here
    raise ValueError(f"path format {format_id} uknown.")


def get_decorator_name(decorator):
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    parts = []
    while isinstance(decorator, ast.Attribute):
        parts.append(decorator.attr)
        decorator = decorator.value
    parts.append(decorator.id)
    return "@" + ".".join(reversed(parts))


def get_modules(paths):
    """Retrieve Python files to check.

    Loop over all given paths, abort if any ends with .pyc and add collect
    the other given files (even those not ending with .py) and all .py
    files under the given directories.

    """
    modules = []
    for path in paths:
        path = path.resolve()
        if path.is_file():
            if path.suffix == ".pyc":
                sys.exit(f"Error: *.pyc files are not supported: {path}")
            else:
                modules.append(path)
        elif path.is_dir():
            modules.extend(path.rglob("*.py"))
        else:
            sys.exit(f"Error: {path} could not be found.")
    return modules


def read_file(filename):
    try:
        # Use encoding detected by tokenize.detect_encoding().
        with tokenize.open(filename) as f:
            return f.read()
    except (SyntaxError, UnicodeDecodeError) as err:
        raise VultureInputException(err) from err


class LoggingList(list):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        # return list.__init__(self)
        list.__init__(self)

    def append(self, item):
        if self._verbose:
            print(f'define {self.typ} "{item.name}"')
        list.append(self, item)


class LoggingSet(set):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        # return set.__init__(self)
        set.__init__(self)

    def add(self, name):
        if self._verbose:
            print(f'use {self.typ} "{name}"')
        set.add(self, name)
