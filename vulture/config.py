"""
This module handles retrieval of configuration values from either the
command-line arguments or the pyproject.toml file.
"""
# pylint: disable=bad-continuation
import argparse
from os.path import exists
from typing import Any, Dict, List, Optional
from typing.io import TextIO

import toml

from .version import __version__

MIN_CONFIDENCE_DEFAULT = 0


def _parse_toml(infile):
    # type: (TextIO) -> Config
    """
    Parse a TOML file for config values.

    It will search for a section named ``[tool.vulture]`` which contains the
    same keys as the CLI arguments seen with ``--help``. All leading dashes are
    removed and other dashes are replaced by underscores (so ``--sort-by-size``
    becomes ``sort_by_size``).

    Arguments containing multiple values are standard TOML lists.

    Example::

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
    data = toml.load(infile)
    vulture_settings = data.get("tool", {}).get("vulture", {})
    output = Config(
        paths=vulture_settings.get("paths", []),
        exclude=vulture_settings.get("exclude", []),
        ignore_decorators=vulture_settings.get("ignore_decorators", []),
        ignore_names=vulture_settings.get("ignore_names", []),
        make_whitelist=vulture_settings.get("make_whitelist", False),
        min_confidence=vulture_settings.get(
            "min_confidence", MIN_CONFIDENCE_DEFAULT),
        sort_by_size=vulture_settings.get("sort_by_size", False),
        verbose=vulture_settings.get("verbose", False),
    )
    return output


def _parse_args(args=None):
    # type: (Optional[List[str]]) -> Config
    """
    Parse CLI arguments

    :param args: A list of strings representing the CLI arguments. If left to
        the default, this will default to sys.argv
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
        default=None,
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
        default=MIN_CONFIDENCE_DEFAULT,
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
    output = Config(
        paths=namespace.paths,
        exclude=namespace.exclude,
        ignore_decorators=namespace.ignore_decorators,
        ignore_names=namespace.ignore_names,
        make_whitelist=namespace.make_whitelist,
        min_confidence=namespace.min_confidence,
        sort_by_size=namespace.sort_by_size,
        verbose=namespace.verbose,
    )
    return output


class Config(Dict[str, Any]):
    """
    A config object wrapping various variables and used to abstract away the
    difference between CLI-arg parsing and TOML loading.
    """
    # pylint: disable=too-many-arguments, too-few-public-methods
    # pylint: disable=useless-object-inheritance
    # pylint: disable=too-many-instance-attributes

    def __getattribute__(self, name):
        # type: (str) -> Any
        if name in self:
            return self[name]
        return super(Config, self).__getattribute__(name)


def make_config():
    # type: () -> Config
    """
    Returns a config object for vulture, merging both ``pyproject.toml`` and
    CLI arguments (CLI will have precedence).
    """
    if exists("pyproject.toml"):
        with open("pyproject.toml") as toml_config:
            app_config = _parse_toml(toml_config)
    cli_config = _parse_args()
    app_config.update(cli_config)
    return app_config
