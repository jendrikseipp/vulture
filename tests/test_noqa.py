import pytest

from vulture.core import NOQA_REGEXP
from . import check, v

assert v  # Silence pyflakes.


@pytest.mark.parametrize(
    "line, codes",
    [
        ("# noqa", ["all"]),
        ("## noqa", ["all"]),
        ("# noqa Hi, go on.", ["all"]),
        ("# noqa: V001", ["V001"]),
        ("# noqa: V001, V007", ["V001", "V007"]),
        ("# NoQA: V001,      V003, \t V004", ["V001", "V003", "V004"]),
    ],
)
def test_noqa_regex_present(line, codes):
    match = NOQA_REGEXP.search(line)
    parsed = [
        c.strip() for c in (match.groupdict()["codes"] or "all").split(",")
    ]
    assert parsed == codes


@pytest.mark.parametrize(
    "line",
    [("# noqa: 123V"), ("# noqa explaination: V012"), ("# noqa: ,V001"),],
)
def test_noqa_regex_no_groups(line):
    assert NOQA_REGEXP.search(line).groupdict()["codes"] == None


@pytest.mark.parametrize(
    "line",
    [("#noqa"), ("##noqa"), ("# n o q a"), ("#NOQA"), ("# Hello, noqa"),],
)
def test_noqa_regex_not_present(line):
    assert bool(NOQA_REGEXP.search(line)) == False


def test_noqa_attributes(v):
    v.scan(
        """\
something.x = 'x'  # noqa: V001
something.z = 'z'  # noqa: V006 (code for unused variable)
something.u = 'u'  # noqa
"""
    )
    check(v.unused_attrs, ["z"])


def test_noqa_classes(v):
    v.scan(
        """\
class QtWidget:  # noqa: V002
    pass

class ABC(QtWidget):
    pass  # noqa: V002 (should not ignore)

class DEF:  # noqa
    pass
"""
    )
    check(v.unused_classes, ["ABC"])


def test_noqa_functions(v):
    v.scan(
        """\
def play(tune, instrument='bongs', _hz='50'):  # noqa: V003
    pass


# noqa
def problems():  # noqa: V004
    ''' They don't go away. :-)'''
    pass  # noqa: V003

def hello(name):  # noqa
    print("Hello")
"""
    )
    check(v.unused_funcs, ["problems"])
    check(v.unused_vars, ["instrument", "tune"])


def test_noqa_imports(v):
    v.scan(
        """\
import foo
import this  # noqa: V004
import zoo
from koo import boo  # noqa
from me import *
import dis  # noqa: V001 (code for unused attr)
"""
    )
    check(v.unused_imports, ["foo", "zoo", "dis"])


def test_noqa_propoerties(v):
    v.scan(
        """\
class Zoo:
    @property  # noqa
    def no_of_coalas(self):
        pass

    @property  # noqa: V005
    def area(self, width, depth):  
        pass

    @property
    def entry_gates(self):  # noqa
        pass

    @property  # noqa: V003 (code for unused function)
    def tickets(self):
        pass
"""
    )
    check(v.unused_props, ["entry_gates", "tickets"])
    check(v.unused_classes, ["Zoo"])
    check(v.unused_vars, ["width", "depth"])


def test_noqa_unreacahble_code(v):
    v.scan(
        """\
def shave_sheeps(sheeps):
    for sheep in sheeps:
        if sheep.bald:
            continue
            sheep.grow_hair()  # noqa: V006
        sheep.shave()
    return sheeps
    for sheep in sheeps:  # noqa: V006
        if sheep.still_has_hair:
            sheep.shave_again()
"""
    )
    check(v.unreachable_code, [])
    check(v.unused_funcs, ["shave_sheeps"])


def test_noqa_variables(v):
    v.scan(
        """\
mitsi = "Mother"  # noqa: V007
harry = "Father"  # noqa
shero = "doggy"   # noqa: V001, V004 (code for unused import, attr)
shinchan.friend = ['masao']  # noqa: V007
"""
    )
    check(v.unused_vars, ["shero"])
    check(v.unused_attrs, ["friend"])


def test_noqa_with_multiple_issue_codes(v):
    v.scan(
        """\
def world(axis):  # noqa: V003, V006
    pass


for _ in range(3):
    continue
    xyz = hello(something, else):  # noqa: V006, V007
"""
    )
    check(v.get_unused_code(), [])


def test_noqa_on_empty_line(v):
    v.scan(
        """\
# noqa
import this
# noqa
"""
    )
    check(v.unused_imports, ["this"])


def test_noqa_with_invalid_codes(v):
    v.scan(
        """\
import this  # V098, A123, F876
"""
    )
    check(v.unused_imports, ["this"])


def test_noqa_with_special_unicode(v):
    v.scan(
        """\
import abc  # noqa: V012, V😎12
import problems  # noqa: V03🙃1
"""
    )
    check(v.unused_imports, ["abc", "problems"])
