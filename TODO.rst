TODOs
=====

* Return with exit code 1 when syntax errors are found or files can't be read.
* Detect unreachable code à la `if False:` (try to evaluate condition).
* Parse all variable names in new format strings (vars with special formatting, etc.)
  Use string.Formatter.parse for this.
* Once we drop Python 2.6 compatibility use argparse instead of optparse.
* Add whitelists directory. It should contain whitelist_python.py for now.
  The file should contain code that traverses an AST and code that uses
  these functions explicitly. Then whitelist.py becomes obsolete. It
  should also contain the code and whitelist code for default_factory.


Non-TODOs
=========

* Ignore hidden files and directories (might be unexpected, use --exclude instead).
* Differentiate between functions and methods. For our purposes methods are
  functions with a "self" parameter and they are stored as attributes, not as
  variables (unclear if this has many benefits).


Notes
=====

* Use astroid if we ever want to support scopes.
