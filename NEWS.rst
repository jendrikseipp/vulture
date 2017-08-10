News
====

0.23 (2017-08-10)
-----------------
* Add ``--min-confidence`` flag (thanks @RJ722).


0.22 (2017-08-04)
-----------------
* Detect unreachable code after ``return``, ``break``, ``continue`` and
  ``raise`` (thanks @RJ722).
* Parse all variable and attribute names in new format strings.
* Extend ast whitelist.


0.21 (2017-07-26)
-----------------
* If an unused item is defined multiple times, report it multiple times.
* Make size estimates for function calls more accurate.
* Create wheel files for Vulture (thanks @RJ722).


0.20 (2017-07-26)
-----------------
* Report unused tuple assignments as dead code.
* Report attribute names that have the same names as variables as dead code.
* Let Item class inherit from ``object`` (thanks @RJ722).
* Handle names imported as aliases like all other used variable names.
* Rename Vulture.used_vars to Vulture.used_names.
* Use function for determining which imports to ignore.
* Only try to import each whitelist file once.
* Store used names and used attributes in sets instead of lists.
* Fix estimating the size of code containing ellipses (...).
* Refactor and simplify code.


0.19 (2017-07-20)
-----------------
* Don't ignore `__foo` variable names.
* Use separate methods for determining whether to ignore classes and functions.
* Only try to find a whitelist for each defined import once (thanks @roivanov).
* Fix finding the last child for many types of AST nodes.


0.18 (2017-07-17)
-----------------
* Make `--sort-by-size` faster and more accurate (thanks @RJ722).


0.17 (2017-07-17)
-----------------
* Add `get_unused_code()` method.
* Return with exit code 1 when syntax errors are found or files can't be read.


0.16 (2017-07-12)
-----------------
* Differentiate between unused classes and functions (thanks @RJ722).
* Add --sort-by-size option (thanks @jackric and @RJ722).
* Count imports as used if they are accessed as module attributes.


0.15 (2017-07-04)
-----------------
* Automatically include whitelists based on imported modules (thanks @RJ722).
* Add --version parameter (thanks @RJ722).
* Add appveyor tests for testing on Windows (thanks @RJ722).


0.14 (2017-04-06)
-----------------
* Add stub whitelist file for Python standard library (thanks @RJ722)
* Ignore class names starting with "Test" in "test\_" files (thanks @thisch).
* Ignore "test\_" functions only in "test\_" files.


0.13 (2017-03-06)
-----------------
* Ignore star-imported names since we cannot detect whether they are used.
* Move repository to GitHub.


0.12 (2017-01-05)
-----------------
* Detect unused imports.
* Use tokenize.open() on Python >= 3.2 for reading input files, assume
  UTF-8 encoding on older Python versions.


0.11 (2016-11-27)
-----------------
* Use the system's default encoding when reading files.
* Report syntax errors instead of aborting.


0.10 (2016-07-14)
-----------------
* Detect unused function and method arguments (issue #15).
* Detect unused \*args and \*\*kwargs parameters.
* Change license from GPL to MIT.


0.9 (2016-06-29)
----------------
* Don't flag attributes as unused if they are used as global variables
  in another module (thanks Florian Bruhin).
* Don't consider "True" and "False" variable names.
* Abort with error message when invoked on .pyc files.


0.8.1 (2015-09-28)
------------------
* Fix code for Python 3.


0.8 (2015-09-28)
----------------
* Do not flag names imported with "import as" as dead code (thanks Tom Terrace).


0.7 (2015-09-26)
----------------
* Exit with exitcode 1 if path on commandline can't be found.
* Test vulture with vulture using a whitelist module for false positives.
* Add tests that run vulture as a script.
* Add "python setup.py test" command for running tests.
* Add support for tox.
* Raise test coverage to 100%.
* Remove ez_setup.py.


0.6 (2014-09-06)
----------------
* Ignore function names starting with "test\_".
* Parse variable names in new format strings (e.g. "This is {x}".format(x="nice")).
* Only parse alphanumeric variable names in format strings and ignore types.
* Abort with exit code 1 on syntax errors.
* Support installation under Windows by using setuptools (thanks Reuben Fletcher-Costin).


0.5 (2014-05-09)
----------------
* If dead code is found, exit with 1.


0.4.1 (2013-09-17)
------------------
* Only warn if a path given on the command line cannot be found.


0.4 (2013-06-23)
----------------
* Ignore unused variables starting with an underscore.
* Show warning for syntax errors instead of aborting directly.
* Print warning if a file cannot be found.


0.3 (2012-03-19)
----------------
* Add support for python3
* Report unused attributes
* Find tuple assignments in comprehensions
* Scan files given on the command line even if they don't end with .py


0.2 (2012-03-18)
----------------
* Only format nodes in verbose mode (gives 4x speedup).


0.1 (2012-03-17)
----------------
* First release.
