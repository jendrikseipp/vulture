# TODOs

* Add --ignore-attributes-for-classes option. When visiting such a class,
  mark all its attributes as used. Fixes (partly):
    * https://github.com/jendrikseipp/vulture/issues/309
    * https://github.com/jendrikseipp/vulture/issues/264
    * https://github.com/jendrikseipp/vulture/issues/249
    * https://github.com/jendrikseipp/vulture/issues/315
  Use these as test cases.
* Honor (speaking) pylint error codes (e.g., # pylint:
  disable=unused-import): unused-import, unused-variable, unused-argument,
  possibly-unused-variable and unreachable-code. See
  https://github.com/janjur/readable-pylint-messages#unused-import.

# Non-TODOs

* Ignore hidden files and directories (might be unexpected, use
  --exclude instead).
* Use Assign instead of Name AST nodes for estimating the size of
  assignments (KISS).
* Only count lines for unused code by storing a function `get_size` in
  Item for computing the size on demand. This is 1.5 times as slow as
  computing no sizes.
* Compute sizes on demand. Storing nodes increases memory usage from
  ~120 MiB to ~580 MiB for tensorflow's Python code.
* Detect unreachable code for `ast.Assert` (`assert False` is common
  idiom for aborting rogue code).
* Detect superfluous expressions like `a <= b`, `42`, `foo and bar`
  occurring outside of a statement (hard to detect if code is
  unneeded).
* Detect that body of `if foo:` is unreachable if foo is only assigned
  "false" values (complicated: e.g., foo = \[\]; foo.append(1); if
  foo: ...).
* Use coverage.py to detect false-positives (\#109). Workflow too
  complicated.
* Ignore some decorators by default: @app.route, @cli.command.
* Ignore functions in conftest.py files that start with "pytest_".
