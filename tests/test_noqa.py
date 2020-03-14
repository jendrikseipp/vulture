import pytest

from vulture.core import NOQA_REGEXP, _parse_error_codes
from . import check, v

assert v  # Silence pyflakes.


@pytest.mark.parametrize(
    "line, codes",
    [
        ("# noqa", ["all"]),
        ("## noqa", ["all"]),
        ("# noqa Hi, go on.", ["all"]),
        ("# noqa: V101", ["V101"]),
        ("# noqa: V101, V106", ["V101", "V106"]),
        ("# NoQA: V101,      V103, \t V104", ["V101", "V103", "V104"]),
    ],
)
def test_noqa_regex_present(line, codes):
    match = NOQA_REGEXP.search(line)
    parsed = _parse_error_codes(match)
    assert parsed == codes


@pytest.mark.parametrize(
    "line",
    [("# noqa: 123V"), ("# noqa explaination: V012"), ("# noqa: ,V101")],
)
def test_noqa_regex_no_groups(line):
    assert NOQA_REGEXP.search(line).groupdict()["codes"] is None


@pytest.mark.parametrize(
    "line",
    [("#noqa"), ("##noqa"), ("# n o q a"), ("#NOQA"), ("# Hello, noqa")],
)
def test_noqa_regex_not_present(line):
    assert bool(NOQA_REGEXP.search(line)) is False


def test_noqa_without_codes(v):
    v.scan(
        """\
import this  # noqa

class Cellar:  # noqa
    @property
    def wine(self, grapes): # noqa
        pass

    def serve(self, quantity=50):  # noqa
        self.quantity_served = quantity  # noqa
        return
        self.pour()  # noqa
"""
    )
    check(v.unused_attrs, [])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_props, [])
    check(v.unreachable_code, [])
    check(v.unused_vars, [])


def test_noqa_specific_issue_codes(v):
    v.scan(
        """\
import this  # noqa: V104

class Cellar:  # noqa: V102
    @property
    def wine(self, grapes):  # noqa: V105, V106
        pass

    def serve(self, quantity=50):  # noqa: V103
        self.quantity_served = quantity  # noqa: V101
        return
        self.pour()  # noqa: V201
"""
    )
    check(v.unused_attrs, [])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_props, [])
    check(v.unreachable_code, [])
    check(v.unused_vars, [])


def test_noqa_attributes(v):
    v.scan(
        """\
something.x = 'x'  # noqa: V101
something.z = 'z'  # noqa: V106 (code for unused variable)
something.u = 'u'  # noqa
"""
    )
    check(v.unused_attrs, ["z"])


def test_noqa_classes(v):
    v.scan(
        """\
class QtWidget:  # noqa: V102
    pass

class ABC(QtWidget):
    pass  # noqa: V102 (should not ignore)

class DEF:  # noqa
    pass
"""
    )
    check(v.unused_classes, ["ABC"])


def test_noqa_functions(v):
    v.scan(
        """\
def play(tune, instrument='bongs', _hz='50'):  # noqa: V103
    pass


# noqa
def problems():  # noqa: V104
    ''' They don't go away. :-)'''
    pass  # noqa: V103

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
import this  # noqa: V104
import zoo
from koo import boo  # noqa
from me import *
import dis  # noqa: V101 (code for unused attr)
"""
    )
    check(v.unused_imports, ["foo", "zoo", "dis"])


def test_noqa_properties(v):
    v.scan(
        """\
class Zoo:
    @property
    def no_of_coalas(self):  # noqa
        pass

    @property
    def area(self, width, depth):  # noqa: V105
        pass

    @property  # noqa  (should not be ignored)
    def entry_gates(self):
        pass

    @property
    def tickets(self):  # noqa: V103 (code for unused function)
        pass
"""
    )
    check(v.unused_props, ["entry_gates", "tickets"])
    check(v.unused_classes, ["Zoo"])
    check(v.unused_vars, ["width", "depth"])


def test_noqa_properties_multiple_decorators(v):
    v.scan(
        """\
class Foo:
    @property
    @make_it_cool
    @log
    def something(self):  # noqa: V105
        pass

    @coolify
    @property
    def something_else(self):  # noqa: V105
        pass

    @a
    @property
    @b  # noqa
    def abcd(self):
        pass
"""
    )
    check(v.unused_props, ["abcd"])


def test_noqa_unreacahble_code(v):
    v.scan(
        """\
def shave_sheep(sheep):
    for a_sheep in sheep:
        if a_sheep.is_bald:
            continue
            a_sheep.grow_hair()  # noqa: V201
        a_sheep.shave()
    return
    for a_sheep in sheep:  # noqa: V201
        if a_sheep.still_has_hair:
            a_sheep.shave_again()
"""
    )
    check(v.unreachable_code, [])
    check(v.unused_funcs, ["shave_sheep"])


def test_noqa_variables(v):
    v.scan(
        """\
mitsi = "Mother"  # noqa: V106
harry = "Father"  # noqa
shero = "doggy"   # noqa: V101, V104 (code for unused import, attr)
shinchan.friend = ['masao']  # noqa: V106 (code for unused variable)
"""
    )
    check(v.unused_vars, ["shero"])
    check(v.unused_attrs, ["friend"])


def test_noqa_with_multiple_issue_codes(v):
    v.scan(
        """\
def world(axis):  # noqa: V103, V201
    pass


for _ in range(3):
    continue
    xyz = hello(something, else):  # noqa: V201, V106
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
