"""module: utils"""

# standard imports
import ast
import os
import sys
import tokenize
from pathlib import Path


class VultureInputException(Exception):
    """class: VultureInputException"""


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
    """function: condition_is_always_false"""
    return not _safe_eval(condition, True)


def condition_is_always_true(condition):
    """function: condition_is_always_true"""
    return _safe_eval(condition, False)


def format_path(path, absolute=False):
    """function: format_path"""
    if not path:
        return path
    if not absolute:
        relpath = os.path.relpath(path)
        # print(f'relative path {relpath}', file=sys.stderr, flush=True)
    else:
        # print('absolute paths set', file=sys.stderr)
        pp = Path(path)  # pylint: disable=invalid-name
        # make the path absolute, resolving any symlinks
        resolved_path = pp.resolve(strict=True)
        # relpath = os.path.abspath(path)
        relpath = str(resolved_path)
        # print(f'abs path {relpath}', file=sys.stderr, flush=True)
    return relpath if not relpath.startswith("..") else path


def get_decorator_name(decorator):
    """function: get_decorator_name"""
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
    """function: read_file"""
    try:
        # Use encoding detected by tokenize.detect_encoding().
        with tokenize.open(filename) as f:  # pylint: disable=invalid-name
            return f.read()
    except (SyntaxError, UnicodeDecodeError) as err:
        raise VultureInputException(err) from err


class LoggingList(list):
    """class: LoggingList"""

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
    """class: LoggingSet"""

    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        # return set.__init__(self)
        set.__init__(self)

    def add(self, name):
        if self._verbose:
            print(f'use {self.typ} "{name}"')
        set.add(self, name)
