from . import check, v

assert v  # Silence pyflakes.


def test_noqa_attributes(v):
    v.scan(
        """\
something.x = 'x'  # noqa: V001
something.z = 'z'  # noqa: V006 (code for unused variable)
something.u = 'u'  # noqa
"""
    )
    check(v.get_unused_code(), ["z"])


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
    check(v.get_unused_code(), ["ABC"])


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
    check(v.get_unused_code(), ["tune", "instrument", "problems"])


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
    check(v.get_unused_code(), ["foo", "zoo", "dis"])


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
    check(
        v.get_unused_code(),
        ["Zoo", "width", "depth", "entry_gates", "tickets"],
    )


def test_noqa_unreacahble_code(v):
    v.scan(
        """\
def shave_sheeps(sheeps):  # noqa: V003
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
    check(v.get_unused_code(), [])


def test_noqa_variables(v):
    v.scan(
        """\
mitsi = "Mother"  # noqa: V007
harry = "Father"  # noqa
shero = "doggy"   # noqa: V001, V004 (code for unused import, attr)
shinchan.friend = ['masao']  # noqa: V007
"""
    )
    check(v.get_unused_code(), ["shero", "friend"])


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
    check(v.get_unused_code(), ["this"])


def test_noqa_with_invalid_codes(v):
    v.scan(
        """\
import this  # V098, A123, F876
"""
    )
    check(v.get_unused_code(), ["this"])


def test_noqa_with_special_unicode(v):
    v.scan(
        """\
import abc  # noqa: V012, V😎12
import problems  # noqa: V03🙃1
"""
    )
    check(v.get_unused_code(), ["abc", "problems"])
