import pytest

from vulture.core import ERROR_CODES
from vulture.noqa import (
    FLAKE8_NOQA_CODE_MAP,
    FLAKE8_NOQA_REGEXP,
    PYLINT_NOQA_CODE_MAP,
    PYLINT_NOQA_REGEXP,
    _parse_error_codes,
    _parse_pylint_codes,
)

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
    match = FLAKE8_NOQA_REGEXP.search(line)
    parsed = _parse_error_codes(match)
    assert parsed == codes


@pytest.mark.parametrize(
    "line",
    [
        "# noqa: 123V",
        "# noqa explanation: V012",
        "# noqa: ,V101",
        "# noqa: #noqa: V102",
        "# noqa: # noqa: V102",
    ],
)
def test_noqa_regex_no_groups(line):
    assert FLAKE8_NOQA_REGEXP.search(line).groupdict()["codes"] is None


@pytest.mark.parametrize(
    "line",
    ["#noqa", "##noqa", "# n o q a", "#NOQA", "# Hello, noqa"],
)
def test_noqa_regex_not_present(line):
    assert not FLAKE8_NOQA_REGEXP.search(line)


def test_noqa_without_codes(v):
    v.scan(
        """\
import this  # noqa

@underground  # noqa
class Cellar:
    @property  # noqa
    def wine(self):
        grapes = True  # noqa

    @without_ice  # noqa
    def serve(self, quantity=50):
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

@underground  # noqa: V102
class Cellar:
    @property  # noqa: V106
    def wine(self):
        grapes = True  # noqa: V107

    @without_ice  # noqa: V103
    def serve(self, quantity=50):
        self.quantity_served = quantity  # noqa: V101
        return
        self.pour()  # noqa: V201
"""
    )
    check(v.unused_attrs, [])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_methods, ["serve"])
    check(v.unused_props, [])
    check(v.unreachable_code, [])
    check(v.unused_vars, [])


def test_noqa_attributes(v):
    v.scan(
        """\
something.x = 'x'  # noqa: V101
something.z = 'z'  # noqa: V107 (code for unused variable)
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
    def no_of_koalas(self):  # noqa
        pass

    @property
    def area(self, width, depth):  # noqa: V105
        pass

    @property  # noqa
    def entry_gates(self):
        pass

    @property  # noqa: V103 (code for unused function)
    def tickets(self):
        pass
"""
    )
    check(v.unused_props, ["no_of_koalas", "area", "tickets"])
    check(v.unused_classes, ["Zoo"])
    check(v.unused_vars, ["width", "depth"])


def test_noqa_multiple_decorators(v):
    v.scan(
        """\
@bar  # noqa: V102
class Foo:
    @property  # noqa: V106
    @make_it_cool
    @log
    def something(self):
        pass

    @coolify
    @property
    def something_else(self):  # noqa: V106
        pass

    @a
    @property
    @b  # noqa
    def abcd(self):
        pass
"""
    )
    check(v.unused_props, ["something_else", "abcd"])
    check(v.unused_classes, [])


def test_noqa_unreachable_code(v):
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
mitsi = "Mother"  # noqa: V107
harry = "Father"  # noqa
shero = "doggy"   # noqa: V101, V104 (code for unused import, attr)
shinchan.friend = ['masao']  # noqa: V107 (code for unused variable)
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
    xyz = hello(something, else):  # noqa: V201, V107
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


@pytest.mark.parametrize(
    "first_file, second_file",
    [
        ("foo = None", "bar = None  # noqa"),
        ("bar = None  # noqa", "foo = None"),
    ],
)
def test_noqa_multiple_files(first_file, second_file, v):
    v.scan(first_file, filename="first_file.py")
    v.scan(second_file, filename="second_file.py")
    check(v.unused_vars, ["foo"])


def test_flake8_noqa_codes(v):
    assert FLAKE8_NOQA_CODE_MAP["F401"] == ERROR_CODES["import"]
    assert FLAKE8_NOQA_CODE_MAP["F841"] == ERROR_CODES["variable"]
    v.scan(
        """\
import this  # noqa: F401

def foo():
    bar = 2  # noqa: F841
"""
    )
    check(v.unused_funcs, ["foo"])
    check(v.unused_imports, [])
    check(v.unused_vars, [])


@pytest.mark.parametrize(
    "line, codes",
    [
        ("# pylint: disable=unused-import", ["unused-import"]),
        (
            "# pylint: disable=unused-import,unused-variable",
            ["unused-import", "unused-variable"],
        ),
        (
            "# pylint: disable=unused-import, unused-argument",
            ["unused-import", "unused-argument"],
        ),
        ("# pylint: disable-all", ["all"]),
        ("# pylint: disable-all  # comment", ["all"]),
        ("# Pylint: Disable=unused-import", ["unused-import"]),
    ],
)
def test_pylint_regex_present(line, codes):
    match = PYLINT_NOQA_REGEXP.search(line)
    assert match is not None, f"Regex should match: {line}"
    parsed = _parse_pylint_codes(match)
    assert parsed == codes, f"Expected {codes}, got {parsed}"


@pytest.mark.parametrize(
    "line",
    [
        # enable is not supported for extracting codes
        "# pylint: enable=unused-import",
        "# pylint: enable-all",
        "# PYLINT: ENABLE=something",
        # Incomplete or incorrect commands
        "# pylint: disable",  # without codes and not disable-all
        "# pylint: disable=",  # empty after =
        "# pylint:",  # only the start
        "# pylint: something-else",  # different command
        "# pylint: disable something",  # without =
        # Not pylint comments
        "# noqa: disable=unused-import",
        "# flake8: noqa",
        "# type: ignore",
        # Comments with other symbols
        "// pylint: disable=unused-import",  # not #
        "<!-- pylint: disable=unused-import -->",  # HTML comment
        # Too many spaces or incorrect format
        "#  pylint : disable = unused-import",  # spaces around :
        "#pylintdisable=unused-import",  # without spaces
    ],
)
def test_pylint_regex_not_present(line):
    match = PYLINT_NOQA_REGEXP.search(line)
    assert match is None or match.groupdict().get("codes") is None, (
        f"Regex should not match or have no codes: {line}"
    )


def test_pylint_code_map():
    assert PYLINT_NOQA_CODE_MAP["unused-import"] == ERROR_CODES["import"]
    assert PYLINT_NOQA_CODE_MAP["unused-variable"] == ERROR_CODES["variable"]
    assert PYLINT_NOQA_CODE_MAP["unused-argument"] == ERROR_CODES["variable"]
    assert (
        PYLINT_NOQA_CODE_MAP["possibly-unused-variable"]
        == ERROR_CODES["variable"]
    )
    assert (
        PYLINT_NOQA_CODE_MAP["unreachable-code"]
        == ERROR_CODES["unreachable_code"]
    )


def test_pylint_unused_import(v):
    v.scan(
        """\
import this  # pylint: disable=unused-import
import that  # pylint: disable=unused-import,unused-variable
import other
"""
    )
    check(v.unused_imports, ["other"])


def test_pylint_unused_variable(v):
    v.scan(
        """\
def foo():
    bar = 2  # pylint: disable=unused-variable
    baz = 3  # pylint: disable=possibly-unused-variable
    qux = 4
"""
    )
    check(v.unused_vars, ["qux"])


def test_pylint_unused_argument(v):
    v.scan(
        """\
def foo(x, y):  # pylint: disable=unused-argument
    pass

def bar(a, b):  # pylint: disable=unused-argument
    return a

def baz(c, d):
    return c
"""
    )
    check(v.unused_vars, ["d"])


def test_pylint_unreachable_code(v):
    v.scan(
        """\
def foo():
    return
    x = 1  # pylint: disable=unreachable-code

def bar():
    return
    y = 2  # pylint: disable=unreachable-code
"""
    )
    check(v.unreachable_code, [])


def test_pylint_disable_all(v):
    v.scan(
        """\
import this  # pylint: disable-all

@underground  # pylint: disable-all
class Cellar:
    @property  # pylint: disable-all
    def wine(self):
        grapes = True  # pylint: disable-all

    @without_ice  # pylint: disable-all
    def serve(self, quantity=50):
        self.quantity_served = quantity  # pylint: disable-all
        return
        self.pour()  # pylint: disable-all
"""
    )
    check(v.unused_attrs, [])
    check(v.unused_classes, [])
    check(v.unused_funcs, [])
    check(v.unused_imports, [])
    check(v.unused_props, [])
    check(v.unreachable_code, [])
    check(v.unused_vars, [])


def test_pylint_multiple_codes(v):
    v.scan(
        """\
import this  # pylint: disable=unused-import,unused-variable

def foo(x):  # pylint: disable=unused-argument
    bar = 2  # pylint: disable=unused-variable
    return
    baz = 3  # pylint: disable=unreachable-code,unused-variable
"""
    )
    check(v.unused_imports, [])
    check(v.unused_funcs, ["foo"])
    check(v.unused_vars, [])
    check(v.unreachable_code, [])


def test_pylint_with_noqa(v):
    v.scan(
        """\
import this  # noqa: F401
import that  # pylint: disable=unused-import
import other
"""
    )
    check(v.unused_imports, ["other"])


def test_pylint_numeric_codes(v):
    """Pylint numeric codes like W0641, W0613, etc"""
    v.scan(
        """\
import this  # pylint: disable=W0611

def foo(x, y):  # pylint: disable=W0613
    color = "red"  # pylint: disable=W0641
    return locals()

def bar(a, b):  # pylint: disable=W0613
    return a

def baz():
    return
    x = 1  # pylint: disable=W0101,W0612
"""
    )
    check(v.unused_imports, [])
    check(v.unused_vars, [])
    check(v.unreachable_code, [])


def test_pylint_mixed_numeric_and_text_codes(v):
    """Test mixing numeric and text pylint codes"""
    v.scan(
        """\
import this  # pylint: disable=W0611,unused-variable
import that  # pylint: disable=unused-import,W0612
"""
    )
    check(v.unused_imports, [])


def test_pylint_code_map_numeric():
    """Numeric pylint codes are correctly mapped"""
    from vulture.core import ERROR_CODES
    from vulture.noqa import PYLINT_NOQA_CODE_MAP

    assert PYLINT_NOQA_CODE_MAP["W0611"] == ERROR_CODES["import"]
    assert PYLINT_NOQA_CODE_MAP["W0612"] == ERROR_CODES["variable"]
    assert PYLINT_NOQA_CODE_MAP["W0613"] == ERROR_CODES["variable"]
    assert PYLINT_NOQA_CODE_MAP["W0641"] == ERROR_CODES["variable"]
    assert PYLINT_NOQA_CODE_MAP["W0101"] == ERROR_CODES["unreachable_code"]
