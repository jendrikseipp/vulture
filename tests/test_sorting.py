from . import v
assert v  # Silence pyflakes


def test_sorting(v):
    v.scan("""\
def foo():
    print("Hello, I am a long function.")
    return "World"

def bar():
    pass
""")
    assert [item.name for item in
            v.get_unused_code(sort_by_size=True)] == ['bar', 'foo']
    assert [item.name for item in
            v.get_unused_code(sort_by_size=False)] == ['foo', 'bar']
