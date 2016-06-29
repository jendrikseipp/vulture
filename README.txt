vulture - Find dead code
========================

Vulture finds unused classes, functions and variables in your code.
This helps you cleanup and find errors in your programs. If you run it
on both your library and test suite you can find untested code.

Due to Python's dynamic nature, static code analyzers like vulture are
likely to miss some dead code. Also, code that is only called
implicitly may be reported as unused. Nonetheless, vulture can be a
very helpful tool for higher code quality.


Features
--------

* fast: uses static code analysis
* lightweight: only one module
* tested: tests itself and has 100% test coverage
* complements *pyflakes* and has the same output syntax
* supports Python 2.6, 2.7 and 3.x


Installation
------------

::

  $ pip install -U vulture


Usage
-----

::

  $ vulture --help

After you have found and deleted dead code, run vulture again, because
it may discover more dead code. You can add false-positives (used code
that is marked as unused) to a python module and add it to the list of
scanned paths (see ``whitelist.py`` for an example).


How does it work?
-----------------

Vulture uses the ``ast`` module to build abstract syntax trees for all
given files. While traversing all syntax trees it records the names of
defined and used objects. Afterwards, it reports the objects which have
been defined, but not used. This analysis ignores scopes and focuses
only on object names.


Similar programs
----------------

* vulture can be used together with *pyflakes*
* The *coverage* module can find unused code more reliably, but requires
  all branches of the code to actually be run.


Feedback
--------

Your feedback is more than welcome. Write emails to jendrikseipp@web.de
or post bugs and feature or pull requests on bitbucket:

https://bitbucket.org/jendrikseipp/vulture/issues


Source download
---------------

The source code is available on bitbucket. Fork away!

https://bitbucket.org/jendrikseipp/vulture
