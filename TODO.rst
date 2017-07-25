TODOs
=====

* Detect unreachable code à la `if False:` (try to evaluate condition).
* Detect dead code after return statements (when visiting a function
  definition, check if there are AST nodes after a return AST node).
* Parse all variable names in new format strings (vars with special formatting, etc.).
  Use string.Formatter.parse for this.
* Once we drop Python 2.6 compatibility use argparse instead of optparse.
* Extend whitelist files.
* Distribute and test vulture wheel file.
* Only count lines for unused code (by storing the node in Item), then
  always list the number of lines in the output.
* If an unused item is defined multiple times, report it multiple times.
* Estimate size for all types of code.
  * Use Assign instead of Name AST nodes for estimating the size of assignments.
* Support Python 3.5 async/await (#20).


Non-TODOs
=========

* Ignore hidden files and directories (might be unexpected, use --exclude instead).
* Differentiate between functions and methods. For our purposes methods are
  functions with a "self" parameter and they are stored as attributes, not as
  variables. However, we can't differentiate between function and method executions.


Notes
=====

* Use astroid if we ever want to support scopes.
