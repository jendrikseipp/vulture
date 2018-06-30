TODOs
=====

* Use coverage.py to detect false-positives (#109).
* Write script for turning SIP files into whitelists (#8).
* Add PyQT whitelist to Vulture repo?


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
* Compute sizes on demand. Storing nodes increases memory usage from
  ~120 MiB to ~580 MiB for tensorflow's Python code.
* Detect unreachable code for ``ast.IfExp`` (rarely used, even more rarely "unused").
* Detect unreachable code for ``ast.Assert`` (``assert False`` is common idiom
  for aborting rogue code).
* Detect superfluous expressions like ``a <= b``, ``42``,  ``foo and bar``
  occuring outside of a statement (hard to detect if code is unneeded).
* Detect that body of ``if foo:`` is unreachable if foo is only assigned "false" values
  (complicated: e.g., foo = []; foo.append(1); if foo: ...).
