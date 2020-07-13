"""
This module handles retrieval of configuration values from either the
command-line arguments or the pyproject.toml file.
"""
from __future__ import print_function
import argparse
import sys
from os.path import abspath, exists
from typing import Any, Dict

import toml

from .version import __version__


class Config(Dict[str, Any]):
    """
    A config object wrapping various variables and used to abstract away the
    difference between CLI-arg parsing and TOML loading.
    """

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

    def __getattribute__(self, name):
        if name in self:
            return self[name]
        return super(Config, self).__getattribute__(name)

    @staticmethod
    def from_dict(data):
        """
        Create a new config object from an existing dictionary, assign possible
        defaults and warn about unprocessed options.
        """
        # keep a copy of the keys, so we can keep track of any unprocessed
        # values.
        remaining_keys = set(data.keys())

        output = Config()
        for key, default in Config.DEFAULTS.items():
            output[key] = data.get(key, default)
            remaining_keys.discard(key)
        for remainder in sorted(remaining_keys):
            print("Unprocessed config option %r" % remainder, file=sys.stderr)
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
    return Config.from_dict(vulture_settings)


def _parse_args(args=None):
    """
    Parse CLI arguments

    :param args: A list of strings representing the CLI arguments. If left to
        the default, this will default to ``sys.argv``.
    """

    def csv(exclude):
        return exclude.split(",")

    usage = "%(prog)s [options] PATH [PATH ...]"
    version = "vulture {}".format(__version__)
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
        help="Comma-separated list of paths to ignore (e.g.,"
        ' "*settings.py,docs/*.py"). {glob_help} A PATTERN without glob'
        " wildcards is treated as *PATTERN*.".format(**locals()),
    )
    parser.add_argument(
        "--ignore-decorators",
        metavar="PATTERNS",
        type=csv,
        help="Comma-separated list of decorators. Functions and classes using"
        ' these decorators are ignored (e.g., "@app.route,@require_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument(
        "--ignore-names",
        metavar="PATTERNS",
        type=csv,
        default=Config.DEFAULTS["ignore_names"],
        help='Comma-separated list of names to ignore (e.g., "visit_*,do_*").'
        " {glob_help}".format(**locals()),
    )
    parser.add_argument(
        "--make-whitelist",
        action="store_true",
        help="Report unused code in a format that can be added to a"
        " whitelist module.",
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=Config.DEFAULTS["min_confidence"],
        help="Minimum confidence (between 0 and 100) for code to be"
        " reported as unused.",
    )
    parser.add_argument(
        "--sort-by-size",
        action="store_true",
        help="Sort unused functions and classes by their lines of code.",
    )
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--version", action="version", version=version)
    namespace = parser.parse_args(args)
    return Config.from_dict(vars(namespace))


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
    cli_config = _parse_args(argv)

    if tomlfile:
        toml_config = _parse_toml(tomlfile)
    else:
        toml_path = abspath("pyproject.toml")
        if exists(toml_path):
            if cli_config.verbose:
                print("Reading config values from %r" % toml_path)
            with open(toml_path) as toml_config:
                toml_config = _parse_toml(toml_config)
        else:
            toml_config = {}
    toml_config.update(cli_config)
    return toml_config
