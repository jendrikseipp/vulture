from . import check, v

assert v  # Silence pyflakes.


def test_typed_dict_members_not_reported(v):
    # Members of a typing.TypedDict are type annotations, not runtime values,
    # so neither the class nor its members should be reported as unused.
    v.scan(
        """\
import typing

class ExampleTypedDict(typing.TypedDict):
    field1: int
    field2: str
"""
    )
    check(v.unused_vars, [])
    check(v.unused_classes, [])


def test_typed_dict_from_typing_extensions_not_reported(v):
    v.scan(
        """\
from typing_extensions import TypedDict

class ExampleTypedDict(TypedDict):
    field1: int
    field2: str
"""
    )
    check(v.unused_vars, [])
    check(v.unused_classes, [])


def test_typed_dict_with_total_false_not_reported(v):
    v.scan(
        """\
from typing import TypedDict

class ExampleTypedDict(TypedDict, total=False):
    field1: int
    field2: str
"""
    )
    check(v.unused_vars, [])
    check(v.unused_classes, [])


def test_normal_class_attribute_still_reported(v):
    # Make sure we did not disable unused-attribute detection for normal
    # classes in the process of fixing TypedDict handling (issue #335).
    v.scan(
        """\
class Foo:
    used: int
    unused: int

    def method(self):
        return self.used
"""
    )
    check(v.unused_vars, ["unused"])
