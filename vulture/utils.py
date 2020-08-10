import ast
import os
import sys
import tokenize


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
        else:
            return any(results)
    elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return not _safe_eval(node.operand, not default)
    else:
        try:
            return ast.literal_eval(node)
        except ValueError:
            return default


def condition_is_always_false(condition):
    return not _safe_eval(condition, True)


def condition_is_always_true(condition):
    return _safe_eval(condition, False)


def format_path(path):
    if not path:
        return path
    relpath = os.path.relpath(path)
    return relpath if not relpath.startswith("..") else path


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
        raise VultureInputException(err)


class LoggingList(list):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return list.__init__(self)

    def append(self, item):
        if self._verbose:
            print(f'define {self.typ} "{item.name}"')
        list.append(self, item)


class LoggingSet(set):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return set.__init__(self)

    def add(self, name):
        if self._verbose:
            print(f'use {self.typ} "{name}"')
        set.add(self, name)
