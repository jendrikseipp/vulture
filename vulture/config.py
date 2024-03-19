"""
This module handles retrieval of configuration values from either the
command-line arguments or the pyproject.toml file.
"""
import argparse
import pathlib

try:
    import tomllib
except ModuleNotFoundError:
    import tomli as tomllib

from .version import __version__

#: Possible configuration options and their respective defaults
DEFAULTS = {
    "config": "pyproject.toml",
    "min_confidence": 0,
    "paths": [],
    "exclude": [],
    "ignore_decorators": [],
    "ignore_names": [],
    "make_whitelist": False,
    "sort_by_size": False,
    "verbose": False,
}


class InputError(Exception):
    def __init__(self, message):
        self.message = message


def _check_input_config(data):
    """
    Checks the types of the values in *data* against the expected types of
    config-values. If a value has the wrong type, raise an InputError.
    """
    for key, value in data.items():
        if key not in DEFAULTS:
            raise InputError(f"Unknown configuration key: {key}")
        # The linter suggests to use "isinstance" here but this fails to
        # detect the difference between `int` and `bool`.
        if type(value) is not type(DEFAULTS[key]):  # noqa: E721
            expected_type = type(DEFAULTS[key]).__name__
            raise InputError(f"Data type for {key} must be {expected_type!r}")


def _check_output_config(config):
    """
    Run sanity checks on the generated config after all parsing and
    preprocessing is done.

    Raise InputError if an error is encountered.
    """
    if not config["paths"]:
        raise InputError("Please pass at least one file or directory")


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
    data = tomllib.load(infile)
    settings = data.get("tool", {}).get("vulture", {})
    _check_input_config(settings)
    return settings


def _parse_args(args=None):
    """
    Parse CLI arguments.

    :param args: A list of strings representing the CLI arguments. If left to
        the default, this will default to ``sys.argv``.
    """

    # Sentinel value to distinguish between "False" and "no default given".
    missing = object()

    def csv(exclude):
        return exclude.split(",")

    usage = "%(prog)s [options] [PATH ...]"
    version = f"vulture {__version__}"
    glob_help = "Patterns may contain glob wildcards (*, ?, [abc], [!abc])."
    parser = argparse.ArgumentParser(prog="vulture", usage=usage)
    parser.add_argument(
        "paths",
        nargs="*",
        metavar="PATH",
        default=missing,
        help="Paths may be Python files or directories. For each directory"
        " Vulture analyzes all contained *.py files.",
    )
    parser.add_argument(
        "--exclude",
        metavar="PATTERNS",
        type=csv,
        default=missing,
        help=f"Comma-separated list of path patterns to ignore (e.g.,"
        f' "*settings.py,docs,*/test_*.py,venv"). {glob_help} A PATTERN'
        f" without glob wildcards is treated as *PATTERN*. Patterns are"
        f" matched against absolute paths.",
    )
    parser.add_argument(
        "--ignore-decorators",
        metavar="PATTERNS",
        type=csv,
        default=missing,
        help=f"Comma-separated list of decorators. Functions and classes using"
        f' these decorators are ignored (e.g., "@app.route,@require_*").'
        f" {glob_help}",
    )
    parser.add_argument(
        "--ignore-names",
        metavar="PATTERNS",
        type=csv,
        default=missing,
        help=f'Comma-separated list of names to ignore (e.g., "visit_*,do_*").'
        f" {glob_help}",
    )
    parser.add_argument(
        "--make-whitelist",
        action="store_true",
        default=missing,
        help="Report unused code in a format that can be added to a"
        " whitelist module.",
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=missing,
        help="Minimum confidence (between 0 and 100) for code to be"
        " reported as unused.",
    )
    parser.add_argument(
        "--sort-by-size",
        action="store_true",
        default=missing,
        help="Sort unused functions and classes by their lines of code.",
    )
    parser.add_argument(
        "--config",
        type=str,
        default="pyproject.toml",
        help="Path to pyproject.toml config file.",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", default=missing
    )
    parser.add_argument("--version", action="version", version=version)
    namespace = parser.parse_args(args)
    cli_args = {
        key: value
        for key, value in vars(namespace).items()
        if value is not missing
    }
    _check_input_config(cli_args)
    return cli_args


def make_config(argv=None, tomlfile=None):
    """
    Returns a config object for vulture, merging both ``pyproject.toml`` and
    CLI arguments (CLI arguments have precedence).

    :param argv: The CLI arguments to be parsed. This value is transparently
        passed through to :py:meth:`argparse.ArgumentParser.parse_args`.
    :param tomlfile: An IO instance containing TOML data. By default this will
        auto-detect an existing ``pyproject.toml`` file and exists solely for
        unit-testing.
    """

    # Parse CLI first to skip sanity checks when --version or --help is given.
    cli_config = _parse_args(argv)

    # If we loaded data from a TOML file, we want to print this out on stdout
    # in verbose mode so we need to keep the value around.
    detected_toml_path = ""

    if tomlfile:
        config = _parse_toml(tomlfile)
        detected_toml_path = str(tomlfile)
    else:
        toml_path = pathlib.Path(cli_config["config"]).resolve()
        if toml_path.is_file():
            with open(toml_path, "rb") as fconfig:
                config = _parse_toml(fconfig)
            detected_toml_path = str(toml_path)
        else:
            config = {}

    # Overwrite TOML options with CLI options, if given.
    config.update(cli_config)

    # Set defaults for missing options.
    for key, value in DEFAULTS.items():
        config.setdefault(key, value)

    if detected_toml_path and config["verbose"]:
        print(f"Reading configuration from {detected_toml_path}")

    _check_output_config(config)

    return config
