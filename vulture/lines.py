import ast
from functools import wraps
import sys

TRAVERSABLE_FIELDS = {
        ast.ClassDef: ('body', 'decorator_list'),
        ast.ExceptHandler: ('body',),
        ast.For: ('body', 'orelse'),
        ast.FunctionDef: ('body', 'decorator_list'),
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
