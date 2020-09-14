"""module: utils"""

# standard imports
import ast
import os
import sys
import tokenize
from pathlib import Path

EMPTY_PATH = ""


class VultureInputException(Exception):
    pass


class PathFormat:
    """
    class: PathFormat

    Base class for path formatting.
    Implements the default behavior of relative path formatting.
    """

    def __init__(self, format_str=None):
        self._format_str = format_str

    def m_format_path(self, path: Path, *args) -> str:
        """method: m_format_path"""
        if not path:
            return EMPTY_PATH

        path_str = str(path)
        relpath_str = os.path.relpath(path_str)

        if relpath_str.startswith(".."):
            if self._format_str:
                formatted_path_str = self._format_str.format(path, *args)
            else:
                formatted_path_str = path
        else:
            if self._format_str:
                formatted_path_str = self._format_str.format(
                    relpath_str, *args
                )
            else:
                formatted_path_str = relpath_str

        return formatted_path_str

    @classmethod
    def __subclasshook__(cls, C):
        """classmethod: __subsclasshook__"""
        if cls is PathFormat:
            if any("m_format_path" in B.__dict__ for B in C.__mro__):
                return True
        return NotImplemented


class AbsolutePathFormat(PathFormat):
    """
    class: AbsolutePathFormat

    Changes the default relative path formatting to absolute.
    """

    def m_format_path(self, path: Path, *args) -> str:
        """method: m_format_path"""
        if not path:
            return EMPTY_PATH

        path_str = str(path)
        resolved_path = path.resolve(strict=True)
        resolved_path_str = str(resolved_path)

        if resolved_path_str.startswith(".."):
            if self._format_str:
                formatted_path_str = self._format_str.format(path_str, *args)
            else:
                formatted_path_str = path_str
        else:
            if self._format_str:
                formatted_path_str = self._format_str.format(
                    resolved_path_str, *args
                )
            else:
                formatted_path_str = resolved_path_str

        return formatted_path_str


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


def get_decorator_name(decorator):
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    parts = []
    while isinstance(decorator, ast.Attribute):
        parts.append(decorator.attr)
        decorator = decorator.value
    parts.append(decorator.id)
    return "@" + ".".join(reversed(parts))


def get_modules(paths, toplevel=True):
    """Take files from the command line even if they don't end with .py."""
    modules = []
    for path in paths:
        path = os.path.abspath(path)
        if toplevel and path.endswith(".pyc"):
            sys.exit(f".pyc files are not supported: {path}")
        if os.path.isfile(path) and (path.endswith(".py") or toplevel):
            modules.append(path)
        elif os.path.isdir(path):
            subpaths = [
                os.path.join(path, filename)
                for filename in sorted(os.listdir(path))
            ]
            modules.extend(get_modules(subpaths, toplevel=False))
        elif toplevel:
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
