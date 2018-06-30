import pytest

from . import v
assert v  # Silence pyflakes

mock_code = """\
import foo

class Foo:
    '''
    This is a long class
    '''
    def __init__(self):
        print("Initialized foo")

    def bar():
        foobar = "unused variable"
        return
        print("A small unused function")
"""


@pytest.fixture()
def check_report(v, capsys, tmpdir):
    def test_report(code, expected, min_confidence=0, sort_by_size=False,
                    make_whitelist=False):
        filename = 'dead_code.py'
        tmpdir.join(filename)
        with open(filename, 'w') as f:
            f.write(code)
        v.scavenge([filename])
        capsys.readouterr()  # Flush verbose output from v.scavenge
        if make_whitelist:
            v.make_whitelist(min_confidence, sort_by_size)
        else:
            v.report(min_confidence, sort_by_size)
        assert capsys.readouterr().out == expected
    return test_report


def test_item_report(check_report):
    code = """\
def foo():
    pass
"""
    expected = """\
dead_code.py:1: unused function 'foo' (60% confidence)
"""
    check_report(code, expected)


def test_min_confidence_report(check_report):
    code = """\
import bar

def foo():
    pass
"""
    min_conf_70 = """\
dead_code.py:1: unused import 'bar' (90% confidence)
"""
    min_conf_0 = """\
dead_code.py:1: unused import 'bar' (90% confidence)
dead_code.py:3: unused function 'foo' (60% confidence)
"""
    check_report(code, min_conf_0)
    check_report(code, min_conf_70, min_confidence=70)


def test_sort_by_size(check_report):
    expected = """\
dead_code.py:1: unused import 'foo' (90% confidence, 1 line)
dead_code.py:11: unused variable 'foobar' (60% confidence, 1 line)
dead_code.py:13: unreachable code after 'return' (100% confidence, 1 line)
dead_code.py:10: unused function 'bar' (60% confidence, 4 lines)
dead_code.py:3: unused class 'Foo' (60% confidence, 11 lines)
"""
    check_report(mock_code, expected, sort_by_size=True)


def test_make_whitelist(check_report):
    code = """\
def foo():
    pass

class Foo:
    def bar():
        pass
"""
    expected = """\
foo # unused function (dead_code.py:1)
Foo # unused class (dead_code.py:4)
bar # unused function (dead_code.py:5)
"""
    check_report(code, expected, make_whitelist=True)


def test_make_whitelist_min_conf(check_report):
    make_whitelist_min_conf_70 = ''
    check_report(
        mock_code, make_whitelist_min_conf_70, min_confidence=70,
        make_whitelist=True)


def test_make_whitelist_sort_size(check_report):
    make_whitelist_sort_size = """\
foobar # unused variable (dead_code.py:11)
bar # unused function (dead_code.py:10)
Foo # unused class (dead_code.py:3)
"""
    check_report(
        mock_code, make_whitelist_sort_size, sort_by_size=True,
        make_whitelist=True)


def test_sort_size_min_conf(check_report):
    sort_size_min_conf_70 = """\
dead_code.py:1: unused import 'foo' (90% confidence, 1 line)
dead_code.py:13: unreachable code after 'return' (100% confidence, 1 line)
"""
    check_report(
        mock_code, sort_size_min_conf_70, sort_by_size=True, min_confidence=70)


def test_make_whitelist_sort_size_min_conf(check_report):
    make_whitelist_sort_size_min_conf_60 = """\
foobar # unused variable (dead_code.py:11)
bar # unused function (dead_code.py:10)
Foo # unused class (dead_code.py:3)
"""
    check_report(
        mock_code, make_whitelist_sort_size_min_conf_60, min_confidence=60,
        sort_by_size=True, make_whitelist=True)
