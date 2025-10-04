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


def test_recursion_error(v):
    # Create code with deeply nested binary operations that will
    # trigger RecursionError during AST visiting
    depth = 500
    code = "result = " + " + ".join(["1"] * depth) + "\n"
    v.scan(code, filename="test_deep.py")
    assert int(v.report()) == ExitCode.InvalidInput
