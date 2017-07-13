import ast
from collections import namedtuple
from functools import wraps
import sys

ENTRY_POINTS = (ast.ClassDef, ast.FunctionDef)

TRAVERSABLE_FIELDS = {
        ast.ClassDef: ('decorator_list', 'body', ),
        ast.ExceptHandler: ('body',),
        ast.For: ('body', 'orelse'),
        ast.FunctionDef: ('decorator_list', 'body',),
        ast.If: ('body', 'orelse'),
        ast.Module: ('body',),
        ast.While: ('body', 'orelse'),
        ast.With: ('body',),
}
if sys.version_info < (3, 0):
    TRAVERSABLE_FIELDS.update({
        ast.TryExcept: ('body', 'handlers', 'orelse'),
        ast.TryFinally: ('body', 'finalbody'),
    })
else:
    TRAVERSABLE_FIELDS.update({
        ast.Try: ('body', 'handlers', 'orelse', 'finalbody')
    })


# Reinventing wheel here to keep vulture lightweight.
def memoize(func):
    _cache = {}

    @wraps(func)
    def wrapped(*args):
        try:
            return _cache[args]
        except KeyError:
            _cache[args] = result = func(*args)
            return result
    return wrapped


@memoize
def estimate_lines(node):
    """
    Recursively count child AST nodes under `node`. It is an approximation
    of the amount of code belonging to the node, which is useful for
    sorting the list of unused code that a developer might want to remove.
    """
    return 1 + sum(estimate_lines(child)
                   for field in TRAVERSABLE_FIELDS.get(node.__class__, ())
                   for child in getattr(node, field))


def _get_range(entry):
    if isinstance(entry, ENTRY_POINTS):
        last_body = entry.body[-1]
        while isinstance(last_body, tuple(TRAVERSABLE_FIELDS.keys())):
            fields = TRAVERSABLE_FIELDS[last_body.__class__]
            for field in reversed(fields):
                children = getattr(last_body, field)
                if children:
                    break
            last_body = children[-1]  # The last child.

        last_line = last_body.lineno
        SourceRange = namedtuple("SourceRange",
                                 ['name', 'start_line', 'last_line'])
        source_range = SourceRange(entry.name, entry.lineno, last_line)
        yield source_range


def count_lines(code):
    span = 1
    for source_range in _get_range(code):
        span = (1 + source_range.last_line - source_range.start_line)
    return span
