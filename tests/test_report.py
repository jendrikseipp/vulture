import pytest

from . import v
assert v  # Silence pyflakes


@pytest.fixture
def check_report(v, capsys, tmpdir):
    def check(code, expected, min_confidence=0, sort_by_size=False,
              make_whitelist=False):
        filename = str(tmpdir.join('dead_code.py'))
        with open(filename, 'w') as f:
            f.write(code)
        v.scavenge([filename])
        capsys.readouterr()  # Flush verbose output from v.scavenge
        v.report(min_confidence, sort_by_size, make_whitelist)
        assert capsys.readouterr().out == expected
    return check


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
dead_code.py:1: unused function 'foo' (60% confidence)
"""
    min_conf_0 = """\
dead_code.py:1: unused import 'bar' (90% confidence)
dead_code.py:3: unused function 'foo' (60% confidence)
"""
    check_report(code, min_conf_0)
    check_report(code, min_conf_70, min_confidence=70)


def test_sort_by_size(check_report):
    code = """\
class Foo:
    '''
    This is a long class
    '''
    def __init__(self):
        print("Initialized foo")

    def bar(foobar):
        print("A small unused function")
"""
    expected = """\
dead_code.py:8: unused variable 'foobar' (100% confidence, 1 line)
dead_code.py:8: unused function 'bar' (60% confidence, 2 lines)
dead_code.py:1: unused class 'Foo' (60% confidence, 9 lines)
"""
    check_report(code, expected, sort_by_size=True)


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


def test_nested_arguments():
    code = """\
import foo

class Foo:
    '''
    This is a long class
    '''
    def __init__(self):
        print("Initialized foo")

    def bar(foobar):
        return
        print("A small unused function")
"""
    expected = """\
dead_code.py:1: unused import 'foo' (90% confidence)
dead_code.py:3: unused class 'Foo' (60% confidence)
dead_code.py:10: unused function 'bar' (60% confidence)
dead_code.py:10: unused variable 'foobar' (100% confidence)
dead_code.py:12: unreachable code after 'return' (100% confidence)
"""
    make_whitelist = """\
Foo # unused class (dead_code.py:3)
bar # unused function (dead_code.py:10)
foobar # unused variable (dead_code.py:10)
"""
    min_conf_70 = """\
dead_code.py:1: unused import 'foo' (90% confidence)
dead_code.py:10: unused variable 'foobar' (100% confidence)
dead_code.py:12: unreachable code after 'return' (100% confidence)
"""
    sort_by_size = """\
dead_code.py:1: unused import 'foo' (90% confidence, 1 line)
dead_code.py:10: unused variable 'foobar' (100% confidence, 1 line)
dead_code.py:12: unreachable code after 'return' (100% confidence, 1 line)
dead_code.py:10: unused function 'bar' (60% confidence, 3 lines)
dead_code.py:3: unused class 'Foo' (60% confidence, 10 lines)
"""
    make_whitelist_min_conf_70 = """\
foobar # unused variable (dead_code.py:10)
"""
    make_whitelist_sort_size = """\
foobar # unused variable (dead_code.py:10)
bar # unused function (dead_code.py:10)
Foo # unused class (dead_code.py:3)
"""
    sort_size_min_conf_70 = """\
dead_code.py:1: unused import 'foo' (90% confidence, 1 line)
dead_code.py:10: unused variable 'foobar' (100% confidence, 1 line)
dead_code.py:12: unreachable code after 'return' (100% confidence, 1 line)
"""
    make_whitelist_sort_size_min_conf = """\
foobar # unused variable (dead_code.py:10)
"""
    check_report(code, expected)
    check_report(code, make_whitelist, make_whitelist=True)
    check_report(code, min_conf_70, min_confidence=70)
    check_report(code, sort_by_size, sort_by_size=True)
    check_report(
        code, make_whitelist_min_conf_70, min_confidence=70,
        make_whitelist=True)
    check_report(
        code, make_whitelist_sort_size, sort_by_size=True, make_whitelist=True)
    check_report(
        code, sort_size_min_conf_70, sort_by_size=True, min_confidence=70)
    check_report(
        code, make_whitelist_sort_size_min_conf, min_confidence=70,
        sort_by_size=True)
