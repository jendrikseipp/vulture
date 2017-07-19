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
* Let Item inherit from "object", not from "str". The new class needs
  members "name", "__eq__" (returns name) and "__hash__" (returns hash(name)).
  * Store used_vars, used_attrs, tuple_assign_vars and names_imported_as_aliases
    as plain str objects in new LoggingSet classes. Use better names for the sets.
* Only count lines for unused code, then always list the number of lines in the output.
* If an unused item is defined multiple times, report it multiple times.
  (Item needs to inherit from "object" first).
* Rethink which attribute names should be ignored.
* Unify ignore-mechanism. Use decorator for logging.


Non-TODOs
=========

* Ignore hidden files and directories (might be unexpected, use --exclude instead).
* Differentiate between functions and methods. For our purposes methods are
  functions with a "self" parameter and they are stored as attributes, not as
  variables. However, we can't differentiate between function and method executions.


Notes
=====

* Use astroid if we ever want to support scopes.
