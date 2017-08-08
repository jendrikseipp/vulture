import ast
import pytest
import sys
from vulture import Vulture


def skip_if_not_has_async(function):
    if not hasattr(ast, 'AsyncFunctionDef'):
        pytest.mark.skip(
            function, reason="needs async support (added in Python 3.5)")


def skip_if_python_3(function):
    if sys.version_info >= (3, 0):
        pytest.mark.skip(
            function, reason="This test is meant for Python 2")


def skip_if_python_2(function):
    if sys.version_info < (3, 0):
        pytest.mark.skip(
            function, reason="needs ast.visit_args (added in Python 3)")


@pytest.fixture
def v():
    return Vulture(verbose=True)


def check(items_or_names, expected_names):
    if isinstance(items_or_names, set):
        # items_or_names is a set of strings.
        assert items_or_names == set(expected_names)
    else:
        # items_or_names is a list of Item objects.
        names = sorted(item.name for item in items_or_names)
        expected_names = sorted(expected_names)
        assert names == expected_names
