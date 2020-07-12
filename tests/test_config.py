"""
This module contains unit-tests for config file and CLI argument parsing
"""
from io import StringIO
from textwrap import dedent

from vulture.config import Config, _parse_args, _parse_toml


def test_cli_args():
    """
    Ensure that CLI arguments are converted to a config object
    """
    expected = dict(
        paths=["path1", "path2"],
        exclude=["exclude1", "exclude2"],
        ignore_decorators=["deco1", "deco2"],
        ignore_names=["name1", "name2"],
        make_whitelist=True,
        min_confidence=10,
        sort_by_size=True,
        verbose=True,
    )
    result = _parse_args([
        "--exclude=exclude1,exclude2",
        "--ignore-decorators=deco1,deco2",
        "--ignore-names=name1,name2",
        "--make-whitelist",
        "--min-confidence=10",
        "--sort-by-size",
        "--verbose",
        "path1",
        "path2",
    ])
    assert isinstance(result, Config)
    assert result == expected


def test_toml_config():
    """
    Ensure parsing of TOML files results in a valid config object
    """
    expected = dict(
        paths=["path1", "path2"],
        exclude=["exclude1", "exclude2"],
        ignore_decorators=["deco1", "deco2"],
        ignore_names=["name1", "name2"],
        make_whitelist=True,
        min_confidence=10,
        sort_by_size=True,
        verbose=True,
    )
    data = StringIO(dedent(
        u"""\
        [tool.vulture]
        exclude = ['exclude1', 'exclude2']
        ignore_decorators = ['deco1', 'deco2']
        ignore_names = ['name1', 'name2']
        make_whitelist = true
        min_confidence = 10
        sort_by_size = true
        verbose = true
        paths = ['path1', 'path2']
        """
    ))
    result = _parse_toml(data)
    assert isinstance(result, Config)
    assert result == expected
