# 2.12 (2024-09-17)

* Use `ruff` for linting and formatting (Anh Trinh, #347, #349).
* Replace `tox` by `pre-commit` for linting and formatting (Anh Trinh, #349).
* Add `--config` flag to specify path to pyproject.toml configuration file (Glen Robertson, #352).

# 2.11 (2024-01-06)

* Switch to tomllib/tomli to support heterogeneous arrays (Sebastian Csar, #340).
* Bump flake8, flake8-comprehensions and flake8-bugbear (Sebastian Csar, #341).
* Provide whitelist parity for `MagicMock` and `Mock` (maxrake, #342).

# 2.10 (2023-10-06)

* Drop support for Python 3.7 (Jendrik Seipp, #323).
* Add support for Python 3.12 (Jendrik Seipp, #332).
* Use `end_lineno` AST attribute to obtain more accurate line counts (Jendrik Seipp).

# 2.9.1 (2023-08-21)

* Use exit code 0 for `--help` and `--version` again (Jendrik Seipp, #321).

# 2.9 (2023-08-20)

* Use exit code 3 when dead code is found (whosayn, #319).
* Treat non-supported decorator names as "@" instead of crashing (Llandy3d and Jendrik Seipp, #284).
* Drop support for Python 3.6 (Jendrik Seipp).

# 2.8 (2023-08-10)

* Add `UnicodeEncodeError` exception handling to `core.py` (milanbalazs, #299).
* Add whitelist for `Enum` attributes `_name_` and `_value_` (Eugene Toder, #305).
* Run tests and add PyPI trove for Python 3.11 (Jendrik Seipp).

# 2.7 (2023-01-08)

* Ignore `setup_module()`, `teardown_module()`, etc. in pytest `test_*.py` files (Jendrik Seipp).
* Add whitelist for `socketserver.TCPServer.allow_reuse_address` (Ben Elliston).
* Clarify that `--exclude` patterns are matched against absolute paths (Jendrik Seipp, #260).
* Fix example in README file (Jendrik Seipp, #272).

# 2.6 (2022-09-19)

* Add basic `match` statement support (kreathon, #276, #291).

# 2.5 (2022-07-03)

* Mark imports in `__all__` as used (kreathon, #172, #282).
* Add whitelist for `pint.UnitRegistry.default_formatter` (Ben Elliston, #258).

# 2.4 (2022-05-19)

* Print absolute filepaths as relative again (as in version 2.1 and before)
  if they are below the current directory (The-Compiler, #246).
* Run tests and add PyPI trove for Python 3.10 (chayim, #266).
* Allow using the `del` keyword to mark unused variables (sshishov, #279).

# 2.3 (2021-01-16)

* Add [pre-commit](https://pre-commit.com) hook (Clément Robert, #244).

# 2.2 (2021-01-15)

* Only parse format strings when being used with `locals()` (jingw, #225).
* Don't override paths in pyproject.toml with empty CLI paths (bcbnz, #228).
* Run continuous integration tests for Python 3.9 (ju-sh, #232).
* Use pathlib internally (ju-sh, #226).

# 2.1 (2020-08-19)

* Treat `getattr/hasattr(obj, "constant_string", ...)` as a reference to
  `obj.constant_string` (jingw, #219).
* Fix false positives when assigning to `x.some_name` but reading via
  `some_name`, at the cost of potential false negatives (jingw, #221).
* Allow reading options from `pyproject.toml` (Michel Albert, #164, #215).

# 2.0 (2020-08-11)

* Parse `# type: ...` comments if on Python 3.8+ (jingw, #220).
* Bump minimum Python version to 3.6 (Jendrik Seipp, #218). The last
  Vulture release that supports Python 2.7 and Python 3.5 is version 1.6.
* Consider all files under `test` or `tests` directories test files
  (Jendrik Seipp).
* Ignore `logging.Logger.propagate` attribute (Jendrik Seipp).

# 1.6 (2020-07-28)

* Differentiate between functions and methods (Jendrik Seipp, #112, #209).
* Move from Travis to GitHub actions (RJ722, #211).

# 1.5 (2020-05-24)

* Support flake8 "noqa" error codes F401 (unused import) and F841 (unused
  local variable) (RJ722, #195).
* Detect unreachable code in conditional expressions
  (Agathiyan Bragadeesh, #178).

# 1.4 (2020-03-30)

* Ignore unused import statements in `__init__.py` (RJ722, #192).
* Report first decorator's line number for unused decorated objects on
  Python 3.8+ (RJ722, #200).
* Check code with black and pyupgrade.

# 1.3 (2020-02-03)

* Detect redundant 'if' conditions without 'else' blocks.
* Add whitelist for `string.Formatter` (Joseph Bylund, #183).

# 1.2 (2019-11-22)

* Fix tests for Python 3.8 (#166).
* Use new `Constant` AST node under Python 3.8+ (#175).
* Add test for f-strings (#177).
* Add whitelist for `logging` module.

# 1.1 (2019-09-23)

* Add `sys.excepthook` to `sys` whitelist.
* Add whitelist for `ctypes` module.
* Check that type annotations are parsed and type comments are ignored
  (thanks @kx-chen).
* Support checking files with BOM under Python 2.7 (#170).

# 1.0 (2018-10-23)

* Add `--ignore-decorators` flag (thanks @RJ722).
* Add whitelist for `threading` module (thanks @andrewhalle).

# 0.29 (2018-07-31)

* Add `--ignore-names` flag for ignoring names matching the given glob
  patterns (thanks @RJ722).

# 0.28 (2018-07-05)

* Add `--make-whitelist` flag for reporting output in whitelist format
  (thanks @RJ722).
* Ignore case of `--exclude` arguments on Windows.
* Add `*-test.py` to recognized test file patterns.
* Add `failureException`, `longMessage` and `maxDiff` to `unittest`
  whitelist.
* Refer to actual objects rather than their mocks in default
  whitelists (thanks @RJ722).
* Don't import any Vulture modules in setup.py (thanks @RJ722).

# 0.27 (2018-06-05)

* Report `while (True): ... else: ...` as unreachable (thanks @RJ722).
* Use `argparse` instead of `optparse`.
* Whitelist Mock.return\_value and Mock.side\_effect in unittest.mock
  module.
* Drop support for Python 2.6 and 3.3.
* Improve documentation and test coverage (thanks @RJ722).

# 0.26 (2017-08-28)

* Detect `async` function definitions (thanks @RJ722).
* Add `Item.get_report()` method (thanks @RJ722).
* Move method for finding Python modules out of Vulture class.

# 0.25 (2017-08-15)

* Detect unsatisfiable statements containing `and`, `or` and `not`.
* Use filenames and line numbers as tie-breakers when sorting by size.
* Store first and last line numbers in Item objects.
* Pass relevant options directly to `scavenge()` and `report()`.

# 0.24 (2017-08-14)

* Detect unsatisfiable `while`-conditions (thanks @RJ722).
* Detect unsatisfiable `if`- and `else`-conditions (thanks @RJ722).
* Handle null bytes in source code.

# 0.23 (2017-08-10)

* Add `--min-confidence` flag (thanks @RJ722).

# 0.22 (2017-08-04)

* Detect unreachable code after `return`, `break`, `continue` and
  `raise` (thanks @RJ722).
* Parse all variable and attribute names in new format strings.
* Extend ast whitelist.

# 0.21 (2017-07-26)

* If an unused item is defined multiple times, report it multiple
  times.
* Make size estimates for function calls more accurate.
* Create wheel files for Vulture (thanks @RJ722).

# 0.20 (2017-07-26)

* Report unused tuple assignments as dead code.
* Report attribute names that have the same names as variables as dead
  code.
* Let Item class inherit from `object` (thanks @RJ722).
* Handle names imported as aliases like all other used variable names.
* Rename Vulture.used\_vars to Vulture.used\_names.
* Use function for determining which imports to ignore.
* Only try to import each whitelist file once.
* Store used names and used attributes in sets instead of lists.
* Fix estimating the size of code containing ellipses (...).
* Refactor and simplify code.

# 0.19 (2017-07-20)

* Don't ignore <span class="title-ref">\_\_foo</span> variable names.
* Use separate methods for determining whether to ignore classes and
  functions.
* Only try to find a whitelist for each defined import once (thanks
  @roivanov).
* Fix finding the last child for many types of AST nodes.

# 0.18 (2017-07-17)

* Make <span class="title-ref">--sort-by-size</span> faster and more
  accurate (thanks @RJ722).

# 0.17 (2017-07-17)

* Add <span class="title-ref">get\_unused\_code()</span> method.
* Return with exit code 1 when syntax errors are found or files can't
  be read.

# 0.16 (2017-07-12)

* Differentiate between unused classes and functions (thanks @RJ722).
* Add --sort-by-size option (thanks @jackric and @RJ722).
* Count imports as used if they are accessed as module attributes.

# 0.15 (2017-07-04)

* Automatically include whitelists based on imported modules (thanks
  @RJ722).
* Add --version parameter (thanks @RJ722).
* Add appveyor tests for testing on Windows (thanks @RJ722).

# 0.14 (2017-04-06)

* Add stub whitelist file for Python standard library (thanks @RJ722)
* Ignore class names starting with "Test" in "test\_" files (thanks
  @thisch).
* Ignore "test\_" functions only in "test\_" files.

# 0.13 (2017-03-06)

* Ignore star-imported names since we cannot detect whether they are
  used.
* Move repository to GitHub.

# 0.12 (2017-01-05)

* Detect unused imports.
* Use tokenize.open() on Python \>= 3.2 for reading input files,
  assume UTF-8 encoding on older Python versions.

# 0.11 (2016-11-27)

* Use the system's default encoding when reading files.
* Report syntax errors instead of aborting.

# 0.10 (2016-07-14)

* Detect unused function and method arguments (issue #15).
* Detect unused \*args and \*\*kwargs parameters.
* Change license from GPL to MIT.

# 0.9 (2016-06-29)

* Don't flag attributes as unused if they are used as global variables
  in another module (thanks Florian Bruhin).
* Don't consider "True" and "False" variable names.
* Abort with error message when invoked on .pyc files.

# 0.8.1 (2015-09-28)

* Fix code for Python 3.

# 0.8 (2015-09-28)

* Do not flag names imported with "import as" as dead code (thanks Tom
  Terrace).

# 0.7 (2015-09-26)

* Exit with exitcode 1 if path on commandline can't be found.
* Test vulture with vulture using a whitelist module for false
  positives.
* Add tests that run vulture as a script.
* Add "python setup.py test" command for running tests.
* Add support for tox.
* Raise test coverage to 100%.
* Remove ez\_setup.py.

# 0.6 (2014-09-06)

* Ignore function names starting with "test\_".
* Parse variable names in new format strings (e.g. "This is
  {x}".format(x="nice")).
* Only parse alphanumeric variable names in format strings and ignore
  types.
* Abort with exit code 1 on syntax errors.
* Support installation under Windows by using setuptools (thanks
  Reuben Fletcher-Costin).

# 0.5 (2014-05-09)

* If dead code is found, exit with 1.

# 0.4.1 (2013-09-17)

* Only warn if a path given on the command line cannot be found.

# 0.4 (2013-06-23)

* Ignore unused variables starting with an underscore.
* Show warning for syntax errors instead of aborting directly.
* Print warning if a file cannot be found.

# 0.3 (2012-03-19)

* Add support for python3
* Report unused attributes
* Find tuple assignments in comprehensions
* Scan files given on the command line even if they don't end with .py

# 0.2 (2012-03-18)

* Only format nodes in verbose mode (gives 4x speedup).

# 0.1 (2012-03-17)

* First release.
