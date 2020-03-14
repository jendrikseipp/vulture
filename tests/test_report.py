import pytest

from . import v

assert v  # Silence pyflakes

mock_code = """\
import foo

class Foo:
    def __init__(self):
        print("Initialized foo")

    def bar(self):
        self.foobar = "unused attribute"
        foobar = "unused variable"
        return
        print("unreachable")

    @property
    def myprop(self):
        pass
"""


@pytest.fixture
def check_report(v, capsys):
    def test_report(code, expected, make_whitelist=False):
        filename = "foo.py"
        v.scan(code, filename=filename)
        capsys.readouterr()
        v.report(make_whitelist=make_whitelist)
        assert capsys.readouterr().out == expected.format(filename=filename)

    return test_report


def test_item_report(check_report):
    expected = """\
{filename}:1: V004 unused import 'foo' (90% confidence)
{filename}:3: V002 unused class 'Foo' (60% confidence)
{filename}:7: V003 unused function 'bar' (60% confidence)
{filename}:8: V001 unused attribute 'foobar' (60% confidence)
{filename}:9: V007 unused variable 'foobar' (60% confidence)
{filename}:11: V006  unreachable code after 'return' (100% confidence)
{filename}:13: V005  unused property 'myprop' (60% confidence)
"""
    check_report(mock_code, expected)


def test_make_whitelist(check_report):
    expected = """\
foo  # unused import ({filename}:1)
Foo  # unused class ({filename}:3)
bar  # unused function ({filename}:7)
_.foobar  # unused attribute ({filename}:8)
foobar  # unused variable ({filename}:9)
# unreachable code after 'return' ({filename}:11)
_.myprop  # unused property ({filename}:13)
"""
    check_report(mock_code, expected, make_whitelist=True)
