import pytest

from . import call_vulture, v
assert v  # silence pyflakes


@pytest.fixture
def check_whitelist(v, tmpdir, capsys):
    def examine(code, expected_out=0, min_confidence=0, sort_by_size=False):
        filename = str(tmpdir.join('myscript.py'))
        whitelist = str(tmpdir.join('whitelist.py'))
        with open(filename, 'w') as f:
            f.write(code)
        v.scavenge([filename])
        capsys.readouterr().out
        v.make_whitelist(min_confidence, sort_by_size)
        with open(whitelist, 'w') as f:
            f.write(capsys.readouterr().out)
        assert call_vulture([filename, whitelist]) == expected_out
    return examine


def test_unused_function(check_whitelist):
    code = """\
def func():
    pass
"""
    check_whitelist(code)


def test_unused_class(check_whitelist):
    code = """\
class Foo:
    def __init__(self):
        pass
"""
    check_whitelist(code)


def test_unused_variables(check_whitelist):
    code = """\
foo = 'unused'
bar = 'variable'
"""
    check_whitelist(code)


def test_unused_import(check_whitelist):
    code = """\
import this
"""
    check_whitelist(code, 1)


def test_unused_attribute(check_whitelist):
    code = """\
class Foo:
    @property
    def bar(self):
        pass
"""
    check_whitelist(code, 1)


def test_unreachable_code(check_whitelist):
    code = """\
def foo():
    return "Foo Bar"
    print("Hello")
"""
    check_whitelist(code, 1)
