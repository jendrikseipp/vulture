import ast

import pytest
from vulture import core


def skip_if_not_has_async(function):
    if not hasattr(ast, 'AsyncFunctionDef'):
        pytest.mark.skip(
            function, reason="needs async support (added in Python 3.5)")


@pytest.fixture
def v():
    return core.Vulture(verbose=True)


def check(items_or_names, expected_names):
    if isinstance(items_or_names, set):
        # items_or_names is a set of strings.
        assert items_or_names == set(expected_names)
    else:
        # items_or_names is a list of Item objects.
        names = sorted(item.name for item in items_or_names)
        expected_names = sorted(expected_names)
        assert names == expected_names
