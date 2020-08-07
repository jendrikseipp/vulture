import codecs

from . import v

assert v  # Silence pyflakes.


def test_encoding1(v):
    v.scan(
        """\
# -*- coding: utf-8 -*-
pass
"""
    )
    assert not v.found_dead_code_or_error


def test_encoding2(v):
    v.scan(
        """\
#! /usr/bin/env python
# -*- coding: utf-8 -*-
pass
"""
    )
    assert not v.found_dead_code_or_error


def test_non_utf8_encoding(v, tmpdir):
    code = ""
    name = "non_utf8"
    non_utf_8_file = str(tmpdir.mkdir(name).join(name + ".py"))
    with open(non_utf_8_file, mode="wb") as f:
        f.write(codecs.BOM_UTF16_LE)
        f.write(code.encode("utf_16_le"))
    v.scavenge([f.name])
    assert v.found_dead_code_or_error


def test_utf8_with_bom(v, tmpdir):
    name = "utf8_bom"
    filename = str(tmpdir.mkdir(name).join(name + ".py"))
    # utf8_sig prepends the BOM to the file.
    with open(filename, mode="w", encoding="utf-8-sig") as f:
        f.write("")
    v.scavenge([f.name])
    assert not v.found_dead_code_or_error
