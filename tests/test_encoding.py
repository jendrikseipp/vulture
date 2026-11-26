import codecs
import os
import sys

import pytest

from vulture.utils import ExitCode

from . import v

assert v  # Silence pyflakes.


def test_encoding1(v):
    v.scan(
        """\
# -*- coding: utf-8 -*-
pass
"""
    )
    assert v.exit_code == ExitCode.NoDeadCode


def test_encoding2(v):
    v.scan(
        """\
#! /usr/bin/env python
# -*- coding: utf-8 -*-
pass
"""
    )
    assert v.exit_code == ExitCode.NoDeadCode


def test_non_utf8_encoding(v, tmp_path):
    code = ""
    name = "non_utf8"
    non_utf_8_file = tmp_path / (name + ".py")
    with open(non_utf_8_file, mode="wb") as f:
        f.write(codecs.BOM_UTF16_LE)
        f.write(code.encode("utf_16_le"))
    v.scavenge([non_utf_8_file])
    assert v.exit_code == ExitCode.InvalidInput


def test_utf8_with_bom(v, tmp_path):
    name = "utf8_bom"
    filepath = tmp_path / (name + ".py")
    # utf8_sig prepends the BOM to the file.
    filepath.write_text("", encoding="utf-8-sig")
    v.scavenge([filepath])
    assert v.exit_code == ExitCode.NoDeadCode


@pytest.mark.skipif(
    sys.platform == "win32" or os.geteuid() == 0,
    reason="Unreadable files need POSIX permissions and a non-root user.",
)
def test_unreadable_file(v, tmp_path, capfd):
    filepath = tmp_path / "unreadable.py"
    filepath.write_text("import os\n")
    filepath.chmod(0o000)
    try:
        v.scavenge([filepath])
    finally:
        filepath.chmod(0o644)
    assert "Could not read file" in capfd.readouterr().err
    assert v.exit_code == ExitCode.InvalidInput
