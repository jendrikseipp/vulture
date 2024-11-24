import pytest

from vulture.utils import ExitCode

from . import call_vulture, v

assert v  # Silence pyflakes.


def test_syntax_error(v):
    v.scan("foo bar")
    assert int(v.report()) == ExitCode.InvalidInput


def test_null_byte(v):
    v.scan("\x00")
    assert int(v.report()) == ExitCode.InvalidInput


def test_confidence_range(v):
    v.scan(
        """\
def foo():
    pass
"""
    )
    with pytest.raises(ValueError):
        v.get_unused_code(min_confidence=150)


def test_invalid_cmdline_args():
    assert (
        call_vulture(["vulture/", "--invalid-argument"])
        == ExitCode.InvalidCmdlineArguments
    )
