from . import v


def test_syntax_error(v):
    v.scan("""foo bar""")
    assert int(v.report()) == 1
