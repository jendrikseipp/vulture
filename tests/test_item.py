from . import v
assert v  # Silence pyflakes


def test_item_repr(v):
    v.scan("""\
import os

message = "foobar"

class Foo:
    def bar():
        pass
""")
    for item in v.get_unused_code():
        assert repr(item) == "'{}'".format(item.name)
