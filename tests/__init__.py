import ast

import pytest
from vulture import core


def check(items_or_names, expected_names):
    if isinstance(items_or_names, set):
        # items_or_names is a set of strings.
        assert items_or_names == set(expected_names)
    else:
        # items_or_names is a list of Item objects.
        names = sorted(item.name for item in items_or_names)
        expected_names = sorted(expected_names)
        assert names == expected_names


def check_unreachable(v, lineno, size, name):
    assert len(v.unreachable_code) == 1
    item = v.unreachable_code[0]
    assert item.lineno == lineno
    assert item.size == size
    assert item.name == name


def skip_if_not_has_async(function):
    if not hasattr(ast, 'AsyncFunctionDef'):
        pytest.mark.skip(
            function, reason="needs async support (added in Python 3.5)")


@pytest.fixture
def v():
    return core.Vulture(verbose=True, sort_by_size=True)
