import codecs

from . import v
assert v  # Silence pyflakes.


def test_encoding1(v):
    v.scan(u"""\
# -*- coding: utf-8 -*-
pass
""")
    assert not v.found_dead_code_or_error


def test_encoding2(v):
    v.scan(u"""\
#! /usr/bin/env python
# -*- coding: utf-8 -*-
pass
""")
    assert not v.found_dead_code_or_error


def test_non_utf8_encoding(v, tmpdir):
    code = ""
    non_utf_8_file = str(tmpdir.mkdir("non_utf8").join("non_utf8.py"))
    with open(non_utf_8_file, 'wb') as f:
        f.write(codecs.BOM_UTF16_LE)
        f.write(code.encode('utf_16_le'))
    v.scavenge([f.name])
    assert v.found_dead_code_or_error
