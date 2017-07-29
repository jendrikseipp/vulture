from . import v
assert v  # Silence pyflakes.


def test_syntax_error(v):
    v.scan("""foo bar""")
    assert int(v.report()) == 1
