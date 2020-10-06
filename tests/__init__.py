import pathlib
import subprocess
import sys

import pytest

from vulture import core

REPO = pathlib.Path(__file__).resolve().parents[1]
WHITELISTS = [
    str(path) for path in (REPO / "vulture" / "whitelists").glob("*.py")
]


def call_vulture(args, **kwargs):
    return subprocess.call(
        [sys.executable, "-m", "vulture"] + args, cwd=REPO, **kwargs
    )


def check(items_or_names, expected_names):
    """items_or_names must be a collection of Items or a set of strings."""
    try:
        assert sorted(item.name for item in items_or_names) == sorted(
            expected_names
        )
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
