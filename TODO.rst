TODOs
=====

* Detect unreachable code à la ``if False:`` (try to evaluate condition).
  * Later more AST nodes: If, IfExp, While, Assert.
* Detect dead code after return statements (check if there are AST nodes
  after an ast.Return node in the same list of AST nodes). Generalize
  this for ``break``, ``continue`` and ``raise``.
* Once we drop Python 2.6 compatibility use argparse instead of optparse.
* Only count lines for unused code by storing a function ``get_size`` in
  Item for computing the size on demand. Then always list the number of
  lines in the output.
* Support Python 3.5 async/await (#20).
* Add confidence values to Items and ``--min-confidence`` flag.


Non-TODOs
=========

* Ignore hidden files and directories (might be unexpected, use --exclude instead).
* Differentiate between functions and methods. For our purposes methods are
  functions with a "self" parameter and they are stored as attributes, not as
  variables. However, we can't differentiate between function and method executions.
* Use Assign instead of Name AST nodes for estimating the size of assignments (KISS).


Notes
=====

* Use astroid if we ever want to support scopes.
