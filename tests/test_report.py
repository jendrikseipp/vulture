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


@pytest.fixture
def check_report(v, capsys, tmpdir):
    def test_report(code, expected, min_confidence=0, sort_by_size=False,
                    make_whitelist=False):
        filename = str(tmpdir.join('dead_code.py'))
        with open(filename, 'w') as f:
            f.write(code)
        v.scavenge([filename])
        capsys.readouterr()  # Flush verbose output from v.scavenge
        if make_whitelist:
            v.make_whitelist(min_confidence, sort_by_size)
        else:
            v.report(min_confidence, sort_by_size)
        assert capsys.readouterr().out == expected.format(filename=filename)
    return test_report


def test_item_report(check_report):
    expected = """\
{filename}:1: unused import 'foo' (90% confidence)
{filename}:3: unused class 'Foo' (60% confidence)
{filename}:10: unused function 'bar' (60% confidence)
{filename}:11: unused variable 'foobar' (60% confidence)
{filename}:13: unreachable code after 'return' (100% confidence)
"""
    check_report(mock_code, expected)


def test_sort_by_size(check_report):
    expected = """\
{filename}:1: unused import 'foo' (90% confidence, 1 line)
{filename}:11: unused variable 'foobar' (60% confidence, 1 line)
{filename}:13: unreachable code after 'return' (100% confidence, 1 line)
{filename}:10: unused function 'bar' (60% confidence, 4 lines)
{filename}:3: unused class 'Foo' (60% confidence, 11 lines)
"""
    check_report(mock_code, expected, sort_by_size=True)


def test_make_whitelist(check_report):
    expected = """\
Foo  # unused class ({filename}:3)
bar  # unused function ({filename}:10)
foobar  # unused variable ({filename}:11)
"""
    check_report(mock_code, expected, make_whitelist=True)
