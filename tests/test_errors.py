import codecs

import pytest

from . import v
assert v  # Silence pyflakes.


def test_syntax_error(v):
    v.scan("foo bar")
    assert int(v.report()) == 1


def test_null_byte(v):
    v.scan("\x00")
    assert int(v.report()) == 1


def test_confidence_range(v):
    v.scan("""\
def foo():
    pass
""")
    with pytest.raises(ValueError):
        v.get_unused_code(min_confidence=150)


def test_non_utf8_encoding(v, tmpdir):
    code = """\
def foo():
    pass

foo()
"""
    non_utf_8_file = str(tmpdir.mkdir("non_utf8").join("non_utf8.py"))
    with open(non_utf_8_file, 'wb') as f:
        f.write(codecs.BOM_UTF16_LE)
        f.write(code.encode('utf_16_le'))
    v.scavenge([f.name])
    assert v.found_dead_code_or_error
