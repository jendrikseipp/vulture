import ast
import glob
import os.path
import subprocess
import sys

import pytest
from vulture import core

DIR = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(DIR)
WHITELISTS = glob.glob(os.path.join(REPO, 'vulture', 'whitelists', '*.py'))

skip_if_not_has_async = pytest.mark.skipif(
    not hasattr(ast, 'AsyncFunctionDef'),
    reason="needs async support (added in Python 3.5)")


def call_vulture(args, **kwargs):
    return subprocess.call(
        [sys.executable, '-m', 'vulture'] + args, cwd=REPO, **kwargs)


def check(items_or_names, expected_names):
    """items_or_names must be a collection of Items or a set of strings."""
    try:
        assert (sorted(item.name for item in items_or_names) ==
                sorted(expected_names))
    except AttributeError:
        assert items_or_names == set(expected_names)


def check_unreachable(v, lineno, size, name):
    assert len(v.unreachable_code) == 1
    item = v.unreachable_code[0]
    assert item.first_lineno == lineno
    assert item.size == size
    assert item.name == name


@pytest.fixture
def v():
    return core.Vulture(verbose=True)
