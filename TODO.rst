TODOs
=====

* Detect unreachable code à la ``while False:`` (by implementing
  ``Vulture.visit_While(self, node)``.
* Detect unreachable code à la ``if False:`` (by implementing
  ``Vulture.visit_If(self, node)``.
  * Detect unreachable ``else`` clauses by detecting ``if True:``.
* Detect unreachable code for ``ast.IfExp``.
* Detect unreachable code for ``ast.Assert``.
* Support Python 3.5 async/await (#20).
* Detect superfluous expressions like ``a <= b``, ``42``,  ``foo and bar``
  occuring outside of a statement.
* Pass relevant options directly to ``scavenge()`` and ``report()``.
* Update README file.
* Once we drop Python 2.6 compatibility use argparse instead of optparse.


Non-TODOs
=========

* Ignore hidden files and directories (might be unexpected, use --exclude instead).
* Differentiate between functions and methods. For our purposes methods are
  functions with a "self" parameter and they are stored as attributes, not as
  variables. However, we can't differentiate between function and method executions.
* Use Assign instead of Name AST nodes for estimating the size of assignments (KISS).
* Only count lines for unused code by storing a function ``get_size`` in
  Item for computing the size on demand. This is 1.5 times as slow as computing
  no sizes.
* Always report number of lines. Increases runtime by a factor of ~1.08.


Notes
=====

* Use astroid if we ever want to support scopes.
