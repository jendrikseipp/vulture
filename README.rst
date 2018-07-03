Vulture - Find dead code
========================

.. image:: https://travis-ci.org/jendrikseipp/vulture.svg?branch=master
   :target: https://travis-ci.org/jendrikseipp/vulture
   :alt: Travis CI build status (Linux)

.. image:: https://ci.appveyor.com/api/projects/status/github/jendrikseipp/vulture?svg=true
   :target: https://ci.appveyor.com/project/jendrikseipp96693/vulture
   :alt: AppVeyor CI build status (Windows)

.. image:: https://coveralls.io/repos/github/jendrikseipp/vulture/badge.svg?branch=master
   :target: https://coveralls.io/github/jendrikseipp/vulture?branch=master

Vulture finds unused code in Python programs. This is useful for
cleaning up and finding errors in large code bases. If you run Vulture
on both your library and test suite you can find untested code.

Due to Python's dynamic nature, static code analyzers like Vulture are
likely to miss some dead code. Also, code that is only called implicitly
may be reported as unused. Nonetheless, Vulture can be a very helpful
tool for higher code quality.


Features
--------

* fast: static code analysis
* tested: tests itself and has complete test coverage
* complements pyflakes and has the same output syntax
* sorts unused classes and functions by size with ``--sort-by-size``
* supports Python 2.7 and Python >= 3.4


Installation
------------

::

  $ pip install vulture  # from PyPI
  $ pip install .        # from cloned repo


Usage
-----

::

  $ vulture myscript.py  # or
  $ python3 -m vulture myscript.py
  $ vulture myscript.py mypackage/
  $ vulture myscript.py --min-confidence 100  # Only report 100% dead code.

The provided arguments may be Python files or directories. For each
directory Vulture analyzes all contained `*.py` files.

After you have found and deleted dead code, run Vulture again, because
it may discover more dead code.

**Handling false positives**

You can add used code that is reported as unused to a Python module and
add it to the list of scanned paths. To obtain such a whitelist
automatically, pass ``--make-whitelist`` to Vulture. ::

  $ vulture mydir --make-whitelist > whitelist.py
  $ vulture mydir whitelist.py

We collect whitelists for common Python modules and packages in
``vulture/whitelists/`` (pull requests are welcome). If you want to
ignore a whole file or directory, use the ``--exclude`` parameter (e.g.,
``--exclude *settings.py,docs/``).

**Marking unused variables**

There are situations where you can't just remove unused variables, e.g.,
in tuple assignments or function signatures. Vulture will ignore these
variables if they start with an underscore (e.g., ``_x, y = get_pos()``).

**Minimum confidence**

You can use the ``--min-confidence`` flag to set the minimum confidence
for code to be reported as unused. Use ``--min-confidence 100`` to only
report code that is guaranteed to be unused within the analyzed files.


How does it work?
-----------------

Vulture uses the ``ast`` module to build abstract syntax trees for all
given files. While traversing all syntax trees it records the names of
defined and used objects. Afterwards, it reports the objects which have
been defined, but not used. This analysis ignores scopes and only takes
object names into account.

Vulture also detects unreachable code by looking for code after
``return``, ``break``, ``continue`` and ``raise`` statements, and by
searching for unsatisfiable ``if``- and ``while``-conditions.


Sort by size
------------

When using the ``--sort-by-size`` option, Vulture sorts unused code by
its number of lines. This helps developers prioritize where to look for
dead code first.



Examples
--------

Consider the following Python script (``dead_code.py``):

.. code:: python

    import os

    class Greeter:
        def greet(self):
            print("Hi")

    def hello_world():
        message = "Hello, world!"
        greeter = Greeter()
        greet_func = getattr(greeter, "greet")
        greet_func()

    if __name__ == "__main__":
        hello_world()

Calling ::

    vulture dead_code.py

results in the following output::

    dead_code.py:1: unused import 'os' (90% confidence)
    dead_code.py:4: unused function 'greet' (60% confidence)
    dead_code.py:8: unused variable 'message' (60% confidence)

Vulture correctly reports "os" and "message" as unused, but it fails to
detect that "greet" is actually used. The recommended method to deal with
false positives like this is to create a whitelist Python file.

**Preparing whitelists**

In a whitelist we simulate the usage of variables, attributes, etc. For
the program above, a whitelist could look as follows:

.. code:: python

    # whitelist_dead_code.py
    from dead_code import Greeter
    Greeter.greet

Alternatively, you can pass ``--make-whitelist`` to Vulture and obtain
an automatically generated whitelist.

Passing both the original program and the whitelist to Vulture ::

    vulture dead_code.py whitelist_dead_code.py

makes Vulture ignore the "greet" method::

    dead_code.py:1: unused import 'os' (90% confidence)
    dead_code.py:8: unused variable 'message' (60% confidence)


Exit codes
----------

+-----------+---------------------------------------------------------------+
| Exit code |                          Description                          |
+===========+===============================================================+
|     0     | No dead code found                                            |
+-----------+---------------------------------------------------------------+
|     1     | Dead code found                                               |
+-----------+---------------------------------------------------------------+
|     1     | Invalid input (file missing, syntax error, wrong encoding)    |
+-----------+---------------------------------------------------------------+
|     2     | Invalid command line arguments                                |
+-----------+---------------------------------------------------------------+


Similar programs
----------------

* Vulture can be used together with *pyflakes*
* The *coverage* module can find unused code more reliably, but requires
  all branches of the code to actually be run.


Participate
-----------

Please visit https://github.com/jendrikseipp/vulture to report any
issues or to make pull requests.

* Contributing guide: `CONTRIBUTING.rst <https://github.com/jendrikseipp/vulture/blob/master/CONTRIBUTING.rst>`_
* Changelog: `NEWS.rst <https://github.com/jendrikseipp/vulture/blob/master/NEWS.rst>`_
* Roadmap: `TODO.rst <https://github.com/jendrikseipp/vulture/blob/master/TODO.rst>`_
