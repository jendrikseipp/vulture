# Vulture - Find dead code

![CI:Test](https://github.com/jendrikseipp/vulture/workflows/CI/badge.svg)
[![Codecov Badge](https://codecov.io/gh/jendrikseipp/vulture/branch/main/graphs/badge.svg)](https://codecov.io/gh/jendrikseipp/vulture?branch=main)

Vulture finds unused code in Python programs. This is useful for
cleaning up and finding errors in large code bases. If you run Vulture
on both your library and test suite you can find untested code.

Due to Python's dynamic nature, static code analyzers like Vulture are
likely to miss some dead code. Also, code that is only called implicitly
may be reported as unused. Nonetheless, Vulture can be a very helpful
tool for higher code quality.

## Features

* fast: uses static code analysis
* tested: tests itself and has complete test coverage
* complements pyflakes and has the same output syntax
* sorts unused classes and functions by size with `--sort-by-size`

## Installation

    $ pip install vulture

## Usage

    $ vulture myscript.py  # or
    $ python3 -m vulture myscript.py
    $ vulture myscript.py mypackage/
    $ vulture myscript.py --min-confidence 100  # Only report 100% dead code.

The provided arguments may be Python files or directories. For each
directory Vulture analyzes all contained
<span class="title-ref">\*.py</span> files.

After you have found and deleted dead code, run Vulture again, because
it may discover more dead code.

## Types of unused code

In addition to finding unused functions, classes, etc., Vulture can detect
unreachable code. Each chunk of dead code is assigned a *confidence value*
between 60% and 100%, where a value of 100% signals that it is certain that the
code won't be executed. Values below 100% are *very rough* estimates (based on
the type of code chunk) for how likely it is that the code is unused.

| Code type | Confidence value |
| ------------------- | -- |
| function/method/class argument, unreachable code | 100% |
| import | 90% |
| attribute, class, function, method, property, variable | 60% |

You can use the `--min-confidence` flag to set the minimum confidence
for code to be reported as unused. Use `--min-confidence 100` to only
report code that is guaranteed to be unused within the analyzed files.

## Handling false positives

When Vulture incorrectly reports chunks of code as unused, you have
several options for suppressing the false positives. If fixing your false
positives could benefit other users as well, please file an issue report.

#### Whitelists

The recommended option is to add used code that is reported as unused to a
Python module and add it to the list of scanned paths. To obtain such a
whitelist automatically, pass `--make-whitelist` to Vulture:

    $ vulture mydir --make-whitelist > whitelist.py
    $ vulture mydir whitelist.py

Note that the resulting `whitelist.py` file will contain valid Python
syntax, but for Python to be able to *run* it, you will usually have to
make some modifications.

We collect whitelists for common Python modules and packages in
`vulture/whitelists/` (pull requests are welcome).

#### Ignoring files

If you want to ignore a whole file or directory, use the `--exclude` parameter
(e.g., `--exclude "*settings.py,*/docs/*.py,*/test_*.py,*/.venv/*.py"`). The
exclude patterns are matched against absolute paths.

#### Flake8 noqa comments

<!-- Hide noqa docs until we decide whether we want to support it.
Another way of ignoring errors is to annotate the line causing the false
positive with `# noqa: <ERROR_CODE>` in a trailing comment (e.g., `#
noqa: V103`). The `ERROR_CODE` specifies what kind of dead code to
ignore (see the table below for the list of error codes). In case no
error code is specified, Vulture ignores all results for the line.
(Note that the line number for decorated objects is the line number of
the first decorator.)
-->

For compatibility with [flake8](https://flake8.pycqa.org/), Vulture
supports the [F401 and
F841](https://flake8.pycqa.org/en/latest/user/error-codes.html) error
codes for ignoring unused imports (`# noqa: F401`) and unused local
variables (`# noqa: F841`). However, we recommend using whitelists instead
of `noqa` comments, since `noqa` comments add visual noise to the code and
make it harder to read.

#### Ignoring names

You can use `--ignore-names foo*,ba[rz]` to let Vulture ignore all names
starting with `foo` and the names `bar` and `baz`. Additionally, the
`--ignore-decorators` option can be used to ignore the names of functions
decorated with the given decorator (but not their arguments or function body).
This is helpful for example in Flask
projects, where you can use `--ignore-decorators "@app.route"` to ignore all
function names with the `@app.route` decorator. Note that Vulture simplifies
decorators it cannot parse: `@foo.bar(x, y)` becomes "@foo.bar" and
`@foo.bar(x, y).baz` becomes "@" internally.

We recommend using whitelists instead of `--ignore-names` or
`--ignore-decorators` whenever possible, since whitelists are
automatically checked for syntactic correctness when passed to Vulture
and often you can even pass them to your Python interpreter and let it
check that all whitelisted code actually still exists in your project.

#### Marking unused variables

There are situations where you can't just remove unused variables, e.g.,
in function signatures. The recommended solution is to use the `del`
keyword as described in the
[PyLint manual](http://pylint-messages.wikidot.com/messages:w0613) and on
[StackOverflow](https://stackoverflow.com/a/14836005):

```python
def foo(x, y):
    del y
    return x + 3
```

Vulture will also ignore all variables that start with an underscore, so
you can use `_x, y = get_pos()` to mark unused tuple assignments or
function arguments, e.g., `def foo(x, _y)`.

#### Minimum confidence

Raise the minimum [confidence value](#types-of-unused-code) with the `--min-confidence` flag.

#### Unreachable code

If Vulture complains about code like `if False:`, you can use a Boolean
flag `debug = False` and write `if debug:` instead. This makes the code
more readable and silences Vulture.

#### Forward references for type annotations

See [#216](https://github.com/jendrikseipp/vulture/issues/216). For
example, instead of `def foo(arg: "Sequence"): ...`, we recommend using

``` python
from __future__ import annotations

def foo(arg: Sequence):
    ...
```


## Configuration

You can also store command line arguments in `pyproject.toml` under the
`tool.vulture` section. Simply remove leading dashes and replace all
remaining dashes with underscores.

Options given on the command line have precedence over options in
`pyproject.toml`.

Example Config:

``` toml
[tool.vulture]
exclude = ["*file*.py", "dir/"]
ignore_decorators = ["@app.route", "@require_*"]
ignore_names = ["visit_*", "do_*"]
make_whitelist = true
min_confidence = 80
paths = ["myscript.py", "mydir", "whitelist.py"]
sort_by_size = true
verbose = true
```

Vulture will automatically look for a `pyproject.toml` in the current working directory.

To use a `pyproject.toml` in another directory, you can use the `--config path/to/pyproject.toml` flag.

## Integrations

You can use a [pre-commit](https://pre-commit.com/#install) hook to run
Vulture before each commit. For this, install pre-commit and add the
following to the `.pre-commit-config.yaml` file in your repository:

```yaml
repos:
  - repo: https://github.com/jendrikseipp/vulture
    rev: 'v2.3'  # or any later Vulture version
    hooks:
      - id: vulture
```

Then run `pre-commit install`. Finally, create a `pyproject.toml` file
in your repository and specify all files that Vulture should check under
`[tool.vulture] --> paths` (see above).

There's also a [GitHub Action for Vulture](https://github.com/gtkacz/vulture-action).

## How does it work?

Vulture uses the `ast` module to build abstract syntax trees for all
given files. While traversing all syntax trees it records the names of
defined and used objects. Afterwards, it reports the objects which have
been defined, but not used. This analysis ignores scopes and only takes
object names into account.

Vulture also detects unreachable code by looking for code after
`return`, `break`, `continue` and `raise` statements, and by searching
for unsatisfiable `if`- and `while`-conditions.

## Sort by size

When using the `--sort-by-size` option, Vulture sorts unused code by its
number of lines. This helps developers prioritize where to look for dead
code first.

## Examples

Consider the following Python script (`dead_code.py`):

``` python
import os

class Greeter:
    def greet(self):
        print("Hi")

def hello_world():
    message = "Hello, world!"
    greeter = Greeter()
    func_name = "greet"
    greet_func = getattr(greeter, func_name)
    greet_func()

if __name__ == "__main__":
    hello_world()
```

Calling :

    $ vulture dead_code.py

results in the following output:

    dead_code.py:1: unused import 'os' (90% confidence)
    dead_code.py:4: unused function 'greet' (60% confidence)
    dead_code.py:8: unused variable 'message' (60% confidence)

Vulture correctly reports `os` and `message` as unused but it fails to
detect that `greet` is actually used. The recommended method to deal
with false positives like this is to create a whitelist Python file.

**Preparing whitelists**

In a whitelist we simulate the usage of variables, attributes, etc. For
the program above, a whitelist could look as follows:

``` python
# whitelist_dead_code.py
from dead_code import Greeter
Greeter.greet
```

Alternatively, you can pass `--make-whitelist` to Vulture and obtain an
automatically generated whitelist.

Passing both the original program and the whitelist to Vulture

    $ vulture dead_code.py whitelist_dead_code.py

makes Vulture ignore the `greet` method:

    dead_code.py:1: unused import 'os' (90% confidence)
    dead_code.py:8: unused variable 'message' (60% confidence)

<!-- Hide noqa docs until we decide whether we want to support it.
**Using "# noqa"**

```python
import os  # noqa

class Greeter:  # noqa: V102
    def greet(self):  # noqa: V103
        print("Hi")
```

## Error codes

For compatibility with [flake8](https://flake8.pycqa.org/), Vulture
supports the [F401 and
F841](https://flake8.pycqa.org/en/latest/user/error-codes.html) error
codes.

| Error codes |    Description    |
| ----------- | ----------------- |
| V101        | Unused attribute  |
| V102        | Unused class      |
| V103        | Unused function   |
| V104, F401  | Unused import     |
| V105        | Unused property   |
| V106        | Unused method     |
| V107, F841  | Unused variable   |
| V201        | Unreachable code  |

-->

## Exit codes

| Exit code |                          Description                          |
| --------- | ------------------------------------------------------------- |
|     0     | No dead code found                                            |
|     1     | Invalid input (file missing, syntax error, wrong encoding)    |
|     2     | Invalid command line arguments                                |
|     3     | Dead code found                                               |

## Similar programs

  - [pyflakes](https://pypi.org/project/pyflakes/) finds unused imports
    and unused local variables (in addition to many other programmatic
    errors).
  - [coverage](https://pypi.org/project/coverage/) finds unused code
    more reliably than Vulture, but requires all branches of the code to
    actually be run.
  - [uncalled](https://pypi.org/project/uncalled/) finds dead code by
    using the abstract syntax tree (like Vulture), regular expressions,
    or both.
  - [dead](https://pypi.org/project/dead/) finds dead code by using the
    abstract syntax tree (like Vulture).

## Participate

Please visit <https://github.com/jendrikseipp/vulture> to report any
issues or to make pull requests.

  - Contributing guide:
    [CONTRIBUTING.md](https://github.com/jendrikseipp/vulture/blob/main/CONTRIBUTING.md)
  - Release notes:
    [CHANGELOG.md](https://github.com/jendrikseipp/vulture/blob/main/CHANGELOG.md)
  - Roadmap:
    [TODO.md](https://github.com/jendrikseipp/vulture/blob/main/TODO.md)
