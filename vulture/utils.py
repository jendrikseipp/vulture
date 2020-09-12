import ast
import os
import pathlib
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
    try:
        return path.relative_to(os.curdir)
    except ValueError:
        return path


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
    """Take files from the command line even if they don't end with .py."""
    modules = []
    for path_str in paths:
        path = pathlib.Path(path_str).resolve()

        if not path.exists():
            sys.exit(f"Error: {path} could not be found.")

        if path.is_file():
            top_paths = (_ for _ in [path])
        else:
            top_paths = path.glob("*")

        for top_path in top_paths:
            if top_path.is_file():
                if top_path.suffix == ".pyc":
                    sys.exit(f".pyc files are not supported: {top_path}")
                else:
                    modules.append(top_path)
            elif not top_path.is_dir():
                sys.exit(f"Error: {top_path} could not be found.")
        sub_paths = path.rglob("*.py")
        for sub_path in sub_paths:
            if sub_path.is_file():
                modules.append(sub_path)
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
