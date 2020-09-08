"""
Unit tests for config file and CLI argument parsing.
"""

from io import StringIO
from textwrap import dedent

import pytest

from vulture.config import (
    DEFAULTS,
    _check_input_config,
    _parse_args,
    _parse_toml,
    make_config,
)


def test_cli_args():
    """
    Ensure that CLI arguments are converted to a config object.
    """
    expected = dict(
        paths=["path1", "path2"],
        exclude=["file*.py", "dir/"],
        ignore_decorators=["deco1", "deco2"],
        ignore_names=["name1", "name2"],
        make_whitelist=True,
        min_confidence=10,
        sort_by_size=True,
        verbose=True,
    )
    result = _parse_args(
        [
            "--exclude=file*.py,dir/",
            "--ignore-decorators=deco1,deco2",
            "--ignore-names=name1,name2",
            "--make-whitelist",
            "--min-confidence=10",
            "--sort-by-size",
            "--verbose",
            "path1",
            "path2",
        ]
    )
    assert isinstance(result, dict)
    assert result == expected


def test_toml_config():
    """
    Ensure parsing of TOML files results in a valid config object.
    """
    expected = dict(
        paths=["path1", "path2"],
        exclude=["file*.py", "dir/"],
        ignore_decorators=["deco1", "deco2"],
        ignore_names=["name1", "name2"],
        make_whitelist=True,
        min_confidence=10,
        sort_by_size=True,
        verbose=True,
    )
    data = StringIO(
        dedent(
            """\
        [tool.vulture]
        exclude = ["file*.py", "dir/"]
        ignore_decorators = ["deco1", "deco2"]
        ignore_names = ["name1", "name2"]
        make_whitelist = true
        min_confidence = 10
        sort_by_size = true
        verbose = true
        paths = ["path1", "path2"]
        """
        )
    )
    result = _parse_toml(data)
    assert isinstance(result, dict)
    assert result == expected


def test_config_merging():
    """
    If we have both CLI args and a ``pyproject.toml`` file, the CLI args should
    have precedence.
    """
    toml = StringIO(
        dedent(
            """\
        [tool.vulture]
        exclude = ["toml_exclude"]
        ignore_decorators = ["toml_deco"]
        ignore_names = ["toml_name"]
        make_whitelist = false
        min_confidence = 10
        sort_by_size = false
        verbose = false
        paths = ["toml_path"]
        """
        )
    )
    cliargs = [
        "--exclude=cli_exclude",
        "--ignore-decorators=cli_deco",
        "--ignore-names=cli_name",
        "--make-whitelist",
        "--min-confidence=20",
        "--sort-by-size",
        "--verbose",
        "cli_path",
    ]
    result = make_config(cliargs, toml)
    expected = dict(
        paths=["cli_path"],
        exclude=["cli_exclude"],
        ignore_decorators=["cli_deco"],
        ignore_names=["cli_name"],
        make_whitelist=True,
        min_confidence=20,
        sort_by_size=True,
        verbose=True,
    )
    assert result == expected


def test_config_merging_missing():
    """
    If we have set a boolean value in the TOML file, but not on the CLI, we
    want the TOML value to be taken.
    """
    toml = StringIO(
        dedent(
            """\
        [tool.vulture]
        verbose = true
        ignore_names = ["name1"]
        """
        )
    )
    cliargs = [
        "cli_path",
    ]
    result = make_config(cliargs, toml)
    assert result["verbose"] is True
    assert result["ignore_names"] == ["name1"]


def test_config_merging_toml_paths_only():
    """
    If we have paths in the TOML but not on the CLI, the TOML paths should be
    used.
    """
    toml = StringIO(
        dedent(
            """\
        [tool.vulture]
        paths = ["path1", "path2"]
        """
        )
    )
    cliargs = [
        "--exclude=test_*.py",
    ]
    result = make_config(cliargs, toml)
    assert result["paths"] == ["path1", "path2"]
    assert result["exclude"] == ["test_*.py"]


def test_invalid_config_options_output():
    """
    If the config file contains unknown options we want to abort.
    """

    with pytest.raises(SystemExit):
        _check_input_config({"unknown_key_1": 1})


@pytest.mark.parametrize("key, value", list(DEFAULTS.items()))
def test_incompatible_option_type(key, value):
    """
    If a config value has a different type from the default value we abort.
    """
    wrong_types = {int, str, list, bool} - {type(value)}
    for wrong_type in wrong_types:
        test_value = wrong_type()
        with pytest.raises(SystemExit):
            _check_input_config({key: test_value})


def test_missing_paths():
    """
    If the script is run without any paths, we want to abort.
    """
    with pytest.raises(SystemExit):
        make_config([])
