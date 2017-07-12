TODOs
=====

* Return with exit code 1 when syntax errors are found or files can't be read.
* Detect unreachable code à la `if False:` (try to evaluate condition).
* Detect dead code after return statements.
* Parse all variable names in new format strings (vars with special formatting, etc.)
  Use string.Formatter.parse for this.
* Once we drop Python 2.6 compatibility use argparse instead of optparse.
* Extend whitelist files.
* Distribute and test vulture wheel file.
* Add get_unused_code() method.
* Let Item inherit from "object", not from "str". The new class needs
  members "name", "__eq__" (returns name) and "__hash__" (returns hash(name)).
* Only count lines for unused code.
* If count_lines() is fast enough, always list the number of lines in the output.

Non-TODOs
=========

* Ignore hidden files and directories (might be unexpected, use --exclude instead).
* Differentiate between functions and methods. For our purposes methods are
  functions with a "self" parameter and they are stored as attributes, not as
  variables (unclear if this has many benefits).


Notes
=====

* Use astroid if we ever want to support scopes.
