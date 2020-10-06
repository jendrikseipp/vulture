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


def test_non_utf8_encoding(v, tmp_path):
    code = ""
    name = "non_utf8"
    non_utf_8_file = tmp_path / (name + ".py")
    with open(non_utf_8_file, mode="wb") as f:
        f.write(codecs.BOM_UTF16_LE)
        f.write(code.encode("utf_16_le"))
    v.scavenge([non_utf_8_file])
    assert v.found_dead_code_or_error


def test_utf8_with_bom(v, tmp_path):
    name = "utf8_bom"
    filepath = tmp_path / (name + ".py")
    # utf8_sig prepends the BOM to the file.
    filepath.write_text("", encoding="utf-8-sig")
    v.scavenge([filepath])
    assert not v.found_dead_code_or_error
