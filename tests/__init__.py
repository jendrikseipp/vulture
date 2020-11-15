import pathlib
import subprocess
from subprocess import PIPE, STDOUT
import sys

import pytest

from vulture import core

REPO = pathlib.Path(__file__).resolve().parents[1]
WHITELISTS = [
    str(path) for path in (REPO / "vulture" / "whitelists").glob("*.py")
]

CALL_TIMEOUT_SEC = 60


def call_vulture(args, **kwargs):
    return subprocess.call(
        [sys.executable, "-m", "vulture"] + args, cwd=REPO, **kwargs
    )


def run_vulture(args_list, **kwargs):
    """
    Run vulture using subprocess.run(...)

    Returns a subprocess.CompletedProcess object
    in order that a caller (i.e. tests) can examine
    the output in more detail than with call_vulture(...)

    added to enable testing of absolute path generation
    """
    check = kwargs.get("check", False)
    if "check" in kwargs:
        del kwargs["check"]
    # WARNING - setting check = True may raise an Error/Exception
    # on process failure
    result = subprocess.run(
        [sys.executable, "-m", "vulture"] + args_list,
        stdin=None,
        input=None,
        stdout=PIPE,
        stderr=STDOUT,
        shell=False,
        cwd=REPO,
        timeout=CALL_TIMEOUT_SEC,
        check=check,
        encoding=None,
        errors=None,
        env=None,
        universal_newlines=True,
        **kwargs
    )
    return result


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
