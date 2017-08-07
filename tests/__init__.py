import ast
import pytest
import sys
from vulture import Vulture

HAS_ASYNC = hasattr(ast, 'AsyncFunctionDef')
PY3 = sys.version_info >= (3, )
PY2 = sys.version_info < (3, )


def skip_if_not_has_async(function):
    if not HAS_ASYNC:
        pytest.mark.skip(
            function, reason="needs async support (added in Python 3.5)")


def skip_if_python_3(function):
    if PY3:
        pytest.mark.skip(
            function, reason="This test was meant for python 2")


def skip_if_python_2(function):
    if PY2:
        pytest.mark.skip(
            function, reason="needs ast.visit_args (added in python3)")


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
