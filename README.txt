vulture - Find dead code
========================

vulture finds unused classes, functions and variables in your code. This helps
you cleanup and find errors in your programs. If you run it on both your
library and test suite you can find untested code.

Due to Python's dynamic nature it is impossible to find all dead code for a
static code analyzer like vulture, because it ignores scopes and scans only
token names. Additionally some dynamic items that are not explicitly called
in the code may be incorrectly reported as dead code.


Features
--------

* Fast: Uses static code analysis
* Lightweight: Only one module
* Tested: Comes with a test suite
* Complements *pyflakes* and has the same output syntax
* Supports Python 2.6, 2.7 and 3.x


Installation
------------

(Install pip: ``sudo apt-get install python-pip``) ::

  $ sudo pip install -U vulture


Usage
-----

::

  $ vulture --help

After you have found and deleted dead code, run vulture again, because it
may discover more dead code.


Similar programs
----------------

* vulture can be used together with *pyflakes*
* The *coverage* module can find unused code more reliably, but requires all
  branches of the code to actually be run.


Feedback
--------

Your feedback is more than welcome. Write emails to jendrikseipp@web.de
or post bugs and feature or pull requests on bitbucket:

https://bitbucket.org/jendrikseipp/vulture/issues


Source download
---------------

The source code is available on bitbucket. Fork away!

https://bitbucket.org/jendrikseipp/vulture
