from . import v
assert v


def test_confidence_import(v):
    v.scan("""\
import foo
a = 1
""")
    assert v.unused_imports[0].confidence == 0.9


def test_confidence_unreachable(v):
    v.scan("""\
def foo():
    return
    bar()

foo()
""")
    assert v.unreachable_code[0].confidence == 1


def test_confidence_others(v):
    v.scan("""
a = 1

def foo():
    pass


class Foo:

    self.b = 'something'

    @property
    def some_prop():
        pass

""")
    assert v.unused_funcs[0].confidence == 0.6
    assert v.unused_classes[0].confidence == 0.6
    assert v.unused_vars[0].confidence == 0.6
    assert v.unused_props[0].confidence == 0.6
    assert v.unused_attrs[0].confidence == 0.6
