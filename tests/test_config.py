"""
This module contains unit-tests for config file and CLI argument parsing
"""
from io import StringIO
from textwrap import dedent
from itertools import permutations

import pytest
from vulture.config import (
    DEFAULTS,
    _parse_args,
    _parse_toml,
    from_dict,
    make_config,
)

#: This dictionary maps types to "incompatible" types in the config. It is used
#: later for parametrizing a test.
WRONG_TYPES = dict(permutations([int, str, list, bool], 2))


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


def test_config_merging_boolan():
    """
    If we have set a boolean value in the TOML file, but not on the CLI, we
    want the TOML value to be taken.

    We'll take the "verbose" flag as example in this test.
    """
    toml = StringIO(
        dedent(
            """\
        [tool.vulture]
        verbose = true
        """
        )
    )
    cliargs = [
        "cli_path",
    ]
    result = make_config(cliargs, toml)
    assert result["verbose"] is True


def test_invalid_config_options_output(capsys):
    """
    If the config file contains unknown options we want to get a non-zero exit
    codew, see them on stderr and not see anything on stdout.
    """

    with pytest.raises(SystemExit) as ext:
        from_dict({"unknown_key_1": 1})
    stdout, stderr = capsys.readouterr()
    assert stdout == ""
    assert "unknown_key_1" in stderr
    assert ext.value.code != 0


@pytest.mark.parametrize(
    "key, wrong_type",
    [(key, WRONG_TYPES[type(value)]) for key, value in DEFAULTS.items()],
)
def test_incompatible_option_type(key, wrong_type):
    """
    If a config value has a different type from the default value we should
    exit with an error-code
    """
    test_value = wrong_type()
    with pytest.raises(SystemExit):
        from_dict({key: test_value})


def test_missing_paths():
    """
    If the script is run without any paths, we want to see a helpful error
    message
    """
    with pytest.raises(SystemExit):
        make_config([])
