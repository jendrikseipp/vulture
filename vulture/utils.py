import ast
from enum import IntEnum
import pathlib
import sys
import tokenize
from typing import Optional, Union


class VultureInputException(Exception):
    pass


class ExitCode(IntEnum):
    NoDeadCode = 0
    InvalidInput = 1
    InvalidCmdlineArguments = 2
    DeadCode = 3


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


def is_ast_string(node):
    return isinstance(node, ast.Constant) and isinstance(node.value, str)


def format_path(path):
    try:
        return path.relative_to(pathlib.Path.cwd())
    except ValueError:
        # Path is not below the current directory.
        return path


def get_decorator_name(decorator):
    if isinstance(decorator, ast.Call):
        decorator = decorator.func
    try:
        parts = []
        while isinstance(decorator, ast.Attribute):
            parts.append(decorator.attr)
            decorator = decorator.value
        parts.append(decorator.id)
    except AttributeError:
        parts = []
    return "@" + ".".join(reversed(parts))


def get_modules(paths):
    """Retrieve Python files to check.

    Loop over all given paths, abort if any ends with .pyc, add the other given
    files (even those not ending with .py) and collect all .py files under the
    given directories.

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
        raise VultureInputException from err


def add_parents(root: ast.AST) -> None:
    # https://stackoverflow.com/a/43311383/7743427:
    root.parent = None
    for node in ast.walk(root):
        for child in ast.iter_child_nodes(node):
            child.parent = node


def parent(node: Optional[ast.AST]) -> Optional[ast.AST]:
    return getattr(node, "parent", None)


def ancestor(
    node: ast.AST, target_ancestor_types, limit: int
) -> Optional[ast.AST]:
    """`limit` is how far back to search before giving up and returning `None` instead"""
    assert limit < 100
    if limit == 0:
        return None
    if not (node := parent(node)) or isinstance(node, target_ancestor_types):
        return node
    return ancestor(node, target_ancestor_types, limit - 1)


def call_info_no_args(call_node: ast.Call) -> str:
    """Returns a string of the portion of the function call that's before the parenthesized arg list."""
    assert sys.version_info.minor >= 9
    return ast.unparse(call_node).split("(")[0]


def recursive_call(node: Union[ast.Name, ast.Attribute]) -> Optional[bool]:
    """Returns a boolean if it can be determined the node is part of a recursive call.
    Otherwise if the function is nested in a complicated way, `None` is returned."""
    if not isinstance((call_node := parent(node)), ast.Call) or not (
        func := ancestor(node, (ast.FunctionDef, ast.AsyncFunctionDef), 10)
    ):
        return False
    if isinstance((func_parent := parent(func)), ast.Module):
        return call_info_no_args(call_node) == func.name
    if not isinstance(func_parent, ast.ClassDef) or not isinstance(
        parent(func_parent), ast.Module
    ):
        return None
    return call_info_no_args(call_node).split(".") == [
        (
            "self"
            if "self" == next((x.arg for x in func.args.args), None)
            else func_parent.name
        ),
        func.name,
    ]


class LoggingList(list):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return super().__init__()

    def append(self, item):
        if self._verbose:
            print(f'define {self.typ} "{item.name}"')
        super().append(item)


class LoggingSet(set):
    def __init__(self, typ, verbose):
        self.typ = typ
        self._verbose = verbose
        return super().__init__()

    def add(self, name):
        if self._verbose:
            print(f'use {self.typ} "{name}"')
        super().add(name)
