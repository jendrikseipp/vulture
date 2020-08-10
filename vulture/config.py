"""
This module handles retrieval of configuration values from either the
command-line arguments or the pyproject.toml file.
"""
import argparse
import sys
from os.path import abspath, exists

import toml

from .version import __version__

#: Possible configuration options and their respective defaults
DEFAULTS = {
    "min_confidence": 0,
    "paths": [],
    "exclude": [],
    "ignore_decorators": [],
    "ignore_names": [],
    "make_whitelist": False,
    "sort_by_size": False,
    "verbose": False,
}

#: sentinel value to distinguish between "False" and "no default given"
NO_DEFAULT = object()


def _check_config_types(data):
    """
    Checks the types of the values in *data* against the expected types of
    config-values. If a value is of the wrong type it will raise a SystemExit.
    """
    given_types = {
        (key, type(value))
        for key, value in data.items()
        if key in DEFAULTS and value is not NO_DEFAULT
    }
    expected_types = {(key, type(value)) for key, value in DEFAULTS.items()}
    incorrect_types = given_types - expected_types
    if incorrect_types:
        keys = ", ".join(sorted(item[0] for item in incorrect_types))
        msg = f"Incorrect data-types for the config values: {keys}"
        sys.exit(msg)


def from_dict(data):
    """
    Create a new config dictionary from an existing one, assign possible
    defaults and warn about unprocessed options.
    """
    _check_config_types(data)

    # keep a copy of the keys, so we can keep track of any unprocessed
    # values.
    unknown_keys = set(data) - set(DEFAULTS)
    if unknown_keys:
        print(
            f"Unknown configuration keys: {sorted(unknown_keys)}",
            file=sys.stderr,
        )
        sys.exit("invalid Config")

    output = {}
    for key, default in DEFAULTS.items():
        output[key] = data.get(key, default)
    return output


def _parse_toml(infile):
    """
    Parse a TOML file for config values.

    It will search for a section named ``[tool.vulture]`` which contains the
    same keys as the CLI arguments seen with ``--help``. All leading dashes are
    removed and other dashes are replaced by underscores (so ``--sort-by-size``
    becomes ``sort_by_size``).

    Arguments containing multiple values are standard TOML lists.

    Example::

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
    data = toml.load(infile)
    vulture_settings = data.get("tool", {}).get("vulture", {})
    return from_dict(vulture_settings)


def _parse_args(args=None):
    """
    Parse CLI arguments

    :param args: A list of strings representing the CLI arguments. If left to
        the default, this will default to ``sys.argv``.
    """

    def csv(exclude):
        return exclude.split(",")

    usage = "%(prog)s [options] PATH [PATH ...]"
    version = f"vulture {__version__}"
    glob_help = "Patterns may contain glob wildcards (*, ?, [abc], [!abc])."
    parser = argparse.ArgumentParser(prog="vulture", usage=usage)
    parser.add_argument(
        "paths",
        nargs="+",
        metavar="PATH",
        help="Paths may be Python files or directories. For each directory"
        " Vulture analyzes all contained *.py files.",
    )
    parser.add_argument(
        "--exclude",
        metavar="PATTERNS",
        type=csv,
        default=[],
        help="Comma-separated list of paths to ignore (e.g.,"
        ' "*settings.py,docs/*.py"). {glob_help} A PATTERN without glob'
        " wildcards is treated as *PATTERN*.".format(**locals()),
    )
    parser.add_argument(
        "--ignore-decorators",
        metavar="PATTERNS",
        type=csv,
        default=[],
        help="Comma-separated list of decorators. Functions and classes using"
        ' these decorators are ignored (e.g., "@app.route,@require_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument(
        "--ignore-names",
        metavar="PATTERNS",
        type=csv,
        default=DEFAULTS["ignore_names"],
        help='Comma-separated list of names to ignore (e.g., "visit_*,do_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument(
        "--make-whitelist",
        action="store_true",
        default=NO_DEFAULT,
        help="Report unused code in a format that can be added to a"
        " whitelist module.",
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=DEFAULTS["min_confidence"],
        help="Minimum confidence (between 0 and 100) for code to be"
        " reported as unused.",
    )
    parser.add_argument(
        "--sort-by-size",
        action="store_true",
        default=NO_DEFAULT,
        help="Sort unused functions and classes by their lines of code.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=NO_DEFAULT
    )
    parser.add_argument("--version", action="version", version=version)
    namespace = parser.parse_args(args)
    return from_dict(vars(namespace))


def make_config(argv=None, tomlfile=None):
    """
    Returns a config object for vulture, merging both ``pyproject.toml`` and
    CLI arguments (CLI will have precedence).

    :param argv: The CLI arguments to be parsed. This value is transparently
        passed through to :py:meth:`argparse.ArgumentParser.parse_args`
    :param tomlfile: An IO instance containing TOML data. By default this will
        auto-detect an existing ``pyproject.toml`` file and exists solely for
        unit-testing.
    """
    # If we loaded data from a TOML file, we want to print this out on stdout
    # in verbose mode so we need to keep the value around.
    detected_toml_path = ""

    if tomlfile:
        config = _parse_toml(tomlfile)
        detected_toml_path = str(tomlfile)
    else:
        toml_path = abspath("pyproject.toml")
        if exists(toml_path):
            with open(toml_path) as config:
                config = _parse_toml(config)
            detected_toml_path = toml_path
        else:
            config = {}

    # We can't use a simple call to dict.update() because some values should
    # not be overwritten in the config. More precisely, if the values have "no
    # real default" in the CLI args, they should not be taken into
    # consideration.
    cli_config = _parse_args(argv)
    for key in config.keys():
        cli_value = cli_config.get(key, NO_DEFAULT)
        if cli_value is not NO_DEFAULT:
            config[key] = cli_value

    if detected_toml_path and config["verbose"]:
        print(f"Reading configuration from {detected_toml_path}")

    return config
